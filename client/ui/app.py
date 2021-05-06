import sys

import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

from client.data_manage import db
from client.ui import widgets


class DocsApp(qw.QApplication):
    FOCUS_LOGIN = 'LoginWindow'
    FOCUS_MAIN = 'MainWindow'

    def __init__(self):
        super().__init__(sys.argv)

        self.db_helper = db.DbHelper()
        self.web_client = None
        self.main_window = None
        self.login_window = widgets.LoginWindow(self)
        self.focus = self.FOCUS_LOGIN

        self.login_window.show()
