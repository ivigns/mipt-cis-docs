import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw

import widgets


class DocsApp(qw.QApplication):
    logged_in = qc.pyqtSignal()

    def __init__(self):
        super().__init__([])

        self.login = None

        self.main_window = widgets.MainWindow(self)
        self.login_window = widgets.LoginWindow(self)

        self.exec()

    @qc.pyqtSlot()
    def on_login(self):
        self.login = self.login_window.login
        if not self.login:
            raise RuntimeError('Null login')
        self.logged_in.emit()
