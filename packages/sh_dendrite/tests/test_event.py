from sh_dendrite.event import Event

class SomethingHappenedEvent(Event):
    pass

def test_event_type_convention():
    event = SomethingHappenedEvent()
    assert event.event_name == "SomethingHappened"