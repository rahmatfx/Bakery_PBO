import pygame
import os
from Room.Room import Room
from UI.Button import Button
from Constant import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    MAINMENU_BG,
    BTN_PLAY,
    BTN_PLAY_HOVER,
    BTN_CREDIT,
    BTN_CREDIT_HOVER,
    BTN_EXIT,
    BTN_EXIT_HOVER,
    COLOR_BG_CREAM,
    FONT_TITLE_SIZE,
    FONT_NAME,
)


class MainMenu(Room):

    def __init__(self):
        super().__init__(name="Main Menu")

        self.title: str = "Cozy Bakery"
        self._scene_manager = None
        self._bg_image: pygame.Surface = None

        self._title_font = pygame.font.SysFont(FONT_NAME, FONT_TITLE_SIZE, bold=True)

        self.buttons: list[Button] = []
        self._build_buttons()

    def enter(self) -> None:
        self._load_background()
        self._build_buttons()
        print("[DEBUG] Entered Main Menu")

    def exit(self) -> None:
        pass

    def _load_background(self) -> None:
        if os.path.exists(MAINMENU_BG):
            self._bg_image = pygame.image.load(MAINMENU_BG).convert()
            self._bg_image = pygame.transform.smoothscale(
                self._bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            print(f"[DEBUG] Background loaded: {MAINMENU_BG}")
        else:
            print(f"[DEBUG] Background not found: {MAINMENU_BG} — using fallback color")
            self._bg_image = None

    def _build_buttons(self) -> None:
        self.buttons.clear()

        btn_width = 220
        btn_height = 55
        center_x = SCREEN_WIDTH // 2 - btn_width // 2
        start_y = SCREEN_HEIGHT // 2 + 30
        spacing = 120

        self.buttons.append(Button(
            x=center_x - btn_width // 1.1, y=start_y + spacing - 5,
            image_path=BTN_PLAY,
            hover_image_path=BTN_PLAY_HOVER,
            label="Play",
            callback=self.play,
        ))

        self.buttons.append(Button(
            x=center_x, y=start_y + spacing,
            image_path=BTN_CREDIT,
            hover_image_path=BTN_CREDIT_HOVER,
            label="Credit",
            callback=self.credit,
        ))

        self.buttons.append(Button(
            x=center_x + btn_width // 1.1, y=start_y + spacing,
            image_path=BTN_EXIT,
            hover_image_path=BTN_EXIT_HOVER,
            label="Exit",
            callback=self.exit_game,
        ))

    def play(self) -> None:
        print("[DEBUG] Play() called — transitioning to Cashier")
        if self._scene_manager:
            self._scene_manager.hide_navigation_ui()
            self._scene_manager.transition_to("Cashier") 

    def credit(self) -> None:

        print("[DEBUG] Credit() called — Cozy Bakery, Made with Pygame & Love")

    def exit_game(self) -> None:
  
        print("[DEBUG] Exit() called — quitting game")
        pygame.event.post(pygame.event.Event(pygame.QUIT))


    def update(self, delta_time: float = 0.0) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    def render(self) -> None:
        if not self.screen:
            return

        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))
        else:
            self.screen.fill(COLOR_BG_CREAM)

        for btn in self.buttons:
            btn.render(self.screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)
