import pygame
import sys
import Constant
from Core.AudioManager import AudioManager
from Core.SceneManager import SceneManager
from Core.MainMenu import MainMenu
from Core.SaveManager import SaveManager
from Core.DialogueTracker import DialogueTracker
from Core.EventTracker import EventTracker
from Order.Cake import Cake
from Room.Cashier import Cashier
from Room.Decoration import Decoration
from Room.RoomBaking import BakingRoom
from Room.Dough import Dough
from Room.EndingRoom import EndingRoom
from Room.DateCutscene import DateCutscene
from Room.DateRoom import DateRoom
from Room.DateEndingScene import DateEndingScene
from Character.NPCRegistry import NPCRegistry


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(Constant.GAME_TITLE)

        self.screen = pygame.display.set_mode(
            (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self.running = False

        self.audio = AudioManager()
        self.audio.register_defaults()

        self.save_manager = SaveManager(Constant.SAVE_FILE)

        self.npc_registry = NPCRegistry(Constant.DATA_DIR)
        saved_affinity = self.save_manager.load_affinity()
        if saved_affinity:
            self.npc_registry.load_affinity(saved_affinity)

        self.dialogue_tracker = DialogueTracker()
        saved_tracker = self.save_manager.load_dialogue_tracker()
        if saved_tracker:
            self.dialogue_tracker.load_save_data(saved_tracker)

        # Date Event Tracker 
        self.date_event_tracker = EventTracker()
        saved_date_events = self.save_manager.load_date_events()
        if saved_date_events:
            self.date_event_tracker.load_save_data(saved_date_events)

        self.scene_manager = SceneManager(self.screen, self.audio)

        self.cake = Cake()

        # Rooms
        main_menu       = MainMenu()
        cashier         = Cashier(self.npc_registry, self.save_manager,
                                  self.dialogue_tracker, self.audio)
        dekorasi        = Decoration()
        baking          = BakingRoom()
        dough           = Dough()
        ending_room     = EndingRoom()
        date_cutscene   = DateCutscene(self.npc_registry,
                                       self.date_event_tracker, self.audio)
        date_room       = DateRoom(self.npc_registry, self.audio)
        date_ending     = DateEndingScene(self.npc_registry, self.audio)

        main_menu.screen       = self.screen
        cashier.screen         = self.screen
        dekorasi.screen        = self.screen
        baking.screen          = self.screen
        dough.screen           = self.screen
        ending_room.screen     = self.screen
        date_cutscene.screen   = self.screen
        date_room.screen       = self.screen
        date_ending.screen     = self.screen

        cashier.cake  = self.cake
        dough.cake    = self.cake
        baking.cake   = self.cake
        dekorasi.cake = self.cake

        baking.audio = self.audio

        # Register rooms 
        self.scene_manager.register_room(cashier)
        self.scene_manager.register_room(dough)
        self.scene_manager.register_room(baking)
        self.scene_manager.register_room(dekorasi)

        self.scene_manager.register_hidden_room(ending_room)
        self.scene_manager.register_hidden_room(main_menu)
        self.scene_manager.register_hidden_room(date_cutscene)
        self.scene_manager.register_hidden_room(date_room)
        self.scene_manager.register_hidden_room(date_ending)

        main_menu.set_scene_manager(self.scene_manager)
        cashier.set_scene_manager(self.scene_manager)
        ending_room.set_scene_manager(self.scene_manager)
        date_cutscene.set_scene_manager(self.scene_manager)
        date_room.set_scene_manager(self.scene_manager)
        date_ending.set_scene_manager(self.scene_manager)

        # Inject date dependencies 
        cashier._date_event_tracker = self.date_event_tracker
        cashier._date_cutscene      = date_cutscene
        date_cutscene._date_room    = date_room
        date_room._date_ending_scene = date_ending

        self.scene_manager.current_room = main_menu
        main_menu.enter()

        self.audio.play_bgm("main_menu")

        self.scene_manager.navigation_ui.build_buttons(
            self.scene_manager.get_room_names()
        )
        self.scene_manager.navigation_ui.set_room(main_menu.name)

    def run(self):
        self.running = True
        while self.running:
            delta_time = self.clock.get_time() / 1000.0
            self._handle_events()
            self._update(delta_time)
            self._render()
            self.clock.tick(Constant.FPS)
        pygame.quit()
        sys.exit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_on_exit()
                self.running = False
                return
            self.scene_manager.handle_event(event)

    def _update(self, delta_time: float) -> None:
        self.audio.update(delta_time)
        self.scene_manager.update(delta_time)

    def _render(self) -> None:
        self.screen.fill((0, 0, 0))
        self.scene_manager.render()
        pygame.display.flip()

    def _save_on_exit(self) -> None:
        self.audio.stop_bgm()
        affinity = self.npc_registry.get_all_affinity()
        self.save_manager.save_affinity(affinity)
        tracker_data = self.dialogue_tracker.get_save_data()
        self.save_manager.save_dialogue_tracker(tracker_data)
        date_event_data = self.date_event_tracker.get_save_data()
        self.save_manager.save_date_events(date_event_data)
        print("[Game] Save on exit complete")