# -*- coding: utf-8 -*-
import json

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/update_doc', methods=['POST'])
def update_doc():
    request_data = request.get_json()
    buffer = request_data['buffer']
    doc_id = int(request_data['doc_id'])
    user_id = int(request_data['user_id'])
    return json.dumps(request_data), 200


@app.route('/get_doc', methods=['GET'])
def get_doc():
    request_data = request.get_json()
    doc_id = int(request_data['doc_id'])
    user_id = int(request_data['user_id'])
    return json.dumps(request_data), 200


@app.route('/list_all_docs', methods=['GET'])
def list_all_docs():
    return json.dumps({'example_doc': 'hello world'}), 200


@app.route('/create_doc', methods=['POST'])
def create_doc():
    request_data = request.get_json()
    user_id = int(request_data['user_id'])
    return json.dumps({'doc creator for user_id': user_id}), 200


@app.route('/health', methods=['GET'])
def return_health():
    resp = jsonify(success=True)
    resp.status_code = 200
    return resp, 200


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return json.dumps({'default': 'response'}), 404


if __name__ == "__main__":
    print("Run with `flask` or a WSGI server!")
