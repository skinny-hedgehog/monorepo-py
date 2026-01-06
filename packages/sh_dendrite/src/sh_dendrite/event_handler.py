from abc import abstractmethod, ABC

# TODO: look into making this a callable instead of a class. This would enable a read model to implement multiple
#  methods for different event types and then register the handling methods individually
class EventHandler(ABC):
    @abstractmethod
    def handle_event(self, events):
        pass