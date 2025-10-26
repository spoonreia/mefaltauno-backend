from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

import app.infra.database.database_service as db

# DB app
default_mysql_connections_app = {
    "tt": "root:MeFaltaUno2024!@localhost:3306/yojuego"
}

default_mysql_connections = default_mysql_connections_app

DB_POOL_SIZE: int = 2
DB_POOL_MAX_SIZE: int = 5
DB_LOG_QUERY: bool = False
DB_CONNECTION_RECYCLE: int = 3600

database_client = db.DatabaseService.create(
    impl=db.BIOMySqlConnection,
    connections=default_mysql_connections,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_POOL_MAX_SIZE,
    echo=DB_LOG_QUERY,
    connection_recycle=DB_CONNECTION_RECYCLE,
)

Base = declarative_base()

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)
