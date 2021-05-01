class UpdateDocRequest:
    attributes = {
        "user_id": "user_id",
        "doc_id": "doc_id",
        "received_version": "received_version",
        "edits": "edits"
    }

    def __init__(self, user_id, doc_id, received_version, edits):
        self._user_id = user_id
        self._doc_id = doc_id
        self._received_version = received_version
        self._edits = edits

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        if user_id is None:
            raise ValueError("Invalid value for `user_id`, must not be `None`")

        self._user_id = user_id

    @property
    def doc_id(self):
        return self._doc_id

    @doc_id.setter
    def doc_id(self, doc_id):
        if doc_id is None:
            raise ValueError("Invalid value for `doc_id`, must not be `None`")

        self._doc_id = doc_id

    @property
    def received_version(self):
        return self._received_version

    @received_version.setter
    def received_version(self, received_version):
        if received_version is None:
            raise ValueError("Invalid value for `received_version`, must not be `None`")

        self._received_version = received_version

    @property
    def edits(self):
        return self._edits

    @edits.setter
    def edits(self, edits):
        if edits is None:
            raise ValueError("Invalid value for `edits`, must not be `None`")

        self._edits = edits

    def to_dict(self):
        result = {}
        for attr, key in self.attributes.items():
            value = getattr(self, attr)
            result[key] = value

        return result
