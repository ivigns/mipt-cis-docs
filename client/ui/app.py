import sys

import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

import client.db.db as db
import client.web.api_client_mock as api_client  # todo: use real client
import client.ui.widgets as widgets


class DocsApp(qw.QApplication):
    logged_in = qc.pyqtSignal(str, int)

    def __init__(self):
        super().__init__(sys.argv)

        self.db_helper = db.DbHelper()
        self.web_client = api_client.ApiClientMock()

        self._main_window = widgets.MainWindow(self)
        self._login_window = widgets.LoginWindow(self)
        self._login_window.show()

    @qc.pyqtSlot(str, int)
    def on_login(self, login: str, user_id: int):
        self.logged_in.emit(login, user_id)
