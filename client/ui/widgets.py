import http.client
import logging
import sys
import typing
import uuid

import PyQt5.QtCore as qc
import PyQt5.QtGui as qgui
import PyQt5.QtWidgets as qw

from client.data_manage import db
from client.data_manage import stack
from client.web import api_client
import client.web.http_connection_mock as conn_mock
from client.web.models.create_doc_request import CreateDocRequest
from client.web.models.get_doc_request import GetDocRequest
from client.web.models.update_doc_request import UpdateDocRequest
from diff_sync import client_diff_sync as diff_sync
from client import resources

logger = logging.getLogger('client')

APP_NAME = 'MiptCisDocs'


def set_icon(window: qw.QWidget):
    icon = qgui.QIcon(":/icons/app.ico")
    window.setWindowIcon(icon)


def center_window(window: qw.QWidget, width: int, height: int):
    x = (qw.QApplication.desktop().width() - width) // 2
    y = (qw.QApplication.desktop().height() - height) // 2
    window.setGeometry(x, y, width, height)


class LoginWindow(qw.QWidget):
    SECRET_LOGIN = 'test_mock'

    def __init__(self, app: typing.Any):
        super().__init__(None, qc.Qt.WindowType.Dialog)

        self._app = app

        welcome_label = qw.QLabel('Welcome!')
        welcome_label.setAlignment(qc.Qt.AlignmentFlag.AlignCenter)

        self._login_edit = qw.QLineEdit()
        self._login_edit.setMaxLength(20)
        self._login_edit.setPlaceholderText('login')

        try:
            host, port = self._app.db_helper.get_host_port()
        except db.DbException as exc:
            logger.exception(exc)
            host, port = '', ''

        self._host_edit = qw.QLineEdit()
        self._host_edit.setText(host)
        self._host_edit.setPlaceholderText('127.0.0.1')

        self._port_edit = qw.QLineEdit()
        self._port_edit.setText(port)
        self._port_edit.setPlaceholderText('80')

        grid_layout = qw.QGridLayout()
        grid_layout.addWidget(qw.QLabel('Login:'), 0, 0)
        grid_layout.addWidget(qw.QLabel('Host:'), 1, 0)
        grid_layout.addWidget(qw.QLabel('Port:'), 2, 0)
        grid_layout.addWidget(self._login_edit, 0, 1)
        grid_layout.addWidget(self._host_edit, 1, 1)
        grid_layout.addWidget(self._port_edit, 2, 1)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 4)

        login_button = qw.QPushButton('Log in')

        layout = qw.QVBoxLayout()
        layout.addWidget(welcome_label, 1)
        layout.addLayout(grid_layout)
        layout.addWidget(login_button)
        self.setLayout(layout)

        self._login_edit.returnPressed.connect(login_button.click)
        self._host_edit.returnPressed.connect(login_button.click)
        self._port_edit.returnPressed.connect(login_button.click)
        login_button.clicked.connect(self._on_login_clicked)

        self.setWindowTitle(f'{APP_NAME} - Log in')
        set_icon(self)
        center_window(self, 300, 100)

    @qc.pyqtSlot()
    def _on_login_clicked(self):
        if not self._app.focus == self._app.FOCUS_LOGIN:
            return

        login = self._login_edit.text()
        if not login:
            qw.QMessageBox.information(
                self,
                'Info',
                'Please enter your login!',
                qw.QMessageBox.StandardButton.Ok,
            )
            return

        host = self._host_edit.text()
        port = self._port_edit.text()
        Connection = http.client.HTTPConnection
        if login == self.SECRET_LOGIN:
            Connection = conn_mock.HTTPConnectionMock
        web_client = api_client.ApiClient(
            f'{host}:{port}', Connection=Connection
        )
        try:
            user_id = web_client.login(login)
        except api_client.NotAllowed:
            qw.QMessageBox.warning(
                self,
                'Error',
                'This user is already logged in. Try other user.',
                qw.QMessageBox.StandardButton.Ok,
            )
            return
        except http.client.HTTPException as exc:
            logger.exception(exc)
            qw.QMessageBox.critical(
                self,
                'Error',
                'Error while connecting to server',
                qw.QMessageBox.StandardButton.Ok,
            )
            return

        try:
            self._app.db_helper.set_host_port(host, port)
        except db.DbException as exc:
            logger.exception(exc)
        self._app.web_client = web_client
        self._app.main_window = MainWindow(
            self._app, login, user_id, f'{host}:{port}'
        )
        self._app.focus = self._app.FOCUS_MAIN

        self._app.main_window.show()
        self.close()


