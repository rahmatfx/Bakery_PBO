class Observer:

    def on_notify(self, event_type: str, data=None) -> None:
        raise NotImplementedError


class Subject:

    def __init__(self):
        self._observers: list[Observer] = []

    def add_observer(self, observer: Observer) -> None:
    
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:

        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, data=None) -> None:
 
        for observer in self._observers:
            observer.on_notify(event_type, data)
