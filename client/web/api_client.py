import json
import socket
import sys
import typing

import http.client

from client.web.models.create_doc_request import CreateDocRequest
from client.web.models.docs_list_response import DocsListResponse, DocsListItem
from client.web.models.update_doc_request import UpdateDocRequest
from client.web.models.update_doc_response import UpdateDocResponse


def catch_parse_errors(func: typing.Callable) -> typing.Callable:
    def wrapped(*args, **kwargs) -> typing.Any:
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError) as exc:
            print(exc, file=sys.stderr)
            raise http.client.ResponseNotReady('Unexpected response')
        except socket.error as exc:
            print(exc, file=sys.stderr)
            raise http.client.HTTPException('Socket error')

    return wrapped


class ApiClient:
    def __init__(
        self, host: str, Connection: typing.Type = http.client.HTTPConnection
    ):
        self._host = host
        self._Connection = Connection

    @catch_parse_errors
    def login(self, login: str) -> int:
        if not isinstance(login, str):
            raise http.client.CannotSendRequest(
                'body should be instance of str'
            )

        response = self._request('POST', '/login', {'login': login})
        return response['user_id']

    @catch_parse_errors
    def update_doc(self, body: UpdateDocRequest) -> UpdateDocResponse:
        if not isinstance(body, UpdateDocRequest):
            raise http.client.CannotSendRequest(
                'body should be instance of UpdateDocRequest'
            )

        response = self._request('POST', '/update_doc', body.to_dict())
        return UpdateDocResponse(**response)

    @catch_parse_errors
    def create_doc(self, body: CreateDocRequest):
        if not isinstance(body, CreateDocRequest):
            raise http.client.CannotSendRequest(
                "body should be instance of CreateDocRequest"
            )

        self._request('POST', '/create_doc', body.to_dict())

    @catch_parse_errors
    def list_all_docs(self) -> DocsListResponse:
        response = self._request('GET', '/list_all_docs', {})
        docs = []
        for item in response['docs']:
            docs.append(DocsListItem(**item))
        return DocsListResponse(docs)

    def _request(self, method: str, query: str, body: dict) -> dict:
        conn = self._Connection(self._host, timeout=4)
        headers = {'Content-type': 'application/json'}
        json_body = json.dumps(body)
        conn.request(method, query, json_body, headers)
        response = conn.getresponse()
        if response.getcode() != 200:
            raise http.client.HTTPException('Request failed')
        return json.loads(response.read().decode())
