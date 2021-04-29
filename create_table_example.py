import psycopg2

if __name__ == "__main__":
# Connect to the PostgreSQL database server
    postgresConnection = psycopg2.connect(
        "dbname=my_db user=db_user password='db_password'")
    
    # Get cursor object from the database connection
    
    cursor = postgresConnection.cursor()
    
    name_Table = "test_table_v100"
    
    # Create table statement
    
    sqlCreateTable = "create table " + name_Table + " (id bigint, title varchar(128), summary varchar(256), story text);"
    
    # Create a table in PostgreSQL database
    
    cursor.execute(sqlCreateTable)
    
    postgresConnection.commit()
    
    # Get the updated list of tables
    
    sqlGetTableList = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name ;"
    
    # Retrieve all the rows from the cursor
    
    cursor.execute(sqlGetTableList)
    
    tables = cursor.fetchall()
    
    # Print the names of the tables
    for table in tables:
        print(table)
