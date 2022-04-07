import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from subprocess import TimeoutExpired
from config import config
from common.convert import LibreOfficeError, convert_to
from common.errors import RestAPIError, InternalServerErrorError
from common.files import uploads_url, save_to

app = Flask(__name__, static_url_path='')

@app.route('/')
def hello():
    return "OK"

@app.route('/upload', methods=['POST'])
def upload_file():
    source = save_to(os.path.join(config['uploads_dir'], 'source'), request.files['file'])

    try:
        result = convert_to(os.path.join(config['uploads_dir'], 'pdf'), source, timeout=15)
    except LibreOfficeError:
        return jsonify({'result': {'source': uploads_url(source), 'doc-conv-failed': 'LibreOfficeError'}})
    except TimeoutExpired:
        return jsonify({'result': {'source': uploads_url(source), 'doc-conv-failed': 'TimeoutExpired'}})

    return jsonify({'result': {'source': uploads_url(source), 'pdf': uploads_url(result)}})

@app.route('/upload/<path:path>', methods=['GET'])
def download_file(path):
    return send_from_directory(config['uploads_dir'], path)

@app.errorhandler(500)
def handle_500_error():
    return InternalServerErrorError().to_response()

@app.errorhandler(RestAPIError)
def handle_rest_api_error(error):
    return error.to_response()

if __name__ == '__main__':
    app.run(host='127.0.0.1', threaded=True)
