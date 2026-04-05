from __future__ import annotations

from collections import deque
from typing import Generic, Iterable, Protocol, TypeVar, runtime_checkable

QueueItem = TypeVar("QueueItem")


@runtime_checkable
class InboxLike(Protocol[QueueItem]):
    def get_nowait(self) -> QueueItem | None: ...


@runtime_checkable
class MailboxLike(InboxLike[QueueItem], Protocol[QueueItem]):
    def put(self, item: QueueItem) -> None: ...

    def __len__(self) -> int: ...


class Mailbox(Generic[QueueItem]):
    def __init__(self, items: Iterable[QueueItem] = ()) -> None:
        self._items: deque[QueueItem] = deque(items)

    def put(self, item: QueueItem) -> None:
        self._items.append(item)

    def extend(self, items: Iterable[QueueItem]) -> None:
        self._items.extend(items)

    def get_nowait(self) -> QueueItem | None:
        if not self._items:
            return None
        return self._items.popleft()

    def empty(self) -> bool:
        return not self._items

    def __len__(self) -> int:
        return len(self._items)
