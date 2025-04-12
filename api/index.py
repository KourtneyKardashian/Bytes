from flask import Flask, request, jsonify, send_file
import requests
import base64
import zipfile
from io import BytesIO
import os

app = Flask(__name__)

url = 'https://skript.gg/api/user/generic/download_launcher'

def download_and_extract_file(auth_token):
    try:
        headers = {
            'Authorization': f'{auth_token}',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        }

        # Send the GET request to the server
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            base64_string = response.json().get('result', '')

            if base64_string:
                decoded_bytes = base64.b64decode(base64_string)

                # Create a temporary file in the /tmp directory
                temp_file_path = '/tmp/downloaded_file.zip'

                # Save the decoded bytes to the temp file
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(decoded_bytes)

                # Open the zip file and extract the exe file
                with zipfile.ZipFile(temp_file_path) as zip_file_obj:
                    zip_contents = zip_file_obj.namelist()

                    for file_name in zip_contents:
                        if file_name.endswith('.exe'):
                            with zip_file_obj.open(file_name) as exe_file:
                                exe_bytes = exe_file.read()

                            # Optionally remove the temporary file after extraction
                            os.remove(temp_file_path)
                            return exe_bytes

            return None
        else:
            return None
    except Exception as e:
        print(f"Error during download or extraction: {e}")
        return None

@app.route('/download-exe', methods=['POST'])
def download_exe():
    try:
        data = request.get_json()
        auth_token = data.get('Authorization', '')

        if not auth_token:
            return jsonify({"error": "Authorization token is missing"}), 400

        exe_data = download_and_extract_file(auth_token)

        if exe_data:
            return send_file(
                BytesIO(exe_data),
                as_attachment=True,
                download_name="extracted_file.exe",
                mimetype="application/octet-stream"
            )
        else:
            return jsonify({"error": "Failed to download or extract the file"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
