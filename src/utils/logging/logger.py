import logging
import os
from pathlib import Path
import datetime
from termcolor import colored
from typing import Any


class Logger:
    """
    Wrapper around the standard logging module with the boilerplate abstracted away.
    """
    def __init__(self, name: str, level: int = logging.INFO) -> None:
        log_directory = self._log_dir()
        log_directory.mkdir(parents=True, exist_ok=True)
        self._level: int = level

        self._setup_logger(name, level)
        self._setup_file_handlers(log_directory, level)
        self._setup_console_handler(level)

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
        new_logger = Logger(name, level=self._level)
        new_logger.logger.handlers = []  # Clear existing handlers
        new_logger._setup_file_handlers(self._log_dir(), self._level)
        new_logger._setup_console_handler(self._level)
        return new_logger

    def _setup_logger(self, name: str, level: int) -> None:
        self.logger = logging.getLogger(name)
        if not self.logger.hasHandlers():
            self.logger.setLevel(level)

    def _setup_file_handlers(self, log_directory: Path, level: int) -> None:
        date = datetime.datetime.now().strftime("%Y%m%d")
        file_handler = self._create_file_handler(log_directory / f"{date}.log", level)
        error_file_handler = self._create_file_handler(log_directory / f"{date}-error.log", logging.ERROR)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_file_handler)

    @staticmethod
    def _format_string() -> str:
        return "%(asctime)s [%(levelname)s] [%(name)s] - %(message)s"

    @classmethod
    def _create_file_handler(cls, file_path: Path, level: int) -> logging.FileHandler:
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(cls._format_string()))
        return file_handler

    def _setup_console_handler(self, level: int) -> None:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(self._format_string()))
        self.logger.addHandler(console_handler)

    def debug(self, message: Any) -> None:
        self.logger.debug(colored(str(message), "white"))

    def info(self, message: Any) -> None:
        self.logger.info(colored(str(message), "cyan"))

    def success(self, message: Any) -> None:
        self.logger.info(colored(str(message), "green"))

    def warning(self, message: Any) -> None:
        self.logger.warning(colored(str(message), "yellow"))

    def error(self, message: Any) -> None:
        self.logger.error(colored(str(message), "red"))