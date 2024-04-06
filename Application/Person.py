from abc import abstractmethod
import psycopg2
from psycopg2 import sql


class Person():
    first_name: str
    last_name: str
    conn: psycopg2._psycopg.connection

    def __init__(self, first_name, last_name, conn) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.conn = conn

    @abstractmethod
    def options(self):
        pass
