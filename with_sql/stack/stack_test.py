from stack import Stack
import psycopg2

if __name__ == "__main__":
    postgresConnection = psycopg2.connect(user="db_user",
                                          password="db_password",
                                          database="my_db")
    cursor = postgresConnection.cursor()
    table_name = "stack"
    cursor.execute(
        "select exists(select * from information_schema.tables where table_name=%s)",
        (table_name,))
    if not cursor.fetchone()[0]:
        print("creating table")
        sqlCreateTable = "create table " + table_name + " (curr_text text not null, version int not null, file_id int not null, user_id int not null, order_id int not null);"
        cursor.execute(sqlCreateTable)
        postgresConnection.commit()
    else:
        print("table exists")

    field_to_id = {"curr_text": 0, "version": 1, "file_id": 2, "user_id": 3,
                   "order_id": 4}
    stack = Stack(table_name, field_to_id, 10, 22)
    stack.print() # empty
    stack.push(("text1", 1))
    stack.push(("text2", 2))
    stack.push(("text3", 3))
    stack.pop()
    stack.print() # text1, text2
    stack.final()
    stack.print() # empty

    stack = Stack(table_name, field_to_id, 10, 22)
    stack.print() # text1, text2
    stack.push(("text5", 5))
    stack.push(("text6", 6))
    stack.pop()
    stack.print() # text1, text2, text5
    stack.final()
    stack.print() # empty

    stack = Stack(table_name, field_to_id, 10, 22)
    stack.print()  # text1, text2, text5
    stack.final()

    stack = Stack(table_name, field_to_id, 10, 21)
    stack.print()  # empty
    stack.final()
