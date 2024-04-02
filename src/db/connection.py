import contextlib
from decimal import Decimal

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker

from config import DBConfig, DBEngineType
from src.core.product import Product
from src.db.models import Base
from src.utils.logging.logger import Logger
from src.db.session import Session
from src.utils.types import nullable


class Database:

    def __init__(self, cfg: DBConfig, logger: Logger) -> None:
        self._cfg: DBConfig = cfg
        self._logger: Logger = logger
        self._db: Engine = self._create_engine()
        self._session = sessionmaker(bind=self._db)
        self.create_tables()

    @property
    def name(self) -> str:
        return self._cfg.db_name

    def _create_engine(self) -> Engine:
        if self._cfg.engine == DBEngineType.POSTGRESQL:
            self._instrument_postgres_db()
        self._logger.debug(
            f"Creating {self._cfg.engine} database engine with user {self._cfg.username} and database {self._cfg.db_name}")
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

    @contextlib.contextmanager
    def in_session(self) -> Session:
        raw_session = self._session()
        sess = Session(raw_session, self._logger.clone("Session"))
        try:
            yield sess
            raw_session.commit()
        except Exception as e:
            self._logger.debug(f"Exception in session: {e}, rolling back...")
            raw_session.rollback()
            raise
        finally:
            raw_session.close()

    def get_product(self, product_id: int) -> nullable(Product):
        try:
            with self.in_session() as session:
                db_product = session.get_product(product_id)
                if db_product:
                    self._logger.debug(f"Found product with {db_product.id=}")
                    return Product.from_db_model(db_product)
                self._logger.debug(f"No product with {product_id=}")
        except Exception as exc:
            self._logger.debug(f"Could not get product with id {product_id}: {exc}")

    def search_products(self, name: str = None, category: int = None, min_price: Decimal = None,
                        max_price: Decimal = None,
                        producer: str = None) -> list[Product]:
        try:
            with self.in_session() as session:
                static_filters = {}

                if name is not None:
                    static_filters['name'] = name
                if producer is not None:
                    static_filters['producer'] = producer

                return [Product.from_db_model(product) for product in
                        session.search_products(static_filters=static_filters, category=category, min_price=min_price,
                                                max_price=max_price)]
        except Exception as exc:
            self._logger.error(f"Could not search for products: {exc}")
            raise

    def insert_product(self, product: Product) -> bool:
        try:
            with self.in_session() as session:
                # update unique constraints
                product.id = session.insert_product(product.to_db_model())
                self._logger.debug(f"Inserted product with id {product.id}")
                return True
        except Exception as exc:
            self._logger.error(f"Could not insert product with id {product.id}\n Exception: {exc}")
        return False

    def delete_product(self, product_id: int) -> bool:
        try:
            with self.in_session() as session:
                if session.delete_product(product_id):
                    self._logger.debug(f"Product with id {product_id} deleted")
                    return True
                self._logger.debug(f"Failed to delete product with id {product_id}")
                return False
        except Exception as exc:
            self._logger.debug(f"Could not delete product with id {product_id}\n Exception: {exc}")
        return False

    def update_product(self, product: Product) -> bool:
        try:
            with self.in_session() as session:
                if existing_product := session.get_product(product.id):
                    return session.update_product(existing_product, product)
                self._logger.debug(f"Product with ID: {product.id} does not exist")
        except Exception as exc:
            self._logger.debug(f"Could not update product with id {product.id}\n Exception: {exc}")
        return False

    def delete_all_products(self):
        try:
            with self.in_session() as session:
                session.delete_all_products()
                self._logger.debug("All products deleted")
        except Exception as exc:
            self._logger.debug(f"Could not delete all products: {exc}")
        return False
