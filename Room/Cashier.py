import pygame
import Constant
from Room.Room import Room
from Character.NPC import NPC
from Order.Order import Order
from UI.OrderUI import OrderUI

_NPC_HIDDEN = 0
_NPC_SLIDING_IN = 1
_NPC_WAITING = 2
_NPC_ORDER_ACTIVE = 3
_NPC_REACTING = 4


class Cashier(Room):

    def __init__(self):
        super().__init__("Cashier")

        self.npc: NPC = None
        self.order: Order = None
        self.cake = None
        self.result: bool = False

        self._state = _NPC_HIDDEN
        self._npc_x: float = -Constant.NPC_WIDTH
        self._npc_target_x: int = Constant.NPC_X

        self._emoji_type: str = ""
        self._emoji_y: float = 0.0
        self._emoji_target_y: float = 0.0
        self._emoji_start_y: float = 0.0
        self._emoji_active: bool = False
        self._emoji_done: bool = False

        self._order_ui = OrderUI()

        self._bg_img = self._load_and_scale(Constant.CASHIER_BG,
                                             Constant.SCREEN_WIDTH,
                                             Constant.SCREEN_HEIGHT)
        self._npc_scaled = self._load_and_scale(Constant.NPC_IMG,
                                                 Constant.NPC_WIDTH,
                                                 Constant.NPC_HEIGHT)
        self._emoji_happy_scaled = self._load_and_scale(Constant.NPC_EMOJI_HAPPY,
                                                         Constant.EMOJI_WIDTH,
                                                         Constant.EMOJI_HEIGHT)
        self._emoji_angry_scaled = self._load_and_scale(Constant.NPC_EMOJI_ANGRY,
                                                         Constant.EMOJI_WIDTH,
                                                         Constant.EMOJI_HEIGHT)

        self._use_npc_fallback = (self._npc_scaled is None)
        self._use_bg_fallback = (self._bg_img is None)

        self._font = None

        self._text_cache: dict[str, pygame.Surface] = {}

    @staticmethod
    def _load_and_scale(path: str, w: int, h: int):
        try:
            img = pygame.image.load(path).convert_alpha()
            scaled = pygame.transform.scale(img, (w, h))
            print(f"[DEBUG Cashier] Loaded & cached: {path}")
            return scaled
        except Exception:
            print(f"[DEBUG Cashier] Image not found, fallback: {path}")
            return None

    def _get_cached_text(self, text: str, color: tuple) -> pygame.Surface:
        key = f"{text}_{color}"
        if key not in self._text_cache:
            self._text_cache[key] = self._font.render(text, True, color)
        return self._text_cache[key]

    def _clear_text_cache(self) -> None:
        self._text_cache.clear()


    def enter(self) -> None:
        print("[DEBUG Cashier] Entering room")
        self._font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_BODY_SIZE)

        if (self._scene_manager and self._scene_manager.consume_timer_expired()):
            print("[DEBUG Cashier] Timer expired entry!")
            return

        if self._state == _NPC_ORDER_ACTIVE:
            print("[DEBUG Cashier] Resuming — order active")
            self._order_ui.show()
            return

        if self._state == _NPC_REACTING:
            print("[DEBUG Cashier] Resuming — reacting")
            return

        if self._state == _NPC_HIDDEN:
            self.showNPC()

    def exit(self) -> None:
        print("[DEBUG Cashier] Exiting room")

    def showNPC(self) -> None:
        self.npc = NPC("Customer")
        self.npc.generateOrder()
        self.order = self.npc.getOrder()

        self._state = _NPC_SLIDING_IN
        self._npc_x = -Constant.NPC_WIDTH

        self._order_ui.set_order(self.order)
        self._order_ui.accepted = False
        self._order_ui.set_position(
            Constant.NPC_X + Constant.NPC_WIDTH + Constant.ORDER_UI_OFFSET_X,
            Constant.NPC_Y + Constant.ORDER_UI_OFFSET_Y
        )
        self._order_ui.hide()

        print(f"[DEBUG Cashier] NPC spawned, sliding in")

    def acceptOrder(self, o: Order) -> Order:
        self._state = _NPC_ORDER_ACTIVE
        print(f"[DEBUG Cashier] Order accepted: {o}")

        if self._scene_manager:
            self._scene_manager.start_timer(Constant.TIMER_DURATION)

        return o

    def onCheckOrder(self, cake) -> None:
        if not self.order or not cake:
            return

        self.cake = cake
        self.result = (
            cake.flavor == self.order.flavor
            and cake.mold == self.order.mold
            and cake.decoration == self.order.decoration
        )

        if self._scene_manager:
            self._scene_manager.stop_timer()

        self._order_ui.hide()

        if self.result:
            self.npc.showHappy(self.result)
            self._start_emoji_popup("happy")
        else:
            self.npc.showAngry(self.result)
            self._start_emoji_popup("angry")

        self._state = _NPC_REACTING
        print(f"[DEBUG Cashier] Check result: {self.result}")

    def getResult(self) -> bool:
        return self.result

    def on_timer_expired(self) -> None:
        print("[DEBUG Cashier] Timer expired!")

        self._npc_x = self._npc_target_x
        self._state = _NPC_REACTING

        self._order_ui.hide()

        self.npc.showAngry(False)
        self._start_emoji_popup("angry")

    def _start_emoji_popup(self, emoji_type: str) -> None:
        self._emoji_type = emoji_type
        self._emoji_active = True
        self._emoji_done = False

        self._emoji_target_y = Constant.NPC_Y - Constant.EMOJI_HEIGHT - 10
        self._emoji_start_y = Constant.NPC_Y + 20
        self._emoji_y = self._emoji_start_y

        print(f"[DEBUG Cashier] Emoji popup started: {emoji_type}")

    def update(self) -> None:
        if self._state == _NPC_SLIDING_IN:
            self._npc_x += Constant.NPC_SLIDE_SPEED
            if self._npc_x >= self._npc_target_x:
                self._npc_x = self._npc_target_x
                self._state = _NPC_WAITING
                self._order_ui.show()
                print("[DEBUG Cashier] NPC slide-in complete")

        if self._emoji_active and not self._emoji_done:
            self._emoji_y -= Constant.EMOJI_POPUP_SPEED
            if self._emoji_y <= self._emoji_target_y:
                self._emoji_y = self._emoji_target_y
                self._emoji_done = True
                print("[DEBUG Cashier] Emoji popup complete")

        if (self._state == _NPC_ORDER_ACTIVE
                and self._scene_manager):
            remaining = self._scene_manager.get_timer_remaining()
            secs = max(0, int(remaining))
            self._order_ui.set_timer_text(f"Time: {secs}s")

    def render(self) -> None:
        if not self.screen:
            return

        self._render_background()
        self._render_npc()
        self._order_ui.render(self.screen)
        self._render_emoji()

        if self._state == _NPC_REACTING and self._emoji_done:
            hint = self._get_cached_text("Click to continue...", Constant.COLOR_DARK_BROWN)
            self.screen.blit(hint,(Constant.NPC_X, Constant.NPC_Y + Constant.NPC_HEIGHT + 20))

    def handle_event(self, event) -> None:
        if self._order_ui.handle_event(event):
            self.acceptOrder(self.order)
            return

        if (self._state == _NPC_REACTING
                and self._emoji_done
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1):
            print("[DEBUG Cashier] New round!")
            self._reset_for_new_round()

    def _render_background(self) -> None:
        if self._bg_img:
            self.screen.blit(self._bg_img, (0, 0))
        else:
            content = pygame.Rect(0, Constant.NAV_BAR_HEIGHT,
                                  Constant.SCREEN_WIDTH,
                                  Constant.SCREEN_HEIGHT - Constant.NAV_BAR_HEIGHT)
            pygame.draw.rect(self.screen, (255, 235, 210), content)

    def _render_npc(self) -> None:
        if not self.npc or self._state == _NPC_HIDDEN:
            return

        npc_x = int(self._npc_x)
        npc_y = Constant.NPC_Y

        if not self._use_npc_fallback:
            self.screen.blit(self._npc_scaled, (npc_x, npc_y))
        else:
            npc_rect = pygame.Rect(npc_x, npc_y,
                                    Constant.NPC_WIDTH, Constant.NPC_HEIGHT)

            shadow = npc_rect.move(4, 4)
            pygame.draw.rect(self.screen, (0, 0, 0), shadow, border_radius=12)

            color = self._get_npc_color()
            pygame.draw.rect(self.screen, color, npc_rect, border_radius=12)
            pygame.draw.rect(self.screen, Constant.COLOR_DARK_BROWN, npc_rect, 2, border_radius=12)

            name_surf = self._get_cached_text(self.npc.name, Constant.COLOR_WHITE)
            self.screen.blit(name_surf,
                name_surf.get_rect(centerx=npc_rect.centerx, y=npc_y + 10))

            expr_surf = self._get_cached_text(f"[{self.npc.expression}]", Constant.COLOR_WHITE)
            self.screen.blit(expr_surf,
                expr_surf.get_rect(centerx=npc_rect.centerx, y=npc_y + 50))

    def _render_emoji(self) -> None:
        if not self._emoji_active:
            return

        emoji_x = int(self._npc_x) + (Constant.NPC_WIDTH - Constant.EMOJI_WIDTH) // 2
        emoji_y = int(self._emoji_y)

        if self._emoji_type == "happy" and self._emoji_happy_scaled:
            self.screen.blit(self._emoji_happy_scaled, (emoji_x, emoji_y))
        elif self._emoji_type == "angry" and self._emoji_angry_scaled:
            self.screen.blit(self._emoji_angry_scaled, (emoji_x, emoji_y))
        else:
            if self._emoji_type == "happy":
                txt = "HAPPY"
                color = (0, 180, 0)
            else:
                txt = "ANGRY"
                color = (220, 50, 50)

            emoji_rect = pygame.Rect(emoji_x, emoji_y,
                                      Constant.EMOJI_WIDTH, Constant.EMOJI_HEIGHT)
            pygame.draw.rect(self.screen, color, emoji_rect, border_radius=50)
            surf = self._get_cached_text(txt, Constant.COLOR_WHITE)
            self.screen.blit(surf, surf.get_rect(center=emoji_rect.center))

    def _get_npc_color(self) -> tuple:
        if not self.npc:
            return Constant.COLOR_WARM_BROWN
        if self.npc.expression == "happy":
            return (100, 200, 100)
        if self.npc.expression == "angry":
            return (220, 80, 80)
        return Constant.COLOR_WARM_BROWN

    def _reset_for_new_round(self) -> None:
        self.npc = None
        self.order = None
        self.cake = None
        self.result = False
        self._state = _NPC_HIDDEN
        self._npc_x = -Constant.NPC_WIDTH
        self._emoji_active = False
        self._emoji_done = False
        self._emoji_type = ""
        self._order_ui.hide()
        self._order_ui.accepted = False
        self._order_ui.set_timer_text("")
        self._clear_text_cache()

        self.showNPC()