from flask import Flask, request, jsonify, Response
import requests
import base64
import pyzipper
from io import BytesIO

app = Flask(__name__)

# The URL for the download
url = 'https://skript.gg/api/user/generic/download_launcher'

# The function to download and extract the .exe file
def download_and_extract_file(auth_token):
    try:
        headers = {
            'Authorization': f'{auth_token}',  # Just use the token directly (no 'Bearer')
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        }

        # Send the GET request to the server
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            base64_string = response.json().get('result', '')

            if base64_string:
                # Decode the base64 string
                decoded_bytes = base64.b64decode(base64_string)

                # Save the decoded bytes as a .zip file in memory
                zip_file = BytesIO(decoded_bytes)

                # Extract the .exe file from the password-protected .zip
                password = "skript.gg"
                with pyzipper.AESZipFile(zip_file) as zip_file_obj:
                    zip_file_obj.setpassword(password.encode('utf-8'))
                    zip_contents = zip_file_obj.namelist()

                    for file_name in zip_contents:
                        if file_name.endswith('.exe'):
                            with zip_file_obj.open(file_name) as exe_file:
                                exe_bytes = exe_file.read()
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
        # Get the authorization token from the request
        data = request.get_json()
        auth_token = data.get('Authorization', '')

        if not auth_token:
            return jsonify({"error": "Authorization token is missing"}), 400

        # Download and extract the file
        exe_data = download_and_extract_file(auth_token)

        if exe_data:
            # Send the extracted .exe file as raw bytes in the response
            return Response(
                exe_data,
                content_type='application/octet-stream',  # Generic content type for binary data
                status=200
            )
        else:
            return jsonify({"error": "Failed to download or extract the file"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel expects a handler in the app.py file, but the serverless function handles the routing automatically
