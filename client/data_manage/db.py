import logging
import os
import typing

import PyQt5.QtSql as qsql

from client.data_manage import data_dir


logger = logging.getLogger('client')


class DbException(Exception):
    def __init__(self, text: str):
        super().__init__()
        self._text = text

    def __str__(self) -> str:
        return self._text


def exec_query(name: str, query: str, **kwargs) -> typing.List[typing.List]:
    db_query = qsql.QSqlQuery()
    if not db_query.prepare(query):
        raise DbException(
            f'Error while preparing {name}: {db_query.lastError().text()}'
        )
    for key, value in kwargs.items():
        db_query.bindValue(f':{key}', value)
    if not db_query.exec():
        raise DbException(
            f'Error while executing {name}: {db_query.lastError().text()}'
        )
    logger.info('Executed query: %s', name)

    records = []
    size = db_query.record().count()
    while db_query.next():
        record = []
        for i in range(size):
            record.append(db_query.value(i))
        records.append(record)
    return records


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
        query = self.INSERT_QUERY.format(table=self._table_name, field=field)
        exec_query(
            'INSERT_QUERY',
            query,
            value=value,
            doc_id=self._doc_id,
            user_id=self._user_id,
        )

    def _get_field(self, field: str) -> typing.Union[str, int]:
        query = self.SELECT_QUERY.format(table=self._table_name, field=field)
        records = exec_query(
            'SELECT_QUERY', query, doc_id=self._doc_id, user_id=self._user_id,
        )

        value = 0 if field.endswith('version') else ''
        for record in records:
            value = record[0] or value
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
    VERSION = 'v1'
    TABLE_NAME = f'users_files_{VERSION}'
    SETUP_DOCS_TABLE = '''
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
    SETUP_HOST_PORT_TABLE = '''
        CREATE TABLE IF NOT EXISTS host_port (
            id INT PRIMARY KEY,
            host VARCHAR NOT NULL,
            port VARCHAR NOT NULL
        );
    '''
    HOST_PORT_ID = 42
    SELECT_HOST_PORT = f'''
        SELECT host, port FROM host_port WHERE id = {HOST_PORT_ID};
    '''
    INSERT_HOST_PORT = f'''
        INSERT INTO host_port (id, host, port)
        VALUES ({HOST_PORT_ID}, :host, :port)
        ON CONFLICT (id) DO UPDATE SET host = :host, port = :port;
    '''

    def __init__(self):
        self._db = qsql.QSqlDatabase.addDatabase('QSQLITE')
        db_path = os.path.join(data_dir.get_data_dir(), '.docs.sqlite')
        self._db.setDatabaseName(db_path)
        if not self._db.open():
            raise DbException(f'Error while opening db')

        exec_query(
            'SETUP_DOCS_TABLE',
            self.SETUP_DOCS_TABLE.format(table=self.TABLE_NAME),
        )
        exec_query('SETUP_HOST_PORT_TABLE', self.SETUP_HOST_PORT_TABLE)

    def get_connector(self, user_id: int, doc_id: int) -> DbConnector:
        return DbConnector(self._db, self.TABLE_NAME, user_id, doc_id)

    def set_host_port(self, host: str, port: str):
        exec_query(
            'INSERT_HOST_PORT', self.INSERT_HOST_PORT, host=host, port=port
        )

    def get_host_port(self) -> typing.Tuple[str, str]:
        records = exec_query('SELECT_HOST_PORT', self.SELECT_HOST_PORT)

        host, port = '35.228.177.41', '80'
        for record in records:
            host, port = record
        return host, port

