import pygame
from Room.Room import Room
from Core.DialogueManager import DialogueManager
from UI.DialogueBox import DialogueBox
from Character.NPCRegistry import NPCRegistry
from Core.EventTracker import EventTracker
import Constant


class DateCutscene(Room):

    def __init__(
        self,
        npc_registry: NPCRegistry = None,
        date_event_tracker: EventTracker = None,
        audio=None,
    ):
        super().__init__("DateCutscene")

        self.npc_registry = npc_registry
        self.date_event_tracker = date_event_tracker
        self.audio = audio

        self.dialogue_manager = DialogueManager()
        self.dialogue_box = DialogueBox()

        self._npc_id: str = ""
        self._npc_name: str = "???"
        self._affinity_level: int = 0
        self._finished: bool = False
        self._player_accepted: bool = True

        # Injected from Game 
        self._date_room = None

        # Images
        self._bg_img: pygame.Surface | None = None
        self._npc_img: pygame.Surface | None = None

        # Fallback placeholder colors 
        self._fallback_bg_color   = (35, 30, 50)
        self._fallback_npc_color  = (180, 130, 180)

    # Asset loading 

    def _load_assets(self) -> None:
        # Background
        try:
            raw = pygame.image.load(Constant.DATE_CUTSCENE_BG).convert_alpha()
            self._bg_img = pygame.transform.scale(
                raw, (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
            print(f"[DateCutscene] BG loaded: {Constant.DATE_CUTSCENE_BG}")
        except Exception:
            print(f"[DateCutscene] BG not found: {Constant.DATE_CUTSCENE_BG}, using fallback")
            self._bg_img = None

        # NPC
        try:
            raw = pygame.image.load(Constant.DATE_CUTSCENE_NPC).convert_alpha()
            self._npc_img = pygame.transform.scale(
                raw, (Constant.DATE_CUTSCENE_NPC_W, Constant.DATE_CUTSCENE_NPC_H))
            print(f"[DateCutscene] NPC loaded: {Constant.DATE_CUTSCENE_NPC}")
        except Exception:
            print(f"[DateCutscene] NPC not found: {Constant.DATE_CUTSCENE_NPC}, using fallback")
            self._npc_img = None

    # Setup 

    def setup(self, npc_id: str, affinity_level: int) -> None:
        self._npc_id = npc_id
        self._affinity_level = affinity_level
        self._finished = False
        self._player_accepted = True

        if self.npc_registry:
            npc_data = self.npc_registry.get(npc_id)
            if npc_data:
                self._npc_name = npc_data.name

        self._load_assets()

        print(f"[DateCutscene] Setup: {self._npc_name} "
              f"(id={npc_id}, level={affinity_level})")

    # Lifecycle 

    def enter(self) -> None:
        self._finished = False
        self._player_accepted = True
        self.dialogue_manager.reset()
        self.dialogue_box.hide()
        self._start_cutscene_dialogue()

    def exit(self) -> None:
        pass    

    def update(self, delta_time: float = 0.0) -> None:
        if not self._finished:
            self.dialogue_box.update(delta_time, self.audio)


    def render(self) -> None:
        if not self.screen:
            return

        sw, sh = Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT

        # Background 
        if self._bg_img:
            self.screen.blit(self._bg_img, (0, 0))
        else:
            # Fallback
            for y in range(sh):
                t = y / sh
                color = self._lerp_color((45, 35, 65), (20, 15, 35), t)
                pygame.draw.line(self.screen, color, (0, y), (sw, y))

        # NPC 
        npc_x = Constant.DATE_CUTSCENE_NPC_X
        npc_y = Constant.DATE_CUTSCENE_NPC_Y
        npc_w = Constant.DATE_CUTSCENE_NPC_W
        npc_h = Constant.DATE_CUTSCENE_NPC_H

        if self._npc_img:
            self.screen.blit(self._npc_img, (npc_x, npc_y))
        else:
            # Fallback
            npc_rect = pygame.Rect(npc_x, npc_y, npc_w, npc_h)
            pygame.draw.rect(self.screen, self._fallback_npc_color, npc_rect,
                             border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), npc_rect, 2,
                             border_radius=8)
            f = pygame.font.Font(None, 28)
            lbl = f.render(f"[{self._npc_name}]", True, (255, 255, 255))
            self.screen.blit(lbl, lbl.get_rect(centerx=npc_rect.centerx,
                                                bottom=npc_rect.top - 8))

        # NPC name label 
        f_name = pygame.font.Font(None, 30)
        name_surf = f_name.render(self._npc_name, True, (255, 255, 255))
        name_rect = name_surf.get_rect(
            centerx=npc_x + npc_w // 2, bottom=npc_y - 12)
        # Name plate bg
        plate = name_rect.inflate(24, 10)
        plate_surf = pygame.Surface(plate.size, pygame.SRCALPHA)
        plate_surf.fill((0, 0, 0, 140))
        self.screen.blit(plate_surf, plate)
        self.screen.blit(name_surf, name_rect)

        # Info bar
        affinity_val = (self.npc_registry.get_affinity(self._npc_id)
                        if self.npc_registry else "?")
        info_font = pygame.font.Font(None, 22)
        info_text = f"Level: {self._affinity_level}  |  Affinity: {affinity_val}"
        info_surf = info_font.render(info_text, True, (200, 200, 200))
        self.screen.blit(info_surf, (16, 16))

        # Dialogue box 
        self.dialogue_box.render(self.screen)

    # Events 

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._finished:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            result = self.dialogue_box.handle_event(event)
            if result != -1:
                self._on_dialogue_advance(result)

    # Dialogue flow

    def _start_cutscene_dialogue(self) -> None:
        entries = [
            {"id": "dc_1", "text": "Hei... udah lama kita gak ngobrol bareng.",
             "next": "dc_2"},
            {"id": "dc_2", "text": "Kali-kali... mau jalan-jalan sama aku?",
             "choices": [
                 {"text": "Mau dong!",       "affinity": 3,  "next": "dc_yes"},
                 {"text": "Boleh juga...",    "affinity": 1,  "next": "dc_ok"},
                 {"text": "Lain kali aja deh","affinity": -1, "next": "dc_no"},
             ]},
            {"id": "dc_yes", "text": "Serius?! Yeay! Ayo kita pergi!", "next": None},
            {"id": "dc_ok",  "text": "Hehe... oke deh, yuk!", "next": None},
            {"id": "dc_no",  "text": "Oh... oke deh... lain kali ya...", "next": None},
        ]
        self.dialogue_manager.start(entries)
        self._show_current_dialogue()

    def _show_current_dialogue(self) -> None:
        entry = self.dialogue_manager.get_current()
        if not entry:
            return
        self.dialogue_box.set_name(self._npc_name)
        self.dialogue_box.set_text(entry.get("text", ""))
        self.dialogue_box.set_choices(entry.get("choices", []))
        self.dialogue_box.show()

    def _on_dialogue_advance(self, choice_index: int) -> None:
        if choice_index == -1:
            return

        result = self.dialogue_manager.advance(choice_index)

        if result.affinity_delta > 0:
            self._player_accepted = True
        elif result.affinity_delta < 0:
            self._player_accepted = False

        if result.affinity_delta != 0 and self.npc_registry:
            self.npc_registry.change_affinity(
                self._npc_id, result.affinity_delta)

        if self.dialogue_manager.is_finished():
            self._finish_cutscene()
        else:
            self._show_current_dialogue()

    def _finish_cutscene(self) -> None:
        self.dialogue_box.hide()
        self._finished = True

        if self.date_event_tracker:
            self.date_event_tracker.mark_triggered(
                self._npc_id, self._affinity_level)

        if self._player_accepted:
            print("[DateCutscene] Player ACCEPTED -> DateRoom")
            if self._date_room:
                self._date_room.setup(self._npc_id, self._affinity_level)
            if self._scene_manager:
                self._scene_manager.transition_to(self._date_room)
        else:
            print("[DateCutscene] Player REJECTED -> Cashier")
            if self._scene_manager:
                self._scene_manager.transition_to("Cashier")

    # Color helper 

    @staticmethod
    def _lerp_color(a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))