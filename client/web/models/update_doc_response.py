import typing


class UpdateDocResponse:
    attributes = {"version": "version", "edits": "edits"}

    def __init__(self, version: int, edits: typing.List[typing.Tuple[str, int]]):
        self._version = version
        self._edits = edits

    @property
    def version(self) -> int:
        return self._version

    @property
    def edits(self) -> typing.List[typing.Tuple[str, int]]:
        return self._edits

    def to_dict(self) -> dict:
        result = {}
        for attr, key in self.attributes.items():
            value = getattr(self, attr)
            result[key] = value

        return result
