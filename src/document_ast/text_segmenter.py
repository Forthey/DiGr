from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

from .text_segment import TextSegment


class SegmentStrategy(ABC):
    @abstractmethod
    def segment(
            self,
            text: str,
            base_start: int,
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        pass


class PassthroughStrategy(SegmentStrategy):
    def segment(
            self,
            text: str,
            base_start: int,
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        return [TextSegment(text=text, start=base_start, end=base_start + len(text))]


class SplitStrategy(SegmentStrategy):
    def segment(
            self,
            text: str,
            base_start: int,
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        boundary_pattern = segmenter_config.get("boundary_pattern")
        if not isinstance(boundary_pattern, str) or not boundary_pattern:
            raise ValueError("Split segmenter requires non-empty 'boundary_pattern'")

        parts: list[TextSegment] = []
        cursor = 0
        for match in re.finditer(boundary_pattern, text, flags=resolve_flags(segmenter_config)):
            parts.append(
                TextSegment(
                    text=text[cursor:match.start()],
                    start=base_start + cursor,
                    end=base_start + match.start(),
                )
            )
            cursor = match.end()

        parts.append(
            TextSegment(
                text=text[cursor:],
                start=base_start + cursor,
                end=base_start + len(text),
            )
        )
        return parts


class MatchStrategy(SegmentStrategy):
    def segment(
            self,
            text: str,
            base_start: int,
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        pattern = segmenter_config.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            raise ValueError("Match segmenter requires non-empty 'pattern'")

        return [
            TextSegment(
                text=match.group(0),
                start=base_start + match.start(),
                end=base_start + match.end(),
            )
            for match in re.finditer(pattern, text, flags=resolve_flags(segmenter_config))
        ]


def resolve_flags(segmenter_config: dict[str, Any]) -> int:
    flags = re.MULTILINE
    for name in segmenter_config.get("flags", []):
        if not isinstance(name, str):
            raise ValueError(f"Regex flag must be a string, got {name!r}")
        try:
            flags |= getattr(re, name)
        except AttributeError as exc:
            raise ValueError(f"Unsupported regex flag: {name}") from exc
    return flags


def _trim_segment(segment: TextSegment) -> TextSegment:
    stripped_left = len(segment.text) - len(segment.text.lstrip())
    stripped_right = len(segment.text.rstrip())
    text = segment.text.strip()
    return TextSegment(
        text=text,
        start=segment.start + stripped_left,
        end=segment.start + stripped_right,
    )


def _finalize_segments(
        segments: list[TextSegment],
        segmenter_config: dict[str, Any],
) -> list[TextSegment]:
    trim = bool(segmenter_config.get("trim", True))
    drop_empty = bool(segmenter_config.get("drop_empty", True))

    result: list[TextSegment] = []
    for segment in segments:
        normalized = _trim_segment(segment) if trim else segment
        if drop_empty and not normalized.text:
            continue
        result.append(normalized)
    return result


class TextSegmenter:
    def __init__(self) -> None:
        self._strategies: dict[str, SegmentStrategy] = {
            "passthrough": PassthroughStrategy(),
            "split": SplitStrategy(),
            "match": MatchStrategy(),
        }

    def register(self, kind: str, strategy: SegmentStrategy) -> None:
        self._strategies[kind] = strategy

    def segment(
            self,
            text: str,
            base_start: int,
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        kind = segmenter_config.get("kind")
        if kind not in self._strategies:
            raise ValueError(
                f"Unsupported segmenter kind: {kind!r}. "
                f"Registered: {', '.join(sorted(self._strategies))}"
            )
        strategy = self._strategies[kind]
        raw_segments = strategy.segment(text, base_start, segmenter_config)
        return _finalize_segments(raw_segments, segmenter_config)
