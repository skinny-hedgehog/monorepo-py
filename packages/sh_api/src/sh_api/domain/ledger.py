from dataclasses import dataclass
from decimal import Decimal
import logging

from sh_dendrite.aggregate import Aggregate
from sh_dendrite.event import Event
from sh_dendrite.event_handler import EventHandler

logger = logging.getLogger(__name__)

#commands
@dataclass
class CreateLedgerCommand:
    initial_balance: Decimal

@dataclass
class CreditLedgerCommand:
    amount: Decimal

@dataclass
class DebitLedgerCommand:
    amount: Decimal

# events
@dataclass
class LedgerCreatedEvent(Event):
    ledger_id: str
    initial_balance: Decimal

@dataclass
class LedgerCreditedEvent(Event):
    ledger_id: str
    amount: Decimal
    current_balance: Decimal

@dataclass
class LedgerDebitEvent(Event):
    ledger_id: str
    amount: Decimal
    current_balance: Decimal

# aggregate
class Ledger(Aggregate):
    def __init__(self,
                 log_id: str,
                 event_store,
                 event_handlers):
        super().__init__(log_id, event_store, event_handlers)
        self.balance = None

    def on(self, event: Event) -> None:
        match event:
            case LedgerCreatedEvent():
                self.balance = event.initial_balance
            case LedgerCreditedEvent():
                self.balance += event.amount
            case LedgerDebitEvent():
                self.balance -= event.amount

    def create_ledger(self, command: CreateLedgerCommand):
        event = LedgerCreatedEvent(self.log_id, command.initial_balance)
        self.apply(event)

    def credit(self, command: CreditLedgerCommand):
        event = LedgerCreditedEvent(self.log_id, command.amount, self.balance)
        self.apply(event)

    def debit(self, command: DebitLedgerCommand):
        event = LedgerDebitEvent(self.log_id, command.amount, self.balance)
        self.apply(event)

# Note: at some point, it will likely make sense to create a base class for different
# types of read models (e.g. RelationalReadModel, TodoListReadModel)
class LedgerReadModel(EventHandler):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def handle_event(self, events):
        for event in events:
            logger.info(f"Event type: {type(event).__name__}, value: {event}")
            match event:
                case LedgerCreatedEvent():
                    e: LedgerCreatedEvent = event
                    self.create_ledger_state(e.ledger_id, e.initial_balance)
                case LedgerCreditedEvent():
                    e: LedgerCreditedEvent = event
                    self.update_ledger_balance(e.ledger_id, e.current_balance)
                case LedgerDebitEvent():
                    e: LedgerDebitEvent = event
                    self.update_ledger_balance(e.ledger_id, e.current_balance)

    def create_ledger_state(self, id_ledger, initial_balance):
        query = """
        INSERT INTO skinny_hedgehog_read_models.ledger_state (ID_ledger, initial_balance, current_balance)
        VALUES (%s, %s, %s)
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, (id_ledger, initial_balance, initial_balance))
        self.db_connection.commit()

    def update_ledger_balance(self, id_ledger, current_balance):
        query = """
        UPDATE skinny_hedgehog_read_models.ledger_state
        SET current_balance = %s
        WHERE ID_ledger = %s
        """
        with self.db_connection.cursor() as cursor:
            cursor.execute(query, (current_balance, id_ledger))
        self.db_connection.commit()