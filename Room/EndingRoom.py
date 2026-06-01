import pygame
from Room.Room import Room
from Core.DialogueManager import DialogueManager, AdvanceResult
from UI.DialogueBox import DialogueBox
from UI.ExpressionSet import ExpressionSet
from UI.EmojiPopup import EmojiPopup
from UI.Animator import Animator
from Character.NPCData import NPCData
import Constant


class EndingRoom(Room):

    def __init__(self):
        super().__init__("Ending")

        self._npc_data: NPCData | None = None
        self._audio = None

        # Assets
        self._background: pygame.Surface | None = None
        self._expression_sprites: dict[str, pygame.Surface] = {}
        self._current_expression: str = "neutral"

        # Dialogue
        self._dialogue_manager = DialogueManager()
        self._dialogue_box     = DialogueBox()

        # Expression / Emoji
        self._expression_set = ExpressionSet()
        self._emoji_popup    = EmojiPopup()
        self._animator       = Animator()
        self._npc_offset: tuple[float, float, float] = (0, 0, 1.0)
        self._emoji_scale: float = 1.0

        # "dialogue" → sedang berjalan | "finished" → selesai, tunggu klik
        self._phase = "dialogue"

        # Font & text cache
        self._font: pygame.font.Font | None = None
        self._text_cache: dict[str, pygame.Surface] = {}

    # ── Setup (dipanggil SceneManager.start_ending sebelum enter) ─────────

    def setup(self, npc_data: NPCData, audio=None) -> None:
        self._npc_data           = npc_data
        self._audio              = audio
        self._phase              = "dialogue"
        self._current_expression = "neutral"
        self._text_cache.clear()
        self._dialogue_manager.reset()
        self._emoji_popup.hide()
        self._animator.stop_all()
        self._npc_offset  = (0, 0, 1.0)
        self._emoji_scale = 1.0

        ending = npc_data.ending

        # Background
        bg_path          = ending.get("background", "")
        self._background = self._load_and_scale(
            bg_path, Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT
        ) if bg_path else None

        # Sprite NPC default/neutral untuk ending
        sprite_path    = ending.get("sprite", npc_data.get_sprite_path())
        default_sprite = self._load_and_scale(
            sprite_path, Constant.NPC_WIDTH, Constant.NPC_HEIGHT
        ) if sprite_path else None

        # Kumpulkan semua expression sprites
        self._expression_sprites = {}
        if default_sprite:
            self._expression_sprites["neutral"] = default_sprite

        for expr_name in npc_data.get_all_expression_names():
            path = npc_data.get_expression_sprite_path(expr_name)
            if path:
                img = self._load_and_scale(path, Constant.NPC_WIDTH, Constant.NPC_HEIGHT)
                if img:
                    self._expression_sprites[expr_name] = img

        # Register ending BGM (key unik per NPC agar bisa play_bgm nanti)
        bgm_path = ending.get("bgm", "")
        if bgm_path and self._audio:
            self._audio.register_bgm(f"ending_{npc_data.id}", bgm_path)

        # Mulai dialogue
        dialogues = ending.get("dialogues", [])
        if dialogues:
            self._dialogue_manager.start(dialogues)

        print(f"[EndingRoom] Setup untuk '{npc_data.name}': "
              f"{len(dialogues)} dialogue, "
              f"expressions={list(self._expression_sprites.keys())}, "
              f"bg={'ada' if self._background else 'TIDAK ADA'}")

    # ── Lifecycle ─────────────────────────────────────────────────────────

    def enter(self) -> None:
        self._font = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_BODY_SIZE)

        # Play ending BGM
        if self._audio and self._npc_data:
            self._audio.play_bgm(f"ending_{self._npc_data.id}")

        # Tampilkan dialogue pertama
        self._show_current_dialogue()
        print(f"[EndingRoom] Enter — phase={self._phase}")

    def exit(self) -> None:
        print("[EndingRoom] Exit")

    # ── Helper ───────────────────────────────────────────────────────────

    @staticmethod
    def _load_and_scale(path: str, w: int, h: int) -> pygame.Surface | None:
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except Exception:
            print(f"[EndingRoom] File tidak ditemukan: {path}")
            return None

    def _get_expression_sprite(self) -> pygame.Surface | None:
        return (self._expression_sprites.get(self._current_expression)
                or self._expression_sprites.get("neutral"))

    def _get_cached_text(self, text: str, color: tuple) -> pygame.Surface:
        key = f"{text}_{color}"
        if key not in self._text_cache:
            self._text_cache[key] = self._font.render(text, True, color)
        return self._text_cache[key]

    # ── Dialogue ─────────────────────────────────────────────────────────

    def _show_current_dialogue(self) -> None:
        entry = self._dialogue_manager.get_current()
        if not entry:
            return

        self._dialogue_box.set_name(self._npc_data.name if self._npc_data else "???")
        self._dialogue_box.set_text(entry.get("text", ""))
        self._dialogue_box.set_choices(entry.get("choices", []))
        self._dialogue_box.show()

    def _on_dialogue_advance(self, choice_result: int) -> None:
        if choice_result == -1:
            return

        advance_result = self._dialogue_manager.advance(choice_result)
        self._apply_dialogue_result(advance_result)

        if self._dialogue_manager.is_finished():
            print("[EndingRoom] Dialogue selesai → phase = finished")
            self._dialogue_box.hide()
            self._phase = "finished"
        else:
            self._show_current_dialogue()

    def _apply_dialogue_result(self, result: AdvanceResult) -> None:
        if result.expression:
            self._current_expression = result.expression

            animation = self._expression_set.get_animation(result.expression)
            if animation == "bounce":
                self._animator.bounce("npc")
            elif animation == "shake":
                self._animator.shake("npc")

            sfx = (self._npc_data.get_expression_sfx(result.expression)
                   if self._npc_data else None)
            if sfx is None:
                sfx = self._expression_set.get_sfx(result.expression)
            if sfx and self._audio:
                self._audio.play_sfx(sfx)

        if result.emoji:
            self._show_emoji_popup(result.emoji)

    # ── Emoji Popup ───────────────────────────────────────────────────────

    def _show_emoji_popup(self, expression: str) -> None:
        surface = self._expression_set.get_surface(expression)
        fallback_text, fallback_color = self._expression_set.get_fallback(expression)
        center_x = Constant.ENDING_NPC_X + Constant.NPC_WIDTH // 2

        self._emoji_popup.show(surface, fallback_text, fallback_color,
                               center_x, Constant.ENDING_NPC_Y)
        self._animator.pop_in("emoji_popup")

        if self._audio:
            self._audio.play_sfx("emoji_popup")

    # ── Update ────────────────────────────────────────────────────────────

    def update(self, delta_time: float = 0.0) -> None:
        offsets           = self._animator.update(delta_time)
        self._npc_offset  = offsets.get("npc", (0, 0, 1.0))
        self._emoji_scale = offsets.get("emoji_popup", (0, 0, 1.0))[2]

        self._emoji_popup.update(delta_time)

        if self._phase == "dialogue":
            self._dialogue_box.update(delta_time, self._audio)

    # ── Render ────────────────────────────────────────────────────────────

    def render(self) -> None:
        if not self.screen:
            return

        self._render_background()
        self._render_npc()
        self._emoji_popup.render(self.screen, self._emoji_scale)

        if self._phase == "dialogue":
            self._dialogue_box.render(self.screen)

        if self._phase == "finished" and self._emoji_popup.is_done():
            hint = self._get_cached_text(
                "Click to return to Main Menu...", Constant.COLOR_DARK_BROWN)
            self.screen.blit(hint,
                hint.get_rect(
                    centerx=Constant.SCREEN_WIDTH // 2,
                    y=Constant.SCREEN_HEIGHT - 60
                ))

    def _render_background(self) -> None:
        if self._background:
            self.screen.blit(self._background, (0, 0))
        else:
            self.screen.fill(Constant.COLOR_BG_CREAM)

    def _render_npc(self) -> None:
        dx, dy, scale = self._npc_offset
        npc_x = int(Constant.ENDING_NPC_X + dx)
        npc_y = int(Constant.ENDING_NPC_Y + dy)

        sprite = self._get_expression_sprite()
        if not sprite:
            return

        if scale != 1.0:
            w      = max(1, int(Constant.NPC_WIDTH * scale))
            h      = max(1, int(Constant.NPC_HEIGHT * scale))
            scaled = pygame.transform.scale(sprite, (w, h))
            self.screen.blit(scaled, (
                npc_x + (Constant.NPC_WIDTH - w) // 2,
                npc_y + (Constant.NPC_HEIGHT - h) // 2,
            ))
        else:
            self.screen.blit(sprite, (npc_x, npc_y))

    # ── Events ────────────────────────────────────────────────────────────

    def handle_event(self, event) -> None:
        if self._phase == "dialogue":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                result = self._dialogue_box.handle_event(event)
                if result != -1:
                    self._on_dialogue_advance(result)
            return

        # Setelah dialogue selesai — klik untuk kembali ke Main Menu
        if (self._phase == "finished"
                and self._emoji_popup.is_done()
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1):
            print("[EndingRoom] Klik → kembali ke Main Menu")
            if self._scene_manager:
                # FIX: go_to_main_menu() — bukan transition_to("MainMenu")
                # MainMenu terdaftar sebagai hidden room dengan nama "Main Menu"
                self._scene_manager.go_to_main_menu()