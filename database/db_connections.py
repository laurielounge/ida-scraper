# database/db_connections.py
import os

import pyodbc
from dotenv import find_dotenv
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from logging_mod.logger import logger

load_dotenv(find_dotenv())


class BaseDatabaseConnection:
    def __init__(self):
        self.database = os.getenv('DB_MSSQL_DATABASE')
        self.mssql_credentials = {
            "hostname": os.getenv('DB_MSSQL_HOSTNAME'),
            "username": os.getenv('DB_MSSQL_USERNAME'),
            "password": os.getenv('DB_MSSQL_PASSWORD'),
            "master_username": os.getenv('DB_MSSQL_MASTER_USERNAME'),
            "master_password": os.getenv('DB_MSSQL_MASTER_PASSWORD'),
            "audit_username": os.getenv('DB_MSSQL_AUDIT_USERNAME'),
            "audit_password": os.getenv('DB_MSSQL_AUDIT_PASSWORD')
        }
        self.driver = 'ODBC Driver 18 for SQL Server'

    def create_engine_for_schema(self, schema_type):
        logger.debug("Creating engine")
        credentials = self.mssql_credentials[f"{schema_type}_username"], self.mssql_credentials[
            f"{schema_type}_password"]
        con_string = f"mssql+pyodbc://{credentials[0]}:{credentials[1]}@{self.mssql_credentials['hostname']}/{self.database}?driver={self.driver}&TrustServerCertificate=Yes"
        return create_engine(con_string, echo=False, future=True)


class DatabaseConnections(BaseDatabaseConnection):
    def __init__(self):
        super().__init__()
        self.audit_engine = self.create_engine_for_schema('audit')
        self.master_engine = self.create_engine_for_schema('master')
        self.AuditSession = sessionmaker(bind=self.audit_engine, autocommit=False, autoflush=False)
        self.MasterSession = sessionmaker(bind=self.master_engine, autocommit=False, autoflush=False)

    def get_audit_session(self):
        logger.debug("Creating session for audit schema")
        return self.AuditSession()

    def get_master_session(self):
        logger.debug("Creating session for master schema")
        return self.MasterSession()


class MSSQLConnector(BaseDatabaseConnection):
    def __init__(self, target_schema='ida_audit'):
        super().__init__()
        self.connection_string = self._build_conn_string(target_schema)

    def _build_conn_string(self, target_schema):
        con_string_template = "DRIVER={od};SERVER={hn};DATABASE={db};UID={un};PWD={pw};TrustServerCertificate=Yes"
        if target_schema == 'ida_audit':
            return con_string_template.format(
                un=self.mssql_credentials['audit_username'],
                pw=self.mssql_credentials['audit_password'],
                hn=self.mssql_credentials['hostname'],
                db=self.database,
                od='{ODBC Driver 18 for SQL Server}'
            )
        else:
            return con_string_template.format(
                un=self.mssql_credentials['master_username'],
                pw=self.mssql_credentials['master_password'],
                hn=self.mssql_credentials['hostname'],
                db=self.database,
                od='{ODBC Driver 18 for SQL Server}'
            )

    class _ConnectionContext:
        def __init__(self, conn_string):
            self.conn_string = conn_string

        def __enter__(self):
            self.conn = pyodbc.connect(self.conn_string)
            self.cursor = self.conn.cursor()
            return self.conn, self.cursor

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.cursor.close()
            self.conn.close()

    def connection(self):
        return self._ConnectionContext(self.connection_string)
