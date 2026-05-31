import pygame
from Room.Room import Room
from Character.NPC import NPC
from Character.NPCData import NPCData
from Character.NPCRegistry import NPCRegistry
from Core.DialogueManager import DialogueManager, AdvanceResult
from Core.DialogueTracker import DialogueTracker
from Core.SaveManager import SaveManager
from UI.OrderUI import OrderUI
from UI.DialogueBox import DialogueBox
from UI.CakeSelectionUI import CakeSelectionUI
from UI.Animator import Animator
from UI.ExpressionSet import ExpressionSet
from UI.EmojiPopup import EmojiPopup
from Order.Order import Order
from Order.Cake import Cake, CakeStep
from Enum.CashierState import CashierState
import Constant


class Cashier(Room):

    def __init__(self, npc_registry: NPCRegistry = None,
                 save_manager: SaveManager = None,
                 dialogue_tracker: DialogueTracker = None,
                 audio=None):
        super().__init__("Cashier")

        self.npc_registry: NPCRegistry = npc_registry
        self.save_manager: SaveManager = save_manager
        self.dialogue_tracker: DialogueTracker = dialogue_tracker or DialogueTracker()
        self.audio = audio

        self.npc: NPC = None
        self.order: Order = None
        self.cake: Cake = None
        self.result: bool = False
        self._cake_options: list[Order] = []

        self._state = CashierState.HIDDEN
        self._npc_x: float = -Constant.NPC_WIDTH
        self._npc_target_x: int = Constant.NPC_X

        self.dialogue_manager = DialogueManager()
        self.dialogue_box = DialogueBox()
        self._current_mood: str = "neutral"
        self._current_variant: str = "a"

        self.cake_selection = CakeSelectionUI()

        self.animator = Animator()
        self._npc_offset: tuple[float, float, float] = (0, 0, 1.0)
        self._emoji_scale: float = 1.0

        self._expression_set = ExpressionSet()
        self._emoji_popup = EmojiPopup()
        self._npc_expression_sprites: dict[str, dict[str, pygame.Surface]] = {}

        self._order_ui = OrderUI()

        self._default_bg = self._load_and_scale(Constant.CASHIER_BG,
                                                 Constant.SCREEN_WIDTH,
                                                 Constant.SCREEN_HEIGHT)
        self._default_npc = self._load_and_scale(Constant.NPC_IMG,
                                                  Constant.NPC_WIDTH,
                                                  Constant.NPC_HEIGHT)
        self._heart_img = self._load_and_scale(Constant.HEART_IMG,
                                                Constant.AFFINITY_HEART_SIZE,
                                                Constant.AFFINITY_HEART_SIZE)

        self._current_bg = self._default_bg
        self._current_npc_img = self._default_npc

        self._sprite_cache: dict[str, pygame.Surface] = {}

        self._font: pygame.font.Font | None = None
        self._font_affinity: pygame.font.Font | None = None
        self._text_cache: dict[str, pygame.Surface] = {}

    # ── Helpers ──

    @staticmethod
    def _load_and_scale(path: str, w: int, h: int) -> pygame.Surface | None:
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except Exception:
            print(f"[DEBUG Cashier] Not found, fallback: {path}")
            return None

    def _load_npc_sprite(self, data: NPCData) -> None:
        if data.id in self._sprite_cache:
            self._current_npc_img = self._sprite_cache[data.id]
            return

        sprite_path = data.get_sprite_path()
        npc_img = (self._load_and_scale(sprite_path, Constant.NPC_WIDTH,
                                         Constant.NPC_HEIGHT)
                   if sprite_path else None)

        self._current_npc_img = npc_img if npc_img else self._default_npc
        self._sprite_cache[data.id] = self._current_npc_img

    def _load_npc_expression_sprites(self, data: NPCData) -> None:
        if data.id in self._npc_expression_sprites:
            return  # sudah di-cache, skip

        sprites: dict[str, pygame.Surface] = {}

        # neutral — pakai sprite default
        neutral_img = self._load_and_scale(
            data.assets.get("sprite", ""),
            Constant.NPC_WIDTH, Constant.NPC_HEIGHT
        )
        if neutral_img:
            sprites["neutral"] = neutral_img

        # happy — sprite saat expression = "happy"
        happy_img = self._load_and_scale(
            data.assets.get("sprite_happy", ""),
            Constant.NPC_WIDTH, Constant.NPC_HEIGHT
        )
        if happy_img:
            sprites["happy"] = happy_img

        # angry — sprite saat expression = "angry"
        angry_img = self._load_and_scale(
            data.assets.get("sprite_angry", ""),
            Constant.NPC_WIDTH, Constant.NPC_HEIGHT
        )
        if angry_img:
            sprites["angry"] = angry_img

        self._npc_expression_sprites[data.id] = sprites
        loaded = list(sprites.keys())
        print(f"[Cashier] Expression sprites '{data.id}': {loaded}")

    def _get_expression_sprite(self) -> pygame.Surface | None:
        if not self.npc:
            return self._default_npc

        npc_id = self.npc.data.id
        expression = self.npc.expression  # "neutral" / "happy" / "angry"
        sprites = self._npc_expression_sprites.get(npc_id, {})

        return (sprites.get(expression)
                or sprites.get("neutral")
                or self._current_npc_img
                or self._default_npc)

    def _get_cached_text(self, text: str, color: tuple) -> pygame.Surface:
        key = f"{text}_{color}"
        if key not in self._text_cache:
            self._text_cache[key] = self._font.render(text, True, color)
        return self._text_cache[key]

    def _clear_text_cache(self) -> None:
        self._text_cache.clear()

    # ── Autosave ──

    def _auto_save(self) -> None:
        if self.save_manager and self.npc_registry:
            affinity = self.npc_registry.get_all_affinity()
            self.save_manager.save_affinity(affinity)
            tracker_data = self.dialogue_tracker.get_save_data()
            self.save_manager.save_dialogue_tracker(tracker_data)

    # ── Lifecycle ──

    def enter(self) -> None:
        print("[DEBUG Cashier] Entering room")
        self._font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_BODY_SIZE)
        self._font_affinity = pygame.font.SysFont(Constant.FONT_NAME,
                                                    Constant.AFFINITY_FONT_SIZE,
                                                    bold=True)

        if self._scene_manager and self._scene_manager.consume_timer_expired():
            print("[DEBUG Cashier] Timer expired entry!")
            return

        if self._state == CashierState.ORDER_ACTIVE:
            self._order_ui.show_order_details()
            return

        if self._state in (CashierState.REACTING, CashierState.DIALOGUE,
                            CashierState.CAKE_SELECT):
            if self._state == CashierState.DIALOGUE:
                self.dialogue_box.show()
            elif self._state == CashierState.CAKE_SELECT:
                self.cake_selection.show()
            return

        if self._state == CashierState.HIDDEN:
            self.showNPC()

    def exit(self) -> None:
        print("[DEBUG Cashier] Exiting room")

    # ── Spawn ──

    def showNPC(self) -> None:
        if self.npc_registry:
            npc_data = self.npc_registry.random()
            self.npc = NPC(npc_data, self.npc_registry)
        else:
            print("[WARN Cashier] No NPCRegistry! Using fallback NPC")
            fallback_data = NPCData(id="fallback", name="Customer",
                                     personality="Generic customer")
            self.npc = NPC(fallback_data)

        self.order = None

        # Load sprite default (neutral) → untuk fallback
        self._load_npc_sprite(self.npc.data)

        self._load_npc_expression_sprites(self.npc.data)

        self._state = CashierState.SLIDING_IN
        self._npc_x = -Constant.NPC_WIDTH
        self.animator.slide("npc", start_dx=-Constant.NPC_WIDTH - Constant.NPC_X,
                             duration=0.6)

        if self.audio:
            self.audio.play_sfx("order_new")

        self._order_ui.set_npc_info(self.npc.name, self.npc.data.personality)
        self._order_ui.accepted = False
        self._order_ui.set_position(
            Constant.NPC_X + Constant.NPC_WIDTH + Constant.ORDER_UI_OFFSET_X,
            Constant.NPC_Y + Constant.ORDER_UI_OFFSET_Y
        )
        self._order_ui.hide()
        self.dialogue_box.hide()
        self.cake_selection.hide()

        print(f"[DEBUG Cashier] NPC spawned: {self.npc.name} "
              f"(affinity: {self.npc.affinity}, level: {self.npc.get_affinity_level()})")

    # ── Order ──

    def acceptOrder(self) -> None:
        print(f"[DEBUG Cashier] Order accepted for {self.npc.name}")
        self._state = CashierState.DIALOGUE

        npc_id = self.npc.data.id
        level = self.npc.get_affinity_level()
        available_moods = self.npc.data.get_moods_for_level(level)

        self._current_mood, self._current_variant = \
            self.dialogue_tracker.resolve_next(
                npc_id, level, available_moods,
                lambda mood: self.npc.data.get_variants_for_level_mood(level, mood)
            )

        self.dialogue_tracker.set_mood(npc_id, self._current_mood)

        entries = self.npc.get_dialogue(self._current_mood, self._current_variant)

        print(f"[DEBUG Cashier] Dialogue: level_{level}, "
              f"mood={self._current_mood}, variant={self._current_variant} "
              f"({len(entries)} entries)")

        if entries:
            self.dialogue_manager.start(entries)
            self._show_current_dialogue()
        else:
            print("[DEBUG Cashier] No dialogue entries, skip to CAKE_SELECT")
            self._start_cake_select()

    def _show_current_dialogue(self) -> None:
        entry = self.dialogue_manager.get_current()
        if not entry:
            return

        self.dialogue_box.set_name(self.npc.name)
        self.dialogue_box.set_text(entry.get("text", ""))
        self.dialogue_box.set_choices(entry.get("choices", []))
        self.dialogue_box.show()

    def _on_dialogue_advance(self, choice_result: int) -> None:
        if choice_result == -1:
            return

        npc_id = self.npc.data.id

        # Simpan set_next dari choice sebelum advance
        if choice_result >= 0:
            choices = self.dialogue_manager.get_current_choices()
            if choice_result < len(choices):
                set_next = choices[choice_result].get("set_next")
                if set_next:
                    self.dialogue_tracker.set_next(npc_id, set_next)

        advance_result = self.dialogue_manager.advance(choice_result)
        self._apply_dialogue_result(advance_result)

        if self.dialogue_manager.is_finished():
            print("[DEBUG Cashier] Dialogue finished")
            self.dialogue_box.hide()
            self._start_cake_select()
        else:
            self._show_current_dialogue()

    def _apply_dialogue_result(self, result: AdvanceResult) -> None:
        if result.affinity_delta != 0 and self.npc:
            self.npc.change_affinity(result.affinity_delta)
            print(f"[DEBUG Cashier] Dialogue affinity: "
                  f"{'+' if result.affinity_delta >= 0 else ''}{result.affinity_delta}, "
                  f"total: {self.npc.affinity}")
            self._auto_save()

        if result.expression:
            self._apply_npc_expression(result.expression)

        if result.emoji:
            self._show_emoji_popup(result.emoji)

    def _apply_npc_expression(self, expression: str) -> None:
        if expression == "happy":
            self.npc.showHappy()          # set self.npc.expression = "happy"
            self.animator.bounce("npc")
            if self.audio:
                self.audio.play_sfx("affinity_up")
        elif expression == "angry":
            self.npc.showAngry()          # set self.npc.expression = "angry"
            self.animator.shake("npc")
        else:
            self.npc.expression = "neutral"

        print(f"[DEBUG Cashier] NPC expression → '{expression}' "
              f"(sprite akan ganti di render)")

    # ── Cake Select ──

    def _start_cake_select(self) -> None:
        self._state = CashierState.CAKE_SELECT
        self._cake_options = self.npc.generate_cake_options()
        self.cake_selection.set_options(self._cake_options,
                                         callback=self._on_cake_selected)
        self.cake_selection.show()
        print("[DEBUG Cashier] Cake selection started")

    def _on_cake_selected(self, index: int) -> None:
        if not (0 <= index < len(self._cake_options)):
            return

        selected_order = self._cake_options[index]
        self.npc.set_order(selected_order)
        self.order = selected_order
        self._order_ui.set_order(self.order)
        self.cake_selection.hide()

        score = self.npc.calculate_preference_score(selected_order)
        print(f"[DEBUG Cashier] Player chose cake {index}: "
              f"{selected_order.flavor} + {selected_order.mold} + "
              f"{selected_order.decoration} (pref score: {score})")

        self._start_order_active()

    # ── Order Active ──

    def _start_order_active(self) -> None:
        self._state = CashierState.ORDER_ACTIVE
        self._order_ui.show_order_details()

        if self.cake:
            self.cake.reset()

        if self._scene_manager:
            self._scene_manager.start_timer(Constant.TIMER_DURATION)

        print("[DEBUG Cashier] Timer started, order active")

    def check_cake(self) -> None:
        if not self.cake:
            print("[WARN Cashier] No Cake!")
            return

        if self.cake.is_complete():
            self.onCheckOrder(self.cake)
        else:
            print(f"[WARN Cashier] Cake belum selesai! step={self.cake.step}")

    def onCheckOrder(self, cake: Cake) -> None:
        if not self.order or not cake:
            return

        correct_cake = cake.matches_order(self.order)

        if self._scene_manager:
            self._scene_manager.stop_timer()

        self._order_ui.hide()

        if correct_cake:
            pref_score = self.npc.calculate_preference_score(self.order)
            affinity_delta = Constant.REWARD_CORRECT_CAKE + pref_score

            if pref_score >= Constant.PREF_SCORE_GOOD:
                self.npc.showHappy()
                self._show_emoji_popup("happy")
                self.animator.bounce("npc")
                if self.audio:
                    self.audio.play_sfx("order_correct")
            else:
                self.npc.expression = "neutral"
                self._show_emoji_popup("angry")
                self.animator.shake("npc")
                if self.audio:
                    self.audio.play_sfx("order_wrong")

            print(f"[DEBUG Cashier] Correct cake! pref={pref_score}, delta={affinity_delta}")
        else:
            affinity_delta = Constant.PENALTY_WRONG_CAKE
            self.npc.showAngry()
            self._show_emoji_popup("angry")
            self.animator.shake("npc")
            if self.audio:
                self.audio.play_sfx("order_wrong")
            print(f"[DEBUG Cashier] Wrong cake! delta={affinity_delta}")

        self.result = correct_cake
        self.npc.change_affinity(affinity_delta)
        self._state = CashierState.REACTING
        self._auto_save()

        print(f"[DEBUG Cashier] Result: {correct_cake}, "
              f"affinity delta: {affinity_delta}, total: {self.npc.affinity}")

    # ── Timer ──

    def on_timer_expired(self) -> None:
        print("[DEBUG Cashier] Timer expired!")
        self._npc_x = self._npc_target_x
        self._state = CashierState.REACTING
        self._order_ui.hide()
        self.dialogue_box.hide()
        self.cake_selection.hide()

        self.npc.change_affinity(Constant.PENALTY_TIMER_EXPIRED)
        self.npc.showAngry()
        self._show_emoji_popup("angry")
        self.animator.shake("npc")
        self._auto_save()

    # ── Emoji Popup ──

    def _show_emoji_popup(self, expression: str) -> None:
        surface = self._expression_set.get_surface(expression)   # global emoji
        fallback_text, fallback_color = self._expression_set.get_fallback(expression)
        center_x = int(self._npc_x) + Constant.NPC_WIDTH // 2

        self._emoji_popup.show(surface, fallback_text, fallback_color,
                               center_x, Constant.NPC_Y)
        self.animator.pop_in("emoji_popup")

        if self.audio:
            self.audio.play_sfx("emoji_popup")

        print(f"[DEBUG Cashier] Emoji popup: {expression} (global)")

    # ── Update ──

    def update(self, delta_time: float = 0.0) -> None:
        offsets = self.animator.update(delta_time)
        self._npc_offset = offsets.get("npc", (0, 0, 1.0))
        self._emoji_scale = offsets.get("emoji_popup", (0, 0, 1.0))[2]

        if self._state == CashierState.SLIDING_IN:
            dx, _, _ = self._npc_offset
            self._npc_x = Constant.NPC_X + dx
            if not self.animator.is_active("npc"):
                self._npc_x = self._npc_target_x
                self._state = CashierState.WAITING
                self._order_ui.show_npc_info()
                print("[DEBUG Cashier] NPC slide-in complete")

        self._emoji_popup.update(delta_time)

        if self._state == CashierState.DIALOGUE:
            self.dialogue_box.update(delta_time, self.audio)

        if self._state == CashierState.ORDER_ACTIVE and self._scene_manager:
            remaining = self._scene_manager.get_timer_remaining()
            self._order_ui.set_timer_text(f"Time: {max(0, int(remaining))}s")

    # ── Render ──

    def render(self) -> None:
        if not self.screen:
            return

        self._render_background()
        self._render_npc()
        self._order_ui.render(self.screen)
        self._emoji_popup.render(self.screen, self._emoji_scale)
        self._render_affinity()

        if self._state == CashierState.DIALOGUE:
            self.dialogue_box.render(self.screen)

        if self._state == CashierState.CAKE_SELECT:
            self.cake_selection.render(self.screen)

        if self._state == CashierState.REACTING and self._emoji_popup.is_done():
            hint = self._get_cached_text("Click to continue...",
                                          Constant.COLOR_DARK_BROWN)
            self.screen.blit(hint,
                (Constant.NPC_X,
                 Constant.NPC_Y + Constant.NPC_HEIGHT + Constant.HINT_CLICK_OFFSET_Y))

    def _render_background(self) -> None:
        if self._current_bg:
            self.screen.blit(self._current_bg, (0, 0))
        else:
            content = pygame.Rect(0, Constant.NAV_BAR_HEIGHT,
                                  Constant.SCREEN_WIDTH,
                                  Constant.SCREEN_HEIGHT - Constant.NAV_BAR_HEIGHT)
            pygame.draw.rect(self.screen, Constant.COLOR_CASHIER_FALLBACK_BG, content)

    def _render_npc(self) -> None:
        if not self.npc or self._state == CashierState.HIDDEN:
            return

        dx, dy, scale = self._npc_offset
        npc_x = int(self._npc_x + dx)
        npc_y = int(Constant.NPC_Y + dy)

        npc_sprite = self._get_expression_sprite()

        if npc_sprite:
            if scale != 1.0:
                w = max(1, int(Constant.NPC_WIDTH * scale))
                h = max(1, int(Constant.NPC_HEIGHT * scale))
                scaled_img = pygame.transform.scale(npc_sprite, (w, h))
                offset_x = (Constant.NPC_WIDTH - w) // 2
                offset_y = (Constant.NPC_HEIGHT - h) // 2
                self.screen.blit(scaled_img, (npc_x + offset_x, npc_y + offset_y))
            else:
                self.screen.blit(npc_sprite, (npc_x, npc_y))
        else:
            # Fallback kotak warna jika semua gambar tidak ada
            npc_rect = pygame.Rect(npc_x, npc_y, Constant.NPC_WIDTH, Constant.NPC_HEIGHT)
            shadow = npc_rect.move(Constant.SHADOW_OFFSET, Constant.SHADOW_OFFSET)
            pygame.draw.rect(self.screen, (0, 0, 0), shadow, border_radius=12)

            color = self._get_npc_color()
            pygame.draw.rect(self.screen, color, npc_rect, border_radius=12)
            pygame.draw.rect(self.screen, Constant.COLOR_DARK_BROWN,
                             npc_rect, 2, border_radius=12)

            name_surf = self._get_cached_text(self.npc.name, Constant.COLOR_WHITE)
            self.screen.blit(name_surf,
                name_surf.get_rect(centerx=npc_rect.centerx, y=npc_y + 10))

            expr_surf = self._get_cached_text(
                f"[{self.npc.expression}]", Constant.COLOR_WHITE)
            self.screen.blit(expr_surf,
                expr_surf.get_rect(centerx=npc_rect.centerx, y=npc_y + 50))

    def _render_affinity(self) -> None:
        if not self.npc or self._state == CashierState.HIDDEN:
            return

        bar_x = int(self._npc_x) + Constant.AFFINITY_BAR_OFFSET_X
        bar_y = Constant.NPC_Y - Constant.AFFINITY_HEART_SIZE - Constant.AFFINITY_BAR_OFFSET_Y

        heart_size = Constant.AFFINITY_HEART_SIZE
        padding = Constant.AFFINITY_PANEL_PADDING

        affinity_surf = None
        if self._font_affinity:
            affinity_surf = self._font_affinity.render(
                str(self.npc.affinity), True, Constant.COLOR_DARK_BROWN)

        text_w = affinity_surf.get_width() if affinity_surf else 30
        panel_w = heart_size + Constant.AFFINITY_TEXT_GAP + text_w + padding * 2
        panel_h = heart_size + padding * 2

        panel_rect = pygame.Rect(bar_x - padding, bar_y - padding, panel_w, panel_h)
        shadow_rect = panel_rect.move(Constant.AFFINITY_SHADOW_OFFSET,
                                       Constant.AFFINITY_SHADOW_OFFSET)
        pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, border_radius=8)
        pygame.draw.rect(self.screen, Constant.COLOR_BG_CREAM, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, Constant.COLOR_WARM_BROWN, panel_rect, 2,
                          border_radius=8)

        if self._heart_img:
            self.screen.blit(self._heart_img, (bar_x, bar_y))
        else:
            heart_rect = pygame.Rect(bar_x + Constant.AFFINITY_SHADOW_OFFSET,
                                      bar_y + Constant.AFFINITY_SHADOW_OFFSET,
                                      heart_size - Constant.SHADOW_OFFSET,
                                      heart_size - Constant.SHADOW_OFFSET)
            pygame.draw.circle(self.screen, Constant.COLOR_HEART_RED,
                               heart_rect.center, heart_size // 2 - Constant.AFFINITY_SHADOW_OFFSET)

        if affinity_surf:
            self.screen.blit(affinity_surf,
                             (bar_x + heart_size + Constant.AFFINITY_TEXT_GAP,
                              bar_y + (heart_size - affinity_surf.get_height()) // 2))

    # ── Events ──

    def handle_event(self, event) -> None:
        if self._state == CashierState.CAKE_SELECT:
            self.cake_selection.handle_event(event)
            return

        if self._state == CashierState.DIALOGUE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                result = self.dialogue_box.handle_event(event)
                if result != -1:
                    self._on_dialogue_advance(result)
            return

        if self._state == CashierState.WAITING:
            if self._order_ui.handle_event(event):
                self.acceptOrder()
            return

        if (self._state == CashierState.REACTING
                and self._emoji_popup.is_done()
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1):
            print("[DEBUG Cashier] New round!")
            self._reset_for_new_round()

    # ── Internal ──

    def _get_npc_color(self) -> tuple:
        if not self.npc:
            return Constant.COLOR_WARM_BROWN
        if self.npc.expression == "happy":
            return Constant.COLOR_NPC_HAPPY
        if self.npc.expression == "angry":
            return Constant.COLOR_NPC_ANGRY
        return Constant.COLOR_WARM_BROWN

    def _reset_for_new_round(self) -> None:
        self.npc = None
        self.order = None
        self.cake = None
        self.result = False
        self._cake_options = []
        self._state = CashierState.HIDDEN
        self._npc_x = -Constant.NPC_WIDTH
        self._current_mood = "neutral"
        self._current_variant = "a"

        self._order_ui.hide()
        self._order_ui.accepted = False
        self._order_ui.set_timer_text("")
        self.dialogue_box.hide()
        self.dialogue_manager.reset()
        self.cake_selection.reset()
        self._emoji_popup.hide()
        self._clear_text_cache()

        self.animator.stop_all()
        self._npc_offset = (0, 0, 1.0)
        self._emoji_scale = 1.0

        self._current_bg = self._default_bg
        self._current_npc_img = self._default_npc

        self.showNPC()