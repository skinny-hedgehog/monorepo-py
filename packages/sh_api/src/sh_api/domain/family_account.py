from sh_dendrite.aggregate import Aggregate
from sh_dendrite.event import Event
from sh_api.setup_account.account_created_event import AccountCreatedEvent
from sh_api.setup_account.create_account_command import CreateAccountCommand

class FamilyAccount(Aggregate):
    def __init__(self,
                 log_id: str,
                 event_store,
                 event_handlers):
        super().__init__(log_id, event_store, event_handlers)
        self.kids = None
        self.admin_last_name = None
        self.admin_first_name = None
        self.admin_email = None
        self.family_name = None

    def on(self, event: Event) -> None:
        match event:
            case AccountCreatedEvent():
                # Handle the AccountCreatedEvent
                self.family_name = event.family_name
                self.admin_email = event.admin_email
                self.admin_first_name = event.admin_first_name
                self.admin_last_name = event.admin_last_name
                self.kids = event.kids
            case _:
                raise ValueError(f"Unhandled event type: {type(event)}")

    def create_account(self, command: CreateAccountCommand):
        # TODO: validate the command
        #  ensure that an aggregate cannot be created if the ID already exists in the event store

        # create and apply AccountCreatedEvent
        event = AccountCreatedEvent(
            family_name=command.family_name,
            admin_email=command.admin_email,
            admin_first_name=command.admin_first_name,
            admin_last_name=command.admin_last_name,
            kids=command.kids
        )

        self.apply(event)