from datetime import datetime

from sh_dendrite.event import Event
from sh_dendrite.event_store import EventStore


class SingleLogEventStore(EventStore):
    def __init__(self, backing_store=[]):
        self.backing_store = backing_store

    def apply(self, log_id: str, event: Event):
        self.backing_store.append(event)

    def get_log(self, log_id: str):
        return self.backing_store

    def get_log_from(self, log_id: str, from_timestamp: datetime):
        pass