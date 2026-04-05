from __future__ import annotations

from pathlib import Path

from actor import Actor, ActorHandle

from ..messages import BuildAstRequest, DocumentLoaded, ParseCompleted, ParseDocumentRequest, ReadDocumentRequest
from ..parse_state import ParseState


class ParserCoordinatorActor(Actor[ParseState, object, object]):
    def __init__(
            self,
            reader: ActorHandle[object] | None,
            builder: ActorHandle[object] | None,
            collector: ActorHandle[object],
    ) -> None:
        super().__init__(ParseState, ParseState.IDLE)
        self._reader = reader
        self._builder = builder
        self._collector = collector

    def set_reader(self, reader: ActorHandle[object]) -> None:
        self._reader = reader

    def set_builder(self, builder: ActorHandle[object]) -> None:
        self._builder = builder

    def on_idle_parse_document_request(self, message: ParseDocumentRequest) -> ParseState:
        format_name = message.format_name or self._detect_format(message.path)
        if self._reader is None:
            raise RuntimeError("reader actor is not configured")
        self._reader.tell(ReadDocumentRequest(path=message.path, format_name=format_name))
        return ParseState.WAITING_FOR_DOCUMENT

    def on_waiting_for_document_document_loaded(self, message: DocumentLoaded) -> ParseState:
        if self._builder is None:
            raise RuntimeError("builder actor is not configured")
        self._builder.tell(BuildAstRequest(document=message.document))
        return ParseState.WAITING_FOR_AST

    def on_waiting_for_ast_parse_completed(self, message: ParseCompleted) -> ParseState:
        self._collector.tell(message)
        return ParseState.COMPLETED

    def _detect_format(self, path: str) -> str:
        suffix = Path(path).suffix.lower().lstrip(".")
        if not suffix:
            raise ValueError(f"Cannot detect format from path without extension: {path}")
        return suffix
