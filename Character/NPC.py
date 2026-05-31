import random
from Order.Order import Order
from Character.NPCData import NPCData
from Character.NPCRegistry import NPCRegistry
from Enum.BakeryEnum import Flavor, Mold, DecorationOption


class NPC:

    def __init__(self, data: NPCData, registry: NPCRegistry = None):
        self.data: NPCData = data
        self.name: str = data.name
        self.expression: str = "neutral"
        self.order: Order = None
        self._registry: NPCRegistry = registry

    # Affinity

    @property
    def affinity(self) -> int:
        if self._registry:
            return self._registry.get_affinity(self.data.id)
        return 0

    def change_affinity(self, delta: int) -> int:
        if self._registry:
            return self._registry.change_affinity(self.data.id, delta)
        return 0

    def get_affinity_level(self) -> int:
        if self._registry:
            return self._registry.get_affinity_level(self.data.id)
        return 0

    # Dialogue

    def get_dialogue(self, mood: str = "neutral",
                     variant: str = "a") -> list[dict]:
        level = self.get_affinity_level()
        return self.data.get_dialogue_entries(level, mood, variant)

    # Cake Options

    def generate_cake_options(self) -> list[Order]:
        options: list[Order] = []

        good_flavor = self._pick_from_or_random(
            self.data.get_preferred_flavors(), Order.randomFlavor, Flavor)
        good_mold = self._pick_from_or_random(
            self.data.get_preferred_molds(), Order.randomMold, Mold)
        good_deco = self._pick_from_or_random(
            self.data.get_preferred_decorations(), Order.randomDecoration,
            DecorationOption)
        options.append(Order(good_flavor, good_mold, good_deco))

        bad_flavor = self._pick_from_or_random(
            self.data.get_disliked_flavors(), Order.randomFlavor, Flavor)
        bad_mold = self._pick_from_or_random(
            self.data.get_disliked_molds(), Order.randomMold, Mold)
        bad_deco = self._pick_from_or_random(
            self.data.get_disliked_decorations(), Order.randomDecoration,
            DecorationOption)
        options.append(Order(bad_flavor, bad_mold, bad_deco))

        for _ in range(3):
            options.append(Order(
                Order.randomFlavor(),
                Order.randomMold(),
                Order.randomDecoration()
            ))

        random.shuffle(options)

        print(f"[NPC] {self.name} generated 5 cake options")
        for i, opt in enumerate(options):
            print(f"  [{i}] {opt.flavor} + {opt.mold} + {opt.decoration}")

        return options

    @staticmethod
    def _pick_from_or_random(pool: list[str], random_fn, enum_class=None):
        if pool:
            picked_str = random.choice(pool)
            if enum_class:
                try:
                    return enum_class(picked_str)  # lookup by VALUE
                except (KeyError, ValueError):
                    return random_fn()
            return picked_str
        return random_fn()

    # Order

    def set_order(self, order: Order) -> None:
        self.order = order
        print(f"[NPC] {self.name} order set: {order}")

    def generateOrder(self) -> Order:
        self.order = Order(
            flavor=Order.randomFlavor(),
            mold=Order.randomMold(),
            decoration=Order.randomDecoration()
        )
        print(f"[NPC] {self.name} generated random order: {self.order}")
        return self.order

    def getOrder(self) -> Order:
        return self.order

    # Preference Score

    def calculate_preference_score(self, order: Order) -> int:
        score = 0
        flavor_str = order.flavor.value if hasattr(order.flavor, 'value') else str(order.flavor)
        mold_str = order.mold.value if hasattr(order.mold, 'value') else str(order.mold)
        deco_str = order.decoration.value if hasattr(order.decoration, 'value') else str(order.decoration)

        if flavor_str in self.data.get_preferred_flavors():
            score += 1
        elif flavor_str in self.data.get_disliked_flavors():
            score -= 1

        if mold_str in self.data.get_preferred_molds():
            score += 1
        elif mold_str in self.data.get_disliked_molds():
            score -= 1

        if deco_str in self.data.get_preferred_decorations():
            score += 1
        elif deco_str in self.data.get_disliked_decorations():
            score -= 1

        return score

    # Expression

    def showHappy(self) -> None:
        self.expression = "happy"
        print(f"[NPC] {self.name} is HAPPY!")

    def showAngry(self) -> None:
        self.expression = "angry"
        print(f"[NPC] {self.name} is ANGRY!")

    # Payment

    def getMoney(self) -> None:
        print(f"[NPC] {self.name} pays for the order!")

    # Debug

    def __str__(self) -> str:
        return (f"NPC({self.name}, expression={self.expression}, "
                f"affinity={self.affinity})")