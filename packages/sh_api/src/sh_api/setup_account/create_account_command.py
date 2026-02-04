from dataclasses import dataclass

@dataclass
class CreateAccountCommand:
    family_name: str
    admin_email: str
    admin_first_name: str
    admin_last_name: str
    kids: list[str]

