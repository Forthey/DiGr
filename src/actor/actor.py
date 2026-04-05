from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Iterable, TypeVar

from .fsm import Fsm
from .mailbox import Mailbox, MailboxLike

State = TypeVar("State", bound=Enum)
QueueItem = TypeVar("QueueItem")
Message = TypeVar("Message")


class Actor(Fsm[State, QueueItem, Message], ABC):
    def __init__(
            self,
            state_type: type[State],
            initial_state: State,
            mailbox: MailboxLike[QueueItem] | None = None,
    ) -> None:
        self._mailbox: MailboxLike[QueueItem] = mailbox or Mailbox[QueueItem]()
        super().__init__(state_type, initial_state, self._mailbox)

    @property
    def mailbox(self) -> MailboxLike[QueueItem]:
        return self._mailbox

    def put(self, item: QueueItem) -> None:
        self._mailbox.put(item)

    def send(self, item: QueueItem) -> None:
        self.put(item)

    def extend(self, items: Iterable[QueueItem]) -> None:
        for item in items:
            self.put(item)

    @property
    def pending(self) -> int:
        return len(self._mailbox)
