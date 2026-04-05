from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextSegment:
    text: str
    start: int
    end: int
