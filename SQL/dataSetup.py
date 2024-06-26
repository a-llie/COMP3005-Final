import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

DB_NAME = 'Gym'
HOST = 'localhost'
PORT = '5432'


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
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASS']
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

    sql_dir = os.path.dirname(__file__)

    if not sql_dir.endswith('SQL'):
        sql_dir = os.path.join(sql_dir, 'SQL')

    files = [None, None]
    for file in os.listdir(sql_dir):
        if file.startswith('schema') and file.endswith('.sql'):
            files[0] = sql_dir + "\\" + file
        elif file.startswith('sample') and file.endswith('.sql'):
            files[1] = sql_dir + "\\" + file

    for file in files:
        if file is not None:
            execute_sql_file(file, conn)

    if files[0] is None:
        print("No schema file found. Exiting.")
        return


if __name__ == "__main__":
    main()
