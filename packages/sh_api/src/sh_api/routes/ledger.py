from decimal import Decimal

from fastapi import APIRouter
import logging


from pydantic import BaseModel

from sh_api.domain.ledger import Ledger, CreateLedgerCommand, CreditLedgerCommand, DebitLedgerCommand
from sh_dendrite.aggregate_factory import AggregateFactory

logger = logging.getLogger(__name__)

class LedgerRouter:
    def __init__(self, aggregate_factory: AggregateFactory):
        self.router = APIRouter(prefix="/ledger")
        self.aggregate_factory = aggregate_factory
        self._register_routes()

    def _register_routes(self):
        self.router.get("/{ledger_id}")(self.get_ledger)
        self.router.post("/")(self.create_ledger)
        self.router.post("/{ledger_id}/credits")(self.credit_ledger)
        self.router.post("/{ledger_id}/debits")(self.debit_ledger)

    async def get_ledger(self, ledger_id: str):
        logger.info(f"Getting ledger {ledger_id}")
        ledger = self.aggregate_factory.load(Ledger, ledger_id)
        return {
            "ledger": ledger_id,
            "balance": ledger.balance,
        }

    async def create_ledger(self):
        ledger = self.aggregate_factory.new(Ledger)

        command = CreateLedgerCommand(initial_balance=Decimal("500.00"))
        ledger.create_ledger(command)

        return {
            "ledger_id": ledger.log_id,
            "balance": ledger.balance,
        }

    class CreditDebitRequest(BaseModel):
        amount: Decimal

    async def credit_ledger(self, ledger_id: str, request: CreditDebitRequest):
        ledger = self.aggregate_factory.load(Ledger, ledger_id)

        amount = request.amount
        ledger.credit(CreditLedgerCommand(amount))

        return {
            "ledger_id": ledger.log_id,
            "balance": ledger.balance,
        }

    async def debit_ledger(self, ledger_id: str, request: CreditDebitRequest):
        ledger = self.aggregate_factory.load(Ledger, ledger_id)

        amount = request.amount
        ledger.debit(DebitLedgerCommand(amount))

        return {
            "ledger_id": ledger.log_id,
            "balance": ledger.balance,
        }

    def get_router(self) -> APIRouter:
        return self.router