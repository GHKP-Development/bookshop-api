from src.utils.types import const


class ProductCategory:
    STATIONERY: const(int) = 1
    DOCUMENTS: const(int) = 2
    OFFICE: const(int) = 4
    BAGS: const(int) = 8
    CASES: const(int) = 16
    NOTEBOOKS: const(int) = 32
    ARTS: const(int) = 64
    TOYS: const(int) = 128
    _mapping: dict[str, int] = {
        "stationery": STATIONERY,
        "documents": DOCUMENTS,
        "office": OFFICE,
        "bags": BAGS,
        "cases": CASES,
        "notebooks": NOTEBOOKS,
        "arts": ARTS,
        "toys": TOYS
    }
    _reverse_mapping: dict[int, str] = {
        v: k for k, v in _mapping
    }

    @classmethod
    def lookup(cls, name: str) -> int:
        return cls._mapping[name]

