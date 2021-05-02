from collections import deque
import os
import typing

import PyQt5.QtCore as qc
import PyQt5.QtSql as qsql


class DbException(Exception):
    def __init__(self, text: str):
        super().__init__()
        self._text = text

    def __str__(self) -> str:
        return self._text


class DbConnector:
    INSERT_QUERY = '''
        INSERT INTO {table} ({field}, doc_id, user_id)
        VALUES (:value, :doc_id, :user_id)
        ON CONFLICT (doc_id, user_id) DO UPDATE SET {field} = :value;
    '''
    SELECT_QUERY = '''
        SELECT {field} FROM {table}
        WHERE doc_id = :doc_id AND user_id = :user_id;
    '''

    def __init__(
        self, db: qsql.QSqlDatabase, table_name: str, user_id: int, doc_id: int
    ):
        self._table_name = table_name
        self._user_id = user_id
        self._doc_id = doc_id
        self._db = db

    def _set_field(self, field: str, value: typing.Union[str, int]):
        query = qsql.QSqlQuery()
        if not query.prepare(
            self.INSERT_QUERY.format(table=self._table_name, field=field)
        ):
            raise DbException(
                'Error while preparing INSERT_QUERY: '
                f'{query.lastError().text()}'
            )
        query.bindValue(':value', value)
        query.bindValue(':doc_id', self._doc_id)
        query.bindValue(':user_id', self._user_id)
        if not query.exec():
            raise DbException(
                'Error while executing INSERT_QUERY: '
                f'{query.lastError().text()}'
            )

    def _get_field(self, field: str) -> typing.Union[str, int]:
        query = qsql.QSqlQuery()
        if not query.prepare(
            self.SELECT_QUERY.format(table=self._table_name, field=field)
        ):
            raise DbException(
                'Error while preparing SELECT_QUERY: '
                f'{query.lastError().text()}'
            )
        query.bindValue(':doc_id', self._doc_id)
        query.bindValue(':user_id', self._user_id)
        if not query.exec():
            raise DbException(
                'Error while executing SELECT_QUERY: '
                f'{query.lastError().text()}'
            )

        value = 0 if field.endswith('version') else ''
        while query.next():
            value = query.value(0) or value
        return value

    def get_text(self) -> str:
        return self._get_field('curr_text')

    def get_shadow(self) -> str:
        return self._get_field('shadow')

    def get_client_version(self) -> int:
        return self._get_field('client_version')

    def get_server_version(self) -> int:
        return self._get_field('server_version')

    def set_text(self, text: str):
        self._set_field('curr_text', text)

    def set_shadow(self, text: str):
        self._set_field('shadow', text)

    def set_client_version(self, version: int):
        self._set_field('client_version', version)

    def set_server_version(self, version: int):
        self._set_field('server_version', version)


class DbHelper:
    DB_DIR = 'MiptCisDocs'
    VERSION = 'v1'
    TABLE_NAME = f'users_files_{VERSION}'
    SETUP_QUERY = '''
        CREATE TABLE IF NOT EXISTS {table} (
            doc_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            client_version BIGINT,
            server_version BIGINT,
            curr_text TEXT,
            shadow TEXT,
            PRIMARY KEY(doc_id, user_id)
        );
    '''

    def __init__(self):
        self._db = qsql.QSqlDatabase.addDatabase('QSQLITE')
        writable_location = qc.QStandardPaths.writableLocation(
            qc.QStandardPaths.StandardLocation.AppDataLocation
        )
        writable_location = os.path.abspath(os.path.join(writable_location, '..', self.DB_DIR))
        if not os.path.exists(writable_location):
            os.mkdir(writable_location)
        self._db.setDatabaseName(
            os.path.join(f'{writable_location}', '.docs.sqlite',)
        )
        if not self._db.open():
            raise DbException(f'Error while opening db')

        query = qsql.QSqlQuery()
        if not query.exec(self.SETUP_QUERY.format(table=self.TABLE_NAME)):
            raise DbException(
                f'Error while db setup: {query.lastError().text()}'
            )

    def get_connector(self, user_id: int, doc_id: int) -> DbConnector:
        return DbConnector(self._db, self.TABLE_NAME, user_id, doc_id)


class Stack(deque):
    def __init__(self, values):
        super().__init__(values)

    def push(self, item):
        self.append(item)

    def top(self):
        return self[-1]

    def empty(self):
        return not self