import pytest

from sh_api.domain.family_account import FamilyAccount
from sh_dendrite.single_log_event_store import SingleLogEventStore
from sh_dendrite.aggregate_factory import AggregateFactory
from sh_api.setup_account.account_created_event import AccountCreatedEvent
from sh_api.setup_account.create_account_command import CreateAccountCommand

@pytest.fixture
def context():
    event_store = SingleLogEventStore([])
    factory = AggregateFactory(event_store, lambda: "const_log_id", {})
    yield {"factory": factory, "event_store": event_store}

@pytest.mark.asyncio
async def test_create_account_emits_account_created_event(context):
    account = context["factory"].new(FamilyAccount)

    command = CreateAccountCommand(
        family_name="Smith",
        admin_email="john@example.com",
        admin_first_name="John",
        admin_last_name="Smith",
        kids=["Amy", "Bob"]
    )

    await account.create_account(command)

    event_store = context["event_store"]

    log = await event_store.get_log("log")
    assert len(log) == 1
    assert isinstance(log.pop(), AccountCreatedEvent)
