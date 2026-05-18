import pygame
from Observer import Subject
import Constant

class NavButton:
    def __init__(self, x: int, y: int, width: int, height: int,
                 label: str, room: str, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label     
        self.room = room       
        self.callback = callback
        self.is_hovered = False

    def update(self, mouse_pos: tuple) -> None:
        prev = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered and not prev:
            print(f"[DEBUG NAV] Hover: {self.label} -> room: {self.room}")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                print(f"[DEBUG NAV] Clicked: {self.label} -> room: {self.room}")
                self.callback(self.room)


class NavigationUI(Subject):

    def __init__(self):
        super().__init__()  
        self.room: str = ""        
        self.buttons: list[NavButton] = []
        self.bar_rect = pygame.Rect(0, 0, Constant.SCREEN_WIDTH, Constant.NAV_BAR_HEIGHT)

    def build_buttons(self, room_names: list[str]) -> None:

        self.buttons.clear()
        count = len(room_names)
        if count == 0:
            return

        total_width = count * (Constant.NAV_BUTTON_WIDTH + 10) - 10
        start_x = (Constant.SCREEN_WIDTH - total_width) // 2
        y = (Constant.NAV_BAR_HEIGHT - Constant.NAV_BUTTON_HEIGHT) // 2

        for i, name in enumerate(room_names):
            btn = NavButton(
                x=start_x + i * (Constant.NAV_BUTTON_WIDTH + 10),
                y=y,
                width=Constant.NAV_BUTTON_WIDTH,
                height=Constant.NAV_BUTTON_HEIGHT,
                label=name,       
                room=name,        
                callback=self._on_button_click,
            )
            self.buttons.append(btn)

        print(f"[DEBUG NAV] Built {count} buttons: {room_names}")

    def _on_button_click(self, room_name: str) -> None:

        print(f"[DEBUG NAV] Emitting 'room_change' event with room: {room_name}")
        self.notify("room_change", room_name)

    def on_room_change(self, room_name: str) -> str:
  
        self.notify("room_change", room_name)
        return room_name

    def get_room(self) -> str:
        return self.room

    def set_room(self, room_name: str) -> None:

        self.room = room_name
        print(f"[DEBUG NAV] Active room set: {room_name}")


    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, surface: pygame.Surface) -> None:
        if Constant.DEBUG_NAV_UI:
            pass
        else:
            # TODO: 
            pass

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)
