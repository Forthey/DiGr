from __future__ import annotations

from dataclasses import dataclass

from .ast_document import AstDocument
from .source_document import SourceDocument


@dataclass(slots=True)
class ParseDocumentRequest:
    path: str
    format_name: str | None = None


@dataclass(slots=True)
class ReadDocumentRequest:
    path: str
    format_name: str


@dataclass(slots=True)
class DocumentLoaded:
    document: SourceDocument


@dataclass(slots=True)
class BuildAstRequest:
    document: SourceDocument


@dataclass(slots=True)
class ParseCompleted:
    document: AstDocument
