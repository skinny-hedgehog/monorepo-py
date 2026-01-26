from datetime import datetime
from sh_dendrite.event import Event
from abc import ABC, abstractmethod

class EventStore(ABC):
    @abstractmethod
    def apply(self, log_id: str, event: Event, consistency_tag: str):
        pass

    @abstractmethod
    def get_log(self, log_id: str):
        pass

    @abstractmethod
    def get_log_from(self, log_id: str, starting_point: Event | datetime):
        pass