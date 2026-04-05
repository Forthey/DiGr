from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class FormatConfig:
    name: str
    reader: dict[str, Any]
    root_entity: str
