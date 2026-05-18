from abc import ABC, abstractmethod
import pygame

class Room(ABC):
    def __init__(self, name: str):
        self.name = name
        self.screen = pygame.surface = None
    
    def Enter(self) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass