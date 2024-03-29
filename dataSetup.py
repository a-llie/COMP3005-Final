import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

DB_NAME = 'Gym'
HOST = 'localhost'
PORT = '5432'

TABLE_CREATION_FILE = 'schema.ddl'
TABLE_POPULATION_FILE = 'sampleData.dml'


def execute_sql_file(file_path, conn):
    with open(file_path, 'r') as sql_file:
        cursor = conn.cursor()
        cursor.execute(sql_file.read())
        conn.commit()


def db_exists(conn, dbname):
    cursor = conn.cursor()
    cursor.execute(
        sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
        [dbname]
    )
    result = cursor.fetchone()
    cursor.close()
    return result is not None


def clear_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """)

    tables = cursor.fetchall()

    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE")

    conn.commit()
    cursor.close()


def main():
    dbname = DB_NAME
    user = 'POSTGRES_USER' #os.environ['POSTGRES_USER']
    password = 'POSTGRES_PASS' # os.environ['POSTGRES_PASS']
    host = HOST
    port = PORT

    conn = psycopg2.connect(dbname='postgres', user=user,
                            password=password, host=host, port=port)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    if not db_exists(conn, dbname):
        print(f"Database '{dbname}' does not exist. Creating...")
        # Create a new PostgreSQL database
        conn.cursor().execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname))
        )
        conn = psycopg2.connect(dbname=DB_NAME, user=user,
                                password=password, host=host, port=port)
    else:
        # Clear the existing database
        print(
            f"Database '{dbname}' already exists. Clearing existing tables...")
        conn = psycopg2.connect(dbname=DB_NAME, user=user,
                                password=password, host=host, port=port)
        clear_db(conn)

    # # Execute SQL commands from the file

    execute_sql_file(TABLE_CREATION_FILE, conn)
    execute_sql_file(TABLE_POPULATION_FILE, conn)

    cursor = conn.cursor()
    cursor.execute(
        "SELECT employee_id, schedule_start FROM schedule ORDER BY employee_id, schedule_start")

    print("Employee ID | Schedule Start")
    for row in cursor.fetchall():
        print(row)

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Exercise e WHERE ( SELECT c.capacity from Class c WHERE c.class_id = e.class_id) = 1")

    print("Exercise")
    for row in cursor.fetchall():
        print(row)


if __name__ == "__main__":
    main()
