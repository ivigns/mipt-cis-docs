import psycopg2
from psycopg2.extensions import AsIs


class Connector:
    def __init__(self, table_name, field_to_id, user_id, file_id):
        self.table_name = table_name
        self.field_to_id = field_to_id
        self.user_id = user_id
        self.file_id = file_id

    def get_text(self):
        return self.get_field("curr_text")

    def get_shadow(self):
        return self.get_field("shadow")

    def get_backup(self):
        return self.get_field("backup")

    def get_field(self, field):
        try:
            connection = psycopg2.connect(user="db_user",
                                          password="db_password",
                                          database="my_db")

            cursor = connection.cursor()

            sql_select_query = """select * from %s where file_id = %s and user_id = %s"""
            cursor.execute(sql_select_query, (AsIs(self.table_name), self.file_id, self.user_id))
            record = cursor.fetchone()
            if record is None:
                return record
            return record[self.field_to_id[field]]
        except (Exception, psycopg2.Error):
            return None
        finally:
            if connection:
                cursor.close()
                connection.close()

    def set_text(self, text):
        return self.set_field("curr_text", text)

    def set_shadow(self, text):
        return self.set_field("shadow", text)

    def set_backup(self, text):
        return self.set_field("backup", text)

    def set_field(self, field, value):
        try:
            connection = psycopg2.connect(user="db_user",
                                          password="db_password",
                                          database="my_db")

            cursor = connection.cursor()

            sql_select_query = """select * from %s where file_id = %s and user_id = %s"""
            cursor.execute(sql_select_query, (AsIs(self.table_name), self.file_id, self.user_id))
            record = cursor.fetchone()

            if record is None:
                cursor.execute(
                    "INSERT INTO %s (%s, file_id, user_id) VALUES(%s, %s, %s)",
                    (AsIs(self.table_name), AsIs(field), value, self.file_id, self.user_id))
                connection.commit()
            else:
                sql_update_query = """Update %s set %s = %s where file_id = %s and user_id = %s"""
                cursor.execute(sql_update_query,
                               (AsIs(self.table_name), AsIs(field), value, self.file_id, self.user_id))
                connection.commit()

            return True
        except (Exception, psycopg2.Error):
            return False

        finally:
            if connection:
                cursor.close()
                connection.close()
