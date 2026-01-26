from dataclasses import dataclass, field
from datetime import datetime, UTC
from importlib import import_module

@dataclass
class Event:
    event_id: str | None = field(default=None, init=False)
    created_time: datetime = field(default=datetime.now(UTC), init=False)
    applied_time: datetime | None = field(default=None, init=False)


    @property
    def event_name(self) -> str:
        # by default convention, returns the name of the class without the 'Event' suffix
        return self.__class__.__name__.replace('Event', '')


    # TODO: evaluate an optimization approach wherein the fx scans on load for all event types and adds them to
    #  global scope - the hypothesis is that this would simplify the process of finding and loading the event class
    @classmethod
    def class_from(cls, event_type: str):
        # Split into module path and class name
        module_path, class_name = event_type.rsplit('.', 1)

        try:
            # Import the module
            module = import_module(module_path)
            # Get the class from the module
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not load event class: {event_type}") from e
