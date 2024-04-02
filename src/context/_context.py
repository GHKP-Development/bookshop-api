import contextlib
import warnings
from typing import Any, Hashable
from datetime import datetime as _dt

from src.utils.singleton import SingletonMeta, ThreadLocalSingletonMeta
from src.utils.types import const


class ContextEntryData:
    """
    A versioned registry entry. It contains a list of historical data and changelogs to log when changes were made.
    The changelog always persists, while the data is only versioned when needed.
    """

    def __init__(self, key: Any, data: Any):
        self.key: Any = key
        self.data: list[Any] = [data]
        self.created_at: const(_dt) = _dt.now()
        self.changelog: list[_dt] = [self.created_at]

    def get_current_data(self) -> Any:
        """
        :return: Latest version of the data for this entry
        """
        return self.data[-1]

    def clone(self, shallow: bool = True) -> 'ContextEntryData':
        new_instance = self.__class__(self.key, self.get_current_data())
        if not shallow:
            new_instance.data = self.data.copy()
            new_instance.changelog = self.changelog.copy()
        return new_instance

    def __str__(self) -> str:
        return str(self.get_current_data())


class _ContextEntry:
    """
    This should never be visible in any downstream app. It exists to abstract the update() method from people using
    a context table.
    """

    def __init__(self, data: ContextEntryData):
        self._data: ContextEntryData = data

    @classmethod
    def new(cls, key: Any, value: Any) -> '_ContextEntry':
        return cls(data=ContextEntryData(key, value))

    def update(self, new_data: Any, preserve_old_data: bool):
        previous_idx = len(self._data.data) - 1
        if not preserve_old_data:
            self.data.data[previous_idx] = None
        self.data.data.append(new_data)
        self.data.changelog.append(_dt.now())

    @property
    def data(self) -> ContextEntryData:
        return self._data


class ContextTable:
    """
    Base class for context tables. Don't use this directly. Use GlobalContextTable or ThreadLocalContextTable
    depending on the use case
    """

    def __init__(self):
        self._table: dict[Any, _ContextEntry] = {}

    def __enter__(self) -> 'ContextTable':
        return self

    def __exit__(self, *_):
        pass

    def clone_context_data_shallow(self) -> dict[Any, Any]:
        return {key: entry.data.get_current_data() for key, entry in self._table.items()}

    def clone_context_data_deep(self) -> list[ContextEntryData]:
        return [entry.data.clone(shallow=False) for entry in self._table.values()]

    def import_data(self, *data: ContextEntryData):
        for entry in data:
            self._add_entry(entry)

    def update_context(self, preserve_old_data: bool = False, **data):
        for key, value in data.items():
            self.upsert(key, value, preserve_old_data=preserve_old_data)

    @contextlib.contextmanager
    def in_context(self, **data):
        try:
            self.update_context(**data, preserve_old_data=True)
            yield
        finally:
            for key in data:
                self.delete(key)

    def exists(self, key: Any) -> bool:
        return self.define_key(key) in self._table

    def get(self, key: Any, default: Any = None) -> Any:
        """
        This will return the current value of the context entry

        :param key: Self explanatory
        :param default: Value to return if the key does not exist
        """
        if entry := self.get_entry(key):
            return entry.get_current_data()
        return default

    def get_entry(self, key: Any) -> ContextEntryData:
        """
        This will return the context entry itself, which contains the historical data and changelog

        :param key: Self explanatory
        """
        if entry := self._table.get(self.define_key(key)):
            return entry.data

    def upsert(self, key: Any, value: Any, preserve_old_data: bool = False):
        """
        :param key: Self explanatory
        :param value: Self explanatory
        :param preserve_old_data: If set to true and the key exists, its old value will not be deleted and will be
        accessible via the entry.
        """
        key = self.define_key(key)
        if key not in self._table:
            self._add_entry(ContextEntryData(key=key, data=value))
        else:
            self._table[key].update(value, preserve_old_data)

    def _add_entry(self, entry: ContextEntryData):
        self._table[entry.key] = _ContextEntry(entry)

    def delete(self, key: Any, preserve_old_data: bool = False):
        """
        :param key: Self explanatory
        :param preserve_old_data: If set to true and the key exists, its old value will not be deleted and will be
        accessible via the entry.
        """
        key = self.define_key(key)
        if not preserve_old_data:
            del self._table[key]
        else:
            if key in self._table:
                self.upsert(key=key, value=None, preserve_old_data=preserve_old_data)

    @staticmethod
    def define_key(key: Any) -> Hashable:
        """
        Determine if a given key is hashable. This prevents errors when trying to use things like lists or sets as
        keys in the registry. If the latter occurs, a warning is shown to alert the user the key they gave is not what
        will be used as a key in the registry.

        :param key: A potential key to use
        :return: The same key if it's hashable, otherwise its string representation.
        """
        try:
            hash(key)
        except ValueError:
            warnings.warn(f"The given key: {key} cannot be hashed, so it is stored by its str() representation instead")
            key = str(key)
        return key

    def __setitem__(self, key: Any, value: Any):
        self.upsert(key, value)

    def __delitem__(self, key: Any):
        del self._table[key]

    def __getitem__(self, key: Any) -> ContextEntryData:
        return self.get(key)


class GlobalContextTable(ContextTable, metaclass=SingletonMeta):
    pass


class ThreadLocalContextTable(ContextTable, metaclass=ThreadLocalSingletonMeta):
    pass
