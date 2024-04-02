import copy
import time
from datetime import datetime as Datetime
import threading

from requests import Session, RequestException

from src.utils.lock import Lock
from src.utils.types import nullable


class LogEngineClient:

    APP_NAME: str = "bookshop"

    def __init__(self, host: str, port: int, bulk_limit: int, bulk_timeout_s: int, protocol: str):
        self._host: str = host
        self._port: int = port
        self._bulk_limit: int = bulk_limit
        self._bulk_timeout_s: int = bulk_timeout_s
        self._protocol: str = protocol
        self._connected: bool = False
        self._session: nullable(Session) = None
        self._connect()
        self._buffer: list[dict] = []
        self._buffer_lock: Lock = Lock()
        self._stopped: bool = False
        self._buffer_cleaner_thread: nullable(threading.Thread) = None
        self._last_cleaned: nullable(Datetime) = None
        self._start_buffer_cleaner()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def is_buffered(self) -> bool:
        return self._bulk_limit and self._bulk_limit > 0

    def _buffer_cleaner_worker(self):
        # Must be started in a thread!
        if not self.is_buffered:
            return
        while not self._stopped:
            if not self._buffer:
                continue
            if self._last_cleaned is None:
                self._last_cleaned = Datetime.now()
                continue
            if (Datetime.now() - self._last_cleaned).seconds >= self._bulk_timeout_s:
                self._log_bulk_async()
                self._last_cleaned = Datetime.now()
            time.sleep(self._bulk_timeout_s / 10)

    def _start_buffer_cleaner(self):
        if not self.is_buffered:
            return
        self._buffer_cleaner_thread = threading.Thread(target=self._buffer_cleaner_worker)
        self._buffer_cleaner_thread.start()

    @property
    def target(self) -> str:
        return f"{self._protocol}://{self._host}:{self._port}"

    def _connect(self) -> bool:
        if not (self._host and self._port):
            return False
        try:
            session = Session()
            response = session.get(f"{self.target}/")
            if response.status_code == 200:
                self._connected = True
                self._session = session
                return True
        except RequestException:
            pass
        return False

    def _log_async(self, data: dict):
        # Maybe this is bad hehe
        threading.Thread(target=self._send, kwargs={"data": data}).start()

    def _log_bulk_async(self):
        # Maybe this is also bad hehehe
        threading.Thread(target=self._bulk_send).start()

    def log(self, data: dict, async_: bool = True):
        if not self.is_buffered:
            if async_:
                return self._log_async(data)
            else:
                return self._send(data)

        with self._buffer_lock:
            self._buffer.append(data)
            if len(self._buffer) >= self._bulk_limit:
                if async_:
                    return self._log_bulk_async()
                else:
                    return self._bulk_send()

    def _send(self, data: dict):
        endpoint = f"{self.target}/applications/{self.APP_NAME}/"
        if not self._connected and not self._connect():
            return
        self._session.post(endpoint, json=data)

    def _bulk_send(self):
        if not self.is_buffered:
            raise RuntimeError("Bulk Send: Bulk sending is not enabled")

        if not self._connected and not self._connect():
            return
        with self._buffer_lock:
            local_buffer = copy.deepcopy(self._buffer)
            self._buffer = []
        endpoint = f"{self.target}/applications/{self.APP_NAME}/bulk"

        self._session.post(endpoint, json=local_buffer)

    def close(self):
        if self._buffer_cleaner_thread:
            self._stopped = True
            self._buffer_cleaner_thread.join(timeout=self._bulk_timeout_s)
        if self._session:
            self._session.close()
        self._connected = False
        self._session = None
        self._buffer = []
        self._buffer_lock = Lock()
        self._buffer_cleaner_thread = None
        self._last_cleaned = None
