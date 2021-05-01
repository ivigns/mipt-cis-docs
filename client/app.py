import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

import widgets


class DocsApp(qw.QApplication):
    logged_in = qc.pyqtSignal(str)

    def __init__(self):
        super().__init__([])

        self.main_window = widgets.MainWindow(self)
        self.login_window = widgets.LoginWindow(self)
        self.login_window.show()

        self.exec()

    @qc.pyqtSlot(str)
    def on_login(self, login: str):
        self.logged_in.emit(login)
