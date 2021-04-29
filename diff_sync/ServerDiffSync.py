import diff_match_patch.diff_match_patch as dmp_module


class ServerDiffSync:
    def __init__(self, db_connector, edits, client_version = 0, server_version = 0):
        self.db_connector = db_connector
        self.edits_stack = edits
        self.client_version = client_version
        self.server_version = server_version
        self.dmp = dmp_module.diff_match_patch()

    def update(self):
        text = self.db_connector.get_text()
        patches = self.dmp.patch_make(self.db_connector.get_shadow(), text)
        if len(patches) == 0:
            return False
        self.edits_stack.push((self.dmp.patch_toText(patches), self.server_version))
        self.server_version += 1
        self.db_connector.set_shadow(text)

    def get_edits(self):
        return self.edits_stack

    def patch_edits(self, edits, received_version):
        shadow, text = None, None

        if received_version < self.server_version:
            self.edits_stack.clear()
            shadow = self.db_connector.get_backup()
            self.server_version -= 1
        else:
            self.filter_stack(received_version)

        while not edits.empty():
            edit = edits.top()
            edits.pop()
            if edit[1] >= self.client_version:
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
            self.db_connector.set_backup(shadow)
            self.db_connector.set_text(text)
            self.client_version += 1

    def filter_stack(self, version):
        while not self.edits_stack.empty() and self.edits_stack.top()[1] <= version:
            self.edits_stack.pop()

    def get_received_version(self):
        return self.client_version
