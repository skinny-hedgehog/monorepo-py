from sh_dendrite.event import Event

class SomethingHappenedEvent(Event):
    pass

def test_event_type_convention():
    event = SomethingHappenedEvent()
    assert event.event_name == "SomethingHappened"

def test_event_name_convention():
    event = SomethingHappenedEvent()
    event_name = event.event_id
    print(event_name)
    assert event_name.startswith(event._created_time.strftime('%Y%m%d%H%M%S%f')[:-3])
    assert event_name.endswith("_SomethingHappened")