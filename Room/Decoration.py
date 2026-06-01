import pygame, os
from Enum.BakeryEnum import DecorationOption, Mold
from Room.Room import Room
from Order.Cake import Cake, CakeStep
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
    berriesTop,
    creamTop,
    oreoTop,
    sprinklesHeart,
    sprinklesStar,
    sprinklesRound,
    chocoHeart,
    chocoStar,
    chocoRound
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
        self.isDecorated = False
        self.cakeImg = None
        self.cakeRect = None
        self.topping = None        # stores the name e.g. "berries"
        self.toppingImage = None   # stores the surface to blit
        self.toppingImages = {}    # all loaded topping surfaces, filled in enter()

        self.berries = DecorButton(
            x=345,
            y=550,
            image_path=berries_decor_IMAGE,
            hover_image_path=berries_hover_IMAGE
        )

        self.sprinkles = DecorButton(
            x=225,
            y=600,
            image_path=sprinkles_decor_IMAGE,
            hover_image_path=sprinkles_hover_IMAGE
        )

        self.chocochip = DecorButton(
            x=800,
            y=560,
            image_path=chocochip_decor_IMAGE,
            hover_image_path=chocochip_hover_IMAGE
        )

        self.cream = DecorButton(
            x=975,
            y=550,
            image_path=cream_decor_IMAGE,
            hover_image_path=cream_hover_IMAGE
        )

        self.oreo = DecorButton(
            x=905,
            y=620,
            image_path=oreo_decor_IMAGE,
            hover_image_path=oreo_hover_IMAGE
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

        if not self.toppingImages:
            topping_paths = {
                "berries":         berriesTop,
                "cream":           creamTop,
                "oreo":            oreoTop,
                "sprinkles_heart": sprinklesHeart,
                "sprinkles_star":  sprinklesStar,
                "sprinkles_round": sprinklesRound,
                "choco_heart":     chocoHeart,
                "choco_star":      chocoStar,
                "choco_round":     chocoRound,
            }

            for key, path in topping_paths.items():
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    w, h = img.get_size()
                    new_w = 150
                    new_h = int(h * (new_w / w))
                    self.toppingImages[key] = pygame.transform.smoothscale(img, (new_w, new_h))

        # sync visual state with cake data on every entry
        if self.cake and self.cake.decoration:
            shape = self.cake.mold.value.lower() if self.cake.mold else "round"

            decoration_to_key = {
                DecorationOption.DRIED_FRUIT: "berries",
                DecorationOption.WHIPCREAM:   "cream",
                DecorationOption.OREO:        "oreo",
                DecorationOption.SPRINKLE:    f"sprinkles_{shape}",
                DecorationOption.CHOCOCHIP:   f"choco_{shape}",
            }

            key = decoration_to_key.get(self.cake.decoration)
            self.topping = self.cake.decoration.value
            self.toppingImage = self.toppingImages.get(key) if key else None
            self.isDecorated = True
        else:
            self.topping = None
            self.toppingImage = None
            self.isDecorated = False


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

            # render topping on top of cake
            if self.toppingImage:
                # fixed for now — swap (SCREEN_WIDTH//2, SCREEN_HEIGHT//2) for cakeRect.center later
                topping_rect = self.toppingImage.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(self.toppingImage, topping_rect)
        else:
            self.screen.fill(COLOR_BG_CREAM)
            t = self._font_heading.render("~ Decoration ~", True, COLOR_DARK_BROWN)
            self.screen.blit(t, t.get_rect(centerx=SCREEN_WIDTH//2, centery=SCREEN_HEIGHT//3))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # block decoration if cake isn't baked yet
            if not self.cake or self.cake.step < CakeStep.BAKED:
                return

            clicked = None

            if self.berries.rect.collidepoint(event.pos):
                clicked = DecorationOption.DRIED_FRUIT
                self.topping = "berries"
                self.toppingImage = self.toppingImages.get("berries")
                print("[debug] berries clicked")

            elif self.sprinkles.rect.collidepoint(event.pos):
                clicked = DecorationOption.SPRINKLE
                self.topping = "sprinkles"
                # pick variant based on cake mold
                shape = self.cake.mold.value.lower() if self.cake.mold else "round"
                self.toppingImage = self.toppingImages.get(f"sprinkles_{shape}")
                print("[debug] sprinkles clicked")
                
            elif self.chocochip.rect.collidepoint(event.pos):
                clicked = DecorationOption.CHOCOCHIP
                self.topping = "chocochip"
                shape = self.cake.mold.value.lower() if self.cake.mold else "round"
                self.toppingImage = self.toppingImages.get(f"choco_{shape}")
                print("[debug] chocochip clicked")

            elif self.cream.rect.collidepoint(event.pos):
                clicked = DecorationOption.WHIPCREAM
                self.topping = "cream"
                self.toppingImage = self.toppingImages.get("cream")
                print("[debug] cream clicked")

            elif self.oreo.rect.collidepoint(event.pos):
                clicked = DecorationOption.OREO
                self.topping = "oreo"
                self.toppingImage = self.toppingImages.get("oreo")
                print("[debug] oreo clicked")

            if clicked:
                self.cake.set_decoration(clicked)
                self.isDecorated = True