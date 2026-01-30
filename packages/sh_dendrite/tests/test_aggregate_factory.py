import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import List

from sh_dendrite.aggregate_factory import AggregateFactory
from sh_dendrite.aggregate import Aggregate
from sh_dendrite.event import Event
from sh_dendrite.event_store import EventStore
from sh_dendrite.event_handler import EventHandler


class ConcreteAggregate(Aggregate):
    """Concrete implementation for testing."""

    def __init__(self, log_id: str, event_store: EventStore, event_handlers: dict = None):
        super().__init__(log_id, event_store, event_handlers or {})
        self.replayed_events: List[Event] = []

    def on(self, event: Event) -> None:
        self.replayed_events.append(event)


class TestAggregateFactoryInit:
    def test_initializes_with_required_params(self):
        event_store = Mock(spec=EventStore)
        log_id_generator = Mock(return_value="test-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)

        assert factory.event_store == event_store
        assert factory.log_id_generator == log_id_generator
        assert factory.event_handlers == event_handlers

    def test_initializes_with_event_handlers(self):
        event_store = Mock(spec=EventStore)
        log_id_generator = Mock(return_value="test-id")
        handler = Mock(spec=EventHandler)
        event_handlers = {Event: [handler]}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)

        assert factory.event_handlers == event_handlers


