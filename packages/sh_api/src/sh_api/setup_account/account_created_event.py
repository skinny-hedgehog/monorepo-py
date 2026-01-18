from dataclasses import dataclass

from sh_dendrite.event import Event


@dataclass
class AccountCreatedEvent(Event):
    family_name: str
    admin_email: str
    admin_first_name: str
    admin_last_name: str
    kids: list[str]