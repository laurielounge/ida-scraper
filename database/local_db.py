import logging
import os
from mysql.connector import pooling
from sqlalchemy import create_engine
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseDatabaseConnection:
    def __init__(self):
        self.mysql_credentials = self.get_credentials()

    def get_credentials(self):
        mysql_hostname = 'localhost'
        mysql_username = os.getenv('DB_MARIA_USER')
        mysql_password = os.getenv('DB_MARIA_PASSWORD')
        return {"hostname": mysql_hostname, "username": mysql_username, "password": mysql_password}


class DatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__()  # Initialize the parent class

        hostname = self.mysql_credentials['hostname']
        username = self.mysql_credentials['username']
        password = self.mysql_credentials['password']
        mysql_pre = "mysql+mysqlconnector:"
        database = 'spider'

        self.connection_string = f'{mysql_pre}//{username}:{password}@{hostname}/{database}'

        self.engine = create_engine(self.connection_string)

    def get_engine(self):
        # Return the engine instance
        return self.engine


class MySQLConnectorPool(BaseDatabaseConnection):
    def __init__(self, pool_name="spider", pool_size=5, database='spider'):
        super().__init__()  # Initialize the parent class
        self.pool = pool_name
        logging.debug(f"Creating pool {self.pool}")
        self.database = database
        hostname = self.mysql_credentials['hostname']
        username = self.mysql_credentials['username']
        password = self.mysql_credentials['password']

        logging.info(f"MySQLConnectorPool: Creating pool hostname is {hostname}")

        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                host=hostname,
                user=username,
                password=password,
                database=self.database,
            )
            logging.debug(f"Pool created {self.pool}")
        except Exception as e:
            self.pool = None
            logging.error(f"Pool creation failed {e}")

    class _ConnectionContext:
        def __init__(self, pool):
            self.pool = pool

        def __enter__(self):
            self.conn = self.pool.get_connection()
            self.cursor = self.conn.cursor(dictionary=True)  # Using dictionary cursor
            return self.conn, self.cursor

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.cursor.close()
            self.conn.close()

    def connection(self):
        return self._ConnectionContext(self.pool)

    def __str__(self):
        return f"{self.__class__.__name__} Database Connection for database {self.database}"
