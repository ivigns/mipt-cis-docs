import typing


class DocsListItem:
    attributes = {"doc_id": "doc_id", "title": "title"}

    def __init__(self, doc_id: int, title: str):
        self._doc_id = doc_id
        self._title = title

    @property
    def doc_id(self) -> int:
        return self._doc_id

    @property
    def title(self) -> str:
        return self._title

    def to_dict(self) -> dict:
        result = {}
        for attr, key in self.attributes.items():
            value = getattr(self, attr)
            result[key] = value

        return result


class DocsListResponse:
    attributes = {"docs": "docs"}

    def __init__(self, docs: typing.List[DocsListItem]):
        self._docs = docs

    @property
    def docs(self) -> typing.List[DocsListItem]:
        return self._docs

    def to_dict(self) -> dict:
        result = {}
        for attr, key in self.attributes.items():
            value = getattr(self, attr)
            result[key] = value

        return result
