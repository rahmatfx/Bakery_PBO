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
        self._dough_image = None
        self._exhaust_neck = None
        self._exhaust_mouth = None
        self._dough_x = 0
        self._dough_y = 200
        self._target_y = 350
        self._dough_speed = 25

    def enter(self):
        print("[DEBUG Dough] Enter room")

        if os.path.exists(DOUGH_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(DOUGH_BG).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT - Constant.NAV_BAR_HEIGHT)
            )
            print("[DEBUG Dough] Background loaded")
            if os.path.exists(Constant.Adonan_IMAGE):
                self._dough_image = pygame.image.load(Constant.Adonan_IMAGE).convert_alpha()

                self._dough_image = pygame.transform.smoothscale(
                    self._dough_image,
                    (250,225)
                )

                self._dough_x = (SCREEN_WIDTH // 2 -125)
                self._dough_y = -200
                print("[DEBUG Dough] Dough image loaded")
            if os.path.exists(Constant.Exhaust_Neck_IMAGE):
                self._exhaust_neck = pygame.image.load(Constant.Exhaust_Neck_IMAGE).convert_alpha()

                self._exhaust_neck = pygame.transform.smoothscale(self._exhaust_neck,(1000, 400))
                print("[DEBUG Dough] Exhaust neck loaded")
            if os.path.exists(Constant.Exhaust_Mouth_IMAGE):
                self._exhaust_mouth = pygame.image.load(Constant.Exhaust_Mouth_IMAGE).convert_alpha()

                self._exhaust_mouth = pygame.transform.smoothscale(self._exhaust_mouth,(950, 350))
                print("[DEBUG Dough] Exhaust mouth loaded")
        else:
            print("[DEBUG Dough] Background not found")

    def update(self):
        if self._dough_y < self._target_y:
            self._dough_y += self._dough_speed
            if self._dough_y > self._target_y:
                self._dough_y = self._target_y

    def exit(self):
        print("[DEBUG Dough] Exit room")

    def render(self):
        if not self.screen:
            return

        if self._bg_image:
            self.screen.blit(self._bg_image, (0, Constant.NAV_BAR_HEIGHT))
            if self._dough_image:
                self.screen.blit(self._dough_image, (self._dough_x, self._dough_y))
            if self._exhaust_neck:
                self.screen.blit(self._exhaust_neck,(SCREEN_WIDTH // 2 - 488,Constant.NAV_BAR_HEIGHT - 300))

            if self._exhaust_mouth:
                self.screen.blit(self._exhaust_mouth,(SCREEN_WIDTH // 2 - 475,Constant.NAV_BAR_HEIGHT - 40))
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