import json

import http.client

from client.web.models.create_doc_request import CreateDocRequest
from client.web.models.docs_list_response import DocsListResponse, DocsListItem
from client.web.models.update_doc_request import UpdateDocRequest
from client.web.models.update_doc_response import UpdateDocResponse


class ApiClient:
    def __init__(self, host):
        self.host = host

    def login(self, login: str) -> int:
        if not isinstance(login, str):
            raise ValueError('body should be instance of str')

        response = self._request('POST', '/login', {'login': login})
        return response['user_id']

    def update_doc(self, body: UpdateDocRequest) -> UpdateDocResponse:
        if not isinstance(body, UpdateDocRequest):
            raise ValueError('body should be instance of UpdateDocRequest')

        response = self._request('POST', '/update_doc', body.to_dict(), headers)
        return UpdateDocResponse(**response)

    def create_doc(self, body: CreateDocRequest):
        if not isinstance(body, CreateDocRequest):
            raise ValueError("body should be instance of CreateDocRequest")

        self._request('POST', '/create_doc', body.to_dict())

    def list_all_docs(self) -> DocsListResponse:
        response = self._request('POST', '/list_all_docs', {})
        docs = []
        for item in response['docs']:
            docs.append(DocsListItem(**item))

        return DocsListResponse(docs)

    def _request(self, method: str, query: str, body: dict) -> dict:
        conn = http.client.HTTPSConnection(self.host)
        headers = {'Content-type': 'application/json'}
        json_body = json.dumps(body)
        conn.request(method, query, json_body, headers)
        response = conn.getresponse()
        return json.loads(response.read().decode())
