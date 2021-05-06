class GetDocResponse:
    attributes = {
        "client_version": "client_version",
        "server_version": "server_version",
        "text": "text",
    }

    def __init__(self, client_version: int, server_version: int, text: str):
        self._client_version = client_version
        self._server_version = server_version
        self._text = text

    @property
    def client_version(self) -> int:
        return self._client_version

    @property
    def server_version(self) -> int:
        return self._server_version

    @property
    def text(self) -> str:
        return self._text

    def to_dict(self) -> dict:
        result = {}
        for attr, key in self.attributes.items():
            value = getattr(self, attr)
            result[key] = value

        return result
