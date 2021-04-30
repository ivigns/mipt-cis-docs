import psycopg2
from psycopg2.extensions import AsIs


class Stack:
    def __init__(self, table_name, field_to_id, user_id, file_id):
        self.table_name = table_name
        self.field_to_id = field_to_id
        self.user_id = user_id
        self.file_id = file_id
        self.stack = self.get_stack()

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        self.stack.pop()

    def clear(self):
        self.stack = []

    def top(self):
        return self.stack[-1]

    def size(self):
        return len(self.stack)

    def empty(self):
        return self.size() == 0

    def print(self):
        print(self.stack)

    def final(self):
        try:
            connection = psycopg2.connect(user="db_user",
                                          password="db_password",
                                          database="my_db")

            cursor = connection.cursor()

            for i, value in enumerate(self.stack):
                curr_text = value[0]
                version = value[1]
                cursor.execute(
                    "INSERT INTO %s (curr_text, version, file_id, user_id, order_id) VALUES(%s, %s, %s, %s, %s)",
                    (
                        AsIs(self.table_name), curr_text, version, self.file_id,
                        self.user_id, i))
                connection.commit()

            return True
        except (Exception, psycopg2.Error):
            return False

        finally:
            self.stack = []
            if connection:
                cursor.close()
                connection.close()

    def get_stack(self):
        try:
            connection = psycopg2.connect(user="db_user",
                                          password="db_password",
                                          database="my_db")

            cursor = connection.cursor()

            sql_select_query = """select * from %s where file_id = %s and user_id = %s"""
            cursor.execute(sql_select_query, (
                AsIs(self.table_name), self.file_id, self.user_id))
            connection.commit()
            stackWithOrder = []
            row = cursor.fetchone()
            while row:
                stackWithOrder.append((row[self.field_to_id["curr_text"]],
                                       row[self.field_to_id["version"]],
                                       row[self.field_to_id["order_id"]]))
                row = cursor.fetchone()

            stackWithOrder = sorted(stackWithOrder, key=lambda x: x[-1])
            stack = []
            for value in stackWithOrder:
                stack.append((value[0], value[1]))

            sql_delete_query = """delete from %s where file_id = %s and user_id = %s"""
            cursor.execute(sql_delete_query, (
                AsIs(self.table_name), self.file_id, self.user_id))
            connection.commit()
            return stack
        except (Exception, psycopg2.Error):
            return []
        finally:
            if connection:
                cursor.close()
                connection.close()
