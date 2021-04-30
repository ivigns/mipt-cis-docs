import typing

import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw


def center_window(window: qw.QWidget, width: int, height: int):
    x = (qw.QApplication.desktop().width() - width) // 2
    y = (qw.QApplication.desktop().height() - height) // 2
    window.setGeometry(x, y, width, height)


class LoginWindow(qw.QWidget):
    _logged_in = qc.pyqtSignal()

    def __init__(self, app: typing.Any):
        super().__init__()

        self.login = None

        label = qw.QLabel('Welcome!')
        label.setAlignment(qc.Qt.AlignmentFlag.AlignCenter)
        self._line_edit = qw.QLineEdit()
        self._line_edit.setPlaceholderText('Login')
        login_button = qw.QPushButton('Log in')

        self._line_edit.returnPressed.connect(login_button.click)
        login_button.clicked.connect(self._on_login)
        self._logged_in.connect(app.on_login)

        layout = qw.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self._line_edit)
        layout.addWidget(login_button)
        self.setLayout(layout)

        self.setWindowTitle('Docs - Log in')
        center_window(self, 300, 100)
        self.show()

    @qc.pyqtSlot()
    def _on_login(self):
        # todo: api request
        self.login = self._line_edit.text()
        self._logged_in.emit()
        self.close()


class MainWindow(qw.QWidget):
    def __init__(self, app: typing.Any):
        super().__init__()

        self._login = None
        self._app = app

        # todo: implement
        self._label = qw.QLabel('{} got bamboozled', self)

        app.logged_in.connect(self._on_login)

        self.setWindowTitle('Docs')
        center_window(self, 500, 500)
        self.hide()

    @qc.pyqtSlot()
    def _on_login(self):
        self._login = self._app.login
        self._label.setText(self._label.text().format(self._login))
        self.show()
