

class Lock:

    def __init__(self):
        self._locked: bool = False

    def __enter__(self) -> 'Lock':
        while self._locked:
            pass
        self._locked = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._locked = False
