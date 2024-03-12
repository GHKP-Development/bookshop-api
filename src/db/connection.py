from decimal import Decimal

from sqlalchemy import Engine, create_engine, text

from config import DBConfig, DBEngineType
from src.core.category import ProductCategory
from src.utils.logging.logger import Logger
from src.db.models import Base, ProductModel


class Database:

    def __init__(self, cfg: DBConfig, logger: Logger) -> None:
        self._cfg: DBConfig = cfg
        self._logger: Logger = logger
        self._db: Engine = self._create_engine()
        self.create_tables()

    def _create_engine(self) -> Engine:
        if self._cfg.engine == DBEngineType.POSTGRESQL:
            self._instrument_postgres_db()
        self._logger.debug(f"Creating {self._cfg.engine} database engine with user {self._cfg.username} and database {self._cfg.db_name}")
        return create_engine(str(self._cfg))

    def _instrument_postgres_db(self):
        self._logger.debug("instrumenting postgres database")
        default_engine = create_engine(
            f'postgresql://{self._cfg.username}:{self._cfg.password}@{self._cfg.host}:{self._cfg.port}/postgres')
        with default_engine.connect() as conn:
            self._logger.debug(f"Searching for database {self._cfg.db_name}")
            conn.execute(text('commit'))  # Required to execute CREATE DATABASE outside of a transaction block
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{self._cfg.db_name}'"))
            if not result.fetchone():
                self._logger.debug(f"Database not found for database {self._cfg.db_name}... creating")
                conn.execute(text(f'CREATE DATABASE {self._cfg.db_name}'))
            else:
                self._logger.debug(f"Database {self._cfg.db_name} already exists")
            conn.execute(text('commit'))

    def create_tables(self):
        Base.metadata.create_all(self._db)
        self._logger.debug("Tables created")

    def get_product(self, product_id: int) -> ProductModel:
        raise NotImplementedError

    def search_products(self, name: str, category: ProductCategory, min_price: Decimal, max_price: Decimal, producer: str) -> list[ProductModel]:
        raise NotImplementedError

    def insert_product(self, product: ProductModel):
        raise NotImplementedError

    def delete_product(self, product_id: int):
        raise NotImplementedError

    def update_product(self, product: ProductModel):
        raise NotImplementedError

