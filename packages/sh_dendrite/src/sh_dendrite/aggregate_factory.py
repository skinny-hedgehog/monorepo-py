from typing import Callable, TypeVar, Type
from opentelemetry import trace
from sh_dendrite.aggregate import Aggregate
from sh_dendrite.event import Event
from sh_dendrite.event_handler import EventHandler
from sh_dendrite.event_store import EventStore

A = TypeVar('A', bound=Aggregate)
E = TypeVar('E', bound=Event)
H = TypeVar('H', bound=EventHandler)

tracer = trace.get_tracer(__name__)

# there may be a more pythonic way to do this since all derived classes will share the
# same values set on the superclass
class AggregateFactory:
    def __init__(self,
                 event_store: EventStore,
                 log_id_generator: Callable[[], str],
                 event_handlers: dict[type[E], list[H]]):
        self.event_store = event_store
        self.log_id_generator = log_id_generator
        self.event_handlers = event_handlers

    def new(self, aggregate_type: Type[A]) -> A:
        instance = aggregate_type(self.log_id_generator(),
                                  self.event_store,
                                  self.event_handlers)

        return instance

    async def load(self,
             aggregate_type: Type[A],
             log_id: str) -> A:

        with tracer.start_as_current_span("aggregate_load") as load_span:
            load_span.set_attribute("aggregate_type", aggregate_type.__name__)
            load_span.set_attribute("log_id", log_id)

            instance = aggregate_type(log_id, self.event_store, self.event_handlers)

            with tracer.start_span("fetch_events") as fetch_span:
                events = await self.event_store.get_log(log_id)
                fetch_span.set_attribute("event_count", len(events))

            with tracer.start_span("replay_events") as replay_span:
                for event in events:
                    instance._on_event(event)
                replay_span.set_attribute("event_count", len(events))

        return instance