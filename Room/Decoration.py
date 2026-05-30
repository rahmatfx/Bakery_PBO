import pygame, os
from Room.Room import Room
from UI.Button import Button
from Constant import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    DEKORASI_BG, 
    COLOR_BG_CREAM, 
    COLOR_DARK_BROWN, 
    FONT_HEADING_SIZE, 
    FONT_BODY_SIZE, 
    FONT_NAME,
    berries_decor_IMAGE,
    berries_hover_IMAGE,
    chocochip_decor_IMAGE,
    chocochip_hover_IMAGE,
    cream_decor_IMAGE,
    cream_hover_IMAGE,
    oreo_decor_IMAGE,
    oreo_hover_IMAGE,
    sprinkles_decor_IMAGE,
    sprinkles_hover_IMAGE,
    CAKE_TEMPORARY)

class DecorButton(Button):
    def __init__(self, x, y, *args, **kwargs):
        super().__init__(0, 0, *args, **kwargs)

        self.anchor_pos = (x, y)

        if self._has_image:
            self.rect = self.image.get_rect(midbottom=self.anchor_pos)
        else:
            self.rect.midbottom = self.anchor_pos

    def update(self, mouse_pos):
        if self._has_image:
            img = self.hover_image if self.is_hovered else self.image

            current_rect = img.get_rect()
            current_rect.midbottom = self.anchor_pos

            self.rect = current_rect

        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, surface):
        if not self._has_image:
            return

        img = self.hover_image if self.is_hovered else self.image

        draw_rect = img.get_rect()
        draw_rect.midbottom = self.anchor_pos

        surface.blit(img, draw_rect)

    def set_position(self, x, y):
        self.anchor_pos = (x, y)

        if self._has_image:
            self.rect = self.image.get_rect(midbottom=self.anchor_pos)
        else:
            self.rect.midbottom = self.anchor_pos

class Decoration(Room):
    def __init__(self):
        super().__init__(name="Decoration")
        self._bg_image = None
        self._font_heading = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)
        self.isDecorated = False
        self.cakeImg = None
        self.cakeRect = None

        self.berries = DecorButton(
            x=345,
            y=550,
            image_path=berries_decor_IMAGE,
            hover_image_path=berries_hover_IMAGE,
            # callback=self.spawn_original
        )

        self.sprinkles = DecorButton(
            x=225,
            y=600,
            image_path=sprinkles_decor_IMAGE,
            hover_image_path=sprinkles_hover_IMAGE,
            # callback=self.spawn_original
        )

        self.chocochip = DecorButton(
            x=800,
            y=560,
            image_path=chocochip_decor_IMAGE,
            hover_image_path=chocochip_hover_IMAGE,
            # callback=self.spawn_original
        )

        self.cream = DecorButton(
            x=975,
            y=550,
            image_path=cream_decor_IMAGE,
            hover_image_path=cream_hover_IMAGE,
            # callback=self.spawn_original
        )

        self.oreo = DecorButton(
            x=905,
            y=620,
            image_path=oreo_decor_IMAGE,
            hover_image_path=oreo_hover_IMAGE,
            # callback=self.spawn_original
        )

        self.berries.image = pygame.transform.smoothscale(self.berries.image, (130, 125))
        self.berries.hover_image = pygame.transform.smoothscale(self.berries.hover_image, (130, 175))

        self.sprinkles.image = pygame.transform.smoothscale(self.sprinkles.image, (70, 140))
        self.sprinkles.hover_image = pygame.transform.smoothscale(self.sprinkles.hover_image, (80, 170))

        self.chocochip.image = pygame.transform.smoothscale(self.chocochip.image, (130, 120))
        self.chocochip.hover_image = pygame.transform.smoothscale(self.chocochip.hover_image, (130, 180))

        self.cream.image = pygame.transform.smoothscale(self.cream.image, (130, 130))
        self.cream.hover_image = pygame.transform.smoothscale(self.cream.hover_image, (130, 180))

        self.oreo.image = pygame.transform.smoothscale(self.oreo.image, (130,120))
        self.oreo.hover_image = pygame.transform.smoothscale(self.oreo.hover_image, (130, 180))


    def enter(self):
        if os.path.exists(DEKORASI_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(DEKORASI_BG).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))


    def update(self): 
        mouse_pos = pygame.mouse.get_pos()
        self.berries.update(mouse_pos)
        self.sprinkles.update(mouse_pos)
        self.chocochip.update(mouse_pos)
        self.cream.update(mouse_pos)
        self.oreo.update(mouse_pos)

    def exit(self): pass

    def render(self):
        if not self.screen: return
        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))

            self.berries.render(self.screen)
            self.sprinkles.render(self.screen)
            self.chocochip.render(self.screen)
            self.cream.render(self.screen)
            self.oreo.render(self.screen)
        else:
            self.screen.fill(COLOR_BG_CREAM)
            t = self._font_heading.render("~ Decoration ~", True, COLOR_DARK_BROWN)
            self.screen.blit(t, t.get_rect(centerx=SCREEN_WIDTH//2, centery=SCREEN_HEIGHT//3))

    def handle_event(self, event): pass