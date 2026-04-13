from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from document_ast.model.ast_node import AstNode

from ..model.query_ast import ContextQuery, FindQuery


def _render_span(start: int, end: int) -> dict[str, int]:
    return {"start": start, "end": end}


@dataclass(slots=True)
class PatternMatchResult:
    name: str
    source_type: str
    matched_text: str | None = None
    nodes: list[AstNode] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = {
            "name": self.name,
            "source_type": self.source_type,
        }
        if self.matched_text is not None:
            result["matched_text"] = self.matched_text
        if self.nodes:
            result["nodes"] = [node.to_dict() for node in self.nodes]
        return result


@dataclass(slots=True)
class FindMatch:
    node: AstNode

    def render(self, return_items: list[str], source_path: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if "nodes" in return_items:
            result["nodes"] = self.node.to_dict()
        if "text" in return_items:
            result["text"] = self.node.text
        if "span" in return_items:
            result["span"] = _render_span(self.node.start, self.node.end)
        if "source" in return_items:
            result["source"] = source_path
        return result


@dataclass(slots=True)
class ContextWindowMatch:
    base_entity: str
    nodes: list[AstNode]
    text: str
    start: int
    end: int
    matches: list[PatternMatchResult]

    def render(self, return_items: list[str], source_path: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if "window" in return_items:
            result["window"] = {
                "base_entity": self.base_entity,
                "span": _render_span(self.start, self.end),
                "text": self.text,
                "nodes": [node.to_dict() for node in self.nodes],
            }
        if "text" in return_items:
            result["text"] = self.text
        if "span" in return_items:
            result["span"] = _render_span(self.start, self.end)
        if "matches" in return_items:
            result["matches"] = [match.to_dict() for match in self.matches]
        if "source" in return_items:
            result["source"] = source_path
        return result


@dataclass(slots=True)
class FindQueryExecutionResult:
    query: FindQuery
    source_path: str
    matches: list[FindMatch]

    def to_dict(self) -> dict[str, Any]:
        return_items = [item for item in (self.query.returns or ["nodes"]) if item != "count"]
        return {
            "type": "find_query_execution_result",
            "count": len(self.matches),
            "returns": list(self.query.returns or ["nodes", "count"]),
            "items": [match.render(return_items, self.source_path) for match in self.matches] if return_items else [],
        }


@dataclass(slots=True)
class ContextQueryExecutionResult:
    query: ContextQuery
    source_path: str
    windows: list[ContextWindowMatch]

    def to_dict(self) -> dict[str, Any]:
        return_items = [item for item in (self.query.returns or ["window"]) if item != "count"]
        return {
            "type": "context_query_execution_result",
            "count": len(self.windows),
            "returns": list(self.query.returns or ["window", "count"]),
            "items": [window.render(return_items, self.source_path) for window in self.windows] if return_items else [],
        }


DslExecutionResult = FindQueryExecutionResult | ContextQueryExecutionResult
