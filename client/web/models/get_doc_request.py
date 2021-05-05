class GetDocRequest:
    attributes = {"user_id": "user_id", "doc_id": "doc_id"}

    def __init__(self, user_id: int, doc_id: int):
        self._user_id = user_id
        self._doc_id = doc_id

    @property
    def user_id(self) -> int:
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        if user_id is None:
            raise ValueError("Invalid value for `user_id`, must not be `None`")

        self._user_id = user_id

    @property
    def doc_id(self) -> int:
        return self._doc_id

    @doc_id.setter
    def doc_id(self, doc_id: int):
        if doc_id is None:
            raise ValueError("Invalid value for `doc_id`, must not be `None`")

        self._doc_id = doc_id

    def to_dict(self) -> dict:
        result = {}
        for attr, key in self.attributes.items():
            value = getattr(self, attr)
            result[key] = value

        return result
