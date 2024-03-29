import psycopg2
from psycopg2 import sql


class Person():
    first_name: str
    last_name: str
    conn: cursor
    

    def __init__(self, first_name, last_name, conn) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.conn = conn
        

        print(f'Person {self.first_name} {self.last_name} created.')
