import psycopg2

from psycopg2.extensions import AsIs
from server_diff_sync import ServerDiffSync


class Connector:
    def __init__(self, docs_table_name, users_table_name, field_to_id, connection, logger):
        self.docs_table_name = docs_table_name
        self.users_table_name = users_table_name
        self.field_to_id = field_to_id

        self.connection = connection
        self.cursor = connection.cursor()

        self.logger = logger

    def check_docs_table(self, table_name):
        try:
            self.cursor.execute(
                "select exists(select * from information_schema.tables where table_name=%s)",
                (table_name,))
            if not self.cursor.fetchone()[0]:
                self.logger.info("creating table %s" % table_name)
                sqlCreateTable = "create table " + table_name + " (curr_text text null, " \
                                                                "shadow text null, " \
                                                                "backup text null, " \
                                                                "doc_id bigint not null, " \
                                                                "user_id bigint not null, " \
                                                                "title text not null, " \
                                                                "server_version text not null DEFAULT 0, " \
                                                                "client_version text not null DEFAULT 0);"
                self.cursor.execute(sqlCreateTable)
                self.connection.commit()
                self.logger.info("Table %s created" % table_name)
            else:
                self.logger.info("Table %s exists" % table_name)
        except Exception as exception:
            self.logger.info("Failed check_docs_table query, reason: %s" % exception)

    def check_users_table(self, table_name):
        try:
            self.cursor.execute(
                "select exists(select * from information_schema.tables where table_name=%s)",
                (table_name,))
            if not self.cursor.fetchone()[0]:
                self.logger.info("creating table %s" % table_name)
                sqlCreateTable = "create table " + table_name + " (login text not null, user_id int not null);"
                self.cursor.execute(sqlCreateTable)
                self.connection.commit()
                self.logger.info("Table %s created" % table_name)
            else:
                self.logger.info("table %s exists" % table_name)
        except Exception as exception:
            self.logger.info("Failed check_users_table query, reason: %s" % exception)

    def get_text(self, doc_id, user_id):
        return self.get_field("curr_text", doc_id, user_id)

    def get_shadow(self, doc_id, user_id):
        return self.get_field("shadow", doc_id, user_id)

    def get_backup(self, doc_id, user_id):
        return self.get_field("backup", doc_id, user_id)

    def get_client_version(self, doc_id, user_id):
        version = self.get_field("client_version", doc_id, user_id)
        if version is not None:
            return version
        else:
            return 0

    def get_server_version(self, doc_id, user_id):
        return self.get_field("server_version", doc_id, user_id)

    def get_field(self, field, doc_id, user_id):
        try:
            sql_select_query = """select * from %s where doc_id = %s and user_id = %s"""
            self.cursor.execute(sql_select_query % (self.docs_table_name, doc_id, user_id))
            record = self.cursor.fetchone()
            self.logger.info(
                "Success get_field query, user_id, doc_id, field, value: %s %s %s %s" % (user_id, doc_id, field, record)
            )
            if record is None:
                return record
            return record[self.field_to_id[field]]
        except Exception as exception:
            self.logger.info("Failed get_field query, reason: %s" % exception)
            return None

    def list_all_docs(self):
        try:
            sql_select_query = """select * from %s"""
            self.cursor.execute(sql_select_query % self.docs_table_name)
            records = self.cursor.fetchall()
            if records is None:
                return records
            result = []
            for row in records:
                result.append({'title': row[self.field_to_id['title']],
                               'doc_id': row[self.field_to_id['doc_id']]})
            return result
        except Exception as exception:
            self.logger.info("Failed get_field query, reason: %s" % exception)
            return None

    def create_doc(self, title, doc_id, user_id):
        self.set_field("title", title, doc_id, user_id)

    def set_text(self, text, doc_id, user_id):
        self.set_field("curr_text", text, doc_id, user_id)

    def set_shadow(self, text, doc_id, user_id):
        self.set_field("shadow", text, doc_id, user_id)

    def set_backup(self, text, doc_id, user_id):
        self.set_field("backup", text, doc_id, user_id)

    def set_client_version(self, version, doc_id, user_id):
        self.set_field("client_version", version, doc_id, user_id)

    def set_server_version(self, version, doc_id, user_id):
        self.set_field("server_version", version, doc_id, user_id)

    def set_login(self, user_login, user_id):
        try:
            sql_select_query = """select * from %s where login = '%s'"""
            self.cursor.execute(sql_select_query % (self.users_table_name, user_login))
            record = self.cursor.fetchone()

            if record is None:
                self.cursor.execute("INSERT INTO %s (login, user_id) VALUES(%s, %s)",
                                    (AsIs(self.users_table_name), user_login, user_id))
                self.connection.commit()
                self.logger.info("User %s added to base" % user_login)
            else:
                self.logger.info("User %s is already known" % user_login)
        except Exception as exception:
            self.logger.info("Failed set_login query, reason: %s" % exception)

    def update_doc(self, doc_id, user_id, received_version, edits):
        self.logger.info("Update doc, document %s accepted, old version %s" % (doc_id, received_version))
        self.server_diff_sync = ServerDiffSync(self, edits, doc_id, user_id, self.logger)
        self.server_diff_sync.patch_edits(edits, received_version)
        self.logger.info("Update doc, document %s patched" % doc_id)
        self.server_diff_sync.update()
        self.logger.info("Update doc, document %s updated")
        return self.server_diff_sync.get_received_version(), self.server_diff_sync.get_edits()

    def set_field(self, field, value, doc_id, user_id):
        try:
            sql_select_query = """select * from %s where doc_id = %s and user_id = %s"""
            self.cursor.execute(sql_select_query, (AsIs(self.docs_table_name), doc_id, user_id))
            record = self.cursor.fetchone()

            if record is None:
                self.cursor.execute(
                    "INSERT INTO %s (%s, doc_id, user_id) VALUES(%s, %s, %s)",
                    (AsIs(self.docs_table_name), AsIs(field), value, doc_id, user_id))
                self.connection.commit()
            else:
                sql_update_query = """Update %s set %s = %s where doc_id = %s and user_id = %s"""
                self.cursor.execute(sql_update_query,
                               (AsIs(self.docs_table_name), AsIs(field), value, doc_id, user_id))
                self.connection.commit()
            self.logger.info(
                "Success set_field query, user_id, doc_id, field, value: %s %s %s %s" % (user_id, doc_id, field, value)
            )
            return True
        except Exception as exception:
            self.logger.info("Failed set_field query, reason: %s" % exception)
            return False
