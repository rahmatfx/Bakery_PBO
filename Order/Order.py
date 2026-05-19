import random
from Enum.BakeryEnum import Flavor, Mold, DecorationOption


class Order:

    def __init__(self, flavor: Flavor = None, mold: Mold = None,
                 decoration: DecorationOption = None):
        self.flavor: Flavor = flavor
        self.mold: Mold = mold
        self.decoration: DecorationOption = decoration

    @staticmethod
    def randomFlavor() -> Flavor:
        return random.choice(list(Flavor))

    @staticmethod
    def randomMold() -> Mold:
        return random.choice(list(Mold))

    @staticmethod
    def randomDecoration() -> DecorationOption:
        return random.choice(list(DecorationOption))
    
    def is_complete(self) -> bool:
        return (self.flavor is not None
                and self.mold is not None
                and self.decoration is not None)

    def __str__(self) -> str:
        return (f"{self.flavor.value} | {self.mold.value} | "
                f"{self.decoration.value}")