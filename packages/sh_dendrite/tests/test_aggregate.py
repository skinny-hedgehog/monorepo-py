import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, UTC

from sh_dendrite.aggregate import Aggregate, uuid_log_id_generator
from sh_dendrite.event import Event
from sh_dendrite.event_store import EventStore


class ConcreteAggregate(Aggregate):
    """Concrete implementation for testing the abstract Aggregate class."""

    def __init__(self, log_id: str, event_store: EventStore, event_handlers: dict = None):
        super().__init__(log_id, event_store, event_handlers or {})
        self.applied_events = []

    def on(self, event: Event) -> None:
        self.applied_events.append(event)


class TestUuidLogIdGenerator:
    def test_returns_string(self):
        result = uuid_log_id_generator()
        assert isinstance(result, str)

    def test_returns_valid_uuid_format(self):
        result = uuid_log_id_generator()
        # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        parts = result.split('-')
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_returns_unique_values(self):
        ids = [uuid_log_id_generator() for _ in range(100)]
        assert len(set(ids)) == 100


class TestAggregateInit:
    def test_initializes_with_required_params(self):
        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        assert aggregate.log_id == "log-123"
        assert aggregate.event_store == event_store
        assert aggregate.event_handlers == {}
        assert aggregate.last_event_name is None

    def test_initializes_with_event_handlers(self):
        event_store = Mock(spec=EventStore)
        handlers = {Event: [Mock()]}
        aggregate = ConcreteAggregate("log-123", event_store, handlers)

        assert aggregate.event_handlers == handlers


class TestAggregateOnEvent:
    def test_updates_last_event_name(self):
        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = "event-456"

        aggregate._on_event(event)

        assert aggregate.last_event_name == "event-456"

    def test_calls_on_method(self):
        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = "event-456"

        aggregate._on_event(event)

        assert event in aggregate.applied_events


class TestAggregateApply:
    @patch('sh_dendrite.aggregate.tracer')
    def test_sets_event_id_when_none(self, mock_tracer):
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock()
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock()

        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = None
        event.event_name = "TestEvent"

        aggregate.apply(event)

        assert event.event_id is not None
        assert "TestEvent" in event.event_id

    @patch('sh_dendrite.aggregate.tracer')
    def test_preserves_existing_event_id(self, mock_tracer):
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock()
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock()

        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = "existing-id"

        aggregate.apply(event)

        assert event.event_id == "existing-id"

    @patch('sh_dendrite.aggregate.tracer')
    def test_sets_applied_time(self, mock_tracer):
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock()
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock()

        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = "test-id"

        before = datetime.now(UTC)
        aggregate.apply(event)
        after = datetime.now(UTC)

        assert before <= event.applied_time <= after

    @patch('sh_dendrite.aggregate.tracer')
    def test_calls_event_store_apply(self, mock_tracer):
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock()
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock()

        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = "test-id"

        aggregate.apply(event)

        event_store.apply.assert_called_once_with("log-123", event, None)

    @patch('sh_dendrite.aggregate.tracer')
    def test_passes_last_event_name_to_store(self, mock_tracer):
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock()
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock()

        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)
        aggregate.last_event_name = "previous-event"

        event = Mock(spec=Event)
        event.event_id = "test-id"

        aggregate.apply(event)

        event_store.apply.assert_called_once_with("log-123", event, "previous-event")

    @patch('sh_dendrite.aggregate.tracer')
    def test_calls_on_method(self, mock_tracer):
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock()
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock()

        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = "test-id"

        aggregate.apply(event)

        assert event in aggregate.applied_events

    @patch('sh_dendrite.aggregate.tracer')
    def test_dispatches_registered_handlers(self, mock_tracer):
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock()
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock()

        event_store = Mock(spec=EventStore)
        handler1 = Mock()
        handler2 = Mock()

        event = Mock(spec=Event)
        event.event_id = "test-id"

        handlers = {type(event): [handler1, handler2]}
        aggregate = ConcreteAggregate("log-123", event_store, handlers)

        aggregate.apply(event)

        handler1.handle_event.assert_called_once_with([event])
        handler2.handle_event.assert_called_once_with([event])

    @patch('sh_dendrite.aggregate.tracer')
    def test_no_handlers_called_when_none_registered(self, mock_tracer):
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock()
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock()

        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = "test-id"

        # Should not raise
        aggregate.apply(event)

    @patch('sh_dendrite.aggregate.tracer')
    def test_creates_tracing_spans(self, mock_tracer):
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value = mock_span

        event_store = Mock(spec=EventStore)
        aggregate = ConcreteAggregate("log-123", event_store)

        event = Mock(spec=Event)
        event.event_id = "test-id"

        aggregate.apply(event)

        span_names = [call[0][0] for call in mock_tracer.start_as_current_span.call_args_list]
        assert "apply.event_store" in span_names
        assert "apply.event_sourcing_handler" in span_names
        assert "apply.event_handlers" in span_names
