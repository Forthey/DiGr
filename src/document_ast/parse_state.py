from __future__ import annotations

from enum import Enum, auto


class ParseState(Enum):
    IDLE = auto()
    WAITING_FOR_DOCUMENT = auto()
    WAITING_FOR_AST = auto()
    COMPLETED = auto()
