class UpdateDocResponse:
    attributes = {
        "doc_id": "doc_id",
        "received_version": "received_version",
        "edits": "edits"
    }

    def __init__(self, doc_id, received_version, edits):
        self._doc_id = doc_id
        self._received_version = received_version
        self._edits = edits

    @property
    def doc_id(self):
        return self._doc_id

    @property
    def received_version(self):
        return self._received_version

    @property
    def edits(self):
        return self._edits

    def to_dict(self):
        result = {}
        for attr, key in self.attributes.items():
            value = getattr(self, attr)
            result[key] = value

        return result
