from typing import Callable, Tuple


QUIET = 0
INFO = 1
DEBUG = 2


class Logger:
    def __init__(self, level: int = INFO, sink: Callable[[str, str], None] = None) -> None:
        self.level = level
        self.sink = sink or (lambda lvl, msg: print(msg))

    def set_level(self, level: int) -> None:
        self.level = level

    def set_sink(self, sink: Callable[[str, str], None]) -> None:
        self.sink = sink

    def info(self, msg: str) -> None:
        if self.level >= INFO:
            self.sink("INFO", msg)

    def debug(self, msg: str) -> None:
        if self.level >= DEBUG:
            self.sink("DEBUG", msg)


_global = Logger()


def get_logger() -> Logger:
    return _global


def set_logger(logger: Logger) -> None:
    global _global
    _global = logger

