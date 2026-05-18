from enum import Enum

class Flavor(Enum):
    CHOCOLATE = "Chocolate"
    STRAWBERRY = "Strawberry"
    ORIGINAL = "Original"


class Mold(Enum):
    ROUND = "Round"
    STAR = "Star"
    HEART = "Heart"


class DecorationOption(Enum):
    OREO = "Oreo"
    SPRINKLE = "Sprinkle"
    CHOCOCHIP = "Chocochip"
    DRIED_FRUIT = "Dried Fruit"
    WHIPCREAM = "Whipcream"