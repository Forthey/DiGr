from __future__ import annotations

from dataclasses import dataclass

from actor import ManualActorDriver

from .actors import AstBuilderActor, DocumentReaderActor, ParserCoordinatorActor, ResultCollectorActor
from .parser_config import ParserConfig


@dataclass(slots=True)
class ParserRuntime:
    driver: ManualActorDriver
    coordinator: ParserCoordinatorActor
    collector: ResultCollectorActor


class ParserRuntimeFactory:
    def create(self, config: ParserConfig) -> ParserRuntime:
        driver = ManualActorDriver(step_limit=1)
        collector = ResultCollectorActor().bind(driver)
        coordinator = ParserCoordinatorActor(
            reader=None,
            builder=None,
            collector=collector.as_handle(),
        ).bind(driver)
        reader = DocumentReaderActor(config, coordinator.as_handle()).bind(driver)
        builder = AstBuilderActor(config, coordinator.as_handle()).bind(driver)
        coordinator.set_reader(reader.as_handle())
        coordinator.set_builder(builder.as_handle())
        return ParserRuntime(driver=driver, coordinator=coordinator, collector=collector)
