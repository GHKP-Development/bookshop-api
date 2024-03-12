import json
from abc import ABCMeta, abstractmethod
from datetime import datetime as dt
from pathlib import Path
from sys import stdout, stderr
from typing import Any, TextIO

from src.context import ThreadLocalContextTable
from src.utils.lock import Lock
from src.utils.logging import level
from src.utils.logging.log_engine_client import LogEngineClient
from src.utils.logging.stack import get_stack
from src.utils.types import nullable, const


def _string_format(lvl: int, logger_name: str, message: str, **tags) -> str:
    ts = dt.now().isoformat("T")
    t = ', '.join(f'{k}={v}' for k, v in tags.items()) if tags else ''
    return f"[{ts}][{level.LogLevelLookup.label_lookup(lvl)}][{logger_name}] {message} ({t})"


class BaseLogHandler(metaclass=ABCMeta):

    def __init__(self, name: str, lvl: int):
        self._name: str = name
        self._level: int = lvl

    def set_level(self, lvl: int):
        self._level = lvl

    def set_name(self, name: str):
        self._name = name

    @abstractmethod
    def format(self, lvl: int, message: str, **tags) -> Any:
        raise NotImplementedError

    @abstractmethod
    def clone(self, name: str) -> 'BaseLogHandler':
        raise NotImplementedError

    @abstractmethod
    def info(self, message: str, **tags):
        raise NotImplementedError

    @abstractmethod
    def debug(self, message: str, **tags):
        raise NotImplementedError

    @abstractmethod
    def warning(self, message: str, **tags):
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str, traceback: bool = True, **tags):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError

    @staticmethod
    def _with_stacktrace(message: str) -> str:
        strace = '\t' + '\n\t'.join(get_stack())
        return f"{message}\n{strace}\n"


class ConsoleHandler(BaseLogHandler):
    def __init__(self, name: str, lvl: int):
        super().__init__(name, lvl)

    def format(self, lvl: int, message: str, **tags) -> str:
        return _string_format(lvl, self._name, message, **tags)

    def clone(self, name: str) -> 'ConsoleHandler':
        return ConsoleHandler(name, self._level)

    def _log(self, target: TextIO, lvl: int, message: str, **tags):
        if lvl <= self._level:
            target.write(self.format(lvl, message, **tags) + '\n')
            target.flush()

    def info(self, message: str, **tags):
        self._log(stdout, level.INFO, message, **tags)

    def debug(self, message: str, **tags):
        self._log(stdout, level.DEBUG, message, **tags)

    def warning(self, message: str, **tags):
        self._log(stderr, level.WARNING, message, **tags)

    def error(self, message: str, traceback: bool = True, **tags):
        if traceback:
            message = self._with_stacktrace(message)
        self._log(stderr, level.ERROR, message, **tags)

    def close(self):
        pass


class FileHandler(BaseLogHandler):

    _locks: dict[str, Lock] = {}

    def __init__(self, name: str, lvl: int, fp: Path):
        if fp.suffix:
            raise ValueError(f"Invalid file path: {fp} (must be a directory)")
        super().__init__(name, lvl)
        self._base_path: Path = fp
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._file: nullable(TextIO) = None
        self._error_file: nullable(TextIO) = None
        self._open_files()

    @property
    def _log_file_path(self) -> Path:
        return self._base_path / f"{dt.now().strftime('%Y-%m-%d')}.log"

    @property
    def _error_file_path(self) -> Path:
        return self._base_path / f"{dt.now().strftime('%Y-%m-%d')}-error.log"

    @classmethod
    def _open_log_file(cls, path: Path, target: TextIO, mode: str = "a+") -> TextIO:
        if not path.exists():
            path.touch()
        if str(path) not in cls._locks:
            cls._locks[str(path)] = Lock()
        if target and not target.closed:
            target.close()
        return path.open(mode=mode)

    def _open_files(self):
        self._file = self._open_log_file(self._log_file_path, self._file)
        self._error_file = self._open_log_file(self._error_file_path, self._error_file)

    def _rotate_files(self):
        if self._file is not None and self._file.name != str(self._log_file_path):
            self._file.close()
            self._error_file.close()
            self._open_files()

    def format(self, lvl: int, message: str, **tags) -> str:
        return _string_format(lvl, self._name, message, **tags)

    def clone(self, name: str) -> 'FileHandler':
        return FileHandler(name, self._level, self._base_path)

    @property
    def _lock(self) -> nullable(Lock):
        return self.__class__._locks.get(str(self._log_file_path), None)

    @property
    def _error_lock(self) -> nullable(Lock):
        return self.__class__._locks.get(str(self._error_file_path), None)

    def _log(self, lvl: int, message: str, **tags):
        if lvl <= self._level:
            with self._lock:
                self._file.write(self.format(lvl, message, **tags) + '\n')
                self._file.flush()

    def _log_error(self, lvl: int, message: str, **tags):
        if self._level >= lvl >= level.WARNING:
            with self._error_lock:
                self._error_file.write(self.format(level.ERROR, message, **tags) + '\n')
                self._error_file.flush()

    def info(self, message: str, **tags):
        self._log(level.INFO, message, **tags)

    def debug(self, message: str, **tags):
        self._log(level.DEBUG, message, **tags)

    def warning(self, message: str, **tags):
        self._log_error(level.WARNING, message, **tags)

    def error(self, message: str, traceback: bool = True, **tags):
        if traceback:
            message = self._with_stacktrace(message)
        self._log_error(level.ERROR, message, **tags)

    def close(self):
        self._file.close()
        self._file = None


class ServerExportHandler(BaseLogHandler):

    def __init__(self, name: str, lvl: int, client: LogEngineClient):
        super().__init__(name, lvl)
        self._client: const(LogEngineClient) = client

    @classmethod
    def new(cls, name: str, lvl: int,
            host: str, port: int,
            bulk_limit: int, bulk_timeout_s: int,
            schema: str) -> 'ServerExportHandler':
        return ServerExportHandler(name, lvl, LogEngineClient(host, port, bulk_limit, bulk_timeout_s, schema))

    def format(self, lvl: int, message: str, **tags) -> dict[str, Any]:
        with ThreadLocalContextTable() as ctx:
            if not tags.get("request_id"):
                tags["request_id"] = ctx.get("request_id", "")
            if not tags.get("source"):
                tags["source"] = ctx.get("source", "")

        data = {
            "timestamp": dt.now().isoformat("T"),
            "level": LogLevelLookup.label_lookup(lvl),
            "request_id": tags.pop("request_id"),
            "message": message,
            "module": self._name,
            "source": tags.pop("source"),
            "tags": tags
        }
        print(json.dumps(data))  # TODO: Remove this line after debug
        return data

    def _send(self, data: dict[str, Any]):
        if self._client.connected and self._level >= level.LogLevelLookup.level_lookup(data["level"]):
            self._client.log(data, async_=True)

    def clone(self, name: str) -> 'ServerExportHandler':
        return ServerExportHandler(name, self._level, self._client)

    def info(self, message: str, **tags):
        self._send(self.format(level.INFO, message))

    def debug(self, message: str, **tags):
        self._send(self.format(level.DEBUG, message))

    def warning(self, message: str, **tags):
        self._send(self.format(level.WARNING, message))

    def error(self, message: str, traceback: bool = True, **tags):
        self._send(self.format(level.ERROR, message))

    def close(self):
        self._client.close()
