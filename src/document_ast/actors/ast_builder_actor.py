from __future__ import annotations

from actor import Actor, ActorHandle

from ..ast_builder import AstBuilder
from ..messages import BuildAstRequest, ParseCompleted
from ..parse_state import ParseState
from ..parser_config import ParserConfig


class AstBuilderActor(Actor[ParseState, object, object]):
    def __init__(
            self,
            config: ParserConfig,
            reply_to: ActorHandle[object],
    ) -> None:
        super().__init__(ParseState, ParseState.IDLE)
        self._builder = AstBuilder(config)
        self._reply_to = reply_to

    def on_idle_build_ast_request(self, message: BuildAstRequest) -> ParseState:
        document = self._builder.build(message.document)
        self._reply_to.tell(ParseCompleted(document))
        return ParseState.IDLE
