from enum import IntEnum
import os
from Enum.BakeryEnum import Flavor, Mold, DecorationOption


class CakeStep(IntEnum):
    EMPTY      = 0   # Belum apa-apa
    DOUGH_SET  = 1   # Dough Room selesai (flavor sudah dipilih)
    BAKED      = 2   # Oven Room selesai (sudah dipanggang)
    DECORATED  = 3   # Decoration Room selesai (topping sudah dipilih)
    COMPLETE   = 4   # Semua step selesai, siap dicek Cashier

class Cake:

    def __init__(self):
        self.flavor: Flavor | None = None
        self.mold: Mold | None = None
        self.decoration: DecorationOption | None = None
        self.topping_surface = None
        self.step: CakeStep = CakeStep.EMPTY
        self.cake_surface = None
        self.is_baking: bool = False
        self.bake_start_time: int | None = None

# urusan dough room

    def set_flavor(self, flavor: Flavor) -> None:
        self.flavor = flavor
        if self.step < CakeStep.DOUGH_SET:
            self.step = CakeStep.DOUGH_SET

    def set_mold(self, mold: Mold) -> None:
        self.mold = mold

# urusan baking room

    def set_baked(self) -> None:
        if self.step < CakeStep.BAKED:
            self.step = CakeStep.BAKED

# urusan decoration room

    def set_decoration(self, decoration: DecorationOption) -> None:
        self.decoration = decoration
        if self.step < CakeStep.DECORATED:
            self.step = CakeStep.DECORATED
        # Kalau semua atribut sudah terisi, otomatis COMPLETE
        if self.flavor and self.mold and self.decoration and self.step >= CakeStep.BAKED:
            self.step = CakeStep.COMPLETE

    def load_topping_image(self, topping_images: dict) -> None:
        """Call this after decoration is set to store the correct topping surface."""
        if not self.decoration or not self.mold:
            self.topping_surface = None
            return

        shape = self.mold.value.lower()

        decoration_to_key = {
            DecorationOption.DRIED_FRUIT: "berries",
            DecorationOption.WHIPCREAM:   "cream",
            DecorationOption.OREO:        "oreo",
            DecorationOption.SPRINKLE:    f"sprinkles_{shape}",
            DecorationOption.CHOCOCHIP:   f"choco_{shape}",
        }

        key = decoration_to_key.get(self.decoration)
        self.topping_surface = topping_images.get(key) if key else None

    def render_topping(self, surface, center: tuple) -> None:
        """Blit the topping surface centered on the given position."""
        if not self.topping_surface:
            return
        rect = self.topping_surface.get_rect(center=center)
        surface.blit(self.topping_surface, rect)

    def load_cake_image(self, baked_cake_dict: dict, width: int = 150) -> None:
        path = baked_cake_dict.get((self.flavor, self.mold))
        if path and os.path.exists(path):
            import pygame
            img = pygame.image.load(path).convert_alpha()
            new_w = width
            new_h = int(img.get_height() * (new_w / img.get_width()))
            self.cake_surface = pygame.transform.smoothscale(img, (new_w, new_h))
        else:
            self.cake_surface = None

    def render_cake(self, surface, center: tuple) -> None:
        if self.cake_surface:
            cake_rect = self.cake_surface.get_rect(center=center)
            surface.blit(self.cake_surface, cake_rect)
            # topping sits near the top of the cake
            topping_center = (cake_rect.centerx, cake_rect.top + 30)
            self.render_topping(surface, topping_center)

    def is_complete(self) -> bool:
        return self.step == CakeStep.COMPLETE

    def reset(self) -> None:
        self.flavor = None
        self.mold = None
        self.decoration = None
        self.topping_surface = None
        self.cake_surface = None 
        self.step = CakeStep.EMPTY

    def matches_order(self, order) -> bool:
        return (
            self.flavor == order.flavor
            and self.mold == order.mold
            and self.decoration == order.decoration
        )

    def __str__(self) -> str:
        flavor_str = self.flavor.value if self.flavor else "???"
        mold_str = self.mold.value if self.mold else "???"
        deco_str = self.decoration.value if self.decoration else "???"
        return f"{flavor_str} | {mold_str} | {deco_str} [{self.step.name}]"
