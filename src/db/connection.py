from sqlalchemy import Engine, create_engine, text

from src.db.config import DBConfig, DBEngineType


class Database:

    def __init__(self, cfg: DBConfig):
        self._cfg: DBConfig = cfg
        self._db: Engine = self._create_engine()

    def _create_engine(self) -> Engine:
        if self._cfg.engine == DBEngineType.POSTGRESQL:
            self._instrument_postgres_db()
        return create_engine(str(self._cfg))

    def _instrument_postgres_db(self) -> None:
        default_engine = create_engine(
            f'postgresql://{self._cfg.username}:{self._cfg.password}@{self._cfg.host}:{self._cfg.port}/postgres')
        with default_engine.connect() as conn:
            conn.execute(text('commit'))  # Required to execute CREATE DATABASE outside of a transaction block
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{self._cfg.db_name}'"))
            if not result.fetchone():
                conn.execute(text(f'CREATE DATABASE {self._cfg.db_name}'))
            conn.execute(text('commit'))
