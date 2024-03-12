import json
from typing import Any
from dataclasses import dataclass
from pathlib import Path
import os

from src.utils.logging import level
from src.utils.logging.level import LogLevelLookup
from src.utils.types import nullable


class DBEngineType:
    SQLITE: str = "sqlite"
    POSTGRESQL: str = "postgresql"


@dataclass(repr=False)
class DBConfig:
    db_name: str
    engine: str
    host: str = None
    port: int = None
    username: str = None
    password: str = None

    def __str__(self) -> str:
        match self.engine:
            case DBEngineType.SQLITE:
                return f'sqlite:///{self.db_name}.db'
            case DBEngineType.POSTGRESQL:
                return f'postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}'
            case _:
                raise ValueError(f"Unrecognized database engine type: {self.engine}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'DBConfig':
        return cls(
            engine=data.get("engine", os.getenv("DATABASE_ENGINE", "postgresql")),
            username=data.get("username", os.getenv("DATABASE_USER", "postgres")),
            password=data.get("password", os.getenv("DATABASE_PASSWORD", "NOT_SET")),
            host=data.get("host", os.getenv("DATABASE_HOST", "localhost")),
            port=data.get("port", os.getenv("DATABASE_PORT", -1)),
            db_name=data.get("name", os.getenv("DATABASE_NAME", "bookshop")),
        )


@dataclass
class LoggingConfig:
    log_level: int
    stacktrace_arg_max_length: int
    log_server_host: nullable(str) = None
    log_server_port: nullable(int) = None
    log_server_bulk_limit: nullable(int) = None
    log_server_bulk_timeout_s: nullable(int) = None
    log_server_schema: nullable(str) = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], debug_mode: bool) -> 'LoggingConfig':
        return cls(
            log_level=LogLevelLookup.level_lookup(data.get("log_level"), default=level.DEBUG if debug_mode else level.ERROR),
            stacktrace_arg_max_length=data.get("stacktrace_arg_max_length", 50),
            log_server_host=data.get("log_server_host"),
            log_server_port=data.get("log_server_port"),
            log_server_bulk_limit=data.get("log_server_bulk_limit"),
            log_server_bulk_timeout_s=data.get("log_server_bulk_timeout_s"),
            log_server_schema=data.get("log_server_schema"),
        )


@dataclass(repr=False)
class Config:
    port: int
    debug_mode: bool
    database: DBConfig
    logging: LoggingConfig

    @classmethod
    def from_file(cls, path: Path = Path("config.json")) -> 'Config':
        with open(path, 'r') as f:
            data = json.load(f)

        debug_mode = data.get("debug_mode", False)
        return cls(
            port=data.get("port", 80),
            debug_mode=debug_mode,
            database=DBConfig.from_dict(data.get("database")) if data.get("database") else None,
            logging=LoggingConfig.from_dict(data.get("logging", {}), debug_mode) if data.get("logging") else None,
        )
