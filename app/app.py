from flask import Flask, request, send_file, abort
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# S3 configuration
S3_BUCKET = 'ap-northeast-1'  # ここにバケット名を入力
S3_REGION = 'yuruhack-assets'  # ここにバケットのリージョンを入力

# Boto3 client
s3 = boto3.client('s3', region_name=S3_REGION)


@app.route('/api/assets/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    # ランダムなファイル名を生成
    tmp_file_name = str(uuid.uuid4())

    # ファイルの保存
    tmp_file_path = f"/tmp/{tmp_file_name}"
    file.save(tmp_file_path)

    filename = secure_filename(file.filename)
    try:
        s3.upload_file(tmp_file_path, S3_BUCKET, filename)
        return {'message': 'File uploaded successfully', 'filename': filename}, 200
    except (NoCredentialsError, PartialCredentialsError):
        return {'error': 'Credentials not available'}, 500
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/assets/<file_name>', methods=['GET'])
def get_file(file_name):
    try:
        file_path = f"/tmp/{secure_filename(file_name)}"
        s3.download_file(S3_BUCKET, file_name, file_path)
        return send_file(file_path)
    except (NoCredentialsError, PartialCredentialsError):
        return {'error': 'Credentials not available'}, 500
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
