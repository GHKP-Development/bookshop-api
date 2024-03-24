from typing import Final, Union


def const(t_: type) -> type:
    return Final[t_]


def nullable(t_: type) -> Union:
    return t_ | None
