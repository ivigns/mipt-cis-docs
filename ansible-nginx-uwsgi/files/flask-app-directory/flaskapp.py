# -*- coding: utf-8 -*-
import json
import psycopg2
import hashlib
import logging

from flask import Flask, jsonify, request, Response
from connector import Connector

DEFAULT_DOCS_INFO_TABLE = "prod_docs"
DEFAULT_DOCS_TEXTS_TABLE = "prod_docs_texts"
DEFAULT_USERS_TABLE = "prod_users"

app = Flask(__name__)

logFormatStr = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatStr, filename="flaskapp.log", level=logging.DEBUG)
formatter = logging.Formatter(logFormatStr, '%m-%d %H:%M:%S')
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)
streamHandler.setFormatter(formatter)
app.logger.addHandler(streamHandler)
app.logger.info("Logging is set up.")
app.logger.info("Service started")

postgresConnection = psycopg2.connect(user="pg_admin_user",
                                      password="pg_admin_pw",
                                      database="pg_default_db",
                                      host='172.17.0.2'
)
postgresConnection.autocommit = True
cursor = postgresConnection.cursor()
field_to_id_docs_info = {
    "shadow": 0,
    "backup": 1,
    "doc_id": 2,
    "user_id": 3,
    "server_version": 4,
    "client_version": 5
}
field_to_id_docs_texts = {
    "curr_text": 0,
    "doc_id": 1,
    "title": 2
}
db_connector = Connector(docs_info_table_name=DEFAULT_DOCS_INFO_TABLE,
                         docs_texts_table_name=DEFAULT_DOCS_TEXTS_TABLE,
                         users_table_name=DEFAULT_USERS_TABLE,
                         field_to_id_docs_info=field_to_id_docs_info,
                         field_to_id_docs_texts=field_to_id_docs_texts,
                         connection=postgresConnection,
                         logger=app.logger)

db_connector.check_docs_table()
db_connector.check_users_table()


@app.route('/login', methods=['POST'])
def login():
    request_data = request.get_json()
    user_login = request_data['login']
    m = hashlib.md5()
    m.update(user_login.encode('utf-8'))
    user_id = str(int(m.hexdigest(), 16))[0:8]
    auth = db_connector.set_login(user_login, user_id)
    if auth:
        return json.dumps({'user_id': int(user_id)}), 200
    else:
        return jsonify(success=False), 403
    
    
@app.route('/logout', methods=['POST'])
def logout():
    request_data = request.get_json()
    user_login = request_data['login']
    db_connector.logout(user_login)
    return jsonify(success=True), 200


@app.route('/create_doc', methods=['POST'])
def create_doc():
    request_data = request.get_json()
    title = request_data['title']
    user_id = int(request_data['user_id'])
    doc_id = int(request_data['doc_id'])
    db_connector.create_doc(title, doc_id, user_id)
    return jsonify(success=True), 200


@app.route('/update_doc', methods=['POST'])
def update_doc():
    request_data = request.get_json()
    edits = request_data['edits']
    received_version = int(request_data['version'])
    doc_id = int(request_data['doc_id'])
    user_id = int(request_data['user_id'])
    new_version, new_edits = db_connector.update_doc(doc_id, user_id, received_version, edits)
    return json.dumps({'edits': new_edits.get_values_list() or [],
                       'version': new_version}), 200


@app.route('/get_doc', methods=['GET'])
def get_doc():
    request_data = request.get_json()
    doc_id = int(request_data['doc_id'])
    user_id = int(request_data['user_id'])
    client_version = db_connector.get_client_version(doc_id, user_id)
    server_version = db_connector.get_server_version(doc_id, user_id)
    text = db_connector.get_text(doc_id, user_id)
    return json.dumps({'client_version': client_version,
                       'server_version': server_version,
                       'text': text}), 200


@app.route('/list_all_docs', methods=['GET'])
def list_all_docs():
    docs = db_connector.list_all_docs()
    return json.dumps({'docs': docs or []}), 200


@app.route('/logs', methods=['GET'])
def return_logs():
    with open("/srv/myapp/appdata/flaskapp.log","r") as file:
        content = file.readlines()
    return Response(content, mimetype='text/plain')


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
