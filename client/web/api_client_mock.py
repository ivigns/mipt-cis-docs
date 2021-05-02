from client.web.models.create_doc_request import CreateDocRequest
from client.web.models.docs_list_response import DocsListResponse, DocsListItem
from client.web.models.update_doc_request import UpdateDocRequest
from client.web.models.update_doc_response import UpdateDocResponse


class ApiClientMock:
    def __init__(self):
        self._docs = [
            DocsListItem(doc_id, f'Document {i}')
            for doc_id, i in zip(
                [9392468011745350111, 9407757923520418271, 9418928317413528031],
                range(1, 4),
            )
        ]

    def login(self, login: str) -> int:
        return 5316191164430650570

    def update_doc(self, body: UpdateDocRequest) -> UpdateDocResponse:
        return UpdateDocResponse(body.version, [])

    def create_doc(self, body: CreateDocRequest):
        self._docs.insert(0, DocsListItem(body.doc_id, body.title))

    def list_all_docs(self) -> DocsListResponse:
        return DocsListResponse(self._docs)
