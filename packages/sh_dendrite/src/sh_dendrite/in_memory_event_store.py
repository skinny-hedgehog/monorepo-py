from datetime import datetime

from sh_dendrite.event_store import EventStore

class InMemoryEventStore(EventStore):
    def __init__(self):
        self.store = {}

    def apply(self, log_id, event, consistency_tag: str):
        if log_id not in self.store:
            self.store[log_id] = []

        self.store[log_id].append((event.event_id, event))

    def get_log(self, log_id: str):
        return [e[0] for e in self.store.get(log_id, [])]

    def get_log_from(self, log_id: str, from_timestamp: datetime):
        raise NotImplementedError("InMemoryEventStore does not support get_log_from")
