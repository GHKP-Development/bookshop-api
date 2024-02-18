import json
import logging
from typing import Any
from dataclasses import dataclass
from pathlib import Path
import os


class DBEngineType:
    SQLITE: str = "sqlite"
    POSTGRESQL: str = "postgresql"


class _LogLevelLookup:
    _mapping: dict[str, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    _reverse_mapping: dict[int, str] = {v: k for k, v in _mapping.items()}

    @classmethod
    def lookup(cls, level: str, default: int = logging.ERROR) -> int:
        return cls._mapping.get(level.upper(), default)

    @classmethod
    def reverse_lookup(cls, level: int, default: str = "ERROR") -> str:
        return cls._reverse_mapping.get(level, default)


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


@dataclass(repr=False)
class Config:
    port: int
    debug_mode: bool
    log_level: int
    database: DBConfig

    @classmethod
    def from_file(cls, path: Path = Path("config.json")) -> 'Config':
        with open(path, 'r') as f:
            data = json.load(f)

        debug_mode = data.get("debug_mode", False)
        return cls(
            port=data.get("port", 80),
            debug_mode=debug_mode,
            log_level=_LogLevelLookup.lookup(
                data.get("log_level"), default=logging.DEBUG if debug_mode else logging.ERROR
            ),
            database=DBConfig.from_dict(data.get("database")) if data.get("database") else None
        )
