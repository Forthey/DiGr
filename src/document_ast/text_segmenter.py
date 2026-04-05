from __future__ import annotations

import re
from typing import Any

from .text_segment import TextSegment


class TextSegmenter:
    def segment(
            self,
            text: str,
            base_start: int,
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        kind = segmenter_config.get("kind")
        if kind == "passthrough":
            return self._passthrough(text, base_start, segmenter_config)
        if kind == "split":
            return self._split(text, base_start, segmenter_config)
        if kind == "match":
            return self._match(text, base_start, segmenter_config)
        raise ValueError(f"Unsupported segmenter kind: {kind!r}")

    def _passthrough(
            self,
            text: str,
            base_start: int,
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        del segmenter_config
        return self._finalize_segments([TextSegment(text=text, start=base_start, end=base_start + len(text))], {})

    def _split(
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
        for match in re.finditer(boundary_pattern, text, flags=self._resolve_flags(segmenter_config)):
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
        return self._finalize_segments(parts, segmenter_config)

    def _match(
            self,
            text: str,
            base_start: int,
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        pattern = segmenter_config.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            raise ValueError("Match segmenter requires non-empty 'pattern'")

        parts = [
            TextSegment(
                text=match.group(0),
                start=base_start + match.start(),
                end=base_start + match.end(),
            )
            for match in re.finditer(pattern, text, flags=self._resolve_flags(segmenter_config))
        ]
        return self._finalize_segments(parts, segmenter_config)

    def _finalize_segments(
            self,
            segments: list[TextSegment],
            segmenter_config: dict[str, Any],
    ) -> list[TextSegment]:
        trim = bool(segmenter_config.get("trim", True))
        drop_empty = bool(segmenter_config.get("drop_empty", True))

        result: list[TextSegment] = []
        for segment in segments:
            normalized = self._trim_segment(segment) if trim else segment
            if drop_empty and not normalized.text:
                continue
            result.append(normalized)
        return result

    def _trim_segment(self, segment: TextSegment) -> TextSegment:
        stripped_left = len(segment.text) - len(segment.text.lstrip())
        stripped_right = len(segment.text.rstrip())
        text = segment.text.strip()
        return TextSegment(
            text=text,
            start=segment.start + stripped_left,
            end=segment.start + stripped_right,
        )

    def _resolve_flags(self, segmenter_config: dict[str, Any]) -> int:
        flags = re.MULTILINE
        for name in segmenter_config.get("flags", []):
            if not isinstance(name, str):
                raise ValueError(f"Regex flag must be a string, got {name!r}")
            try:
                flags |= getattr(re, name)
            except AttributeError as exc:
                raise ValueError(f"Unsupported regex flag: {name}") from exc
        return flags
