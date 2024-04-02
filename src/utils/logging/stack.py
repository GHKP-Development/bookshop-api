import inspect
import re
from pathlib import Path
from typing import Any

from src.utils.types import const

_object_regex: const(re.Pattern) = re.compile(r"<(.+?) object at 0x\w+>")

ARG_MAX_LEN: int = 50


def _format_function_call(func_name: str, args: dict[str, Any]) -> str:
    first_arg = None
    if container := args.pop("self", None):
        first_arg = 'self'
        caller = f"{container.__class__.__name__}.{func_name}"
    elif container := args.pop("cls", None):
        first_arg = 'cls'
        caller = f"{container.__name__}.{func_name}"
    else:
        caller = func_name
    items = []
    if first_arg:
        items.append(first_arg)
    for k, v in args.items():
        if isinstance(v, str):
            val_s = f'"{v}"'
        else:
            val_s = str(v)
        if _object_regex.match(val_s):
            val_s = f"<{v.__class__.__name__}>"
        if len(val_s) > ARG_MAX_LEN:
            half = ARG_MAX_LEN // 2
            val_s = val_s[:half] + "..." + val_s[half+3:]
        items.append(f"{k}={val_s}")
    args_str = ', '.join(items)
    return f"{caller}({args_str})"


def get_stack(base_dir: str = "src", blacklist: tuple[str] = ("logging",)) -> list[str]:
    stack = inspect.stack()
    stack_str = []
    for t in stack[1:]:
        parts = []
        reached_base = False
        blacklisted = False

        for part in Path(t.filename).parts:
            if part == base_dir:
                reached_base = True
            if reached_base:
                parts.append(part)
            if part in blacklist:
                blacklisted = True
                break
        if blacklisted or not reached_base:
            continue

        module_path = ".".join(parts)

        stack_str.append(f"{module_path}:{t.lineno} {_format_function_call(t.function, t.frame.f_locals.copy())}")

    stack_str.reverse()
    return stack_str
