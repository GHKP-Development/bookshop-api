from typing import Final


def const(t_: type) -> type:
    return Final[t_]
