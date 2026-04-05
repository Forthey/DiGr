# Быстрый старт

## Импорты

Обычно достаточно импортов:

```python
from src.actor import (
    Actor,
    ActorHandle,
    AsyncioActorDriver,
    ManualActorDriver,
    ThreadedActorDriver,
)
```

Если нужны низкоуровневые архитектурные контракты, их стоит импортировать из `src.actor.arch`.

## Минимальный актор

```python
from enum import Enum, auto

from src.actor import Actor


class State(Enum):
    IDLE = auto()
    DONE = auto()


class Start:
    pass


class DemoActor(Actor[State, object, object]):
    def __init__(self) -> None:
        super().__init__(State, State.IDLE)

    def on_idle_start(self, message: Start) -> State:
        print("handled Start")
        return State.DONE
```

## `ManualActorDriver`

Используй `ManualActorDriver`, когда нужен явный контроль над исполнением.

```python
from src.actor import ManualActorDriver

driver = ManualActorDriver(step_limit=1)
actor = DemoActor(driver=driver)

actor.put(Start())

driver.proceed()
assert actor.state is State.DONE
```

Ключевые свойства:

- детерминированное исполнение
- удобно тестировать
- хорошо подходит для явных внешних циклов обработки

## `ThreadedActorDriver`

Используй `ThreadedActorDriver`, когда нужен фоновый worker-thread.

```python
from src.actor import ThreadedActorDriver

driver = ThreadedActorDriver(step_limit=1)
actor = DemoActor(driver=driver)

actor.put(Start())
driver.wait_until_idle(timeout=1.0)

assert actor.state is State.DONE
driver.close()
```

## `AsyncioActorDriver`

Используй `AsyncioActorDriver`, когда приложение уже работает внутри `asyncio` event loop.

```python
import asyncio

from src.actor import AsyncioActorDriver


async def main() -> None:
    driver = AsyncioActorDriver(step_limit=1)
    actor = DemoActor(driver=driver)

    actor.put(Start())
    await driver.join()

    assert actor.state is State.DONE
    await driver.aclose()


asyncio.run(main())
```

## `ActorHandle`

`ActorHandle` это лёгкий объект, через который можно отправлять сообщения в актор, не передавая наружу сам объект актора.

Это удобно потому что:

- отправитель зависит только от способности доставить сообщение
- получатель можно заменить другой реализацией `Output`
- архитектура становится менее связанной

```python
from enum import Enum, auto

from src.actor import Actor, ActorHandle, ManualActorDriver


class CollectorState(Enum):
    WAIT = auto()
    DONE = auto()


class WorkerState(Enum):
    IDLE = auto()
    DONE = auto()


class Start:
    pass


class Pong:
    pass


class Collector(Actor[CollectorState, object, object]):
    def __init__(self, driver: ManualActorDriver) -> None:
        super().__init__(CollectorState, CollectorState.WAIT, driver=driver)
        self.received: list[str] = []

    def on_wait_pong(self, message: Pong) -> CollectorState:
        self.received.append("pong")
        return CollectorState.DONE


class Worker(Actor[WorkerState, object, object]):
    def __init__(self, reply_to: ActorHandle[object], driver: ManualActorDriver) -> None:
        super().__init__(WorkerState, WorkerState.IDLE, driver=driver)
        self._reply_to = reply_to

    def on_idle_start(self, message: Start) -> WorkerState:
        self._reply_to.tell(Pong())
        return WorkerState.DONE


driver = ManualActorDriver()
collector = Collector(driver)
worker = Worker(collector.as_handle(), driver)

worker.put(Start())
driver.drain()

assert collector.received == ["pong"]
```

## Порядок поиска обработчика

Для состояния `ACTIVE` и сообщения `PingMessage` FSM ищет обработчик в таком порядке:

1. `on_active_ping_message`
2. `on_active`
3. `on_ping_message`
4. `on_any`

## Практические правила

- Политику исполнения и планирования держи только в драйверах.
- Переходы между состояниями держи внутри actor/FSM handlers.
- Передавай `ActorHandle` или `Output`, а не конкретные объекты акторов.
- В тестах по умолчанию используй `ManualActorDriver`, если не нужно специально проверять thread/event-loop поведение.
