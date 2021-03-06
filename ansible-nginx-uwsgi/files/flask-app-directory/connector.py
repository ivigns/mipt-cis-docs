import psycopg2

from psycopg2.extensions import AsIs
from server_diff_sync import ServerDiffSync
from mock_stack import MockStack


class Connector:
    def __init__(self, docs_info_table_name, docs_texts_table_name, users_table_name, field_to_id_docs_info, field_to_id_docs_texts, connection, logger):
        self.docs_info_table_name = docs_info_table_name
        self.docs_texts_table_name = docs_texts_table_name
        self.users_table_name = users_table_name
        self.field_to_id_docs_info = field_to_id_docs_info
        self.field_to_id_docs_texts = field_to_id_docs_texts
        
        self.connection = connection
        self.cursor = connection.cursor()

        self.logger = logger

    def check_docs_table(self):
        try:
            self.cursor.execute(
                "select exists(select * from information_schema.tables where table_name=%s)",
                (self.docs_info_table_name,))
            if not self.cursor.fetchone()[0]:
                self.logger.info("creating tables %s, %s" % (self.docs_info_table_name, self.docs_texts_table_name))
                sqlCreateTable = "create table " + self.docs_info_table_name + " (shadow text null DEFAULT '', " \
                                                                "backup text null DEFAULT '', " \
                                                                "doc_id bigint not null, " \
                                                                "user_id bigint not null, " \
                                                                "server_version int not null DEFAULT 0, " \
                                                                "client_version int not null DEFAULT 0);"
                self.cursor.execute(sqlCreateTable)

                sqlCreateTable = "create table " + self.docs_texts_table_name + " (curr_text text null DEFAULT '', " \
                                                                "doc_id bigint not null, " \
                                                                "title text not null DEFAULT '');"
                self.cursor.execute(sqlCreateTable)
                self.logger.info("Tables %s, %s created" % (self.docs_info_table_name, self.docs_texts_table_name))
            else:
                self.logger.info("Tables %s, %s exists" % (self.docs_info_table_name, self.docs_texts_table_name))
        except Exception as exception:
            self.logger.info("Failed check_docs_table query, reason: %s" % exception)

    def check_users_table(self):
        try:
            self.cursor.execute(
                "select exists(select * from information_schema.tables where table_name=%s)",
                (self.users_table_name,))
            if not self.cursor.fetchone()[0]:
                self.logger.info("creating table %s" % self.users_table_name)
                sqlCreateTable = "create table " + self.users_table_name + " (login text not null, user_id int not null, is_online int not null DEFAULT 0);"
                self.cursor.execute(sqlCreateTable)
                
                self.logger.info("Table %s created" % self.users_table_name)
            else:
                self.logger.info("table %s exists" % self.users_table_name)
        except Exception as exception:
            self.logger.info("Failed check_users_table query, reason: %s" % exception)

    def get_text(self, doc_id, user_id):
        value = self.get_field("curr_text", doc_id, user_id, table_name=self.docs_texts_table_name, field_to_id=self.field_to_id_docs_texts)
        if value is not None:
            return value
        else:
            return ''

    def get_shadow(self, doc_id, user_id):
        value = self.get_field("shadow", doc_id, user_id)
        if value is not None:
            return value
        else:
            return ''

    def get_backup(self, doc_id, user_id):
        value = self.get_field("backup", doc_id, user_id)
        if value is not None:
            return value
        else:
            return ''

    def get_client_version(self, doc_id, user_id):
        version = self.get_field("client_version", doc_id, user_id)
        if version is not None:
            self.logger.info("Success get_client_version query, value: %s" % version)
            return version
        else:
            self.logger.info("Success get_client_version query, value: %d" % 0)
            return 0

    def get_server_version(self, doc_id, user_id):
        version = self.get_field("server_version", doc_id, user_id)
        if version is not None:
            self.logger.info("Success get_server_version query, value: %s" % version)
            return version
        else:
            self.logger.info("Success get_server_version query, value: %d" % 0)
            return 0

    def get_field(self, field, doc_id, user_id, table_name=None, field_to_id=None):
        if table_name is None:
            table_name = self.docs_info_table_name
        if field_to_id is None:
            field_to_id = self.field_to_id_docs_info
        try:
            if table_name != self.docs_info_table_name:
                sql_select_query = """select * from %s where doc_id = %s"""
                self.cursor.execute(sql_select_query % (table_name, doc_id))
            else:
                sql_select_query = """select * from %s where doc_id = %s and user_id = %s"""
                self.cursor.execute(sql_select_query % (table_name, doc_id, user_id))

            record = self.cursor.fetchone()
            self.logger.info(
                "Success get_field query, field, record: %s %s" % (field, record)
            )
            if record is None:
                return record
            return record[field_to_id[field]]
        except Exception as exception:
            self.logger.info("Failed get_field query, reason: %s" % exception)
            return None

    def list_all_docs(self):
        try:
            sql_select_query = """select * from %s"""
            self.cursor.execute(sql_select_query % self.docs_texts_table_name)
            records = self.cursor.fetchall()
            if records is None:
                return records
            result = []
            for row in records:
                result.append({'title': row[self.field_to_id_docs_texts['title']],
                               'doc_id': row[self.field_to_id_docs_texts['doc_id']]})
            return result[::-1]
        except Exception as exception:
            self.logger.info("Failed get_field query, reason: %s" % exception)
            return None

    def create_doc(self, title, doc_id, user_id):
        self.set_field("title", title, doc_id, user_id, table_name=self.docs_texts_table_name)

    def set_text(self, text, doc_id, user_id):
        self.set_field("curr_text", text, doc_id, user_id, table_name=self.docs_texts_table_name)

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
                
                self.logger.info("New user %s added to base" % user_login)
                return True
            else:
                sql_select_query = """select * from %s where login = '%s' and is_online = 1"""
                self.cursor.execute(sql_select_query % (self.users_table_name, user_login))
                user_is_online = self.cursor.fetchone()
                if user_is_online is not None:
                    self.logger.info("User %s is already online, access denied" % user_login)
                    return False
                else:
                    sql_update_query = """Update %s set %s = %s where login = '%s'"""
                    self.cursor.execute(sql_update_query %
                                        (self.users_table_name, "is_online", 1, user_login))
                    self.logger.info("User %s is online" % user_login)
                    return True
        except Exception as exception:
            self.logger.info("Failed set_login query, reason: %s" % exception)

    def logout(self, user_login):
        sql_update_query = """Update %s set %s = %s where login = '%s'"""
        self.cursor.execute(sql_update_query %
                            (self.users_table_name, "is_online", 0, user_login))
        self.logger.info("User %s is logged out" % user_login)

    def update_doc(self, doc_id, user_id, received_version, edits):
        edits_stack = MockStack(edits)
        self.logger.info("Update doc, document %s accepted, old version %s, edits %s" % (doc_id, received_version, edits))
        self.server_diff_sync = ServerDiffSync(self, MockStack([]), doc_id, user_id, self.logger)
        self.server_diff_sync.patch_edits(edits_stack, received_version)
        self.logger.info("Update doc, document %s patched, ready to update" % doc_id)
        self.server_diff_sync.update()
        self.logger.info("Update doc, document %s updated" % doc_id)
        return self.server_diff_sync.get_received_version(), self.server_diff_sync.get_edits()

    def set_field(self, field, value, doc_id, user_id, table_name=None):
        if table_name is None:
            table_name = self.docs_info_table_name
        try:
            if table_name != self.docs_info_table_name:
                sql_select_query = """select * from %s where doc_id = %s"""
                self.cursor.execute(sql_select_query, (AsIs(table_name), doc_id))

                record = self.cursor.fetchone()
                if record is None:
                    self.cursor.execute(
                        "INSERT INTO %s (%s, doc_id) VALUES(%s, %s)",
                        (AsIs(table_name), AsIs(field), value, doc_id))

                else:
                    sql_update_query = """Update %s set %s = %s where doc_id = %s"""
                    self.cursor.execute(sql_update_query,
                                        (AsIs(table_name), AsIs(field), value, doc_id))
            else:
                sql_select_query = """select * from %s where doc_id = %s and user_id = %s"""
                self.cursor.execute(sql_select_query, (AsIs(table_name), doc_id, user_id))

                record = self.cursor.fetchone()
                if record is None:
                    self.cursor.execute(
                        "INSERT INTO %s (%s, doc_id, user_id) VALUES(%s, %s, %s)",
                        (AsIs(table_name), AsIs(field), value, doc_id, user_id))

                else:
                    sql_update_query = """Update %s set %s = %s where doc_id = %s and user_id = %s"""
                    self.cursor.execute(sql_update_query,
                                   (AsIs(table_name), AsIs(field), value, doc_id, user_id))
                
            self.logger.info(
                "Success set_field query, user_id, doc_id, field, value: %s %s %s %s" % (user_id, doc_id, field, value)
            )
            return True
        except Exception as exception:
            self.logger.info("Failed set_field query, reason: %s" % exception)
            return False
