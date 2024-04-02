import os
from pathlib import Path
from typing import Any

from config import LoggingConfig
from src.utils.logging import stack
from src.utils.logging.handler import BaseLogHandler, ConsoleHandler, FileHandler, ServerExportHandler


class Logger:

    def __init__(self, name: str, lvl: int, handlers: list[BaseLogHandler]):

        self._level: int = lvl
        self._name: str = name
        self._handlers: list[BaseLogHandler] = handlers

    @classmethod
    def from_config(cls, name: str, cfg: LoggingConfig) -> 'Logger':
        if cfg.stacktrace_arg_max_length:
            stack.ARG_MAX_LEN = cfg.stacktrace_arg_max_length
        handlers: list[BaseLogHandler] = [
            ConsoleHandler(name, cfg.log_level),
            FileHandler(name, cfg.log_level, cls._log_dir()),
            ServerExportHandler.new(  # TODO: Revert this to where the handler is added only if host and port are given
                name=name, lvl=cfg.log_level,
                host=cfg.log_server_host, port=cfg.log_server_port,
                bulk_limit=cfg.log_server_bulk_limit, bulk_timeout_s=cfg.log_server_bulk_timeout_s,
                schema=cfg.log_server_schema
            )]
        return Logger(name, cfg.log_level, handlers)

    @staticmethod
    def _log_dir() -> Path:
        if os.name == 'nt':
            return Path(os.getenv('LOCALAPPDATA'), 'bookshop')
        else:
            return Path("/var/log/bookshop/")

    def clone(self, name: str) -> 'Logger':
        """
        Create a new logger with the same configuration as this one, but with a different name. Useful for creating
        child loggers for downstream components.
        """
        handlers = [h.clone(name) for h in self._handlers]
        return Logger(name, lvl=self._level, handlers=handlers)

    def debug(self, message: Any, **tags):
        for handler in self._handlers:
            handler.debug(message, **tags)

    def info(self, message: Any, **tags):
        for handler in self._handlers:
            handler.info(message, **tags)

    def warning(self, message: Any, **tags):
        for handler in self._handlers:
            handler.warning(message, **tags)

    def error(self, message: Any, traceback: bool = True, **tags):
        for handler in self._handlers:
            handler.error(message, traceback, **tags)

    def close(self):
        for handler in self._handlers:
            handler.close()
