from diff_match_patch import diff_match_patch as dmp_module


class ServerDiffSync:
    def __init__(self, db_connector, edits, doc_id, user_id, logger):
        self.db_connector = db_connector
        self.edits_stack = edits
        self.doc_id = doc_id
        self.user_id = user_id
        self.logger = logger

        self.client_version = db_connector.get_client_version(doc_id, user_id)
        self.server_version = db_connector.get_server_version(doc_id, user_id)
        self.dmp = dmp_module()

    def update(self):
        self.logger.info("Update doc: starting")
        text = self.db_connector.get_text(self.doc_id, self.user_id)
        patches = self.dmp.patch_make(self.db_connector.get_shadow(self.doc_id, self.user_id), text)
        if len(patches) == 0:
            return False
        self.logger.info("Update doc: text and patches %s , %s" % (text, patches))
        self.edits_stack.push((self.dmp.patch_toText(patches), self.server_version))
        self.server_version += 1
        self.db_connector.set_shadow(text, self.doc_id, self.user_id)
        self.db_connector.set_server_version(self.server_version, self.doc_id, self.user_id)
        self.logger.info("Update doc: new server version %s" % self.server_version)
        return True

    def get_edits(self):
        return self.edits_stack

    def patch_edits(self, edits, received_version):
        shadow, text = None, None

        text_patch_result = ''
        shadow_patch_result = ''
        while not edits.empty():
            edit = edits.top()
            edits.pop()
            if edit[1] >= self.client_version:
                if shadow is None or text is None:
                    if received_version < self.server_version:
                        self.edits_stack.clear()
                        shadow = self.db_connector.get_backup(self.doc_id, self.user_id)
                        self.server_version -= 1
                    else:
                        self.filter_stack(received_version)

                self.logger.info("Update doc: patch edits, running dmp patch apply: edits version, client version: %s, %s" % (edit[1], self.client_version))
                if shadow is None:
                    shadow = self.db_connector.get_shadow(self.doc_id, self.user_id)
                if text is None:
                    text = self.db_connector.get_text(self.doc_id, self.user_id)

                patch = self.dmp.patch_fromText(edit[0])

                shadow_patch_result = self.dmp.patch_apply(patch, shadow)
                shadow = shadow_patch_result[0]

                text_patch_result = self.dmp.patch_apply(patch, text)
                text = text_patch_result[0]

        self.logger.info("Update doc: patch edits - text, text_patch_result, shadow, shadow_patch_result: %s, %s, %s, %s" % (text, text_patch_result, shadow, shadow_patch_result))
        if text is not None and shadow is not None:
            self.db_connector.set_shadow(shadow, self.doc_id, self.user_id)
            self.db_connector.set_backup(shadow, self.doc_id, self.user_id)
            self.db_connector.set_text(text, self.doc_id, self.user_id)
            self.client_version += 1
            self.db_connector.set_client_version(self.client_version, self.doc_id, self.user_id)
        self.logger.info(
            "Update doc: patch edits - client_version %s" % self.client_version)

    def filter_stack(self, version):
        while not self.edits_stack.empty() and self.edits_stack.top()[1] <= version:
            self.edits_stack.pop()

    def get_received_version(self):
        return self.client_version
