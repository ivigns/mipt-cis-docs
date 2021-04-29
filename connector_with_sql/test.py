from connector import Connector
import psycopg2

if __name__ == "__main__":
    postgresConnection = psycopg2.connect(user="db_user",
                                          password="db_password",
                                          database="my_db")
    cursor = postgresConnection.cursor()
    table_name = "test_v10"
    cursor.execute(
        "select exists(select * from information_schema.tables where table_name=%s)",
        (table_name,))
    if not cursor.fetchone()[0]:
        print("creating table")
        sqlCreateTable = "create table " + table_name + " (curr_text text null, shadow text null, backup text null, file_id int not null, user_id int not null);"
        cursor.execute(sqlCreateTable)
        postgresConnection.commit()
    else:
        print("table exists")
    
    field_to_id = {"curr_text": 0, "shadow": 1, "backup": 2, "file_id": 3,
     "user_id": 4}
    connector = Connector(table_name, field_to_id, 10, 20)
    connector.set_text("test2")
    print(connector.get_text())
    connector.set_text("test3")
    print(connector.get_text())
    print(connector.get_backup())
    connector.set_shadow("shadow1")
    print(connector.get_shadow())

    connector2 = Connector(table_name, field_to_id, 30, 24)
    connector2.set_text("test2")
    print(connector2.get_text())
    connector2.set_text("test5")
    print(connector2.get_text())
    print(connector2.get_backup())
    connector2.set_shadow("shadow10")
    print(connector2.get_shadow())
