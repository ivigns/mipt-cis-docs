import typing

import PyQt5.QtSql as qsql


class DbConnector:
    INSERT_QUERY = '''
        INSERT INTO {table} ({field}, file_id, user_id)
        VALUES ({value}, {file_id}, {user_id})
        ON CONFLICT (file_id, user_id) DO UPDATE SET {field} = {value};
    '''
    SELECT_QUERY = '''
        SELECT {field} FROM {table}
        WHERE file_id = {file_id} AND user_id = {user_id};
    '''

    def __init__(
        self, db: qsql.QSqlDatabase, table_name: str, login: str, doc_name: str
    ):
        self._table_name = table_name
        self._user_id = login
        self._file_id = doc_name
        self._db = db

    def _set_field(self, field: str, text: str):
        query = qsql.QSqlQuery()
        query.exec(
            self.INSERT_QUERY.format(
                table=self._table_name,
                field=field,
                value=text,
                file_id=self._file_id,
                user_id=self._user_id,
            )
        )

    def _get_field(self, field: str) -> typing.Optional[str]:
        query = qsql.QSqlQuery()
        query.exec(
            self.SELECT_QUERY.format(
                table=self._table_name,
                field=field,
                file_id=self._file_id,
                user_id=self._user_id,
            )
        )
        result = None
        while query.next():
            result = query.value(0)
        return result

    def get_text(self) -> typing.Optional[str]:
        return self._get_field('curr_text')

    def get_shadow(self) -> typing.Optional[str]:
        return self._get_field('shadow')

    def set_text(self, text: str):
        self._set_field('curr_text', text)

    def set_shadow(self, text: str):
        self._set_field('shadow', text)


class DbHelper:
    VERSION = 'v1'
    TABLE_NAME = f'users_files_{self.VERSION}'
    SETUP_QUERY = '''
        CREATE TABLE IF NOT EXISTS {table} (
            file_id VARCHAR NOT NULL,
            user_id VARCHAR NOT NULL,
            curr_text TEXT,
            shadow TEXT,
            PRIMARY KEY(file_id, user_id)
        );
    '''

    def __init__(self):
        self._db = qsql.QSqlDatabase.addDatabase('QSQLITE')
        self._db.setDatabaseName('.docs.sqlite')
        self._db.open()

        query = qsql.QSqlQuery()
        ok = query.exec(SETUP_QUERY.format(table=self.TABLE_NAME))
        if not ok:
            raise RuntimeError('Error while db setup')

    def get_connector(self, login: str, doc_name: str) -> DbConnector:
        return DbConnector(self._db, self.TABLE_NAME, login, doc_name)