class DocListItem(qw.QListWidgetItem):
    def __init__(self, title: str, doc_id: id, icon: qgui.QIcon):
        super().__init__()

        self.doc_id = doc_id

        self.setIcon(icon)
        self.setText(title)


class MainWindow(qw.QMainWindow):
    STATUS_TIMEOUT = 2000

    def __init__(self, app: typing.Any, login: str, user_id: int, host: str):
        super().__init__()

        self._login = login
        self._user_id = user_id
        self._app = app
        self._opened_docs = {}

        login_label = qw.QLabel(f'Logged in as <b>{login}</b>')
        login_label.setFixedHeight(50)
        login_label.setAlignment(
            qc.Qt.AlignmentFlag.AlignLeft | qc.Qt.AlignmentFlag.AlignVCenter
        )
        host_label = qw.QLabel(f'Server host: <b>{host}</b>')
        host_label.setFixedHeight(50)
        host_label.setAlignment(
            qc.Qt.AlignmentFlag.AlignRight | qc.Qt.AlignmentFlag.AlignVCenter
        )
        label_layout = qw.QHBoxLayout()
        label_layout.addStretch(1)
        label_layout.addWidget(login_label, 20)
        label_layout.addWidget(host_label, 20)
        label_layout.addStretch(1)

        new_doc_button = qw.QPushButton('New Document')
        update_button = qw.QPushButton('Update')
        caption_layout = qw.QHBoxLayout()
        caption_layout.addWidget(qw.QLabel('Documents:'))
        caption_layout.addStretch(1)
        caption_layout.addWidget(new_doc_button)
        caption_layout.addWidget(update_button)

        self._docs_list = qw.QListWidget()
        self._on_docs_list_update()

        logout_button = qw.QPushButton('Log out')
        bottom_layout = qw.QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(logout_button)

        layout = qw.QVBoxLayout()
        layout.addLayout(label_layout)
        layout.addLayout(caption_layout)
        layout.addWidget(self._docs_list, 1)
        layout.addLayout(bottom_layout)
        self.setCentralWidget(qw.QWidget())
        self.centralWidget().setLayout(layout)

        new_doc_button.clicked.connect(self._on_new_doc)
        update_button.clicked.connect(self._on_docs_list_update)
        self._docs_list.itemActivated.connect(self._on_doc_clicked)
        logout_button.clicked.connect(self._on_logout)

        self.setWindowTitle(APP_NAME)
        set_icon(self)
        center_window(self, 600, 500)

    @qc.pyqtSlot()
    def _on_docs_list_update(self):
        try:
            response = self._app.web_client.list_all_docs()
        except http.client.HTTPException as exc:
            logger.exception(exc)
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
                self._app, doc.doc_id, doc.text(), self._user_id,
            )
            doc_window.activateWindow()
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

        doc_id = uuid.uuid1().int >> 65
        request = CreateDocRequest(title, self._user_id, doc_id)
        try:
            self._app.web_client.create_doc(request)
        except http.client.HTTPException as exc:
            logger.exception(exc)
            self.statusBar().showMessage(
                'Error while connecting to server', self.STATUS_TIMEOUT
            )
            return

        self._on_docs_list_update()

    def _logout_from_server(self):
        retry = True
        while retry:
            try:
                self._app.web_client.logout(self._login)
            except http.client.HTTPException as exc:
                logger.exception(exc)
                pressed = qw.QMessageBox.warning(
                    self,
                    'Warning',
                    'Cannot log out from server',
                    qw.QMessageBox.StandardButton.Close
                    | qw.QMessageBox.StandardButton.Retry,
                    qw.QMessageBox.StandardButton.Retry,
                )
                if pressed != qw.QMessageBox.StandardButton.Retry:
                    retry = False
            else:
                retry = False

    @qc.pyqtSlot()
    def _on_logout(self):
        if not self._app.focus == self._app.FOCUS_MAIN:
            return

        self.close()
        docs = list(self._opened_docs.values())
        for doc in docs:
            doc.close()

        self._app.web_client = None
        self._app.login_window = LoginWindow(self._app)
        self._app.focus = self._app.FOCUS_LOGIN

        self._app.login_window.show()

    @qc.pyqtSlot(str)
    def on_doc_closed(self, doc_id: str):
        if int(doc_id) in self._opened_docs:
            self._opened_docs.pop(int(doc_id))
        else:
            logger.error('Tried to close already closed doc')

    def closeEvent(self, event: qgui.QCloseEvent):
        self._logout_from_server()
        event.accept()


