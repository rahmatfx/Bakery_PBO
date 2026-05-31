from enum import IntEnum
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
        self.step: CakeStep = CakeStep.EMPTY

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

    def is_complete(self) -> bool:
        return self.step == CakeStep.COMPLETE

    def reset(self) -> None:
        self.flavor = None
        self.mold = None
        self.decoration = None
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
