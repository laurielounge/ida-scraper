# /database/base_route.py

from database.db_connections import DatabaseConnections

db_connection = DatabaseConnections()


def get_db():
    with db_connection.get_master_session() as db:
        yield db
