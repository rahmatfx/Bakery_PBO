import pygame, os
from Enum.BakeryEnum import DecorationOption, Mold, Flavor
from Room.Room import Room
from Order.Cake import Cake, CakeStep
from UI.Button import Button
import Constant

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
    berriesTop,
    creamTop,
    oreoTop,
    sprinklesHeart,
    sprinklesStar,
    sprinklesRound,
    chocoHeart,
    chocoStar,
    chocoRound,
    BAKED_CAKE
)


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
        self.cake = None          # injected by Game.py
        self.isDecorated = False
        self.cakeRect = None
        self.toppingImages = {}   # filled in enter()

        self.berries = DecorButton(
            x=345, y=550,
            image_path=berries_decor_IMAGE,
            hover_image_path=berries_hover_IMAGE
        )
        self.sprinkles = DecorButton(
            x=225, y=600,
            image_path=sprinkles_decor_IMAGE,
            hover_image_path=sprinkles_hover_IMAGE
        )
        self.chocochip = DecorButton(
            x=800, y=560,
            image_path=chocochip_decor_IMAGE,
            hover_image_path=chocochip_hover_IMAGE
        )
        self.cream = DecorButton(
            x=975, y=550,
            image_path=cream_decor_IMAGE,
            hover_image_path=cream_hover_IMAGE
        )
        self.oreo = DecorButton(
            x=905, y=620,
            image_path=oreo_decor_IMAGE,
            hover_image_path=oreo_hover_IMAGE
        )

        self.berries.image       = pygame.transform.smoothscale(self.berries.image,       (130, 125))
        self.berries.hover_image = pygame.transform.smoothscale(self.berries.hover_image, (130, 175))

        self.sprinkles.image       = pygame.transform.smoothscale(self.sprinkles.image,       (70,  140))
        self.sprinkles.hover_image = pygame.transform.smoothscale(self.sprinkles.hover_image, (80,  170))

        self.chocochip.image       = pygame.transform.smoothscale(self.chocochip.image,       (130, 120))
        self.chocochip.hover_image = pygame.transform.smoothscale(self.chocochip.hover_image, (130, 180))

        self.cream.image       = pygame.transform.smoothscale(self.cream.image,       (130, 130))
        self.cream.hover_image = pygame.transform.smoothscale(self.cream.hover_image, (130, 180))

        self.oreo.image       = pygame.transform.smoothscale(self.oreo.image,       (130, 120))
        self.oreo.hover_image = pygame.transform.smoothscale(self.oreo.hover_image, (130, 180))


    def enter(self):
        if os.path.exists(DEKORASI_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(DEKORASI_BG).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

        print("=== DECORATION ENTER ===")
        print(f"cake: {self.cake}")
        if self.cake:
            print(f"step: {self.cake.step}")
            print(f"flavor: {self.cake.flavor}")
            print(f"mold: {self.cake.mold}")
            path = BAKED_CAKE.get((self.cake.flavor, self.cake.mold))
            print(f"path: {path}")
            print(f"path exists: {os.path.exists(path) if path else False}")

        # load cake image
        if self.cake and self.cake.step >= CakeStep.BAKED:
            self.cake.load_cake_image(BAKED_CAKE)
            self.cakeRect = self.cake.cake_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 170)
            ) if self.cake.cake_surface else None

        if not self.toppingImages:
            topping_paths = {
                "berries":          berriesTop,
                "cream":            creamTop,
                "oreo":             oreoTop,
                "sprinkles_heart":  sprinklesHeart,
                "sprinkles_star":   sprinklesStar,
                "sprinkles_round":  sprinklesRound,
                "choco_heart":      chocoHeart,
                "choco_star":       chocoStar,
                "choco_round":      chocoRound,
            }
            topping_widths = {
                "berries":          130,
                "cream":            130,
                "oreo":             130,
                "sprinkles_heart":  140,
                "sprinkles_star":   140,
                "sprinkles_round":  140,
                "choco_heart":      145,
                "choco_star":       145,
                "choco_round":      145,
            }
            for key, path in topping_paths.items():
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    w, h = img.get_size()
                    target_w = topping_widths.get(key, 150)
                    target_h = int(h * (target_w / w))
                    self.toppingImages[key] = pygame.transform.smoothscale(img, (target_w, target_h))

        # sync topping visual with cake state on every entry
        if self.cake and self.cake.decoration:
            self.cake.load_topping_image(self.toppingImages)
            self.isDecorated = True
        else:
            self.isDecorated = False


    def update(self, delta_time=0):
        mouse_pos = pygame.mouse.get_pos()
        self.berries.update(mouse_pos)
        self.sprinkles.update(mouse_pos)
        self.chocochip.update(mouse_pos)
        self.cream.update(mouse_pos)
        self.oreo.update(mouse_pos)


    def exit(self):
        pass


    def render(self):
        if not self.screen:
            return

        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))

            self.berries.render(self.screen)
            self.sprinkles.render(self.screen)
            self.chocochip.render(self.screen)
            self.cream.render(self.screen)
            self.oreo.render(self.screen)

            if self.cakeRect:
                self.cake.render_cake(self.screen, center=self.cakeRect.center)

            if self.cake and self.cake.step < CakeStep.BAKED:
                warn = self._font_body.render("Kue belum dipanggang!", True, COLOR_DARK_BROWN)
                self.screen.blit(warn, warn.get_rect(centerx=SCREEN_WIDTH // 2, centery=50))
        else:
            self.screen.fill(COLOR_BG_CREAM)
            t = self._font_heading.render("~ Decoration ~", True, COLOR_DARK_BROWN)
            self.screen.blit(t, t.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 3))


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if not self.cake or self.cake.step < CakeStep.BAKED:
                return

            clicked = None

            if self.berries.rect.collidepoint(event.pos):
                clicked = DecorationOption.DRIED_FRUIT
                print("[debug] berries clicked")

            elif self.sprinkles.rect.collidepoint(event.pos):
                clicked = DecorationOption.SPRINKLE
                print("[debug] sprinkles clicked")

            elif self.chocochip.rect.collidepoint(event.pos):
                clicked = DecorationOption.CHOCOCHIP
                print("[debug] chocochip clicked")

            elif self.cream.rect.collidepoint(event.pos):
                clicked = DecorationOption.WHIPCREAM
                print("[debug] cream clicked")

            elif self.oreo.rect.collidepoint(event.pos):
                clicked = DecorationOption.OREO
                print("[debug] oreo clicked")

            if clicked:
                self.cake.set_decoration(clicked)
                self.cake.load_topping_image(self.toppingImages)
                self.isDecorated = True