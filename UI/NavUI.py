import pygame
from Observer import Subject
from UI.Button import Button
import Constant


class NavButton(Button):

    def __init__(self, x: int, y: int, width: int, height: int,
                 label: str, room: str, callback=None):
        super().__init__(x, y, width, height, label=label)
        self.room = room
        self._nav_callback = callback  

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self._nav_callback:
                print(f"[DEBUG NAV] Clicked: {self.label} -> room: {self.room}")
                self._nav_callback(self.room)


class NavigationUI(Subject):

    def __init__(self):
        super().__init__()
        self.room: str = ""
        self.buttons: list[NavButton] = []
        self.timer_text: str = ""

        self.bar_rect = pygame.Rect(
            Constant.NAV_BAR_X,
            Constant.NAV_BAR_Y,
            Constant.NAV_BAR_WIDTH,
            Constant.NAV_BAR_HEIGHT
        )

        self.font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_SMALL_SIZE)

        self.bar_bg_img = self._load_and_scale(Constant.NAV_BAR_BG,
                                                Constant.NAV_BAR_WIDTH,
                                                Constant.NAV_BAR_HEIGHT)
        self.btn_normal_img = self._load_and_scale(Constant.NAV_BTN_NORMAL,
                                                    Constant.NAV_BUTTON_WIDTH,
                                                    Constant.NAV_BUTTON_HEIGHT)
        self.btn_hover_img = self._load_and_scale(Constant.NAV_BTN_HOVER,
                                                   Constant.NAV_BUTTON_WIDTH,
                                                   Constant.NAV_BUTTON_HEIGHT)
        self.btn_active_img = self._load_and_scale(Constant.NAV_BTN_ACTIVE,
                                                    Constant.NAV_BUTTON_WIDTH,
                                                    Constant.NAV_BUTTON_HEIGHT)

        self._text_cache: dict[str, pygame.Surface] = {}

    @staticmethod
    def _load_and_scale(path: str, w: int, h: int):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except Exception:
            return None

    def _get_cached_text(self, text: str, color: tuple) -> pygame.Surface:
        key = f"{text}_{color}"
        if key not in self._text_cache:
            self._text_cache[key] = self.font.render(text, True, color)
        return self._text_cache[key]

    def build_buttons(self, room_names: list[str]) -> None:
        self.buttons.clear()
        count = len(room_names)
        if count == 0:
            return

        total_width = (count * Constant.NAV_BUTTON_WIDTH
                       + (count - 1) * Constant.NAV_BTN_SPACING)
        start_x = (Constant.SCREEN_WIDTH - total_width) // 2
        y = (Constant.NAV_BAR_Y
             + (Constant.NAV_BAR_HEIGHT - Constant.NAV_BUTTON_HEIGHT) // 2)

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

    def get_room(self) -> str:
        return self.room

    def set_room(self, room_name: str) -> None:
        self.room = room_name
        print(f"[DEBUG NAV] Active room set: {room_name}")

    def set_timer_text(self, text: str) -> None:
        self.timer_text = text

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self, surface: pygame.Surface) -> None:

        if self.bar_bg_img:
            surface.blit(self.bar_bg_img, self.bar_rect.topleft)
        else:
            pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN, self.bar_rect)
            pygame.draw.line(surface, Constant.COLOR_DARK_BROWN,
                             (self.bar_rect.x, self.bar_rect.bottom - 1),
                             (self.bar_rect.right, self.bar_rect.bottom - 1), 2)

        for btn in self.buttons:
            is_active = (btn.room == self.room)
            is_hover = btn.is_hovered

            if is_active and self.btn_active_img:
                surface.blit(self.btn_active_img, btn.rect.topleft)
            elif is_hover and self.btn_hover_img:
                surface.blit(self.btn_hover_img, btn.rect.topleft)
            elif self.btn_normal_img:
                surface.blit(self.btn_normal_img, btn.rect.topleft)
            else:
                if is_active:
                    color = Constant.COLOR_PINK_ACCENT
                elif is_hover:
                    color = Constant.COLOR_LIGHT_BROWN
                else:
                    color = Constant.COLOR_BG_CREAM

                pygame.draw.rect(surface, color, btn.rect, border_radius=8)
                pygame.draw.rect(surface, Constant.COLOR_DARK_BROWN,
                                 btn.rect, 2, border_radius=8)

            text_color = Constant.COLOR_WHITE if is_active else Constant.COLOR_DARK_BROWN
            text_surf = self._get_cached_text(btn.label, text_color)
            surface.blit(text_surf, text_surf.get_rect(center=btn.rect.center))

        if self.timer_text:
            timer_surf = self.font.render(self.timer_text, True, Constant.COLOR_WHITE)
            timer_rect = timer_surf.get_rect(
                right=Constant.SCREEN_WIDTH - 20,
                centery=self.bar_rect.centery
            )
            pill = timer_rect.inflate(20, 8)
            pygame.draw.rect(surface, Constant.COLOR_DARK_BROWN, pill, border_radius=6)
            surface.blit(timer_surf, timer_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)