def _set_cursor_pos(
    position_tuple: typing.Tuple[int, int],
    mode: qgui.QTextCursor.MoveMode,
    cursor: qgui.QTextCursor,
):
    line = position_tuple[0]
    column = position_tuple[1]

    cursor.setPosition(0, mode)
    cursor.movePosition(
        qgui.QTextCursor.MoveOperation.Down, mode, line,
    )

    column = min(column, cursor.block().length())
    cursor.movePosition(
        qgui.QTextCursor.MoveOperation.Right, mode, column,
    )


class DocWindow(qw.QMainWindow):
    TIMER_TIMEOUT = 3000
    _closed = qc.pyqtSignal(str)

    def __init__(
        self, app: typing.Any, doc_id: int, title: str, user_id: int,
    ):
        super().__init__(app.main_window)

        self._app = app
        self._doc_id = doc_id
        self._title = title
        self._user_id = user_id
        self._saved = False
        self._status_message = None
        db_connector = self._app.db_helper.get_connector(user_id, doc_id)
        self._diff_sync = diff_sync.ClientDiffSync(
            db_connector, stack.Stack([])
        )

        self._textedit = qw.QTextEdit()
        self._load_doc()

        layout = qw.QVBoxLayout()
        layout.addWidget(self._textedit)
        layout.setContentsMargins(qc.QMargins(0, 0, 0, 0))
        self.setCentralWidget(qw.QWidget())
        self.centralWidget().setLayout(layout)

        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(
            '&Import', self._on_import, qgui.QKeySequence.StandardKey.Open
        )
        file_menu.addAction(
            '&Export', self._on_export, qgui.QKeySequence.StandardKey.SaveAs
        )
        file_menu.addAction(
            '&Save', self._save_doc, qgui.QKeySequence.StandardKey.Save
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
        self._timer.setInterval(self.TIMER_TIMEOUT)
        self._timer.setSingleShot(False)
        self._timer.start()

        self._textedit.textChanged.connect(self._on_edit)
        self._timer.timeout.connect(self._on_timer_timeout)
        self._closed.connect(self._app.main_window.on_doc_closed)

        self.setWindowTitle(f'{APP_NAME} - {self._title}')
        set_icon(self)
        center_window(self, 500, 700)

        self.show()
        self._save_doc(force=True)

    def _load_doc(self):
        text = None
        try:
            response = self._app.web_client.get_doc(
                GetDocRequest(self._user_id, self._doc_id)
            )
            text = response.text
            self._diff_sync.db_connector.set_text(text)
            self._diff_sync.db_connector.set_shadow(text)
            self._diff_sync.db_connector.set_client_version(
                response.client_version
            )
            self._diff_sync.db_connector.set_server_version(
                response.server_version
            )
        except http.client.HTTPException as exc:
            logger.exception(exc)
            qw.QMessageBox.warning(
                self._app.main_window,
                'Warning',
                'Cannot obtain actual version from server. '
                'Using local version instead.',
                qw.QMessageBox.StandardButton.Ok,
            )
        except db.DbException as exc:
            logger.exception(exc)
            qw.QMessageBox.critical(
                self._app.main_window,
                'Error',
                'Cannot save downloaded doc to db',
                qw.QMessageBox.StandardButton.Ok,
            )
            self.close()
            return

        if text is None:
            try:
                text = self._diff_sync.db_connector.get_text()
            except db.DbException as exc:
                logger.exception(exc)
                qw.QMessageBox.critical(
                    self._app.main_window,
                    'Error',
                    'Cannot load doc from db',
                    qw.QMessageBox.StandardButton.Ok,
                )
                self.close()
                return

        self._textedit.setPlainText(text)

    def _show_status(self):
        text_status = 'Saved' if self._saved else 'Unsaved changes'
        self.statusBar().showMessage(
            text_status
            + (f': {self._status_message}' if self._status_message else '')
        )

    @qc.pyqtSlot()
    def _on_edit(self):
        self._saved = False
        self._status_message = None
        self._show_status()

    def _set_text(self, text: str):
        cursor = self._textedit.textCursor()
        cursor_pos = (cursor.blockNumber(), cursor.columnNumber())
        cursor_anchor = None
        if cursor.hasSelection():
            cursor.setPosition(
                cursor.anchor(), qgui.QTextCursor.MoveMode.MoveAnchor
            )
            cursor_anchor = (cursor.blockNumber(), cursor.columnNumber())

        cursor = qgui.QTextCursor(self._textedit.document())
        cursor.select(qgui.QTextCursor.SelectionType.Document)
        cursor.insertText(text)

        new_cursor = self._textedit.textCursor()
        if cursor_anchor is not None:
            _set_cursor_pos(
                cursor_anchor, qgui.QTextCursor.MoveMode.MoveAnchor, new_cursor
            )
            _set_cursor_pos(
                cursor_pos, qgui.QTextCursor.MoveMode.KeepAnchor, new_cursor
            )
        else:
            _set_cursor_pos(
                cursor_pos, qgui.QTextCursor.MoveMode.MoveAnchor, new_cursor
            )
        self._textedit.setTextCursor(new_cursor)

    @qc.pyqtSlot()
    def _on_timer_timeout(self):
        self._save_doc(force=True)

    @qc.pyqtSlot()
    def _save_doc(self, force=False):
        saved_to_server = False

        if not self._saved or force:
            try:
                self._diff_sync.db_connector.set_text(
                    self._textedit.toPlainText()
                )
                updated = self._diff_sync.update()
                if updated or force:
                    edits = self._diff_sync.get_edits()
                    version = self._diff_sync.get_received_version()
                    request = UpdateDocRequest(
                        self._user_id, self._doc_id, version, list(edits)
                    )
                    response = self._app.web_client.update_doc(request)
                    self._diff_sync.patch_edits(
                        stack.Stack(response.edits), response.version
                    )
                    saved_to_server = True
                text = self._diff_sync.db_connector.get_text()
            except (http.client.HTTPException, db.DbException) as exc:
                logger.exception(exc)
                self._saved = False
                self._status_message = 'Error while saving'
            else:
                self._set_text(text)
                if saved_to_server:
                    self._saved = True
                    self._status_message = None

        self._show_status()

    @qc.pyqtSlot()
    def _on_import(self):
        filename, _ = qw.QFileDialog.getOpenFileName(
            self, 'Import document', f'{self._title}.txt', 'Text files (*.txt)'
        )
        if filename:
            try:
                with open(filename, 'r') as import_file:
                    self._textedit.setPlainText(import_file.read())
            except OSError as exc:
                logger.exception(exc)
                qw.QMessageBox.critical(
                    self,
                    'Error',
                    'Cannot read selected file',
                    qw.QMessageBox.StandardButton.Ok,
                )
            else:
                logger.info('Import doc from %s', filename)

        self._save_doc()

    @qc.pyqtSlot()
    def _on_export(self):
        self._save_doc()

        filename, _ = qw.QFileDialog.getSaveFileName(
            self, 'Export document', f'{self._title}.txt', 'Text files (*.txt)'
        )
        if filename:
            try:
                with open(filename, 'w') as export_file:
                    print(self._textedit.toPlainText(), file=export_file)
            except OSError as exc:
                logger.exception(exc)
                qw.QMessageBox.critical(
                    self,
                    'Error',
                    'Cannot write in selected file',
                    qw.QMessageBox.StandardButton.Ok,
                )
            else:
                logger.info('Export doc to %s', filename)

    def closeEvent(self, event: qgui.QCloseEvent):
        self._save_doc()
        self._closed.emit(str(self._doc_id))
        self._timer.stop()
        event.accept()
