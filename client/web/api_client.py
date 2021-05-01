import json
from client.web.models.update_doc_request import UpdateDocRequest
from client.web.models.update_doc_response import UpdateDocResponse
from client.web.models.create_doc_request import CreateDocRequest

import http.client


class ApiClient:
    def __init__(self, host):
        self.host = host

    def update_doc(self, body):
        if not isinstance(body, UpdateDocRequest):
            raise ValueError("body should be instance of UpdateDocRequest")

        conn = http.client.HTTPSConnection(self.host)
        headers = {'Content-type': 'application/json'}
        json_body = json.dumps(body.to_dict())

        conn.request('POST', '/update_doc', json_body, headers)

        response = conn.getresponse()

        return UpdateDocResponse(**json.loads(response.read().decode()))

    def create_docs(self, body):
        if not isinstance(body, CreateDocRequest):
            raise ValueError("body should be instance of CreateDocRequest")

        conn = http.client.HTTPSConnection(self.host)
        headers = {'Content-type': 'application/json'}
        json_body = json.dumps(body.to_dict())

        conn.request('POST', '/create_doc', json_body, headers)

        response = conn.getresponse()

        return json.loads(response.read().decode())

    def get_doc(self, doc_id, user_id):
        conn = http.client.HTTPSConnection(self.host)
        headers = {'Content-type': 'application/json'}
        json_body = json.dumps({'doc_id': doc_id, 'user_id': user_id})

        conn.request('GET', '/get_doc', json_body, headers)

        response = conn.getresponse()

        return json.loads(response.read().decode())

    def list_all_docs(self, user_id):
        conn = http.client.HTTPSConnection(self.host)
        headers = {'Content-type': 'application/json'}
        json_body = json.dumps({'user_id': user_id})

        conn.request('GET', '/list_all_docs', json_body, headers)

        response = conn.getresponse()

        return json.loads(response.read().decode())



