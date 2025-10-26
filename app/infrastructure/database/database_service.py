from abc import ABCMeta, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


class DatabaseConnection(metaclass=ABCMeta):
    @abstractmethod
    def get_session(self, key) -> Session:
        pass

    @abstractmethod
    def get_engine(self, key):
        pass


class BIOMySqlConnection(DatabaseConnection):
    def __init__(self, connections, pool_size=10, max_overflow=10, echo=True, connection_recycle=3600):
        self.engines = {}
        self.sessions = {}
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.echo = echo
        self.pool_recycle = connection_recycle
        self.__load_datasources(connections)

    def __load_datasources(self, connections):
        url_driver = "mysql+pymysql://"
        for key in connections:
            self.engines[key] = create_engine(
                f"{url_driver}{connections[key]}",
                pool_pre_ping=True,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                echo=self.echo,
                pool_recycle=self.pool_recycle,
            )
            self.sessions[key] = sessionmaker(self.engines[key], autocommit=False, expire_on_commit=False)

    def get_session(self, key) -> Session:
        return self.sessions[key]()

    def get_engine(self, key):
        return self.engines[key]


class DatabaseService:
    @staticmethod
    def create(impl: DatabaseConnection, connections: dict, **params) -> DatabaseConnection:
        return impl(connections, **params)
