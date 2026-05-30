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
from UI.Button import Button


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
        self._dough_entered = False
        self._selected_dough = None

        self._Btn_Original = Button(
            x=-110,
            y=-5,
            image_path=Constant.BTN_Original_IMAGE,
            hover_image_path=Constant.BTN_Original_IMAGE,
            callback=self.spawn_original
        )

        self._Btn_Coklat = Button(
            x=-125,
            y=270,
            image_path=Constant.BTN_Coklat_IMAGE,
            hover_image_path=Constant.BTN_Coklat_IMAGE,
            callback=self.spawn_coklat
        )

        self._Btn_Strawberry = Button(
            x=-125,
            y=122,
            image_path=Constant.BTN_Strawberry_IMAGE,
            hover_image_path=Constant.BTN_Strawberry_IMAGE,
            callback=self.spawn_strawberry
        )

        self._Btn_Original.image = pygame.transform.smoothscale(self._Btn_Original.image, (450, 300))
        self._Btn_Original.hover_image = pygame.transform.smoothscale(self._Btn_Original.hover_image, (450, 300))

        self._Btn_Coklat.image = pygame.transform.smoothscale(self._Btn_Coklat.image, (450, 300))
        self._Btn_Coklat.hover_image = pygame.transform.smoothscale(self._Btn_Coklat.hover_image, (450, 300))

        self._Btn_Strawberry.image = pygame.transform.smoothscale(self._Btn_Strawberry.image, (450, 310))
        self._Btn_Strawberry.hover_image = pygame.transform.smoothscale(self._Btn_Strawberry.hover_image, (450, 310))

        self._Btn_Original.hitbox = pygame.Rect(0, 70, 230, 135)
        self._Btn_Coklat.hitbox = pygame.Rect(0, 347, 230, 140)
        self._Btn_Strawberry.hitbox = pygame.Rect(0, 205, 230, 140)

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
        mouse_pos = pygame.mouse.get_pos()

        self._Btn_Original.is_hovered = self._Btn_Original.hitbox.collidepoint(mouse_pos)
        self._Btn_Coklat.is_hovered = self._Btn_Coklat.hitbox.collidepoint(mouse_pos)
        self._Btn_Strawberry.is_hovered = self._Btn_Strawberry.hitbox.collidepoint(mouse_pos)

        if self._dough_entered and self._dough_y < self._target_y:
            self._dough_y += self._dough_speed
            if self._dough_y >= self._target_y:
                self._dough_y = self._target_y
                print(f"[DEBUG Dough] {self._selected_flavor} dough entered the room")

    def exit(self):
        print("[DEBUG Dough] Exit room")

    def spawn_original(self):
        print("[DEBUG Dough] Spawn original dough")
        self._selected_flavor = "Original"
        self._dough_image = pygame.image.load(Constant.Adonan_IMAGE).convert_alpha()
        self._dough_image = pygame.transform.smoothscale(
            self._dough_image,
            (250,225)
        )
        self._dough_entered = True
        self._dough_y = -150

    def spawn_coklat(self):
        print("[DEBUG Dough] Spawn chocolate dough")
        self._selected_flavor = "Coklat"
        self._dough_image = pygame.image.load(Constant.Adonan_Coklat_IMAGE).convert_alpha()
        self._dough_image = pygame.transform.smoothscale(
            self._dough_image,
            (250,225)
        )
        self._dough_entered = True
        self._dough_y = -250

    def spawn_strawberry(self):
        print("[DEBUG Dough] Spawn strawberry dough")
        self._selected_flavor = "Strawberry"
        self._dough_image = pygame.image.load(Constant.Adonan_Strawberry_IMAGE).convert_alpha()
        self._dough_image = pygame.transform.smoothscale(
            self._dough_image,
            (250,225)
        )
        self._dough_entered = True
        self._dough_y = -350

    def render(self):
        if not self.screen:
            return

        if self._bg_image:
            self.screen.blit(self._bg_image, (0, Constant.NAV_BAR_HEIGHT))
            if self._dough_image and self._dough_entered:
                self.screen.blit(self._dough_image, (self._dough_x, self._dough_y))
            if self._exhaust_neck:
                self.screen.blit(self._exhaust_neck,(SCREEN_WIDTH // 2 - 488,Constant.NAV_BAR_HEIGHT - 300))

            if self._exhaust_mouth:
                self.screen.blit(self._exhaust_mouth,(SCREEN_WIDTH // 2 - 475,Constant.NAV_BAR_HEIGHT - 40))

            self._Btn_Original.render(self.screen)
            self._Btn_Coklat.render(self.screen)
            self._Btn_Strawberry.render(self.screen)

            pygame.draw.rect(self.screen, (255,255,255), self._Btn_Original.hitbox, 3)
            pygame.draw.rect(self.screen, (255,255,255), self._Btn_Coklat.hitbox, 3)
            pygame.draw.rect(self.screen, (255,255,255), self._Btn_Strawberry.hitbox, 3)

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
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self._Btn_Original.hitbox.collidepoint(event.pos):
                self.spawn_original()
            if self._Btn_Coklat.hitbox.collidepoint(event.pos):
                self.spawn_coklat()
            if self._Btn_Strawberry.hitbox.collidepoint(event.pos):
                self.spawn_strawberry()