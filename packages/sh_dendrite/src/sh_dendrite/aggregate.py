from datetime import datetime, UTC
import uuid
from abc import ABC, abstractmethod
from typing import TypeVar

from opentelemetry import trace

from sh_dendrite.event import Event
from sh_dendrite.event_store import EventStore

tracer = trace.get_tracer(__name__)

def uuid_log_id_generator() -> str:
    return str(uuid.uuid4())

E = TypeVar('E', bound=EventStore)

class Aggregate(ABC):
    def __init__(self,
                 log_id: str,
                 event_store: EventStore,
                 event_handlers: dict[type[Event], list] = {}):
        self.log_id = log_id
        self.event_store = event_store
        self.event_handlers = event_handlers
        self.last_event_name: str | None = None

    @abstractmethod
    def on(self, event: Event) -> None:
        pass

    def _on_event(self, event: Event) -> None:
        self.last_event_name = event.event_id
        self.on(event)

    def apply(self, event: Event) -> None:
        # set key values on the event before persisting
        applied_time = datetime.now(UTC)
        if event.event_id is None:
            event.event_id = f"{applied_time.strftime('%Y%m%d%H%M%S%f')[:-3]}_{event.event_name}"
        event.applied_time = applied_time

        # ensure the event is applied in durable storage
        with tracer.start_as_current_span("apply.event_store"):
            self.event_store.apply(self.log_id, event, self.last_event_name)

        # apply the event to the aggregate
        with tracer.start_as_current_span("apply.event_sourcing_handler"):
            self.on(event)

        # dispatch any registered handlers for the event type
        with tracer.start_as_current_span("apply.event_handlers"):
            handlers = self.event_handlers.get(type(event), [])
            for handler in handlers:
                handler.handle_event([event])