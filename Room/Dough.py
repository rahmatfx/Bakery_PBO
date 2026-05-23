import pygame
import os
import Constant
from Room.Room import Room
from Constant import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DOUGH_BG,
    COLOR_BG_CREAM,
    COLOR_DARK_BROWN,
    FONT_HEADING_SIZE,
    FONT_BODY_SIZE,
    FONT_NAME
)


class Dough(Room):
    def __init__(self):
        super().__init__(name="Dough")
        self._bg_image = None
        self._font_heading = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)

    def enter(self):
        print("[DEBUG Dough] Enter room")

        if os.path.exists(DOUGH_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(DOUGH_BG).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT - Constant.NAV_BAR_HEIGHT)
            )
            print("[DEBUG Dough] Background loaded")
        else:
            print("[DEBUG Dough] Background not found")

    def update(self):
        pass

    def exit(self):
        print("[DEBUG Dough] Exit room")

    def render(self):
        if not self.screen:
            return

        if self._bg_image:
            self.screen.blit(self._bg_image, (0, Constant.NAV_BAR_HEIGHT))
        else:
            self.screen.fill(COLOR_BG_CREAM)

            title = self._font_heading.render(
                "~ Dough Room ~",
                True,
                COLOR_DARK_BROWN
            )
            self.screen.blit(
                title,
                title.get_rect(
                    centerx=SCREEN_WIDTH // 2,
                    centery=SCREEN_HEIGHT // 2
                )
            )

    def handle_event(self, event):
        pass