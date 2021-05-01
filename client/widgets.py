import typing

import PyQt5.QtCore as qc
import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qgui

APP_NAME = 'Docs'


def center_window(window: qw.QWidget, width: int, height: int):
    x = (qw.QApplication.desktop().width() - width) // 2
    y = (qw.QApplication.desktop().height() - height) // 2
    window.setGeometry(x, y, width, height)


class LoginWindow(qw.QWidget):
    _logged_in = qc.pyqtSignal(str)

    def __init__(self, app: typing.Any):
        super().__init__(None, qc.Qt.WindowType.Dialog)

        self._login = None

        label = qw.QLabel('Welcome!')
        label.setAlignment(qc.Qt.AlignmentFlag.AlignCenter)
        self._line_edit = qw.QLineEdit()
        self._line_edit.setPlaceholderText('Login')
        login_button = qw.QPushButton('Log in')

        layout = qw.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self._line_edit)
        layout.addWidget(login_button)
        self.setLayout(layout)

        self._line_edit.returnPressed.connect(login_button.click)
        login_button.clicked.connect(self._on_login_clicked)
        self._logged_in.connect(app.on_login)

        self.setWindowTitle(f'{APP_NAME} - Log in')
        center_window(self, 300, 100)

    @qc.pyqtSlot()
    def _on_login_clicked(self):
        self._login = self._line_edit.text()
        if not self._login:
            qw.QMessageBox.information(
                self,
                'Info',
                'Please enter your login!',
                qw.QMessageBox.StandardButton.Ok,
            )
            return

        # todo: api request
        self._logged_in.emit(self._login)
        self.close()


class DocListItem(qw.QListWidgetItem):
    def __init__(self, doc_name: str, icon: qgui.QIcon):
        super().__init__()

        self.doc_name = doc_name

        self.setIcon(icon)
        self.setText(doc_name)


class MainWindow(qw.QMainWindow):
    def __init__(self, app: typing.Any):
        super().__init__()

        self._login = None

        self._login_label = qw.QLabel()
        self._login_label.setFixedHeight(50)
        self._login_label.setAlignment(
            qc.Qt.AlignmentFlag.AlignLeft | qc.Qt.AlignmentFlag.AlignVCenter
        )
        label_layout = qw.QHBoxLayout()
        label_layout.addStretch(1)
        label_layout.addWidget(self._login_label, 20)
        label_layout.addStretch(1)

        new_doc_button = qw.QPushButton('New Document')
        update_button = qw.QPushButton('Update')
        caption_layout = qw.QHBoxLayout()
        caption_layout.addWidget(qw.QLabel('Documents:'))
        caption_layout.addStretch(1)
        caption_layout.addWidget(new_doc_button)
        caption_layout.addWidget(update_button)

        self._docs_list = qw.QListWidget()

        layout = qw.QVBoxLayout()
        layout.addLayout(label_layout)
        layout.addLayout(caption_layout)
        layout.addWidget(self._docs_list, 1)
        self.setCentralWidget(qw.QWidget())
        self.centralWidget().setLayout(layout)

        app.logged_in.connect(self._on_login)
        new_doc_button.clicked.connect(self._on_new_doc)
        update_button.clicked.connect(self._on_docs_list_update)
        self._docs_list.itemActivated.connect(self._on_doc_clicked)

        self.setWindowTitle(APP_NAME)
        center_window(self, 600, 500)

    @qc.pyqtSlot(str)
    def _on_login(self, login: str):
        self._login = login
        self._login_label.setText(f'Logged in as <b>{self._login}</b>')
        self._on_docs_list_update()
        self.show()

    @qc.pyqtSlot()
    def _on_docs_list_update(self):
        self._docs_list.clear()
        # todo: api request
        import random

        for _ in range(random.randint(0, 10)):
            item = DocListItem(
                f'New text document {random.randint(1, 100)}',
                self.style().standardIcon(qw.QStyle.StandardPixmap.SP_FileIcon),
            )
            self._docs_list.addItem(item)

        self.statusBar().showMessage('Updated documents list', 2000)

    @qc.pyqtSlot(qw.QListWidgetItem)
    def _on_doc_clicked(self, doc: DocListItem):
        # todo: api request
        doc_window = DocWindow(doc.doc_name, self._login, self)
        doc_window.show()

    @qc.pyqtSlot()
    def _on_new_doc(self):
        text, ok = qw.QInputDialog.getText(
            self,
            f'{APP_NAME} - New Document',
            'Name new document:',
            text='New Document',
        )
        if not ok or not text:
            self.statusBar().showMessage('New document was not created', 2000)
            return

        # todo: db + api request
        self._on_docs_list_update()


class DocWindow(qw.QMainWindow):
    def __init__(self, doc_name: str, login: str, main_window: qw.QWidget):
        super().__init__(main_window)

        self._doc_name = doc_name
        self._login = login
        self._saved = False

        self._textedit = qw.QTextEdit()
        self._load_text()
        self._on_save()

        layout = qw.QVBoxLayout()
        layout.addWidget(self._textedit)
        layout.setContentsMargins(qc.QMargins(0, 0, 0, 0))
        self.setCentralWidget(qw.QWidget())
        self.centralWidget().setLayout(layout)

        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(
            '&Save', self._on_save, qgui.QKeySequence.StandardKey.Save
        )
        file_menu.addAction('Save and &close', self.close)
        file_menu.menuAction().setStatusTip('File actions')

        self._timer = qc.QTimer(self)
        self._timer.setInterval(5 * 1000)
        self._timer.setSingleShot(False)
        self._timer.start()

        self._textedit.textChanged.connect(self._on_edit)
        self._timer.timeout.connect(self._on_save)

        self.setWindowTitle(f'{APP_NAME} - {self._doc_name}')
        center_window(self, 500, 700)

    def _load_text(self):
        # todo: db + api request
        self._textedit.setText('Sample text')

    @qc.pyqtSlot(bool)
    def _change_status(self, status: bool):
        self._saved = status
        if self._saved:
            self.statusBar().showMessage('Saved')
        else:
            self.statusBar().showMessage('Unsaved changes')

    @qc.pyqtSlot()
    def _on_edit(self):
        self._change_status(False)

    @qc.pyqtSlot()
    def _on_save(self):
        if self._saved:
            self._change_status(True)
            return

        # todo: db + api request
        self._change_status(True)

    def closeEvent(self, event: qgui.QCloseEvent):
        self._on_save()
        event.accept()
