from Order.Order import Order


class NPC:

    def __init__(self, name: str = "Customer"):
        self.name: str = name
        self.expression: str = "neutral"  
        self.order: Order = None

    def generateOrder(self) -> Order:
        self.order = Order(
            flavor=Order.randomFlavor(),
            mold=Order.randomMold(),
            decoration=Order.randomDecoration()
        )
        print(f"[NPC] {self.name} generated order: {self.order}")
        return self.order

    def showHappy(self, result: bool) -> None:
        if result:
            self.expression = "happy"
            print(f"[NPC] {self.name} is HAPPY!")

    def showAngry(self, result: bool) -> None:
        if not result:
            self.expression = "angry"
            print(f"[NPC] {self.name} is ANGRY!")

    def getOrder(self) -> Order:
        return self.order

    def getMoney(self) -> None:
        print(f"[NPC] {self.name} pays for the order!")