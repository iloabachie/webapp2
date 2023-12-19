# create popstgres database.

import psycopg2
from psycopg2 import sql

# Replace 'username', 'password', 'localhost', '5432', and 'new_database' with your PostgreSQL credentials
connection_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '3984',
    'host': 'localhost'#,
   # 'port': '5432'
}

# Connect to the default 'postgres' database (it should always exist)
conn = psycopg2.connect(**connection_params)
conn.autocommit = True  # Set autocommit to True for database creation

# Create a cursor
cursor = conn.cursor()

# Replace 'new_database' with the name you want for your new database
new_database_name = 'new_database'

# Create a new PostgreSQL database
create_database_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_database_name))
cursor.execute(create_database_query)

# Close the cursor and connection
cursor.close()
conn.close()
 