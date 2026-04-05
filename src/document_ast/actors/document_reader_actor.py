from __future__ import annotations

from actor import Actor, ActorHandle

from ..messages import DocumentLoaded, ReadDocumentRequest
from ..parse_state import ParseState
from ..parser_config import ParserConfig
from ..source_reader_registry import SourceReaderRegistry


class DocumentReaderActor(Actor[ParseState, object, object]):
    def __init__(
            self,
            config: ParserConfig,
            reply_to: ActorHandle[object],
    ) -> None:
        super().__init__(ParseState, ParseState.IDLE)
        self._config = config
        self._reply_to = reply_to
        self._registry = SourceReaderRegistry()

    def on_idle_read_document_request(self, message: ReadDocumentRequest) -> ParseState:
        if self._config.format_name != message.format_name:
            raise ValueError(
                f"Runtime config is for format '{self._config.format_name}', "
                f"got request for '{message.format_name}'"
            )
        document = self._registry.read(
            message.path,
            message.format_name,
            self._config.format_config.reader,
        )
        self._reply_to.tell(DocumentLoaded(document))
        return ParseState.IDLE
