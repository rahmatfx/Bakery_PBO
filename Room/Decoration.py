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


# Semua topping path dan target width dikumpulkan di sini supaya tidak berserakan
TOPPING_ASSETS = {
    "berries":          (berriesTop,      130),
    "cream":            (creamTop,        130),
    "oreo":             (oreoTop,         130),
    "sprinkles_heart":  (sprinklesHeart,  140),
    "sprinkles_star":   (sprinklesStar,   140),
    "sprinkles_round":  (sprinklesRound,  140),
    "choco_heart":      (chocoHeart,      145),
    "choco_star":       (chocoStar,       145),
    "choco_round":      (chocoRound,      145),
}


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
            r = img.get_rect()
            r.midbottom = self.anchor_pos
            self.rect = r
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, surface):
        if not self._has_image:
            return
        img = self.hover_image if self.is_hovered else self.image
        r = img.get_rect()
        r.midbottom = self.anchor_pos
        surface.blit(img, r)

    def set_position(self, x, y):
        self.anchor_pos = (x, y)
        if self._has_image:
            self.rect = self.image.get_rect(midbottom=self.anchor_pos)
        else:
            self.rect.midbottom = self.anchor_pos


class Decoration(Room):
    def __init__(self):
        super().__init__(name="Decoration")

        self._bg_image     = None
        self._font_heading = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body    = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)

        self.cake: Cake    = None
        self.cakeRect      = None
        self.toppingImages = {}   # di-cache, hanya load sekali

        # Tombol dekorasi
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

        # Map tombol → DecorationOption (buat handle_event yang clean)
        self._deco_map = {
            self.berries:   DecorationOption.DRIED_FRUIT,
            self.sprinkles: DecorationOption.SPRINKLE,
            self.chocochip: DecorationOption.CHOCOCHIP,
            self.cream:     DecorationOption.WHIPCREAM,
            self.oreo:      DecorationOption.OREO,
        }

    # ------------------------------------------------------------------ #
    #  ENTER / EXIT                                                        #
    # ------------------------------------------------------------------ #

    def enter(self):
        print("=== DECORATION ENTER ===")
        self._load_bg()
        self._load_topping_assets()
        self._sync_from_cake()

    def exit(self):
        pass

    # ------------------------------------------------------------------ #
    #  VISUAL HELPERS                                                      #
    # ------------------------------------------------------------------ #

    def _load_bg(self):
        if os.path.exists(DEKORASI_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(DEKORASI_BG).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

    def _load_topping_assets(self):
        """Load semua gambar topping — hanya sekali, di-cache di self.toppingImages."""
        if self.toppingImages:
            return
        for key, (path, target_w) in TOPPING_ASSETS.items():
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                w, h = img.get_size()
                self.toppingImages[key] = pygame.transform.smoothscale(
                    img, (target_w, int(h * target_w / w)))

    def _sync_from_cake(self):
        """
        Rebuild visual state dari cake object — dipanggil setiap enter().
        Tidak ada flag boolean tersendiri; semua derived dari cake.
        """
        if not self.cake:
            self.cakeRect = None
            return

        print(f"[DEBUG Deco] step={self.cake.step}, flavor={self.cake.flavor}, mold={self.cake.mold}")

        # Load gambar kue kalau sudah dipanggang
        if self.cake.step >= CakeStep.BAKED:
            self.cake.load_cake_image(BAKED_CAKE)
            self.cakeRect = (
                self.cake.cake_surface.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 170))
                if self.cake.cake_surface else None
            )
        else:
            self.cakeRect = None

        # Sync topping kalau dekorasi sudah dipilih (misal user balik ke room ini)
        if self.cake.decoration:
            self.cake.load_topping_image(self.toppingImages)

    # ------------------------------------------------------------------ #
    #  UPDATE                                                              #
    # ------------------------------------------------------------------ #

    def update(self, delta_time=0):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._deco_map:
            btn.update(mouse_pos)

    # ------------------------------------------------------------------ #
    #  RENDER                                                              #
    # ------------------------------------------------------------------ #

    def render(self):
        if not self.screen:
            return

        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))

            # Render semua tombol dekorasi
            for btn in self._deco_map:
                btn.render(self.screen)

            # Render kue + topping
            if self.cakeRect:
                self.cake.render_cake(self.screen, center=self.cakeRect.center)

            # Peringatan kalau kue belum dipanggang
            if self.cake and self.cake.step < CakeStep.BAKED:
                warn = self._font_body.render("Kue belum dipanggang!", True, COLOR_DARK_BROWN)
                self.screen.blit(warn, warn.get_rect(centerx=SCREEN_WIDTH // 2, centery=50))

        else:
            self.screen.fill(COLOR_BG_CREAM)
            t = self._font_heading.render("~ Decoration ~", True, COLOR_DARK_BROWN)
            self.screen.blit(t, t.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 3))

    # ------------------------------------------------------------------ #
    #  EVENTS                                                              #
    # ------------------------------------------------------------------ #

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if not self.cake or self.cake.step < CakeStep.BAKED:
            return

        for btn, deco in self._deco_map.items():
            if btn.rect.collidepoint(event.pos):
                self.cake.set_decoration(deco)
                self.cake.load_topping_image(self.toppingImages)
                print(f"[debug] {deco.value} clicked")
                break