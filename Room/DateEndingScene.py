import pygame
from Room.Room import Room
from Character.NPCRegistry import NPCRegistry
from Core.DialogueManager import DialogueManager
from UI.DialogueBox import DialogueBox
import Constant


class DateEndingScene(Room):

    def __init__(self, npc_registry: NPCRegistry = None, audio=None):
        super().__init__("DateEndingScene")

        self.npc_registry = npc_registry
        self.audio = audio

        self._npc_id: str = ""
        self._npc_name: str = "???"
        self._affinity_level: int = 0
        self._mood: float = 50.0

        self._dialogue_manager = DialogueManager()
        self._dialogue_box = DialogueBox()
        self._dialogue_active: bool = False
        self._bg_img: pygame.Surface | None = None
        self._npc_img: pygame.Surface | None = None
        self._assets_loaded: bool = False

        self._fade_alpha: float = 255.0
        self._fade_speed: float = 300.0
        self._fading_in: bool = True

        self._date_event_tracker = None


    def _load_assets(self) -> None:
        try:
            raw = pygame.image.load(Constant.DATE_CUTSCENE_BG).convert()
            self._bg_img = pygame.transform.scale(
                raw, (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
            print(f"[DateEnding] BG loaded (BG_Event.png)")
        except Exception:
            self._bg_img = None

        try:
            raw = pygame.image.load(Constant.DATE_ROOM_SUNSET_NPC).convert_alpha()
            self._npc_img = pygame.transform.scale(
                raw, (Constant.DATE_ROOM_SUNSET_NPC_W,
                      Constant.DATE_ROOM_SUNSET_NPC_H))
            print(f"[DateEnding] NPC loaded (npc_sunset.png)")
        except Exception:
            self._npc_img = None

        self._assets_loaded = True


    def setup(self, npc_id: str, affinity_level: int, mood: float, npc_name: str = "???") -> None:
        self._npc_id = npc_id
        self._affinity_level = affinity_level
        self._mood = mood
        self._npc_name = npc_name
        self._fade_alpha = 255.0
        self._fading_in = True
        self._dialogue_active = False
        self._dialogue_manager.reset()
        self._dialogue_box.hide()

        self._load_assets()
        self._start_ending_dialogue()
        print(f"[DateEnding] Setup: {npc_name}, mood={mood:.0f}")


    def enter(self) -> None:
        if not self._assets_loaded:
            self._load_assets()
        self._fade_alpha = 255.0
        self._fading_in = True


    def update(self, delta_time: float = 0.0) -> None:
        if self._fading_in:
            self._fade_alpha -= self._fade_speed * delta_time
            if self._fade_alpha <= 0:
                self._fade_alpha = 0
                self._fading_in = False

        if self._dialogue_active:
            self._dialogue_box.update(delta_time, self.audio)


    def _start_ending_dialogue(self) -> None:
        entries = self._get_ending_dialogue()
        if entries:
            self._dialogue_manager.start(entries)
            self._dialogue_active = True
            self._show_current_dialogue()

        if self._mood >= 80:
            bonus = 5
            tier = "GREAT"
        elif self._mood >= 50:
            bonus = 3
            tier = "GOOD"
        else:
            bonus = 1
            tier = "AWKWARD"

        if self.npc_registry and bonus != 0:
            self.npc_registry.change_affinity(self._npc_id, bonus)

        # Mark event as triggered
        if self._date_event_tracker:
            key = f"{self._npc_id}:{self._affinity_level}"
            self._date_event_tracker.mark_triggered(key)
            print(f"[DateEnding] Event marked as triggered: {key}")

        print(f"[DateEnding] Tier: {tier}, Affinity bonus: +{bonus}")

    def _get_ending_dialogue(self) -> list[dict]:
        if self._mood >= 80:
            return [
                {"id": "e1", "text": f"{self._npc_name} tersenyum lebar... 'Hari ini seru banget! Terima kasih ya...'", "next": "e2"},
                {"id": "e2", "text": "'Kita harus ngulang ini lagi suatu saat!' Matanya berbinar-binar.", "next": "e3"},
                {"id": "e3", "text": "Kamu merasakan kehangatan yang luar biasa... Date yang sempurna.", "next": None},
            ]
        elif self._mood >= 50:
            return [
                {"id": "e1", "text": f"{self._npc_name} tersenyum tipis... 'Lumayan juga hari ini, terima kasih ya.'", "next": "e2"},
                {"id": "e2", "text": "'Mungkin lain kali kita bisa coba tempat lain?' katanya santai.", "next": None},
            ]
        else:
            return [
                {"id": "e1", "text": f"{self._npc_name} terdiam sejenak... '...Hmm, hari ini agak aneh ya.'", "next": "e2"},
                {"id": "e2", "text": "'Mungkin lain kali bisa lebih baik...' katanya pelan.", "next": None},
            ]

    def _show_current_dialogue(self) -> None:
        entry = self._dialogue_manager.get_current()
        if not entry:
            return
        self._dialogue_box.set_name(self._npc_name)
        self._dialogue_box.set_text(entry.get("text", ""))
        self._dialogue_box.set_choices(entry.get("choices", []))
        self._dialogue_box.show()

    def _on_dialogue_advance(self, choice_index: int) -> None:
        if choice_index == -1:
            return

        result = self._dialogue_manager.advance(choice_index)

        if result.affinity_delta != 0 and self.npc_registry:
            self.npc_registry.change_affinity(self._npc_id, result.affinity_delta)

        if self._dialogue_manager.is_finished():
            self._dialogue_box.hide()
            self._dialogue_active = False
            print(f"[DateEnding] Dialogue done -> Cashier")
            if self._scene_manager:
                self._scene_manager.transition_to("Cashier")
        else:
            self._show_current_dialogue()


    def render(self) -> None:
        if not self.screen:
            return

        sw, sh = Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT

        if self._bg_img:
            self.screen.blit(self._bg_img, (0, 0))
        else:
            self._draw_bg_fallback(sw, sh)

        if self._npc_img:
            self.screen.blit(self._npc_img,
                (Constant.DATE_ROOM_SUNSET_NPC_X,
                 Constant.DATE_ROOM_SUNSET_NPC_Y))
        else:
            fw, fh = 300, 450
            fx = sw // 2 - fw // 2
            fy = 150
            rect = pygame.Rect(fx, fy, fw, fh)
            pygame.draw.rect(self.screen, (190, 140, 190), rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=10)
            f = pygame.font.Font(None, 24)
            lbl = f.render(f"{self._npc_name}", True, (255, 255, 255))
            self.screen.blit(lbl, lbl.get_rect(centerx=fx + fw // 2,
                                                centery=fy + fh // 2))

        # Mood tier label 
        f_tier = pygame.font.Font(None, 32)
        if self._mood >= 80:
            tier_text = "Perfect Date!"
            tier_color = (255, 200, 100)
        elif self._mood >= 50:
            tier_text = "Good Date"
            tier_color = (180, 220, 100)
        else:
            tier_text = "Awkward Date..."
            tier_color = (220, 180, 80)
        tier_s = f_tier.render(tier_text, True, tier_color)
        tier_r = tier_s.get_rect(centerx=sw // 2, y=60)
        plate = tier_r.inflate(30, 12)
        ps = pygame.Surface(plate.size, pygame.SRCALPHA)
        ps.fill((0, 0, 0, 120))
        self.screen.blit(ps, plate)
        self.screen.blit(tier_s, tier_r)

        if self._dialogue_active:
            self._dialogue_box.render(self.screen)

        # Fade overlay 
        if self._fade_alpha > 0:
            fade_surf = pygame.Surface((sw, sh))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(int(self._fade_alpha))
            self.screen.blit(fade_surf, (0, 0))

    # BG Fallback

    def _draw_bg_fallback(self, sw: int, sh: int) -> None:
        for y in range(sh):
            t = y / sh
            r = int(255 - t * 100)
            g = int(140 - t * 80)
            b = int(60 + t * 60)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (sw, y))
        pygame.draw.circle(self.screen, (255, 200, 80), (sw // 2, 200), 60)
        pygame.draw.circle(self.screen, (255, 230, 150), (sw // 2, 200), 40)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self._fading_in:
            return

        if self._dialogue_active:
            result = self._dialogue_box.handle_event(event)
            if result != -1:
                self._on_dialogue_advance(result)