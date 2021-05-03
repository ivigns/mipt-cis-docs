import sys

import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

import client.db.db as db
import client.ui.widgets as widgets


class DocsApp(qw.QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        self.db_helper = db.DbHelper()
        self.web_client = None
        self.main_window = None
        self.login_window = widgets.LoginWindow(self)

        self.login_window.show()
