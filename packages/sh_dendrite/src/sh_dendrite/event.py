from dataclasses import dataclass
from datetime import datetime
from importlib import import_module

@dataclass
class Event:
    _created_time = datetime.now()

    @property
    def event_type(self) -> str:
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



    @property
    def event_name(self) -> str:
        # TODO: I'm uncomfortable with sorting being based on time, since more workers increase the potential for
        #  clock draft and incorrect ordering. Look into using or implementing some kind of vector clock or other
        #  causality-based algorithm for defining the event name
        return f"{self._created_time.strftime('%Y%m%d%H%M%S%f')[:-3]}_{self.event_type}"
