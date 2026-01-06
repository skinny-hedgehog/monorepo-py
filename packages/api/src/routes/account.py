from fastapi import APIRouter

from domain.family_account import FamilyAccount
from setup_account.create_account_command import CreateAccountCommand
from sh_dendrite.aggregate_factory import AggregateFactory


class AccountRouter:
    def __init__(self, aggregate_factory: AggregateFactory):
        self.router = APIRouter(prefix="/accounts")
        self.aggregate_factory = aggregate_factory
        self._register_routes()

    def _register_routes(self):
        self.router.post("/")(self.create_account)
        self.router.get("/{account_id}")(self.get_account)

    async def create_account(self):
        command = CreateAccountCommand(
            family_name="Smith",
            admin_email="john@smith.family",
            admin_first_name="John",
            admin_last_name="Smith",
            kids=["Amy", "Bob"]
        )

        account = self.aggregate_factory.new(FamilyAccount)
        account.create_account(command)
        return account

    async def get_account(self, account_id: str):
        account = self.aggregate_factory.load(FamilyAccount, account_id)
        return {
            "family_name": account.family_name,
            "admin_email": account.admin_email,
            "admin_first_name": account.admin_first_name,
            "admin_last_name": account.admin_last_name,
            "kids": account.kids
        }

    def get_router(self) -> APIRouter:
        return self.router