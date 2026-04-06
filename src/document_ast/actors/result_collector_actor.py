from __future__ import annotations

from actor import Actor

from ..ast_document import AstDocument
from ..messages import CollectorMessage, ParseCompleted
from ..parse_state import WorkerState


class ResultCollectorActor(Actor[WorkerState, CollectorMessage, CollectorMessage]):
    def __init__(self) -> None:
        super().__init__(WorkerState, WorkerState.IDLE)
        self.result: AstDocument | None = None

    def on_idle_parse_completed(self, message: ParseCompleted) -> WorkerState:
        self.result = message.document
        return WorkerState.IDLE
