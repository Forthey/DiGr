from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class EntityConfig:
    name: str
    contains: str | None
    segmenter: dict[str, Any]
