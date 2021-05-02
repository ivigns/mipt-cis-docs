import http.client
import sys
import typing
import uuid

import PyQt5.QtCore as qc
import PyQt5.QtGui as qgui
import PyQt5.QtWidgets as qw

from client.db import db
from client.web import api_client_mock as api_client  # todo: use real client
from client.web.models.create_doc_request import CreateDocRequest
from client.web.models.update_doc_request import UpdateDocRequest
from diff_sync import client_diff_sync as diff_sync

APP_NAME = 'Docs'


def center_window(window: qw.QWidget, width: int, height: int):
    x = (qw.QApplication.desktop().width() - width) // 2
    y = (qw.QApplication.desktop().height() - height) // 2
    window.setGeometry(x, y, width, height)


class LoginWindow(qw.QWidget):
    _logged_in = qc.pyqtSignal(str, int)

    def __init__(self, app: typing.Any):
        super().__init__(None, qc.Qt.WindowType.Dialog)

        self._login = None
        self._user_id = None
        self._web_client: api_client.ApiClientMock = app.web_client

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

        try:
            self._user_id = self._web_client.login(self._login)
        except (http.client.HTTPException, KeyError) as exc:
            print(exc, file=sys.stderr)
            qw.QMessageBox.critical(
                self,
                'Error',
                'Error while connecting to server',
                qw.QMessageBox.StandardButton.Ok,
            )
            return

        self._logged_in.emit(self._login, self._user_id)
        self.close()


class DocListItem(qw.QListWidgetItem):
    def __init__(self, title: str, doc_id: id, icon: qgui.QIcon):
        super().__init__()

        self.doc_id = doc_id

        self.setIcon(icon)
        self.setText(title)


class MainWindow(qw.QMainWindow):
    STATUS_TIMEOUT = 2000

    def __init__(self, app: typing.Any):
        super().__init__()

        self._login = None
        self._user_id = None
        self._db_helper: db.DbHelper = app.db_helper
        self._web_client: api_client.ApiClientMock = app.web_client

        self._opened_docs = {}

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

    @qc.pyqtSlot(str, int)
    def _on_login(self, login: str, user_id: int):
        self._login = login
        self._user_id = user_id
        self._login_label.setText(f'Logged in as <b>{self._login}</b>')
        self._on_docs_list_update()
        self.show()

    @qc.pyqtSlot()
    def _on_docs_list_update(self):
        try:
            response = self._web_client.list_all_docs()
        except (http.client.HTTPException, KeyError) as exc:
            print(exc, file=sys.stderr)
            self.statusBar().showMessage(
                'Error while connecting to server', self.STATUS_TIMEOUT
            )
            return
        else:
            self._docs_list.clear()
            for doc in response.docs:
                self._docs_list.addItem(
                    DocListItem(
                        doc.title,
                        doc.doc_id,
                        self.style().standardIcon(
                            qw.QStyle.StandardPixmap.SP_FileIcon
                        ),
                    )
                )

        self.statusBar().showMessage(
            'Updated documents list', self.STATUS_TIMEOUT
        )

    @qc.pyqtSlot(qw.QListWidgetItem)
    def _on_doc_clicked(self, doc: DocListItem):
        if doc.doc_id in self._opened_docs:
            self._opened_docs[doc.doc_id].activateWindow()
        else:
            doc_window = DocWindow(
                doc.doc_id,
                doc.text(),
                self._user_id,
                self,
                self._db_helper.get_connector(self._user_id, doc.doc_id),
                self._web_client,
            )
            self._opened_docs[doc.doc_id] = doc_window

    @qc.pyqtSlot()
    def _on_new_doc(self):
        title, ok = qw.QInputDialog.getText(
            self, f'New Document', 'Name new document:', text='New Document',
        )
        if not ok or not title:
            self.statusBar().showMessage(
                'New document was not created', self.STATUS_TIMEOUT
            )
            return

        doc_id = uuid.uuid1().int >> 64
        request = CreateDocRequest(title, self._user_id, doc_id)
        try:
            self._web_client.create_doc(request)
        except (http.client.HTTPException, KeyError) as exc:
            print(exc, file=sys.stderr)
            self.statusBar().showMessage(
                'Error while connecting to server', self.STATUS_TIMEOUT
            )
            return

        self._on_docs_list_update()

    @qc.pyqtSlot(str)
    def on_doc_closed(self, doc_id: str):
        self._opened_docs.pop(int(doc_id))


