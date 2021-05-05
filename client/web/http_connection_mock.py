import json
import random

import http.client


class HTTPSocketMock:
    def __init__(self, text: str):
        self._text = text

    def decode(self) -> str:
        return self._text


class HTTPResponseMock:
    def __init__(self, response_dict: dict, response_code: int):
        self._text = json.dumps(response_dict)
        self._code = response_code

    def read(self) -> HTTPSocketMock:
        return HTTPSocketMock(self._text)

    def getcode(self) -> int:
        return self._code


docs = [
    {'doc_id': doc_id, 'title': f'Document {i}'}
    for doc_id, i in zip(
        [9392468011745350111, 9407757923520418271, 9418928317413528031],
        range(1, 4),
    )
]


class HTTPConnectionMock:
    ACTUAL_HOST = '1.2.3.4:1234'

    def __init__(self, host: str, **kwargs):
        self._host = host
        self._response_dict = None
        self._response_code = None

    def request(self, method: str, query: str, json_body: str, headers: str):
        assert headers == {'Content-type': 'application/json'}
        # imitate working only on specific host
        if self._host != self.ACTUAL_HOST:
            raise http.client.InvalidURL('bad host')
        # imitate bad service
        if random.randint(0, 100) % 7 == 0:
            self._response_dict = self._response_dict = {
                'code': 'INTERNAL_ERROR',
                'message': 'internal server error',
            }
            self._response_code = 500
            return

        # imitate handlers
        body = json.loads(json_body)
        if (method, query) == ('POST', '/login'):
            self._response_dict = {'user_id': 5316191164430650570}
            if random.randint(0, 100) % 3 == 0:
                self._response_code = 403
            else:
                self._response_code = 200
        elif (method, query) == ('POST', '/logout'):
            self._response_dict = {}
            self._response_code = 200
        elif (method, query) == ('GET', '/get_doc'):
            self._response_dict = {
                'client_version': 0,
                'server_version': 0,
                'text': 'Sample text',
            }
            self._response_code = 200
        elif (method, query) == ('POST', '/update_doc'):
            self._response_dict = {
                'version': body['edits'][-1][1]
                if body['edits']
                else body['version'],
                'edits': [],
            }
            self._response_code = 200
        elif (method, query) == ('POST', '/create_doc'):
            docs.insert(0, {key: body[key] for key in ['doc_id', 'title']})
            self._response_dict = {}
            self._response_code = 200
        elif (method, query) == ('GET', '/list_all_docs'):
            self._response_dict = {'docs': docs}
            self._response_code = 200
        else:
            self._response_dict = {
                'code': 'NOT_FOUND',
                'message': 'handler not found',
            }
            self._response_code = 404

    def getresponse(self) -> HTTPResponseMock:
        return HTTPResponseMock(self._response_dict, self._response_code)
