from enum import Enum

from src.utils.types import const


class ProductCategory(Enum):
    STATIONERY: const(int) = 1
    DOCUMENTS: const(int) = 2
    OFFICE: const(int) = 4
    BAGS: const(int) = 8
    CASES: const(int) = 16
    NOTEBOOKS: const(int) = 32
    ARTS: const(int) = 64
    TOYS: const(int) = 128
