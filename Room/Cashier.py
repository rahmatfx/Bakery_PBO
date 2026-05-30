import pygame
import os
from Room.Room import Room
from Character.NPC import NPC
from Character.NPCData import NPCData
from Character.NPCRegistry import NPCRegistry
from Core.DialogueManager import DialogueManager
from Core.SaveManager import SaveManager
from UI.OrderUI import OrderUI
from UI.DialogueBox import DialogueBox
from UI.CakeSelectionUI import CakeSelectionUI          
from Order.Order import Order
from Enum.CashierState import CashierState
import Constant
                            
class Cashier(Room):

    def __init__(self, npc_registry: NPCRegistry = None,
                 save_manager: SaveManager = None):
        super().__init__("Cashier")

        # Dependencies
        self.npc_registry: NPCRegistry = npc_registry
        self.save_manager: SaveManager = save_manager

        # NPC & Order state 
        self.npc: NPC = None
        self.order: Order = None
        self.cake = None
        self.result: bool = False
        self._cake_options: list = []                   

        self._state = CashierState.HIDDEN
        self._npc_x: float = -Constant.NPC_WIDTH
        self._npc_target_x: int = Constant.NPC_X

        # Dialogue
        self.dialogue_manager = DialogueManager()
        self.dialogue_box = DialogueBox()

        # Cake Selection 
        self.cake_selection = CakeSelectionUI()

        # Emoji animation 
        self._emoji_type: str = ""
        self._emoji_y: float = 0.0
        self._emoji_target_y: float = 0.0
        self._emoji_start_y: float = 0.0
        self._emoji_active: bool = False
        self._emoji_done: bool = False

        # UI 
        self._order_ui = OrderUI()

        # Default assets 
        self._default_bg = self._load_and_scale(Constant.CASHIER_BG,
                                                 Constant.SCREEN_WIDTH,
                                                 Constant.SCREEN_HEIGHT)
        self._default_npc = self._load_and_scale(Constant.NPC_IMG,
                                                  Constant.NPC_WIDTH,
                                                  Constant.NPC_HEIGHT)
        self._default_emoji_happy = self._load_and_scale(Constant.NPC_EMOJI_HAPPY,
                                                          Constant.EMOJI_WIDTH,
                                                          Constant.EMOJI_HEIGHT)
        self._default_emoji_angry = self._load_and_scale(Constant.NPC_EMOJI_ANGRY,
                                                          Constant.EMOJI_WIDTH,
                                                          Constant.EMOJI_HEIGHT)
        self._heart_img = self._load_and_scale(Constant.HEART_IMG,
                                                Constant.AFFINITY_HEART_SIZE,
                                                Constant.AFFINITY_HEART_SIZE)

        # Current NPC assets
        self._current_bg = self._default_bg
        self._current_npc_img = self._default_npc
        self._current_emoji_happy = self._default_emoji_happy
        self._current_emoji_angry = self._default_emoji_angry

        # Asset cache per NPC id 
        self._npc_asset_cache: dict[str, dict] = {}

        # Fonts & text cache 
        self._font = None
        self._font_affinity = None
        self._text_cache: dict[str, pygame.Surface] = {}

    # Asset loading helpers 

    @staticmethod
    def _load_and_scale(path: str, w: int, h: int):
        try:
            img = pygame.image.load(path).convert_alpha()
            scaled = pygame.transform.scale(img, (w, h))
            print(f"[DEBUG Cashier] Loaded: {path}")
            return scaled
        except Exception:
            print(f"[DEBUG Cashier] Not found, fallback: {path}")
            return None

    def _load_npc_assets(self, data: NPCData) -> None:
        if data.id in self._npc_asset_cache:
            cached = self._npc_asset_cache[data.id]
            self._current_npc_img = cached["sprite"]
            self._current_emoji_happy = cached["happy"]
            self._current_emoji_angry = cached["angry"]
            return

        sprite_path = data.get_sprite_path()
        happy_path = data.get_emoji_happy_path()
        angry_path = data.get_emoji_angry_path()

        npc_img = (self._load_and_scale(sprite_path,
                    Constant.NPC_WIDTH, Constant.NPC_HEIGHT)
                   if sprite_path else None)
        happy_img = (self._load_and_scale(happy_path,
                     Constant.EMOJI_WIDTH, Constant.EMOJI_HEIGHT)
                     if happy_path else None)
        angry_img = (self._load_and_scale(angry_path,
                     Constant.EMOJI_WIDTH, Constant.EMOJI_HEIGHT)
                     if angry_path else None)

        self._current_npc_img = npc_img if npc_img else self._default_npc
        self._current_emoji_happy = happy_img if happy_img else self._default_emoji_happy
        self._current_emoji_angry = angry_img if angry_img else self._default_emoji_angry

        self._npc_asset_cache[data.id] = {
            "sprite": self._current_npc_img,
            "happy": self._current_emoji_happy,
            "angry": self._current_emoji_angry,
        }
        print(f"[DEBUG Cashier] Assets loaded & cached for: {data.id}")

    # Text cache

    def _get_cached_text(self, text: str, color: tuple) -> pygame.Surface:
        key = f"{text}_{color}"
        if key not in self._text_cache:
            self._text_cache[key] = self._font.render(text, True, color)
        return self._text_cache[key]

    def _clear_text_cache(self) -> None:
        self._text_cache.clear()

    # Auto-save 

    def _auto_save(self) -> None:
        if self.save_manager and self.npc_registry:
            affinity = self.npc_registry.get_all_affinity()
            self.save_manager.save_affinity(affinity)

    # Room lifecycle

    def enter(self) -> None:
        print("[DEBUG Cashier] Entering room")
        self._font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_BODY_SIZE)
        self._font_affinity = pygame.font.SysFont(Constant.FONT_NAME,
                                                    Constant.AFFINITY_FONT_SIZE,
                                                    bold=True)

        if (self._scene_manager and self._scene_manager.consume_timer_expired()):
            print("[DEBUG Cashier] Timer expired entry!")
            return

        if self._state == CashierState.ORDER_ACTIVE:
            print("[DEBUG Cashier] Resuming — order active")
            self._order_ui.show_order_details()      
            return

        if self._state == CashierState.REACTING:
            print("[DEBUG Cashier] Resuming — reacting")
            return

        if self._state == CashierState.DIALOGUE:
            print("[DEBUG Cashier] Resuming — dialogue active")
            self.dialogue_box.show()
            return

        if self._state == CashierState.CAKE_SELECT:
            print("[DEBUG Cashier] Resuming — cake selection")
            self.cake_selection.show()
            return

        if self._state == CashierState.HIDDEN:
            self.showNPC()

    def exit(self) -> None:
        print("[DEBUG Cashier] Exiting room")

    # NPC spawning 

    def showNPC(self) -> None:
        if self.npc_registry:
            npc_data = self.npc_registry.random()
            self.npc = NPC(npc_data, self.npc_registry)
        else:
            print("[WARN Cashier] No NPCRegistry! Using fallback NPC")
            fallback_data = NPCData(id="fallback", name="Customer",
                                     personality="Generic customer")
            self.npc = NPC(fallback_data)

        # Order belum ada — baru di-set setelah cake selection
        self.order = None                           # ← tambah

        self._load_npc_assets(self.npc.data)

        self._state = CashierState.SLIDING_IN
        self._npc_x = -Constant.NPC_WIDTH

        # OrderUI: mode NPC Info (gak perlu order)
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
              f"(affinity: {self.npc.affinity}, "
              f"level: {self.npc.get_affinity_level()})")

    # Order handling

    def acceptOrder(self) -> None:
        print(f"[DEBUG Cashier] Order accepted for {self.npc.name}")

        self._state = CashierState.DIALOGUE

        entries = self.npc.get_dialogue()
        if entries:
            self.dialogue_manager.start(entries)
            self._show_current_dialogue()
        else:
            print("[DEBUG Cashier] No dialogue, skip to CAKE_SELECT")
            self._start_cake_select()

    def _show_current_dialogue(self) -> None:
        entry = self.dialogue_manager.get_current()
        if not entry:
            return

        text = entry.get("text", "")
        choices = entry.get("choices", [])

        self.dialogue_box.set_name(self.npc.name)
        self.dialogue_box.set_text(text)
        self.dialogue_box.set_choices(choices)
        self.dialogue_box.show()

        print(f"[DEBUG Cashier] Showing dialogue: {text[:40]}... "
              f"({len(choices)} choices)")

    def _on_dialogue_advance(self, choice_result: int) -> None:
        if choice_result == -1:
            return

        if choice_result >= 0:
            affinity_delta = self.dialogue_manager.advance(choice_result)
        else:
            affinity_delta = self.dialogue_manager.advance()

        if affinity_delta != 0 and self.npc:
            self.npc.change_affinity(affinity_delta)
            print(f"[DEBUG Cashier] Dialogue affinity: "
                  f"{'+' if affinity_delta >= 0 else ''}{affinity_delta}, "
                  f"total: {self.npc.affinity}")
            self._auto_save()

        if self.dialogue_manager.is_finished():
            print("[DEBUG Cashier] Dialogue finished")
            self.dialogue_box.hide()
            self._start_cake_select()                       
        else:
            self._show_current_dialogue()

    # Cake Selection

    def _start_cake_select(self) -> None:
        self._state = CashierState.CAKE_SELECT

        self._cake_options = self.npc.generate_cake_options()

        self.cake_selection.set_options(
            self._cake_options,
            callback=self._on_cake_selected
        )
        self.cake_selection.show()

        print("[DEBUG Cashier] Cake selection started")

    def _on_cake_selected(self, index: int) -> None:
        if index < 0 or index >= len(self._cake_options):
            return

        selected_order = self._cake_options[index]

        # Set order NPC ke kue yang dipilih player
        self.npc.set_order(selected_order)
        self.order = selected_order

        # Update OrderUI
        self._order_ui.set_order(self.order)

        # Hide cake selection
        self.cake_selection.hide()

        print(f"[DEBUG Cashier] Player chose cake {index}: "
              f"{selected_order.flavor} + {selected_order.mold} + "
              f"{selected_order.decoration}")

        # Hitung preference score (buat info debug)
        score = self.npc.calculate_preference_score(selected_order)
        print(f"[DEBUG Cashier] Preference score: {score}")

        self._start_order_active()

    # Order Active 

    def _start_order_active(self) -> None:
        self._state = CashierState.ORDER_ACTIVE        
        self._order_ui.show_order_details() 

        if self._scene_manager:
            self._scene_manager.start_timer(Constant.TIMER_DURATION)

        print("[DEBUG Cashier] Timer started, order active")

    def onCheckOrder(self, cake) -> None:
        if not self.order or not cake:
            return

        self.cake = cake

        # Cek apakah kue yang dibake cocok sama order 
        correct_cake = (
            cake.flavor == self.order.flavor
            and cake.mold == self.order.mold
            and cake.decoration == self.order.decoration
        )

        if self._scene_manager:
            self._scene_manager.stop_timer()

        self._order_ui.hide()

        # Scoring berbasis preference
        if correct_cake:
            # Kue bener! Preference score = per-attribute bonus
            pref_score = self.npc.calculate_preference_score(self.order)

            # Minimum +1 (kue bener), + preference bonus per attribute
            # pref_score: +1 per preferred, -1 per disliked
            # Jadi kalau semua preferred: +3, kalau netral: 0, kalau disliked: negatif
            affinity_delta = 1 + pref_score

            if pref_score >= 2:
                self.npc.showHappy()
                self._start_emoji_popup("happy")
                print(f"[DEBUG Cashier] Great match! pref={pref_score}, delta={affinity_delta}")
            elif pref_score >= 1:
                self.npc.showHappy()
                self._start_emoji_popup("happy")
                print(f"[DEBUG Cashier] Good match! pref={pref_score}, delta={affinity_delta}")
            elif pref_score == 0:
                self.npc.showHappy()
                self._start_emoji_popup("happy")
                print(f"[DEBUG Cashier] OK match, neutral. pref={pref_score}, delta={affinity_delta}")
            else:
                # Kue bener tapi isinya disliked
                self.npc.expression = "neutral"
                self._start_emoji_popup("angry")
                print(f"[DEBUG Cashier] Correct but bad taste. pref={pref_score}, delta={affinity_delta}")
        else:
            # Kue salah!
            affinity_delta = -2
            self.npc.showAngry()
            self._start_emoji_popup("angry")
            print(f"[DEBUG Cashier] Wrong cake! delta={affinity_delta}")

        self.result = correct_cake
        self.npc.change_affinity(affinity_delta)
        self._state = CashierState.REACTING
        self._auto_save()

        print(f"[DEBUG Cashier] Result: {correct_cake}, "
              f"affinity delta: {affinity_delta}, "
              f"total: {self.npc.affinity}")
        

    def getResult(self) -> bool:
        return self.result

    # Timer 

    def on_timer_expired(self) -> None:
        print("[DEBUG Cashier] Timer expired!")

        self._npc_x = self._npc_target_x
        self._state = CashierState.REACTING

        self._order_ui.hide()
        self.dialogue_box.hide()
        self.cake_selection.hide()

        self.npc.change_affinity(-2)
        self.npc.showAngry()
        self._start_emoji_popup("angry")
        self._auto_save()

    # Emoji popup

    def _start_emoji_popup(self, emoji_type: str) -> None:
        self._emoji_type = emoji_type
        self._emoji_active = True
        self._emoji_done = False

        self._emoji_target_y = Constant.NPC_Y - Constant.EMOJI_HEIGHT - 10
        self._emoji_start_y = Constant.NPC_Y + 20
        self._emoji_y = self._emoji_start_y

        print(f"[DEBUG Cashier] Emoji popup started: {emoji_type}")

    # Update 

    def update(self) -> None:
        if self._state == CashierState.SLIDING_IN:
            self._npc_x += Constant.NPC_SLIDE_SPEED
            if self._npc_x >= self._npc_target_x:
                self._npc_x = self._npc_target_x
                self._state = CashierState.WAITING
                self._order_ui.show_npc_info() 
                print("[DEBUG Cashier] NPC slide-in complete")

        if self._emoji_active and not self._emoji_done:
            self._emoji_y -= Constant.EMOJI_POPUP_SPEED
            if self._emoji_y <= self._emoji_target_y:
                self._emoji_y = self._emoji_target_y
                self._emoji_done = True

        if self._state == CashierState.DIALOGUE:
            self.dialogue_box.update()

        if (self._state == CashierState.ORDER_ACTIVE                and self._scene_manager):
            remaining = self._scene_manager.get_timer_remaining()
            secs = max(0, int(remaining))
            self._order_ui.set_timer_text(f"Time: {secs}s")

    # Render 

    def render(self) -> None:
        if not self.screen:
            return

        self._render_background()
        self._render_npc()
        self._order_ui.render(self.screen)
        self._render_emoji()
        self._render_affinity()

        if self._state == CashierState.DIALOGUE:
            self.dialogue_box.render(self.screen)

        if self._state == CashierState.CAKE_SELECT:                
            self.cake_selection.render(self.screen)

        if self._state == CashierState.REACTING and self._emoji_done:
            hint = self._get_cached_text("Click to continue...",
                                          Constant.COLOR_DARK_BROWN)
            self.screen.blit(hint,
                (Constant.NPC_X, Constant.NPC_Y + Constant.NPC_HEIGHT + 20))

    def _render_background(self) -> None:
        if self._current_bg:
            self.screen.blit(self._current_bg, (0, 0))
        else:
            content = pygame.Rect(0, Constant.NAV_BAR_HEIGHT,
                                  Constant.SCREEN_WIDTH,
                                  Constant.SCREEN_HEIGHT - Constant.NAV_BAR_HEIGHT)
            pygame.draw.rect(self.screen, (255, 235, 210), content)

    def _render_npc(self) -> None:
        if not self.npc or self._state == CashierState.HIDDEN:
            return

        npc_x = int(self._npc_x)
        npc_y = Constant.NPC_Y

        if self._current_npc_img:
            self.screen.blit(self._current_npc_img, (npc_x, npc_y))
        else:
            npc_rect = pygame.Rect(npc_x, npc_y,
                                    Constant.NPC_WIDTH, Constant.NPC_HEIGHT)
            shadow = npc_rect.move(4, 4)
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

    def _render_emoji(self) -> None:
        if not self._emoji_active:
            return

        emoji_x = int(self._npc_x) + (Constant.NPC_WIDTH - Constant.EMOJI_WIDTH) // 2
        emoji_y = int(self._emoji_y)

        if self._emoji_type == "happy" and self._current_emoji_happy:
            self.screen.blit(self._current_emoji_happy, (emoji_x, emoji_y))
        elif self._emoji_type == "angry" and self._current_emoji_angry:
            self.screen.blit(self._current_emoji_angry, (emoji_x, emoji_y))
        else:
            if self._emoji_type == "happy":
                txt, color = "HAPPY", (0, 180, 0)
            else:
                txt, color = "ANGRY", (220, 50, 50)

            emoji_rect = pygame.Rect(emoji_x, emoji_y,
                                      Constant.EMOJI_WIDTH, Constant.EMOJI_HEIGHT)
            pygame.draw.rect(self.screen, color, emoji_rect, border_radius=50)
            surf = self._get_cached_text(txt, Constant.COLOR_WHITE)
            self.screen.blit(surf, surf.get_rect(center=emoji_rect.center))

    def _render_affinity(self) -> None:
        if not self.npc or self._state == CashierState.HIDDEN:
            return

        bar_x = int(self._npc_x) + 10
        bar_y = Constant.NPC_Y - Constant.AFFINITY_HEART_SIZE - 12

        heart_size = Constant.AFFINITY_HEART_SIZE
        padding = 8

        # Background panel 
        affinity_text = str(self.npc.affinity)
        affinity_surf = None
        if self._font_affinity:
            affinity_surf = self._font_affinity.render(
                affinity_text, True, Constant.COLOR_DARK_BROWN)

        text_w = affinity_surf.get_width() if affinity_surf else 30
        panel_w = heart_size + 8 + text_w + padding * 2
        panel_h = heart_size + padding * 2

        panel_rect = pygame.Rect(bar_x - padding, bar_y - padding,
                                  panel_w, panel_h)
        pygame.draw.rect(self.screen, (0, 0, 0), panel_rect.move(2, 2),
                          border_radius=8)
        pygame.draw.rect(self.screen, Constant.COLOR_BG_CREAM,
                          panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, Constant.COLOR_WARM_BROWN,
                          panel_rect, 2, border_radius=8)

        # Heart image
        if self._heart_img:
            self.screen.blit(self._heart_img, (bar_x, bar_y))
        else:
            heart_rect = pygame.Rect(bar_x + 2, bar_y + 2,
                                      heart_size - 4, heart_size - 4)
            pygame.draw.circle(self.screen, Constant.COLOR_HEART_RED,
                               heart_rect.center, heart_size // 2 - 2)

        # Angka affinity 
        if affinity_surf:
            self.screen.blit(affinity_surf,
                             (bar_x + heart_size + 8,
                              bar_y + (heart_size - affinity_surf.get_height()) // 2))

    # Event handling 

    def handle_event(self, event) -> None:
        # Cake Selection 
        if self._state == CashierState.CAKE_SELECT:
            result = self.cake_selection.handle_event(event)
            return

        # Dialogue 
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
                and self._emoji_done
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1):
            print("[DEBUG Cashier] New round!")
            self._reset_for_new_round()

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
        self._cake_options = []                           
        self._state = CashierState.HIDDEN
        self._npc_x = -Constant.NPC_WIDTH
        self._emoji_active = False
        self._emoji_done = False
        self._emoji_type = ""
        self._order_ui.hide()
        self._order_ui.accepted = False
        self._order_ui.set_timer_text("")
        self.dialogue_box.hide()
        self.dialogue_manager.reset()
        self.cake_selection.reset()                       
        self._clear_text_cache()

        self._current_bg = self._default_bg
        self._current_npc_img = self._default_npc
        self._current_emoji_happy = self._default_emoji_happy
        self._current_emoji_angry = self._default_emoji_angry

        self.showNPC()