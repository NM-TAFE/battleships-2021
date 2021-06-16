from abc import abstractmethod


class ClientInterface:
    @abstractmethod
    def add_event_listener(self, event=None, handler=None):
        pass

    @abstractmethod
    def join(self):
        pass

    @abstractmethod
    def attack(self, vector):
        pass

    @abstractmethod
    def hit(self):
        pass

    @abstractmethod
    def miss(self):
        pass

    @abstractmethod
    def defeat(self):
        pass
