class MockConnector:
    def __init__(self, text, shadow, backup = None):
        self.text = text
        self.shadow = shadow
        self.backup = backup

    def get_text(self):
        return self.text

    def get_shadow(self):
        return self.shadow

    def get_backup(self):
        return self.backup

    def set_text(self, text):
        self.text = text

    def set_shadow(self, text):
        self.shadow = text

    def set_backup(self, text):
        self.backup = text