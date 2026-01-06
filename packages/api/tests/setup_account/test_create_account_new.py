import pytest

from domain.family_account import FamilyAccount
from tests.single_log_event_store import SingleLogEventStore
from sh_dendrite.aggregate_factory import AggregateFactory
from setup_account.account_created_event import AccountCreatedEvent
from setup_account.create_account_command import CreateAccountCommand

@pytest.fixture
def context():
    event_store = SingleLogEventStore([])
    factory = AggregateFactory(event_store, lambda: "const_log_id", {})
    yield {"factory": factory, "event_store": event_store}

def test_create_account_emits_account_created_event(context):
    account = context["factory"].new(FamilyAccount)

    command = CreateAccountCommand(
        family_name="Smith",
        admin_email="john@example.com",
        admin_first_name="John",
        admin_last_name="Smith",
        kids=["Amy", "Bob"]
    )

    account.create_account(command)

    event_store = context["event_store"]

    assert len(event_store.get_log("log")) == 1
    assert isinstance(event_store.get_log("log").pop(), AccountCreatedEvent)
