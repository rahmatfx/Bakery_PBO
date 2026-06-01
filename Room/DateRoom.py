import pygame
import math
import random
from Room.Room import Room
from Character.NPCRegistry import NPCRegistry
from Core.DialogueManager import DialogueManager
from UI.DialogueBox import DialogueBox
import Constant


class DateRoom(Room):

    def __init__(self, npc_registry: NPCRegistry = None, audio=None):
        super().__init__("DateRoom")

        self.npc_registry = npc_registry
        self.audio = audio

        self._npc_id: str = ""
        self._npc_name: str = "???"
        self._affinity_level: int = 0
      
        self._dialogue_manager = DialogueManager()
        self._dialogue_box = DialogueBox()
        self._dialogue_active: bool = False

        self._spots = [
            {"name": "Taman",      "desc": "Taman yang asri dengan bunga-bunga..."},
            {"name": "Food Stall", "desc": "Aroma makanan yang menggoda..."},
            {"name": "Danau",      "desc": "Danau yang tenang dengan pemandangan indah..."},
            {"name": "Sunset Hill","desc": "Bukit dengan pemandangan sunset..."},
        ]
        self._current_spot: int = -1
        self._spot_interacted: bool = False

        self._state: str = "WALKING"

        # Parallax 
        self._parallax_offset: float = 0.0
        self._parallax_speed: float = 100.0
        self._walk_timer: float = 0.0
        self._walk_duration: float = 2.5
        self._bob_timer: float = 0.0

        # Mood Meter
        self._mood: float = 50.0
        self._mood_max: float = 100.0

        # Random Encounter
        self._encounter_count: int = 0
        self._encounter_max: int = 2
        self._encounter_chance: float = 0.4
        self._encounter_type: str = ""

        self._date_ending_scene = None

        #  Walking images (parallax scene)
        self._npc_date_img: pygame.Surface | None = None
        self._mc_date_img: pygame.Surface | None  = None
        self._bg_img: pygame.Surface | None = None
        self._cloud_img: pygame.Surface | None = None
        self._tree_img: pygame.Surface | None = None
        self._flower_img: pygame.Surface | None = None
        self._bush_img: pygame.Surface | None = None

        # Spot backgrounds (full scene saat AT_SPOT)
        self._spot_bgs: dict[int, pygame.Surface | None] = {
            0: None, 1: None, 2: None, 3: None,
        }

        # Spot NPC images (full image saat AT_SPOT)
        self._spot_npcs: dict[int, pygame.Surface | None] = {
            0: None, 1: None, 2: None, 3: None,
        }

        self._assets_loaded: bool = False

        # UI rects 
        self._btn_interact: pygame.Rect | None = None
        self._btn_next: pygame.Rect | None = None
        self._btn_home: pygame.Rect | None = None

    # Asset loading 

    def _load_assets(self) -> None:
        # NPC walking sprite
        try:
            raw = pygame.image.load(Constant.DATE_ROOM_NPC_IMG).convert_alpha()
            self._npc_date_img = pygame.transform.scale(
                raw, (Constant.DATE_ROOM_NPC_W, Constant.DATE_ROOM_NPC_H))
            print(f"[DateRoom] NPC sprite loaded")
        except Exception:
            self._npc_date_img = None

        # MC walking sprite
        try:
            raw = pygame.image.load(Constant.DATE_ROOM_MC_IMG).convert_alpha()
            self._mc_date_img = pygame.transform.scale(
                raw, (Constant.DATE_ROOM_MC_W, Constant.DATE_ROOM_MC_H))
            print(f"[DateRoom] MC sprite loaded")
        except Exception:
            self._mc_date_img = None

        # Background (static gunung)
        try:
            raw = pygame.image.load(Constant.DATE_ROOM_BG).convert()
            self._bg_img = pygame.transform.scale(
                raw, (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
            print(f"[DateRoom] BG loaded")
        except Exception:
            self._bg_img = None

        # Cloud (FAR parallax)
        try:
            raw = pygame.image.load(Constant.DATE_ROOM_CLOUD_IMG).convert_alpha()
            self._cloud_img = pygame.transform.scale(
                raw, (Constant.DATE_ROOM_CLOUD_W, Constant.DATE_ROOM_CLOUD_H))
            print(f"[DateRoom] Cloud loaded")
        except Exception:
            self._cloud_img = None

        # Tree (MID parallax)
        try:
            raw = pygame.image.load(Constant.DATE_ROOM_TREE_IMG).convert_alpha()
            self._tree_img = pygame.transform.scale(
                raw, (Constant.DATE_ROOM_TREE_W, Constant.DATE_ROOM_TREE_H))
            print(f"[DateRoom] Tree loaded")
        except Exception:
            self._tree_img = None

        # Flower (NEAR parallax)
        try:
            raw = pygame.image.load(Constant.DATE_ROOM_FLOWER_IMG).convert_alpha()
            self._flower_img = pygame.transform.scale(
                raw, (Constant.DATE_ROOM_FLOWER_W, Constant.DATE_ROOM_FLOWER_H))
            print(f"[DateRoom] Flower loaded")
        except Exception:
            self._flower_img = None

        # Bush (ground decoration)
        try:
            raw = pygame.image.load(Constant.DATE_ROOM_BUSH_IMG).convert_alpha()
            self._bush_img = pygame.transform.scale(
                raw, (Constant.DATE_ROOM_BUSH_W, Constant.DATE_ROOM_BUSH_H))
            print(f"[DateRoom] Bush loaded")
        except Exception:
            self._bush_img = None

        # Spot backgrounds (full scene) 
        spot_bg_config = {
            0: (Constant.DATE_ROOM_TAMAN_BG,  "Taman BG"),
            1: (Constant.DATE_ROOM_STALL_BG,  "Stall BG"),
            2: (Constant.DATE_ROOM_DANAU_BG,  "Danau BG"),
            3: (Constant.DATE_ROOM_SUNSET_BG, "Sunset BG"),
        }
        for idx, (path, label) in spot_bg_config.items():
            try:
                raw = pygame.image.load(path).convert()
                self._spot_bgs[idx] = pygame.transform.scale(
                    raw, (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
                print(f"[DateRoom] {label} loaded")
            except Exception:
                self._spot_bgs[idx] = None

        # Spot NPC images (full image per spot) 
        spot_npc_config = {
            0: (Constant.DATE_ROOM_TAMAN_NPC,  Constant.DATE_ROOM_TAMAN_NPC_W,
                Constant.DATE_ROOM_TAMAN_NPC_H,  "Taman NPC"),
            1: (Constant.DATE_ROOM_STALL_NPC,  Constant.DATE_ROOM_STALL_NPC_W,
                Constant.DATE_ROOM_STALL_NPC_H,  "Stall NPC"),
            2: (Constant.DATE_ROOM_DANAU_NPC,  Constant.DATE_ROOM_DANAU_NPC_W,
                Constant.DATE_ROOM_DANAU_NPC_H,  "Danau NPC"),
            3: (Constant.DATE_ROOM_SUNSET_NPC, Constant.DATE_ROOM_SUNSET_NPC_W,
                Constant.DATE_ROOM_SUNSET_NPC_H, "Sunset NPC"),
        }
        for idx, (path, w, h, label) in spot_npc_config.items():
            try:
                raw = pygame.image.load(path).convert_alpha()
                self._spot_npcs[idx] = pygame.transform.scale(raw, (w, h))
                print(f"[DateRoom] {label} loaded")
            except Exception:
                self._spot_npcs[idx] = None

        self._assets_loaded = True

    # Setup 

    def setup(self, npc_id: str, affinity_level: int) -> None:
        self._npc_id = npc_id
        self._affinity_level = affinity_level
        self._current_spot = -1
        self._spot_interacted = False
        self._state = "WALKING"
        self._walk_timer = 0.0
        self._parallax_offset = 0.0
        self._bob_timer = 0.0
        self._mood = 50.0
        self._encounter_count = 0
        self._encounter_type = ""
        self._dialogue_active = False
        self._dialogue_manager.reset()
        self._dialogue_box.hide()

        if self.npc_registry:
            npc_data = self.npc_registry.get(npc_id)
            if npc_data:
                self._npc_name = npc_data.name

        self._load_assets()
        print(f"[DateRoom] Setup: {self._npc_name}, level={affinity_level}, mood=50")


    def enter(self) -> None:
        if not self._assets_loaded:
            self._load_assets()
        self._current_spot = -1
        self._spot_interacted = False
        self._state = "WALKING"
        self._walk_timer = 0.0
        self._parallax_offset = 0.0
        self._bob_timer = 0.0
        self._mood = 50.0
        self._encounter_count = 0
        self._dialogue_active = False
        self._dialogue_manager.reset()
        self._dialogue_box.hide()
        print("[DateRoom] Entered — walking to first spot")


    def update(self, delta_time: float = 0.0) -> None:
        self._bob_timer += delta_time

        if self._state == "WALKING":
            self._walk_timer += delta_time
            self._parallax_offset += self._parallax_speed * delta_time
            if self._walk_timer >= self._walk_duration:
                self._arrive_at_spot()

        if self._dialogue_active:
            self._dialogue_box.update(delta_time, self.audio)

    # Arrive / Depart

    def _arrive_at_spot(self) -> None:
        self._current_spot += 1
        self._spot_interacted = False
        self._state = "AT_SPOT"
        self._dialogue_active = False
        spot = self._spots[self._current_spot]
        print(f"[DateRoom] Arrived at spot {self._current_spot}: {spot['name']}")

    def _depart_spot(self) -> None:
        if (self._encounter_count < self._encounter_max
                and random.random() < self._encounter_chance
                and self._current_spot < len(self._spots) - 1):
            self._start_encounter()
            return
        self._start_walking()

    def _start_walking(self) -> None:
        self._state = "WALKING"
        self._walk_timer = 0.0
        next_idx = self._current_spot + 1
        if next_idx < len(self._spots):
            print(f"[DateRoom] Walking to {self._spots[next_idx]['name']}...")

    # Spot Interaction 

    def _start_spot_dialogue(self) -> None:
        entries = self._get_spot_dialogue(self._current_spot)
        if entries:
            self._dialogue_manager.start(entries)
            self._dialogue_active = True
            self._show_current_dialogue()
        else:
            self._spot_interacted = True

    def _show_current_dialogue(self) -> None:
        entry = self._dialogue_manager.get_current()
        if not entry:
            return
        self._dialogue_box.set_name(self._npc_name)
        self._dialogue_box.set_text(entry.get("text", ""))
        self._dialogue_box.set_choices(entry.get("choices", []))
        self._dialogue_box.show()

    def _on_spot_dialogue_advance(self, choice_index: int) -> None:
        if choice_index == -1:
            return

        choices = self._dialogue_manager.get_current_choices()
        if 0 <= choice_index < len(choices):
            mood_delta = choices[choice_index].get("mood", 0)
            self._change_mood(mood_delta)

        result = self._dialogue_manager.advance(choice_index)

        if result.affinity_delta != 0 and self.npc_registry:
            self.npc_registry.change_affinity(self._npc_id, result.affinity_delta)

        if self._dialogue_manager.is_finished():
            self._dialogue_box.hide()
            self._dialogue_active = False
            self._spot_interacted = True

            if self._current_spot == len(self._spots) - 1:
                print(f"[DateRoom] Sunset dialogue done -> DateEndingScene (mood={self._mood:.0f})")
                if self._date_ending_scene:
                    self._date_ending_scene.setup(
                        self._npc_id, self._affinity_level,
                        self._mood, self._npc_name)
                if self._scene_manager:
                    self._scene_manager.transition_to(self._date_ending_scene)
        else:
            self._show_current_dialogue()

    # Spot Dialogue Data

    def _get_spot_dialogue(self, spot_index: int) -> list[dict]:
        dialogues = {
            0: [
                {"id": "t1", "text": "Taman ini indah ya... udah lama gak ke sini.", "next": "t2"},
                {"id": "t2", "text": "Mau ngapain di sini?",
                 "choices": [
                     {"text": "Tanya tentang dirinya",        "affinity": 2, "mood": 15, "next": "ta"},
                     {"text": "Bercanda sama dia",             "affinity": 1, "mood": 10, "next": "tb"},
                     {"text": "Diam aja nikmatin pemandangan", "affinity": 0, "mood": 5,  "next": "tc"},
                 ]},
                {"id": "ta", "text": "Lucy tersipu... 'Kamu tiba-tiba aja nanya... tapi aku suka.'", "next": None},
                {"id": "tb", "text": "Lucy ketawa... 'Kamu memang suka bercanda ya! Lucu sih...'", "next": None},
                {"id": "tc", "text": "Dua-duanya diam... tapi nyaman. Angin semilir menyentuh wajah.", "next": None},
            ],
            1: [
                {"id": "f1", "text": "Wah, baunya enak banget! Aku laper nih...", "next": "f2"},
                {"id": "f2", "text": "Mau beli apa?",
                 "choices": [
                     {"text": "Beliin dia es krim",               "affinity": 3, "mood": 15, "next": "fa"},
                     {"text": "Tanya dulu dia mau apa",           "affinity": 2, "mood": 10, "next": "fb"},
                     {"text": "Pura-pura nggak lihat dia laper",  "affinity": -1, "mood": -10, "next": "fc"},
                 ]},
                {"id": "fa", "text": "'Ih, kamu perhatian banget! Terima kasih ya~' Lucy senang.", "next": None},
                {"id": "fb", "text": "'Hmm... aku mau yang manis-manis aja deh!' Lucy mikir serius.", "next": None},
                {"id": "fc", "text": "Lucy melirik dengan tatapan tidak senang... '...Baiklah.'", "next": None},
            ],
            2: [
                {"id": "d1", "text": "Danaunya tenang banget... kayak bisa lupa semuanya.", "next": "d2"},
                {"id": "d2", "text": "Ada batu di tepi danau, mau ngapain?",
                 "choices": [
                     {"text": "Skip batu ke danau bareng",  "affinity": 2, "mood": 15, "next": "da"},
                     {"text": "Duduk di tepi danau",         "affinity": 1, "mood": 10, "next": "db"},
                     {"text": "Usil percikin air ke dia",    "affinity": -1, "mood": -5, "next": "dc"},
                 ]},
                {"id": "da", "text": "'Hahaha kena! Aku juga skip ya!' Lucy melempar batu ke danau.", "next": None},
                {"id": "db", "text": "Kalian duduk di tepi danau... keheningan yang nyaman.", "next": None},
                {"id": "dc", "text": "'Ih! Basah nih!' Lucy cemberut, tapi sedikit tersenyum.", "next": None},
            ],
            3: [
                {"id": "s1", "text": "Matahari mulai terbenam... pemandangannya indah sekali.", "next": "s2"},
                {"id": "s2", "text": "Lucy menatapmu lembut... 'Makasih hari ini...'",
                 "choices": [
                     {"text": "Senang bisa bareng kamu",  "affinity": 3, "mood": 20, "next": "sa"},
                     {"text": "Iya, lumayan juga",        "affinity": 0, "mood": 5,  "next": "sb"},
                 ]},
                {"id": "sa", "text": "Lucy tersenyum hangat... matanya berbinar di cahaya sunset.", "next": None},
                {"id": "sb", "text": "Lucy mengangguk pelan... mungkin sedikit kecewa.", "next": None},
            ],
        }
        return dialogues.get(spot_index, [])

    # Random Encounter 

    def _start_encounter(self) -> None:
        self._encounter_count += 1
        encounter_types = ["rain", "friend", "fall"]
        self._encounter_type = random.choice(encounter_types)
        self._state = "ENCOUNTER"

        entries = self._get_encounter_dialogue(self._encounter_type)
        if entries:
            self._dialogue_manager.start(entries)
            self._dialogue_active = True
            self._show_current_dialogue()

        print(f"[DateRoom] Random encounter: {self._encounter_type}")

    def _get_encounter_dialogue(self, encounter_type: str) -> list[dict]:
        encounters = {
            "rain": [
                {"id": "r1", "text": "Hujan tiba-tiba turun! Payungmu cuma satu...", "next": "r2"},
                {"id": "r2", "text": "Apa yang harus dilakukan?",
                 "choices": [
                     {"text": "Bagi payung, aku basah gapapa", "affinity": 3, "mood": 20, "next": "ra"},
                     {"text": "Lari bareng ke tempat berteduh!",  "affinity": 1, "mood": 10, "next": "rb"},
                 ]},
                {"id": "ra", "text": "Lucy kaget... 'Kamu nggak apa-apa?' Matanya penuh perhatian.", "next": None},
                {"id": "rb", "text": "Kalian berlarian under hujan! Lucy tertawa riang.", "next": None},
            ],
            "friend": [
                {"id": "fr1", "text": "Teman Lucy lewat dan menyapa! 'Eh, Lucy! Lagi sama siapa?'", "next": "fr2"},
                {"id": "fr2", "text": "Bagaimana reaksimu?",
                 "choices": [
                     {"text": "Sapa balik dengan ramah",   "affinity": 2, "mood": 10, "next": "fra"},
                     {"text": "Biar Lucy aja yang ngobrol", "affinity": -1, "mood": -5, "next": "frb"},
                 ]},
                {"id": "fra", "text": "Lucy tersenyum bangga... 'Ini temanku!' bisiknya.", "next": None},
                {"id": "frb", "text": "Lucy tampak sedikit canggung... 'Yaudah, aku dulu ya.'", "next": None},
            ],
            "fall": [
                {"id": "fl1", "text": "Lucy terpeleset! 'Aww...'", "next": "fl2"},
                {"id": "fl2", "text": "Apa yang kamu lakukan?",
                 "choices": [
                     {"text": "Langsung bantu dia bangun", "affinity": 3, "mood": 15, "next": "fla"},
                     {"text": "Tawa dulu baru bantu",      "affinity": -1, "mood": -5, "next": "flb"},
                 ]},
                {"id": "fla", "text": "'Hati-hati ya...' Lucy tersenyum malu sambil berdiri.", "next": None},
                {"id": "flb", "text": "'Ih, jahat!' Lucy cemberut, tapi akhirnya ikut tertawa.", "next": None},
            ],
        }
        return encounters.get(encounter_type, [])

    def _on_encounter_advance(self, choice_index: int) -> None:
        if choice_index == -1:
            return

        choices = self._dialogue_manager.get_current_choices()
        if 0 <= choice_index < len(choices):
            mood_delta = choices[choice_index].get("mood", 0)
            self._change_mood(mood_delta)

        result = self._dialogue_manager.advance(choice_index)

        if result.affinity_delta != 0 and self.npc_registry:
            self.npc_registry.change_affinity(self._npc_id, result.affinity_delta)

        if self._dialogue_manager.is_finished():
            self._dialogue_box.hide()
            self._dialogue_active = False
            self._state = "WALKING"
            self._walk_timer = 0.0
            print(f"[DateRoom] Encounter done, continue walking (mood={self._mood:.0f})")
        else:
            self._show_current_dialogue()

    # Mood

    def _change_mood(self, delta: float) -> None:
        self._mood = max(0, min(self._mood_max, self._mood + delta))
        print(f"[DateRoom] Mood {'+' if delta >= 0 else ''}{delta} -> {self._mood:.0f}")


    def render(self) -> None:
        if not self.screen:
            return

        sw, sh = Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT

        #  Scene: WALKING = parallax, AT_SPOT/ENCOUNTER = spot BG + NPC ─
        if self._state in ("AT_SPOT", "ENCOUNTER"):
            # Spot background (full screen)
            spot_bg = self._spot_bgs.get(self._current_spot)
            if spot_bg:
                self.screen.blit(spot_bg, (0, 0))
            else:
                self._draw_spot_bg_fallback(sw, sh)

            # Spot NPC (full image)
            self._draw_spot_npc()

            # Encounter overlay
            if self._state == "ENCOUNTER":
                overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
                overlay.fill((0, 0, 30, 80))
                self.screen.blit(overlay, (0, 0))

                ef = pygame.font.Font(None, 36)
                labels = {"rain": "~ Hujan Tiba-tiba! ~",
                          "friend": "~ Teman Lucy! ~",
                          "fall": "~ Lucy Jatuh! ~"}
                et = ef.render(labels.get(self._encounter_type, "~ Event! ~"),
                              True, (255, 255, 150))
                self.screen.blit(et, et.get_rect(centerx=sw // 2, y=100))
        else:
            # Walking scene parallax layers
            if self._bg_img:
                self.screen.blit(self._bg_img, (0, 0))
            else:
                self.screen.fill((120, 180, 100))

            self._draw_cloud_layer()
            self._draw_tree_layer()
            self._draw_flower_layer()

            # Ground
            ground_y = 470
            pygame.draw.rect(self.screen, (80, 160, 60),
                             (0, ground_y, sw, sh - ground_y))

            # Bush
            self._draw_bush_layer()

            # Road
            road_y = ground_y + 10
            road_h = 55
            pygame.draw.rect(self.screen, (180, 170, 155),
                             (0, road_y, sw, road_h))
            dash_off = int(self._parallax_offset * 0.7) % 60
            for x in range(-dash_off, sw, 60):
                pygame.draw.rect(self.screen, (220, 210, 190),
                                 (x, road_y + road_h // 2 - 3, 30, 6))

            # Walking sprites
            self._draw_sprites()

        #  Mood Meter 
        self._draw_mood_meter()

        # Progress bar 
        self._draw_progress_bar()

        # State UI 
        if self._state == "WALKING":
            self._draw_walking_ui()
        elif self._state == "AT_SPOT":
            self._draw_at_spot_ui()

        # Dialogue box (on top) 
        if self._dialogue_active:
            self._dialogue_box.render(self.screen)

    # Cloud layer

    def _draw_cloud_layer(self) -> None:
        cw = Constant.DATE_ROOM_CLOUD_W
        cy = Constant.DATE_ROOM_CLOUD_Y
        speed = Constant.DATE_ROOM_CLOUD_SPEED
        gap = 100
        offset = int(self._parallax_offset * speed) % (cw + gap)
        sw = Constant.SCREEN_WIDTH

        if self._cloud_img:
            for i in range(-1, sw // (cw + gap) + 2):
                x = i * (cw + gap) - offset
                self.screen.blit(self._cloud_img, (x, cy))
        else:
            for i in range(-1, sw // (cw + gap) + 2):
                x = i * (cw + gap) - offset
                cloud_rect = pygame.Rect(x, cy, cw, Constant.DATE_ROOM_CLOUD_H)
                pygame.draw.ellipse(self.screen, (230, 230, 245), cloud_rect)

    # Tree layer (MID) 

    def _draw_tree_layer(self) -> None:
        tw = Constant.DATE_ROOM_TREE_W
        th = Constant.DATE_ROOM_TREE_H
        ty = Constant.DATE_ROOM_TREE_Y
        speed = Constant.DATE_ROOM_TREE_SPEED
        gap = Constant.DATE_ROOM_TREE_GAP
        offset = int(self._parallax_offset * speed) % (tw + gap)
        sw = Constant.SCREEN_WIDTH

        if self._tree_img:
            for i in range(-1, sw // (tw + gap) + 2):
                x = i * (tw + gap) - offset
                self.screen.blit(self._tree_img, (x, ty))
        else:
            for i in range(-1, sw // (tw + gap) + 2):
                x = i * (tw + gap) - offset
                pygame.draw.rect(self.screen, (100, 70, 30),
                                 (x + tw // 2 - 6, ty + th - 25, 12, 25))
                pts = [(x, ty + th - 20), (x + tw // 2, ty), (x + tw, ty + th - 20)]
                pygame.draw.polygon(self.screen, (50, 140, 50), pts)

    # Flower layer (NEAR) 

    def _draw_flower_layer(self) -> None:
        fw = Constant.DATE_ROOM_FLOWER_W
        fh = Constant.DATE_ROOM_FLOWER_H
        fy = Constant.DATE_ROOM_FLOWER_Y
        speed = Constant.DATE_ROOM_FLOWER_SPEED
        gap = Constant.DATE_ROOM_FLOWER_GAP
        offset = int(self._parallax_offset * speed) % (fw + gap)
        sw = Constant.SCREEN_WIDTH

        if self._flower_img:
            for i in range(-1, sw // (fw + gap) + 2):
                x = i * (fw + gap) - offset
                self.screen.blit(self._flower_img, (x, fy))
        else:
            for i in range(-1, sw // (fw + gap) + 2):
                x = i * (fw + gap) - offset
                pygame.draw.circle(self.screen, (220, 100, 100),
                                   (x + fw // 2, fy + fh // 2), fw // 3)
                pygame.draw.rect(self.screen, (50, 150, 50),
                                 (x + fw // 2 - 2, fy + fh // 2, 4, fh // 2))

    # Bush layer (ground decoration) 

    def _draw_bush_layer(self) -> None:
        bw = Constant.DATE_ROOM_BUSH_W
        bh = Constant.DATE_ROOM_BUSH_H
        by = Constant.DATE_ROOM_BUSH_Y
        speed = Constant.DATE_ROOM_BUSH_SPEED
        gap = Constant.DATE_ROOM_BUSH_GAP
        offset = int(self._parallax_offset * speed) % (bw + gap)
        sw = Constant.SCREEN_WIDTH

        if self._bush_img:
            for i in range(-1, sw // (bw + gap) + 2):
                x = i * (bw + gap) - offset
                self.screen.blit(self._bush_img, (x, by))
        else:
            for i in range(-1, sw // (bw + gap) + 2):
                x = i * (bw + gap) - offset
                pygame.draw.ellipse(self.screen, (60, 130, 50),
                                    (x, by, bw, bh))
                pygame.draw.ellipse(self.screen, (80, 155, 65),
                                    (x + 5, by + 3, bw - 10, bh - 6))

    # Walking Sprites 

    def _draw_sprites(self):
        is_walking = self._state == "WALKING"
        bob = int(Constant.DATE_ROOM_BOB_AMOUNT *
                  abs(math.sin(self._bob_timer * 10))) if is_walking else 0
        f = pygame.font.Font(None, 20)

        # MC (Player) 
        mc_x = Constant.DATE_ROOM_MC_X
        mc_y = Constant.DATE_ROOM_MC_Y - bob
        mc_w = Constant.DATE_ROOM_MC_W
        mc_h = Constant.DATE_ROOM_MC_H

        if self._mc_date_img:
            self.screen.blit(self._mc_date_img, (mc_x, mc_y))
        else:
            mc_rect = pygame.Rect(mc_x, mc_y, mc_w, mc_h)
            pygame.draw.rect(self.screen, (100, 180, 140), mc_rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 255, 255), mc_rect, 2, border_radius=6)

        lbl_mc = f.render("Player", True, (255, 255, 255))
        self.screen.blit(lbl_mc,
            lbl_mc.get_rect(centerx=mc_x + mc_w // 2, bottom=mc_y - 6))

        # NPC 
        npc_x = Constant.DATE_ROOM_NPC_X
        npc_y = Constant.DATE_ROOM_NPC_Y - bob
        npc_w = Constant.DATE_ROOM_NPC_W
        npc_h = Constant.DATE_ROOM_NPC_H

        if self._npc_date_img:
            self.screen.blit(self._npc_date_img, (npc_x, npc_y))
        else:
            npc_rect = pygame.Rect(npc_x, npc_y, npc_w, npc_h)
            pygame.draw.rect(self.screen, (190, 140, 190), npc_rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 255, 255), npc_rect, 2, border_radius=6)

        lbl_npc = f.render(self._npc_name, True, (255, 255, 255))
        self.screen.blit(lbl_npc,
            lbl_npc.get_rect(centerx=npc_x + npc_w // 2, bottom=npc_y - 6))

    # Spot NPC (full image, bukan walking sprite)

    def _draw_spot_npc(self) -> None:
        npc_img = self._spot_npcs.get(self._current_spot)
        spot = self._current_spot

        if npc_img:
            configs = {
                0: (Constant.DATE_ROOM_TAMAN_NPC_X,
                    Constant.DATE_ROOM_TAMAN_NPC_Y,
                    Constant.DATE_ROOM_TAMAN_NPC_W,
                    Constant.DATE_ROOM_TAMAN_NPC_H),
                1: (Constant.DATE_ROOM_STALL_NPC_X,
                    Constant.DATE_ROOM_STALL_NPC_Y,
                    Constant.DATE_ROOM_STALL_NPC_W,
                    Constant.DATE_ROOM_STALL_NPC_H),
                2: (Constant.DATE_ROOM_DANAU_NPC_X,
                    Constant.DATE_ROOM_DANAU_NPC_Y,
                    Constant.DATE_ROOM_DANAU_NPC_W,
                    Constant.DATE_ROOM_DANAU_NPC_H),
                3: (Constant.DATE_ROOM_SUNSET_NPC_X,
                    Constant.DATE_ROOM_SUNSET_NPC_Y,
                    Constant.DATE_ROOM_SUNSET_NPC_W,
                    Constant.DATE_ROOM_SUNSET_NPC_H),
            }
            x, y, w, h = configs.get(spot, (0, 0, 300, 500))
            self.screen.blit(npc_img, (x, y))
        else:
            # Fallback
            sw = Constant.SCREEN_WIDTH
            fallback_w, fallback_h = 300, 450
            fx = sw // 2 - fallback_w // 2
            fy = 150
            rect = pygame.Rect(fx, fy, fallback_w, fallback_h)
            pygame.draw.rect(self.screen, (190, 140, 190), rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=10)
            f = pygame.font.Font(None, 24)
            lbl = f.render(f"{self._npc_name} (NPC)", True, (255, 255, 255))
            self.screen.blit(lbl, lbl.get_rect(centerx=fx + fallback_w // 2,
                                                centery=fy + fallback_h // 2))

    # Spot BG Fallback (kalau image belum ada)

    def _draw_spot_bg_fallback(self, sw: int, sh: int) -> None:
        spot = self._current_spot

        if spot == 0:  # Taman
            self.screen.fill((120, 190, 100))
            # Bangku taman
            pygame.draw.rect(self.screen, (139, 90, 43),
                             (sw // 2 - 100, 400, 200, 15), border_radius=3)
            pygame.draw.rect(self.screen, (139, 90, 43),
                             (sw // 2 - 100, 360, 8, 55))
            pygame.draw.rect(self.screen, (139, 90, 43),
                             (sw // 2 + 92, 360, 8, 55))
            # Bunga besar
            for cx, cy in [(200, 350), (900, 320), (1050, 370)]:
                pygame.draw.circle(self.screen, (220, 100, 120), (cx, cy), 25)
                pygame.draw.circle(self.screen, (255, 160, 180), (cx, cy), 15)

        elif spot == 1:  # Food Stall
            self.screen.fill((200, 180, 150))
            # Atap stall
            pygame.draw.rect(self.screen, (180, 60, 40),
                             (sw // 2 - 180, 200, 360, 25))
            # Badan stall
            pygame.draw.rect(self.screen, (210, 170, 120),
                             (sw // 2 - 170, 225, 340, 200))
            # Meja
            pygame.draw.rect(self.screen, (160, 110, 60),
                             (sw // 2 - 160, 380, 320, 20), border_radius=3)

        elif spot == 2:  # Danau
            # Langit
            self.screen.fill((140, 200, 240))
            # Danau besar — beneran luas
            pygame.draw.ellipse(self.screen, (60, 130, 190),
                                (100, 250, sw - 200, 300))
            pygame.draw.ellipse(self.screen, (80, 160, 220),
                                (180, 290, sw - 360, 200))
            # Batu tepi
            for rx in [150, 350, sw - 350, sw - 200]:
                pygame.draw.ellipse(self.screen, (140, 140, 140),
                                    (rx, 500, 60, 30))

        elif spot == 3:  # Sunset
            # Gradient sunset
            for y in range(sh):
                t = y / sh
                r = int(255 - t * 80)
                g = int(140 - t * 80)
                b = int(60 + t * 60)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (sw, y))
            # Matahari
            pygame.draw.circle(self.screen, (255, 200, 80),
                               (sw // 2, 200), 60)
            pygame.draw.circle(self.screen, (255, 230, 150),
                               (sw // 2, 200), 40)

    # Mood Meter

    def _draw_mood_meter(self):
        x, y, w, h = 30, 120, 28, 300

        f = pygame.font.Font(None, 22)
        lbl = f.render("Mood", True, (255, 255, 255))
        self.screen.blit(lbl, lbl.get_rect(centerx=x + w // 2, bottom=y - 6))

        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, w, h), border_radius=6)

        ratio = self._mood / self._mood_max
        fill_h = int(h * ratio)
        if fill_h > 0:
            if self._mood < 30:
                color = (220, 80, 80)
            elif self._mood < 60:
                color = (220, 180, 80)
            elif self._mood < 80:
                color = (180, 220, 100)
            else:
                color = (255, 150, 200)

            fill_rect = pygame.Rect(x, y + h - fill_h, w, fill_h)
            pygame.draw.rect(self.screen, color, fill_rect, border_radius=6)

        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, w, h), 2, border_radius=6)

        val = f.render(f"{self._mood:.0f}", True, (255, 255, 255))
        self.screen.blit(val, val.get_rect(centerx=x + w // 2, top=y + h + 6))

    # Progress bar 

    def _draw_progress_bar(self):
        sw = Constant.SCREEN_WIDTH
        bx, by, bw, bh = 80, 80, sw - 160, 6

        pygame.draw.rect(self.screen, (40, 40, 40), (bx, by, bw, bh), border_radius=3)

        total = len(self._spots)
        if self._state == "WALKING":
            prog = (self._current_spot + 1 + self._walk_timer / self._walk_duration) / total
        else:
            prog = (self._current_spot + 1) / total
        prog = min(1.0, max(0.0, prog))

        fill = int(bw * prog)
        if fill > 0:
            pygame.draw.rect(self.screen, (255, 200, 100),
                             (bx, by, fill, bh), border_radius=3)

        f = pygame.font.Font(None, 18)
        for i, spot in enumerate(self._spots):
            mx = bx + int(bw * (i + 0.5) / total)
            c = (255, 255, 255) if i <= self._current_spot else (140, 140, 140)
            pygame.draw.circle(self.screen, c, (mx, by + bh // 2), 8)
            s = f.render(spot["name"], True, c)
            self.screen.blit(s, s.get_rect(centerx=mx, top=by + 14))

    # Walking UI

    def _draw_walking_ui(self):
        sw = Constant.SCREEN_WIDTH
        next_idx = self._current_spot + 1
        if 0 <= next_idx < len(self._spots):
            f = pygame.font.Font(None, 36)
            txt = f.render(f"Menuju {self._spots[next_idx]['name']}...",
                           True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(centerx=sw // 2, y=110))
            pct = min(100, int(self._walk_timer / self._walk_duration * 100))
            f2 = pygame.font.Font(None, 24)
            p = f2.render(f"{pct}%", True, (200, 200, 200))
            self.screen.blit(p, p.get_rect(centerx=sw // 2, y=146))

    # At-Spot UI

    def _draw_at_spot_ui(self):
        sw, sh = Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT
        spot = self._spots[self._current_spot]

        f_big = pygame.font.Font(None, 44)
        name_s = f_big.render(spot["name"], True, (255, 255, 255))
        nr = name_s.get_rect(centerx=sw // 2, y=100)
        plate = nr.inflate(40, 16)
        ps = pygame.Surface(plate.size, pygame.SRCALPHA)
        ps.fill((0, 0, 0, 120))
        self.screen.blit(ps, plate)
        self.screen.blit(name_s, nr)

        f_desc = pygame.font.Font(None, 26)
        ds = f_desc.render(spot["desc"], True, (220, 220, 220))
        self.screen.blit(ds, ds.get_rect(centerx=sw // 2, y=150))

        bw, bh = 200, 50
        bx = sw - bw - 60
        by = sh - bh - 60

        if not self._spot_interacted:
            self._btn_interact = pygame.Rect(bx, by, bw, bh)
            self._btn_next = None
            self._btn_home = None
            pygame.draw.rect(self.screen, (100, 180, 100),
                             self._btn_interact, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255),
                             self._btn_interact, 2, border_radius=10)
            bf = pygame.font.Font(None, 28)
            bt = bf.render("Ajak Ngobrol", True, (255, 255, 255))
            self.screen.blit(bt, bt.get_rect(center=self._btn_interact.center))
        else:
            self._btn_interact = None
            is_last = self._current_spot == len(self._spots) - 1

            if is_last:
                self._btn_home = pygame.Rect(bx, by, bw, bh)
                self._btn_next = None
                pygame.draw.rect(self.screen, (180, 80, 130),
                                 self._btn_home, border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 self._btn_home, 2, border_radius=10)
                bf = pygame.font.Font(None, 28)
                bt = bf.render("Ke Sunset...", True, (255, 255, 255))
                self.screen.blit(bt, bt.get_rect(center=self._btn_home.center))
            else:
                self._btn_next = pygame.Rect(bx, by, bw, bh)
                self._btn_home = None
                pygame.draw.rect(self.screen, (80, 140, 200),
                                 self._btn_next, border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 self._btn_next, 2, border_radius=10)
                bf = pygame.font.Font(None, 30)
                bt = bf.render("Lanjut ->", True, (255, 255, 255))
                self.screen.blit(bt, bt.get_rect(center=self._btn_next.center))

    # Events 

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self._dialogue_active:
            result = self._dialogue_box.handle_event(event)
            if result != -1:
                if self._state == "ENCOUNTER":
                    self._on_encounter_advance(result)
                else:
                    self._on_spot_dialogue_advance(result)
            return

        if self._state == "AT_SPOT":
            if self._btn_interact and self._btn_interact.collidepoint(event.pos):
                self._start_spot_dialogue()
            elif self._btn_next and self._btn_next.collidepoint(event.pos):
                self._depart_spot()
            elif self._btn_home and self._btn_home.collidepoint(event.pos):
                print(f"[DateRoom] Going to DateEndingScene (mood={self._mood:.0f})")
                if self._date_ending_scene:
                    self._date_ending_scene.setup(
                        self._npc_id, self._affinity_level,
                        self._mood, self._npc_name)
                if self._scene_manager:
                    self._scene_manager.transition_to(self._date_ending_scene)

    # Color helpers

    @staticmethod
    def _lerp_color(a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

    @staticmethod
    def _darken(c, amt):
        return tuple(max(0, v - amt) for v in c)

    @staticmethod
    def _lighten(c, amt):
        return tuple(min(255, v + amt) for v in c)
