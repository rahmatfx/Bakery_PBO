import pygame
import Constant
from Room.Room import Room
from Observer import Observer
from UI.NavUI import NavigationUI

_IDLE = 0
_FADE_OUT = 1
_FADE_IN = 2

class SceneManager(Observer):
    def __init__(self, screen: pygame.surface):
        self.screen = screen
        self.current_room: Room = None
        self.room_kitchen: Room = None
        self.room_bakery: Room = None
        self.room_storage: Room = None
        self.room_garden: Room = None

        self.navigation_ui = NavigationUI()
        self.navigation_ui.add_observer(self)  
        self._nav_visible = True

        self._state = _IDLE
        self._fade_alpha = 0
        self._next_room: Room = None
        self._fade_surface = pygame.Surface((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
        self._fade_surface.fill((0, 0, 0))


    def on_notify(self, event_type: str, data=None) -> None:

        if event_type == "room_change":
            room_name: str = data 
            print(f"[DEBUG SM] Received 'room_change' event, target: {room_name}")

            if self.current_room.name == room_name:
                print(f"[DEBUG SM] Same room ({room_name}), no change needed")
                return

            target_room = self._get_room_by_name(room_name)
            if target_room:
                self._start_transition(target_room)
            else:
                print(f"[DEBUG SM] Unknown room: {room_name}")

    def _get_room_by_name(self, name: str) -> Room:
       
        match name:
            case "Kitchen":     return self.room_kitchen
            case "Bakery Shop": return self.room_bakery
            case "Storage":     return self.room_storage
            case "Garden":      return self.room_garden
            case _:             return None

    def get_room_names(self) -> list[str]:
        return ["Kitchen", "Bakery Shop", "Storage", "Garden"]

    def start_transition(self, room: Room) -> None:
        if self._state != _IDLE:
            return 

        self._next_room = room
        self._state = _FADE_OUT
        self._fade_alpha = 0
        print(f"[DEBUG SM] Transition: {self.current_room.name if self.current_room else 'None'} -> {room.name}")

    def _apply_room_change(self) -> None:

        self.current_room = self._next_room
        self.current_room.enter()

        self.navigation_ui.set_room(self.current_room.name)
        print(f"[DEBUG SM] Current room: {self.current_room.name}")
        self._next_room = None

    def show_navigation_ui(self) -> None:
        self._nav_visible = True

    def hide_navigation_ui(self) -> None:
        self._nav_visible = False

    def update(self) -> None:

        if self._state == _FADE_OUT:
            self._fade_alpha += Constant.TRANSITION_SPEED
            if self._fade_alpha >= 255:
                self._fade_alpha = 255
                self._apply_room_change()
                self._state = _FADE_IN

        elif self._state == _FADE_IN:
            self._fade_alpha -= Constant.TRANSITION_SPEED
            if self._fade_alpha <= 0:
                self._fade_alpha = 0
                self._state = _IDLE
                print("[DEBUG SM] Transition complete")

        if self._nav_visible:
            self.navigation_ui.update()

        if self.current_room:
            self.update_room(self.current_room)

    def update_room(self, current_room: Room) -> None:
        current_room.update()


    def render(self) -> None:
        if self.current_room:
            self.current_room.render()

        if self._nav_visible and self.current_room:
            self.navigation_ui.render(self.screen)

        if self._fade_alpha > 0:
            self._fade_surface.set_alpha(int(self._fade_alpha))
            self.screen.blit(self._fade_surface, (0, 0))

    def handle_event(self, event) -> None:
        if self._nav_visible:
            self.navigation_ui.handle_event(event)

        if self.current_room and self._state == _IDLE:
            self.current_room.handle_event(event)
