from __future__ import annotations
import pygame

from Room.Room import Room
from Room.Minigame.KeepHappyMinigame import KeepHappyMinigame

from Character.NPC import NPC
from Character.NPCData import NPCData
from Character.NPCRegistry import NPCRegistry
from Core.DialogueManager import DialogueManager, AdvanceResult
from Core.DialogueTracker import DialogueTracker
from Core.EventTracker import EventTracker
from Core.SaveManager import SaveManager

from UI.OrderUI import OrderUI
from UI.DialogueBox import DialogueBox
from UI.CakeSelectionUI import CakeSelectionUI
from UI.Animator import Animator
from UI.ExpressionSet import ExpressionSet
from UI.EmojiPopup import EmojiPopup
from UI.CashierRenderer import CashierRenderer, CashierRenderContext

from Order.Order import Order
from Order.Cake import Cake
from Enum.CashierState import CashierState
import Constant


class Cashier(Room):

    def __init__(
        self,
        npc_registry: NPCRegistry   = None,
        save_manager: SaveManager   = None,
        dialogue_tracker: DialogueTracker = None,
        audio=None,
    ) -> None:
        super().__init__("Cashier")

        self.npc_registry     = npc_registry
        self.save_manager     = save_manager
        self.dialogue_tracker = dialogue_tracker or DialogueTracker()
        self.audio            = audio

        # Date event
        self._date_event_tracker: EventTracker | None = None
        self._date_cutscene       = None

        # State
        self.npc: NPC | None       = None
        self.order: Order | None   = None
        self.cake: Cake | None     = None
        self.result: bool          = False
        self._cake_options: list[Order] = []

        self._state           = CashierState.HIDDEN
        self._npc_x: float    = -Constant.NPC_WIDTH
        self._npc_target_x    = Constant.NPC_X
        self._current_mood    = "neutral"
        self._current_variant = "a"

        self.dialogue_manager  = DialogueManager()
        self.dialogue_box      = DialogueBox()
        self.cake_selection    = CakeSelectionUI()
        self._order_ui         = OrderUI()
        self._expression_set   = ExpressionSet()
        self._emoji_popup      = EmojiPopup()
        self.animator          = Animator()

        self._minigame  = KeepHappyMinigame()
        self._renderer  = CashierRenderer()
        self._render_ctx = CashierRenderContext()

        self._timer_on_exit: float = 0.0

        # Anim
        self._npc_offset: tuple[float, float, float] = (0, 0, 1.0)
        self._emoji_scale: float = 1.0

        # Assets
        self._default_bg  = self._load_and_scale(
            Constant.CASHIER_BG, Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT)
        self._default_npc = self._load_and_scale(
            Constant.NPC_IMG, Constant.NPC_WIDTH, Constant.NPC_HEIGHT)
        self._heart_img   = self._load_and_scale(
            Constant.HEART_IMG, Constant.AFFINITY_HEART_SIZE, Constant.AFFINITY_HEART_SIZE)

        self._current_bg      = self._default_bg
        self._current_npc_img = self._default_npc

        # Sprite cache per NPC
        self._sprite_cache: dict[str, pygame.Surface]             = {}
        self._npc_expression_sprites: dict[str, dict[str, pygame.Surface]] = {}

    @staticmethod
    def _load_and_scale(path: str, w: int, h: int) -> pygame.Surface | None:
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except Exception:
            print(f"[Cashier] Asset not found: {path}")
            return None

    def _load_npc_sprite(self, data: NPCData) -> None:
        if data.id in self._sprite_cache:
            self._current_npc_img = self._sprite_cache[data.id]
            return
        path = data.get_sprite_path()
        img  = self._load_and_scale(path, Constant.NPC_WIDTH, Constant.NPC_HEIGHT) if path else None
        self._current_npc_img         = img or self._default_npc
        self._sprite_cache[data.id]   = self._current_npc_img

    def _load_npc_expression_sprites(self, data: NPCData) -> None:
        if data.id in self._npc_expression_sprites:
            return
        sprites: dict[str, pygame.Surface] = {}
        default = self._load_and_scale(data.get_sprite_path(),
                                        Constant.NPC_WIDTH, Constant.NPC_HEIGHT)
        if default:
            sprites["neutral"] = default
        for expr in data.get_all_expression_names():
            path = data.get_expression_sprite_path(expr)
            if path:
                img = self._load_and_scale(path, Constant.NPC_WIDTH, Constant.NPC_HEIGHT)
                if img:
                    sprites[expr] = img
        self._npc_expression_sprites[data.id] = sprites

    def _get_expression_sprite(self) -> pygame.Surface | None:
        if not self.npc:
            return self._default_npc
        sprites = self._npc_expression_sprites.get(self.npc.data.id, {})
        return (sprites.get(self.npc.expression)
                or sprites.get("neutral")
                or self._current_npc_img
                or self._default_npc)

    def enter(self) -> None:
        self._renderer.init_fonts()

        if self._scene_manager and self._scene_manager.consume_timer_expired():
            self.on_timer_expired()
            return

        if self._state == CashierState.ORDER_ACTIVE:
            self._order_ui.show_order_details()
            elapsed = 0.0
            if self._timer_on_exit > 0 and self._scene_manager:
                elapsed = self._timer_on_exit - self._scene_manager.get_timer_remaining()
                self._timer_on_exit = 0.0
            self._minigame.resume(elapsed)
            return

        if self._state in (CashierState.REACTING,
                            CashierState.DIALOGUE,
                            CashierState.CAKE_SELECT):
            if self._state == CashierState.DIALOGUE:
                self.dialogue_box.show()
            elif self._state == CashierState.CAKE_SELECT:
                self.cake_selection.show()
            return

        if self._state == CashierState.HIDDEN:
            if self._check_date_event():
                return
            self._spawn_npc()
            self._debug_ending_status()
            self._check_and_trigger_ending()

    def exit(self) -> None:
        if self._state == CashierState.ORDER_ACTIVE and self._scene_manager:
            self._timer_on_exit = self._scene_manager.get_timer_remaining()

    def _spawn_npc(self) -> None:
        if self.npc_registry:
            npc_data = self.npc_registry.random()
            self.npc = NPC(npc_data, self.npc_registry)
        else:
            fallback = NPCData(id="fallback", name="Customer", personality="Generic customer")
            self.npc = NPC(fallback)

        self.order = None
        self._load_npc_sprite(self.npc.data)
        self._load_npc_expression_sprites(self.npc.data)

        self._state = CashierState.SLIDING_IN
        self._npc_x = -Constant.NPC_WIDTH
        self.animator.slide("npc",
                             start_dx=-Constant.NPC_WIDTH - Constant.NPC_X,
                             duration=0.6)

        if self.audio:
            self.audio.play_sfx("order_new")

        self._order_ui.set_npc_info(self.npc.name, self.npc.data.personality)
        self._order_ui.accepted = False
        self._order_ui.set_position(
            Constant.NPC_X + Constant.NPC_WIDTH + Constant.ORDER_UI_OFFSET_X,
            Constant.NPC_Y + Constant.ORDER_UI_OFFSET_Y,
        )
        self._order_ui.hide()
        self.dialogue_box.hide()
        self.cake_selection.hide()

    def showNPC(self) -> None:
        self._spawn_npc()

    def acceptOrder(self) -> None:
        self._state = CashierState.DIALOGUE
        npc_id  = self.npc.data.id
        level   = self.npc.get_affinity_level()
        moods   = self.npc.data.get_moods_for_level(level)

        self._current_mood, self._current_variant = (
            self.dialogue_tracker.resolve_next(
                npc_id, level, moods,
                lambda mood: self.npc.data.get_variants_for_level_mood(level, mood),
            )
        )
        self.dialogue_tracker.set_mood(npc_id, self._current_mood)

        entries = self.npc.get_dialogue(self._current_mood, self._current_variant)
        if entries:
            self.dialogue_manager.start(entries)
            self._show_current_dialogue()
        else:
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
        npc_id  = self.npc.data.id
        choices = self.dialogue_manager.get_current_choices()
        if 0 <= choice_result < len(choices):
            set_next = choices[choice_result].get("set_next")
            if set_next:
                self.dialogue_tracker.set_next(npc_id, set_next)

        result = self.dialogue_manager.advance(choice_result)
        self._apply_dialogue_result(result)

        if self.dialogue_manager.is_finished():
            self.dialogue_box.hide()
            self._start_cake_select()
        else:
            self._show_current_dialogue()

    def _apply_dialogue_result(self, result: AdvanceResult) -> None:
        if result.affinity_delta != 0 and self.npc:
            self.npc.change_affinity(result.affinity_delta)
            self._auto_save()
        if result.expression:
            self._apply_npc_expression(result.expression)
        if result.emoji:
            self._show_emoji_popup(result.emoji)

    def _apply_npc_expression(self, expression: str) -> None:
        self.npc.expression = expression
        anim = self._expression_set.get_animation(expression)
        if anim == "bounce":
            self.animator.bounce("npc")
        elif anim == "shake":
            self.animator.shake("npc")
        elif anim == "fade":
            self.animator.fade("npc")

        sfx = self.npc.data.get_expression_sfx(expression) or self._expression_set.get_sfx(expression)
        if sfx and self.audio:
            self.audio.play_sfx(sfx)


    def _start_cake_select(self) -> None:
        self._state = CashierState.CAKE_SELECT
        self._cake_options = self.npc.generate_cake_options()
        self.cake_selection.set_options(self._cake_options,
                                         callback=self._on_cake_selected)
        self.cake_selection.show()

    def _on_cake_selected(self, index: int) -> None:
        if not (0 <= index < len(self._cake_options)):
            return
        selected = self._cake_options[index]
        self.npc.set_order(selected)
        self.order = selected
        self._order_ui.set_order(self.order)
        self.cake_selection.hide()
        self._start_order_active()

    def _start_order_active(self) -> None:
        self._state = CashierState.ORDER_ACTIVE
        self._order_ui.show_order_details()
        if self.cake:
            self.cake.reset()
        if self._scene_manager:
            self._scene_manager.start_timer(Constant.TIMER_DURATION)
        self._minigame.start()

    def check_cake(self) -> None:
        if not self.cake:
            return
        if self.cake.is_complete():
            self.onCheckOrder(self.cake)

    def onCheckOrder(self, cake: Cake) -> None:
        if not self.order or not cake:
            return

        correct = cake.matches_order(self.order)
        if self._scene_manager:
            self._scene_manager.stop_timer()
        self._order_ui.hide()
        self._minigame.stop()

        if correct:
            pref        = self.npc.calculate_preference_score(self.order)
            delta       = Constant.REWARD_CORRECT_CAKE + pref
            if pref >= Constant.PREF_SCORE_GOOD:
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
        else:
            delta = Constant.PENALTY_WRONG_CAKE
            self.npc.showAngry()
            self._show_emoji_popup("angry")
            self.animator.shake("npc")
            if self.audio:
                self.audio.play_sfx("order_wrong")

        self.result = correct
        self.npc.change_affinity(delta)
        self._state = CashierState.REACTING
        if self.cake:
            self.cake.reset()
        self._auto_save()


    def on_timer_expired(self) -> None:
        self._npc_x  = self._npc_target_x
        self._state  = CashierState.REACTING
        self._order_ui.hide()
        self.dialogue_box.hide()
        self.cake_selection.hide()
        self._minigame.stop()

        self.npc.change_affinity(Constant.PENALTY_TIMER_EXPIRED)
        self.npc.showAngry()
        self._show_emoji_popup("angry")
        self.animator.shake("npc")
        self._auto_save()

    def _check_and_trigger_ending(self) -> bool:
        if not self.npc or not self.npc.data.has_ending():
            return False
        if self.npc.affinity < self.npc.data.get_ending_threshold():
            return False
        self._order_ui.hide()
        self.dialogue_box.hide()
        self.cake_selection.hide()
        self._emoji_popup.hide()
        if self._scene_manager:
            self._scene_manager.start_ending(self.npc.data)
        return True

    def _check_date_event(self) -> bool:
        if (not self.npc_registry
                or not self._scene_manager
                or not self._date_event_tracker
                or not self._date_cutscene):
            return False

        npc_id = Constant.DATE_EVENT_NPC_ID
        npc_data = self.npc_registry.get(npc_id)
        if not npc_data:
            return False

        level = self.npc_registry.get_affinity_level(npc_id)
        min_level = Constant.DATE_EVENT_MIN_LEVEL

        if level < min_level:
            return False

        # Sudah trigger di level ini?
        if self._date_event_tracker.has_triggered(npc_id, level):
            return False

        # TRIGGER
        print(f"[Cashier] DATE EVENT triggered for {npc_data.name} "
              f"(level {level}, affinity "
              f"{self.npc_registry.get_affinity(npc_id)})")

        self._date_cutscene.setup(npc_id, level)
        self._scene_manager.transition_to(self._date_cutscene)
        return True

    # Emoji

    def _show_emoji_popup(self, expression: str) -> None:
        surface = self._expression_set.get_surface(expression)
        fallback_text, fallback_color = self._expression_set.get_fallback(expression)
        center_x = int(self._npc_x) + Constant.NPC_WIDTH // 2

        self._emoji_popup.show(surface, fallback_text, fallback_color,
                               center_x, Constant.NPC_Y)
        self.animator.pop_in("emoji_popup")

        if self.audio:
            sfx = self._expression_set.get_expression_config(expression).get("popup_sfx", "emoji_popup")
            self.audio.play_sfx(sfx)

    # Update

    def update(self, delta_time: float = 0.0) -> None:
        offsets           = self.animator.update(delta_time)
        self._npc_offset  = offsets.get("npc", (0, 0, 1.0))
        self._emoji_scale = offsets.get("emoji_popup", (0, 0, 1.0))[2]

        if self._state == CashierState.SLIDING_IN:
            dx, _, _ = self._npc_offset
            self._npc_x = Constant.NPC_X + dx
            if not self.animator.is_active("npc"):
                self._npc_x = self._npc_target_x
                self._state = CashierState.WAITING
                self._order_ui.show_npc_info()

        self._emoji_popup.update(delta_time)

        if self._state == CashierState.DIALOGUE:
            self.dialogue_box.update(delta_time, self.audio)

        if self._state == CashierState.ORDER_ACTIVE:
            if self._scene_manager:
                remaining = self._scene_manager.get_timer_remaining()
                self._order_ui.set_timer_text(f"Time: {max(0, int(remaining))}s")

            if self._minigame.just_succeeded:
                self._on_minigame_success()

            self._minigame.update(delta_time, self._npc_x)

    # Minigame reward

    def _on_minigame_success(self) -> None:
        if self.npc:
            self.npc.change_affinity(Constant.MG_AFFINITY_BONUS)
            self.npc.expression = "happy"
            self._auto_save()
        if self._scene_manager:
            self._scene_manager.add_time(Constant.MG_TIMER_BONUS)
        self.animator.bounce("npc")
        self._show_emoji_popup("happy")
        if self.audio:
            self.audio.play_sfx("affinity_up")

    # Render

    def render(self) -> None:
        if not self.screen:
            return
        self._build_render_context()
        self._renderer.render(
            self.screen,
            self._render_ctx,
            self._order_ui,
            self.dialogue_box,
            self.cake_selection,
            self._minigame,
        )
    def _render_above_nav(self, screen: pygame.Surface) -> None:
        self._emoji_popup.render(screen, self._emoji_scale)

    def _build_render_context(self) -> None:
        ctx             = self._render_ctx
        ctx.state       = self._state
        ctx.npc         = self.npc
        ctx.npc_x       = self._npc_x
        ctx.npc_offset  = self._npc_offset
        ctx.npc_sprite  = self._get_expression_sprite()
        ctx.emoji_scale = self._emoji_scale
        ctx.background  = self._current_bg
        ctx.heart_img   = self._heart_img
        ctx.cake        = self.cake

    # Events

    def handle_event(self, event: pygame.event.Event) -> None:
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

        if self._state == CashierState.ORDER_ACTIVE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._minigame.handle_click(event.pos):
                    pass
                elif (self.cake and self.cake.is_complete()
                    and hasattr(self._renderer, '_submit_btn_rect')
                    and self._renderer._submit_btn_rect
                    and self._renderer._submit_btn_rect.collidepoint(event.pos)):
                    self.check_cake()
            return

        if (self._state == CashierState.REACTING
                and self._emoji_popup.is_done()
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1):
            self._reset_for_new_round()

    # Helpers

    def _auto_save(self) -> None:
        if self.save_manager and self.npc_registry:
            self.save_manager.save_affinity(self.npc_registry.get_all_affinity())
            self.save_manager.save_dialogue_tracker(self.dialogue_tracker.get_save_data())

    def _reset_for_new_round(self) -> None:
        if self._check_and_trigger_ending():
            return

        # Check date event before new NPC
        if self._check_date_event():
            return

        self.npc = None
        self.order = None
        self.cake = None
        self.result = False
        self._cake_options = []
        self._state           = CashierState.HIDDEN
        self._npc_x           = -Constant.NPC_WIDTH
        self._current_mood    = "neutral"
        self._current_variant = "a"

        self._order_ui.hide()
        self._order_ui.accepted = False
        self._order_ui.set_timer_text("")
        self.dialogue_box.hide()
        self.dialogue_manager.reset()
        self.cake_selection.reset()
        self._emoji_popup.hide()
        self._renderer.clear_text_cache()
        self._minigame.reset()

        self.animator.stop_all()
        self._npc_offset  = (0, 0, 1.0)
        self._emoji_scale = 1.0

        self._current_bg      = self._default_bg
        self._current_npc_img = self._default_npc

        self._spawn_npc()

    # Debug

    def _debug_ending_status(self) -> None:
        if not self.npc:
            return
        npc, data = self.npc, self.npc.data
        has_threshold    = "ending" in data.affinity_thresholds
        threshold        = data.affinity_thresholds.get("ending", -1)

        print(f"[DEBUG Ending] NPC={data.name} affinity={npc.affinity} "
              f"threshold={threshold if has_threshold else 'N/A'} "
              f"has_ending={data.has_ending()} "
              f"reached={'YES' if has_threshold and npc.affinity >= threshold else 'NO'}")