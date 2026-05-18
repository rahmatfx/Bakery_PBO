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

        self.bar_rect = pygame.Rect(
            Constant.NAV_BAR_X,
            Constant.NAV_BAR_Y,
            Constant.NAV_BAR_WIDTH,
            Constant.NAV_BAR_HEIGHT
        )

        self.font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_SMALL_SIZE)

        self.bar_bg_img = self._load_image(Constant.NAV_BAR_BG)
        self.btn_normal_img = self._load_image(Constant.NAV_BTN_NORMAL)
        self.btn_hover_img = self._load_image(Constant.NAV_BTN_HOVER)
        self.btn_active_img = self._load_image(Constant.NAV_BTN_ACTIVE)

    @staticmethod
    def _load_image(path: str):
        try:
            img = pygame.image.load(path).convert_alpha()
            print(f"[DEBUG NAV] Loaded: {path}")
            return img
        except Exception:
            print(f"[DEBUG NAV] Image not found, using fallback: {path}")
            return None

    def build_buttons(self, room_names: list[str]) -> None:
        self.buttons.clear()
        count = len(room_names)
        if count == 0:
            return

        total_width = count * Constant.NAV_BUTTON_WIDTH + (count - 1) * Constant.NAV_BTN_SPACING
        start_x = (Constant.SCREEN_WIDTH - total_width) // 2
        y = Constant.NAV_BAR_Y + (Constant.NAV_BAR_HEIGHT - Constant.NAV_BUTTON_HEIGHT) // 2

        for i, name in enumerate(room_names):
            btn = NavButton(
                x=start_x + i * (Constant.NAV_BUTTON_WIDTH + Constant.NAV_BTN_SPACING),
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
        if self.bar_bg_img:
            scaled = pygame.transform.scale(self.bar_bg_img, (self.bar_rect.width, self.bar_rect.height))
            surface.blit(scaled, self.bar_rect.topleft)
        else:
            pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN, self.bar_rect)
            pygame.draw.line(surface, Constant.COLOR_DARK_BROWN, 
                           (self.bar_rect.x, self.bar_rect.y),
                           (self.bar_rect.right, self.bar_rect.y), 2)

        for btn in self.buttons:
            is_active = (btn.room == self.room)
            is_hover = btn.is_hovered

            if is_active and self.btn_active_img:
                img = pygame.transform.scale(self.btn_active_img, (btn.rect.width, btn.rect.height))
                surface.blit(img, btn.rect.topleft)
            elif is_hover and self.btn_hover_img:
                img = pygame.transform.scale(self.btn_hover_img, (btn.rect.width, btn.rect.height))
                surface.blit(img, btn.rect.topleft)
            elif self.btn_normal_img:
                img = pygame.transform.scale(self.btn_normal_img, (btn.rect.width, btn.rect.height))
                surface.blit(img, btn.rect.topleft)
            else:
                if is_active:
                    color = Constant.COLOR_PINK_ACCENT
                elif is_hover:
                    color = Constant.COLOR_LIGHT_BROWN
                else:
                    color = Constant.COLOR_CREAM if hasattr(Constant, 'COLOR_BG_CREAM') else (255, 248, 231)

                pygame.draw.rect(surface, color, btn.rect, border_radius=8)
                pygame.draw.rect(surface, Constant.COLOR_DARK_BROWN, btn.rect, 2, border_radius=8)

            text_color = Constant.COLOR_WHITE if is_active else Constant.COLOR_DARK_BROWN
            text_surf = self.font.render(btn.label, True, text_color)
            text_rect = text_surf.get_rect(center=btn.rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)