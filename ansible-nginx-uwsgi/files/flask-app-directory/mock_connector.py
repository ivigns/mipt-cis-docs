class MockConnector:
    def __init__(self, text, shadow, backup = None):
        self.text = text
        self.shadow = shadow
        self.backup = backup
        self.client_version = 0
        self.server_version = 0

    def get_text(self):
        return self.text

    def get_shadow(self):
        return self.shadow

    def get_backup(self):
        return self.backup

    def get_client_version(self):
        return self.client_version

    def get_server_version(self):
        return self.server_version

    def set_text(self, text):
        self.text = text

    def set_shadow(self, text):
        self.shadow = text

    def set_backup(self, text):
        self.backup = text

    def set_client_version(self, version):
        self.client_version = version

    def set_server_version(self, version):
        self.server_version = version