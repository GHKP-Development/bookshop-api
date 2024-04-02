from threading import Thread
from types import NoneType
from typing import Callable, Any

from ._context import ThreadLocalContextTable, ContextEntryData


class ContextThread(Thread):
    """
    An extension to python's threading API allowing for local context table to be cloned and passed to the new thread.

    Usage:
    >>> from src.context import ThreadLocalContextTable

    >>> def func():
    >>>     print(ThreadLocalContextTable().get('request_id'))

    >>> ThreadLocalContextTable().update_context(request_id='<test_request_id>')
    >>> ContextThread(target=func).start()

    ---
    > <test_request_id>

    """

    def __init__(self, group: NoneType = None, target: Callable = None, name: str = None,
                 args: tuple[Any] = (), kwargs: dict[str, Any] = None, *, daemon: bool = None):
        Thread.__init__(self, group=group, target=target, name=name,
                        args=args, kwargs=kwargs, daemon=daemon)
        self._context: list[ContextEntryData] = ThreadLocalContextTable().clone_context_data_deep()

    def run(self):
        with ThreadLocalContextTable() as ctx:
            ctx.import_data(*self._context)
            super().run()
