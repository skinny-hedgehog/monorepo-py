from dataclasses import dataclass
from decimal import Decimal

from sh_dendrite.aggregate import Aggregate
from sh_dendrite.event import Event
from sh_dendrite.event_store import EventStore


@dataclass
class ConcurrencyLedgerCreated(Event):
    initial_balance: Decimal

@dataclass
class ConcurrencyLedgerUpdated(Event):
    updated_amount: Decimal

class ConcurrencyLedger(Aggregate):
    def __init__(self,
                 log_id: str,
                 event_store: EventStore,
                 event_handlers: dict[type[Event], list] = {}):
        super().__init__(log_id, event_store, event_handlers)
        self.balance = 0.0

    def on(self, event: Event) -> None:
        match event:
            case ConcurrencyLedgerCreated():
                self.balance = event.initial_balance
            case ConcurrencyLedgerUpdated():
                self.balance += event.updated_amount

    def create_ledger(self, initial_balance: Decimal) -> None:
        event = ConcurrencyLedgerCreated(initial_balance=initial_balance)
        self.apply(event)

    def update_ledger(self, amount: Decimal) -> None:
        event = ConcurrencyLedgerUpdated(updated_amount=amount)
        self.apply(event)