class TestAggregateFactoryNew:
    def test_creates_new_aggregate_instance(self):
        event_store = Mock(spec=EventStore)
        log_id_generator = Mock(return_value="generated-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = factory.new(ConcreteAggregate)

        assert isinstance(aggregate, ConcreteAggregate)

    def test_uses_log_id_generator(self):
        event_store = Mock(spec=EventStore)
        log_id_generator = Mock(return_value="generated-id-123")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = factory.new(ConcreteAggregate)

        log_id_generator.assert_called_once()
        assert aggregate.log_id == "generated-id-123"

    def test_passes_event_store_to_aggregate(self):
        event_store = Mock(spec=EventStore)
        log_id_generator = Mock(return_value="test-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = factory.new(ConcreteAggregate)

        assert aggregate.event_store == event_store

    def test_passes_event_handlers_to_aggregate(self):
        event_store = Mock(spec=EventStore)
        log_id_generator = Mock(return_value="test-id")
        handler = Mock(spec=EventHandler)
        event_handlers = {Event: [handler]}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = factory.new(ConcreteAggregate)

        assert aggregate.event_handlers == event_handlers


class TestAggregateFactoryLoad:
    @pytest.mark.asyncio
    @patch('sh_dendrite.aggregate_factory.tracer')
    async def test_loads_aggregate_with_log_id(self, mock_tracer):
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        event_store = Mock(spec=EventStore)
        event_store.get_log = AsyncMock(return_value=[])
        log_id_generator = Mock(return_value="generated-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = await factory.load(ConcreteAggregate, "existing-log-id")

        assert aggregate.log_id == "existing-log-id"

    @pytest.mark.asyncio
    @patch('sh_dendrite.aggregate_factory.tracer')
    async def test_fetches_events_from_store(self, mock_tracer):
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        event_store = Mock(spec=EventStore)
        event_store.get_log = AsyncMock(return_value=[])
        log_id_generator = Mock(return_value="generated-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        await factory.load(ConcreteAggregate, "log-123")

        event_store.get_log.assert_called_once_with("log-123")

    @pytest.mark.asyncio
    @patch('sh_dendrite.aggregate_factory.tracer')
    async def test_replays_events_on_aggregate(self, mock_tracer):
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        event1 = Mock(spec=Event)
        event1.event_id = "event-1"
        event2 = Mock(spec=Event)
        event2.event_id = "event-2"
        event3 = Mock(spec=Event)
        event3.event_id = "event-3"

        event_store = Mock(spec=EventStore)
        event_store.get_log = AsyncMock(return_value=[event1, event2, event3])
        log_id_generator = Mock(return_value="generated-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = await factory.load(ConcreteAggregate, "log-123")

        assert len(aggregate.replayed_events) == 3
        assert aggregate.replayed_events == [event1, event2, event3]

    @pytest.mark.asyncio
    @patch('sh_dendrite.aggregate_factory.tracer')
    async def test_updates_last_event_name_after_replay(self, mock_tracer):
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        event1 = Mock(spec=Event)
        event1.event_id = "event-1"
        event2 = Mock(spec=Event)
        event2.event_id = "event-2"

        event_store = Mock(spec=EventStore)
        event_store.get_log = AsyncMock(return_value=[event1, event2])
        log_id_generator = Mock(return_value="generated-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = await factory.load(ConcreteAggregate, "log-123")

        assert aggregate.last_event_name == "event-2"

    @pytest.mark.asyncio
    @patch('sh_dendrite.aggregate_factory.tracer')
    async def test_handles_empty_event_log(self, mock_tracer):
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        event_store = Mock(spec=EventStore)
        event_store.get_log = AsyncMock(return_value=[])
        log_id_generator = Mock(return_value="generated-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = await factory.load(ConcreteAggregate, "empty-log")

        assert aggregate.replayed_events == []
        assert aggregate.last_event_name is None

    @pytest.mark.asyncio
    @patch('sh_dendrite.aggregate_factory.tracer')
    async def test_creates_tracing_spans(self, mock_tracer):
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        event_store = Mock(spec=EventStore)
        event_store.get_log = AsyncMock(return_value=[])
        log_id_generator = Mock(return_value="generated-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        await factory.load(ConcreteAggregate, "log-123")

        mock_tracer.start_as_current_span.assert_called_once_with("aggregate_load")
        span_names = [call[0][0] for call in mock_tracer.start_span.call_args_list]
        assert "fetch_events" in span_names
        assert "replay_events" in span_names

    @pytest.mark.asyncio
    @patch('sh_dendrite.aggregate_factory.tracer')
    async def test_sets_span_attributes(self, mock_tracer):
        mock_load_span = MagicMock()
        mock_fetch_span = MagicMock()
        mock_replay_span = MagicMock()

        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_load_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)

        def start_span_side_effect(name):
            mock_span = MagicMock()
            if name == "fetch_events":
                mock_span.__enter__ = Mock(return_value=mock_fetch_span)
            else:
                mock_span.__enter__ = Mock(return_value=mock_replay_span)
            mock_span.__exit__ = Mock(return_value=None)
            return mock_span

        mock_tracer.start_span.side_effect = start_span_side_effect

        event = Mock(spec=Event)
        event.event_id = "event-1"

        event_store = Mock(spec=EventStore)
        event_store.get_log = AsyncMock(return_value=[event])
        log_id_generator = Mock(return_value="generated-id")
        event_handlers = {}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        await factory.load(ConcreteAggregate, "log-123")

        mock_load_span.set_attribute.assert_any_call("aggregate_type", "ConcreteAggregate")
        mock_load_span.set_attribute.assert_any_call("log_id", "log-123")
        mock_fetch_span.set_attribute.assert_called_with("event_count", 1)
        mock_replay_span.set_attribute.assert_called_with("event_count", 1)

    @pytest.mark.asyncio
    @patch('sh_dendrite.aggregate_factory.tracer')
    async def test_passes_event_handlers_to_loaded_aggregate(self, mock_tracer):
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(return_value=None)
        mock_tracer.start_span.return_value.__enter__ = Mock(return_value=mock_span)
        mock_tracer.start_span.return_value.__exit__ = Mock(return_value=None)

        event_store = Mock(spec=EventStore)
        event_store.get_log = AsyncMock(return_value=[])
        log_id_generator = Mock(return_value="generated-id")
        handler = Mock(spec=EventHandler)
        event_handlers = {Event: [handler]}

        factory = AggregateFactory(event_store, log_id_generator, event_handlers)
        aggregate = await factory.load(ConcreteAggregate, "log-123")

        assert aggregate.event_handlers == event_handlers
