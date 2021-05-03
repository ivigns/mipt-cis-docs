import diff_match_patch.diff_match_patch as dmp_module


class ClientDiffSync:
    def __init__(self, db_connector, edits):
        self.db_connector = db_connector
        self.edits_stack = edits
        self.client_version = db_connector.get_client_version()
        self.server_version = db_connector.get_server_version()
        self.dmp = dmp_module.diff_match_patch()

    def update(self):
        text = self.db_connector.get_text()
        patches = self.dmp.patch_make(self.db_connector.get_shadow(), text)
        if len(patches) == 0:
            return False
        self.edits_stack.push(
            (self.dmp.patch_toText(patches), self.client_version)
        )
        self.client_version += 1
        self.db_connector.set_shadow(text)
        self.db_connector.set_client_version(self.client_version)

        return True

    def get_edits(self):
        return self.edits_stack

    def patch_edits(self, edits, received_version):
        self.filter_stack(received_version)

        shadow, text = None, None

        while not edits.empty():
            edit = edits.top()
            edits.pop()
            if edit[1] >= self.server_version:
                if shadow is None:
                    shadow = self.db_connector.get_shadow()
                if text is None:
                    text = self.db_connector.get_text()

                patch = self.dmp.patch_fromText(edit[0])

                shadow_patch_result = self.dmp.patch_apply(patch, shadow)
                shadow = shadow_patch_result[0]

                text_patch_result = self.dmp.patch_apply(patch, text)
                text = text_patch_result[0]

        if text is not None and shadow is not None:
            self.db_connector.set_shadow(shadow)
            self.db_connector.set_text(text)
            self.server_version += 1
            self.db_connector.set_server_version(self.server_version)

    def filter_stack(self, version):
        while (
            not self.edits_stack.empty()
            and self.edits_stack.top()[1] <= version
        ):
            self.edits_stack.pop()

    def get_received_version(self):
        return self.server_version
