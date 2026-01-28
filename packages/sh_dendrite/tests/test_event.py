import pytest
from datetime import datetime, UTC
from dataclasses import dataclass
from unittest.mock import patch, MagicMock

from sh_dendrite.event import Event


@dataclass
class TestEvent(Event):
    """Concrete event for testing."""
    data: str = "test"


@dataclass
class MyCustomEvent(Event):
    """Another concrete event with 'Event' suffix."""
    value: int = 42


@dataclass
class SomethingHappened(Event):
    """Event without 'Event' suffix in name."""
    pass


class TestEventInit:
    def test_event_id_defaults_to_none(self):
        event = TestEvent()
        assert event.event_id is None

    def test_event_id_not_in_init(self):
        with pytest.raises(TypeError):
            TestEvent(event_id="should-fail")

    def test_created_time_defaults_to_now(self):
        before = datetime.now(UTC)
        event = TestEvent()
        after = datetime.now(UTC)

        assert before <= event.created_time <= after

    def test_created_time_not_in_init(self):
        with pytest.raises(TypeError):
            TestEvent(created_time=datetime.now(UTC))

    def test_applied_time_defaults_to_none(self):
        event = TestEvent()
        assert event.applied_time is None

    def test_applied_time_not_in_init(self):
        with pytest.raises(TypeError):
            TestEvent(applied_time=datetime.now(UTC))

    def test_subclass_fields_work(self):
        event = TestEvent(data="custom")
        assert event.data == "custom"


class TestEventName:
    def test_removes_event_suffix(self):
        event = TestEvent()
        assert event.event_name == "Test"

    def test_removes_event_suffix_from_custom(self):
        event = MyCustomEvent()
        assert event.event_name == "MyCustom"

    def test_no_event_suffix_unchanged(self):
        event = SomethingHappened()
        assert event.event_name == "SomethingHappened"

    def test_event_name_is_property(self):
        assert isinstance(Event.event_name, property)


class TestClassFrom:
    def test_loads_valid_event_class(self):
        # Load the TestEvent class from this test module
        event_type = f"{TestEvent.__module__}.TestEvent"
        loaded_class = Event.class_from(event_type)

        assert loaded_class is TestEvent

    def test_loaded_class_is_instantiable(self):
        event_type = f"{TestEvent.__module__}.TestEvent"
        loaded_class = Event.class_from(event_type)

        instance = loaded_class(data="loaded")
        assert isinstance(instance, TestEvent)
        assert instance.data == "loaded"

    def test_raises_value_error_for_invalid_module(self):
        with pytest.raises(ValueError, match="Could not load event class"):
            Event.class_from("nonexistent.module.SomeEvent")

    def test_raises_value_error_for_invalid_class(self):
        with pytest.raises(ValueError, match="Could not load event class"):
            Event.class_from(f"{TestEvent.__module__}.NonExistentClass")

    def test_raises_value_error_wraps_import_error(self):
        with pytest.raises(ValueError) as exc_info:
            Event.class_from("invalid.module.path.Event")

        assert exc_info.value.__cause__ is not None

    def test_raises_value_error_wraps_attribute_error(self):
        with pytest.raises(ValueError) as exc_info:
            Event.class_from(f"{TestEvent.__module__}.DoesNotExist")

        assert isinstance(exc_info.value.__cause__, AttributeError)

    @patch('sh_dendrite.event.import_module')
    def test_calls_import_module_with_correct_path(self, mock_import):
        mock_module = MagicMock()
        mock_module.SomeClass = TestEvent
        mock_import.return_value = mock_module

        Event.class_from("some.module.path.SomeClass")

        mock_import.assert_called_once_with("some.module.path")

    @patch('sh_dendrite.event.import_module')
    def test_gets_class_from_module(self, mock_import):
        mock_module = MagicMock()
        mock_class = MagicMock()
        mock_module.MyClass = mock_class
        mock_import.return_value = mock_module

        result = Event.class_from("my.module.MyClass")

        assert result is mock_class


class TestEventMutability:
    def test_event_id_can_be_set(self):
        event = TestEvent()
        event.event_id = "new-id"
        assert event.event_id == "new-id"

    def test_applied_time_can_be_set(self):
        event = TestEvent()
        now = datetime.now(UTC)
        event.applied_time = now
        assert event.applied_time == now
