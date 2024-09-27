import pyodbc
from sqlalchemy import create_engine
import os


class BaseDatabaseConnection:
    def __init__(self):
        self.mssql_credentials = self.get_credentials()
        self.database = 'IDA'

    def get_credentials(self):
        mssql_hostname = os.getenv('DB_MSSQL_HOSTNAME')
        mssql_username = os.getenv('DB_MSSQL_USER')
        mssql_password = os.getenv('DB_MSSQL_PASSWORD')
        mssql_audit_username = os.getenv('DB_MSSQL_AUDIT_USER')
        mssql_audit_password = os.getenv('DB_MSSQL_AUDIT_PASSWORD')
        mssql_master_username = os.getenv('DB_MSSQL_MASTER_USER')
        mssql_master_password = os.getenv('DB_MSSQL_MASTER_PASSWORD')
        return {"hostname": mssql_hostname, "username": mssql_username, "password": mssql_password,
                "master_username": mssql_master_username, "master_password": mssql_master_password,
                "audit_username": mssql_audit_username, "audit_password": mssql_audit_password}


class DatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__()  # Initialize the parent class

        # Connection strings for SQLAlchemy with pyodbc
        con_string_template = "mssql+pyodbc://{un}:{pw}@{hn}/{db}?driver={od}&TrustServerCertificate=Yes"

        # Audit engine using ida_audit user
        audit_con_string = con_string_template.format(
            un=self.mssql_credentials['audit_username'],
            pw=self.mssql_credentials['audit_password'],
            hn=self.mssql_credentials['hostname'],
            db=self.database,
            od='ODBC+Driver+18+for+SQL+Server'
        )
        self.audit_engine = create_engine(audit_con_string)

        # Master engine using ida_master user
        master_con_string = con_string_template.format(
            un=self.mssql_credentials['master_username'],
            pw=self.mssql_credentials['master_password'],
            hn=self.mssql_credentials['hostname'],
            db=self.database,
            od='ODBC+Driver+18+for+SQL+Server'
        )
        self.master_engine = create_engine(master_con_string)

    def get_audit_engine(self):
        # Return the engine instance for ida_audit schema
        return self.audit_engine

    def get_master_engine(self):
        # Return the engine instance for ida_master schema
        return self.master_engine


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
