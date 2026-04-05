from __future__ import annotations

from actor import Actor

from ..ast_document import AstDocument
from ..messages import ParseCompleted
from ..parse_state import ParseState


class ResultCollectorActor(Actor[ParseState, object, object]):
    def __init__(self) -> None:
        super().__init__(ParseState, ParseState.IDLE)
        self.result: AstDocument | None = None

    def on_idle_parse_completed(self, message: ParseCompleted) -> ParseState:
        self.result = message.document
        return ParseState.COMPLETED

    def on_completed_parse_completed(self, message: ParseCompleted) -> ParseState:
        self.result = message.document
        return ParseState.COMPLETED