class DocWindow(qw.QMainWindow):
    _closed = qc.pyqtSignal(str)

    def __init__(
        self,
        doc_id: int,
        title: str,
        user_id: int,
        main_window: qw.QWidget,
        db_connector: db.DbConnector,
        web_client: api_client.ApiClientMock,
    ):
        super().__init__(main_window)

        self._doc_id = doc_id
        self._user_id = user_id
        self._saved = False
        self._diff_sync = diff_sync.ClientDiffSync(db_connector, db.Stack([]))
        self._web_client = web_client

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
        file_menu.addAction(
            'Save and &close', self.close, qgui.QKeySequence.StandardKey.Close
        )
        file_menu.menuAction().setStatusTip('File actions')

        edit_menu = self.menuBar().addMenu('&Edit')
        edit_menu.addAction(
            'Select &all',
            self._textedit.selectAll,
            qgui.QKeySequence.StandardKey.SelectAll,
        )
        edit_menu.addAction(
            '&Undo', self._textedit.undo, qgui.QKeySequence.StandardKey.Undo
        )
        edit_menu.addAction(
            '&Redo', self._textedit.redo, qgui.QKeySequence.StandardKey.Redo
        )
        edit_menu.addAction(
            '&Copy', self._textedit.copy, qgui.QKeySequence.StandardKey.Copy
        )
        edit_menu.addAction(
            'C&ut', self._textedit.cut, qgui.QKeySequence.StandardKey.Cut
        )
        edit_menu.addAction(
            '&Paste', self._textedit.paste, qgui.QKeySequence.StandardKey.Paste
        )
        edit_menu.menuAction().setStatusTip('Text edit actions')

        self._timer = qc.QTimer(self)
        self._timer.setInterval(5 * 1000)
        self._timer.setSingleShot(False)
        self._timer.start()

        self._textedit.textChanged.connect(self._on_edit)
        self._timer.timeout.connect(self._on_save)
        self._closed.connect(main_window.on_doc_closed)

        self.setWindowTitle(f'{APP_NAME} - {title}')
        center_window(self, 500, 700)

        self.show()

    def _load_text(self):
        try:
            text = self._diff_sync.db_connector.get_text()
        except db.DbException as exc:
            print(exc, file=sys.stderr)
            qw.QMessageBox.critical(
                self,
                'Error',
                'Cannot load doc from db',
                qw.QMessageBox.StandardButton.Ok,
            )
            self.close()
            return
        else:
            self._textedit.setPlainText(text)

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

    def _set_text(self, text: str):
        cursor = self._textedit.textCursor()
        cursor_pos = cursor.position()
        cursor_anchor = None
        if cursor.hasSelection():
            cursor_anchor = cursor.anchor()

        cursor = qgui.QTextCursor(self._textedit.document())
        cursor.select(qgui.QTextCursor.SelectionType.Document)
        cursor.insertText(text)

        new_cursor = self._textedit.textCursor()
        if cursor_anchor is not None:
            new_cursor.setPosition(
                cursor_anchor, qgui.QTextCursor.MoveMode.MoveAnchor
            )
            new_cursor.setPosition(
                cursor_pos, qgui.QTextCursor.MoveMode.KeepAnchor
            )
        else:
            new_cursor.setPosition(
                cursor_pos, qgui.QTextCursor.MoveMode.MoveAnchor
            )
        self._textedit.setTextCursor(new_cursor)

    @qc.pyqtSlot()
    def _on_save(self):
        if not self._saved:
            try:
                self._diff_sync.db_connector.set_text(
                    self._textedit.toPlainText()
                )
                if self._diff_sync.update():
                    edits = self._diff_sync.get_edits()
                    version = self._diff_sync.get_received_version()
                    request = UpdateDocRequest(
                        self._user_id, self._doc_id, version, edits
                    )
                    response = self._web_client.update_doc(request)
                    self._diff_sync.patch_edits(
                        db.Stack(response.edits), response.version
                    )
                text = self._diff_sync.db_connector.get_text()
            except (http.client.HTTPException, KeyError, db.DbException) as exc:
                print(exc, file=sys.stderr)
                self.statusBar().showMessage(
                    'Unsaved changes: Error while saving'
                )
                return
            else:
                self._set_text(text)

        self._change_status(True)

    def closeEvent(self, event: qgui.QCloseEvent):
        self._on_save()
        self._closed.emit(str(self._doc_id))
        event.accept()
