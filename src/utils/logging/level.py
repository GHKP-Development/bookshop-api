from src.utils.types import const

DEBUG_LABEL: const(str) = "DEBUG"
INFO_LABEL: const(str) = "INFO "
WARNING_LABEL: const(str) = "WARN "
ERROR_LABEL: const(str) = "ERROR"


DEBUG: const(int) = 20
INFO: const(int) = 10
WARNING: const(int) = 5
ERROR: const(int) = 1


class LogLevelLookup:
    _mapping: dict[str, int] = {
        DEBUG_LABEL: DEBUG,
        INFO_LABEL: INFO,
        WARNING_LABEL: WARNING,
        ERROR_LABEL: ERROR,
    }
    _reverse_mapping: dict[int, str] = {v: k for k, v in _mapping.items()}

    @classmethod
    def level_lookup(cls, level: str, default: int = ERROR) -> int:
        return cls._mapping.get(level.upper(), default)

    @classmethod
    def label_lookup(cls, level: int, default: str = ERROR_LABEL) -> str:
        return cls._reverse_mapping.get(level, default)
