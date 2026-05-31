import pygame
import sys
import Constant
from Core.SceneManager import SceneManager
from Core.MainMenu import MainMenu
from Core.SaveManager import SaveManager
from Core.DialogueTracker import DialogueTracker
from Room.Cashier import Cashier
from Room.Decoration import Decoration
from Room.RoomBaking import BakingRoom
from Room.Dough import Dough
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

        self.save_manager = SaveManager(Constant.SAVE_FILE)

        self.npc_registry = NPCRegistry(Constant.DATA_DIR)
        saved_affinity = self.save_manager.load_affinity()
        if saved_affinity:
            self.npc_registry.load_affinity(saved_affinity)

        # DialogueTracker
        self.dialogue_tracker = DialogueTracker()
        saved_tracker = self.save_manager.load_dialogue_tracker()
        if saved_tracker:
            self.dialogue_tracker.load_save_data(saved_tracker)

        self.scene_manager = SceneManager(self.screen)

        # Rooms
        main_menu = MainMenu()
        cashier = Cashier(self.npc_registry, self.save_manager,
                          self.dialogue_tracker)
        dekorasi = Decoration()
        baking = BakingRoom()
        dough = Dough()

        main_menu.screen = self.screen
        cashier.screen = self.screen
        dekorasi.screen = self.screen
        baking.screen = self.screen
        dough.screen = self.screen

        self.scene_manager.room_cashier = cashier
        self.scene_manager.room_decoration = dekorasi
        self.scene_manager.room_baking = baking
        self.scene_manager.room_dough = dough

        main_menu.set_scene_manager(self.scene_manager)
        cashier.set_scene_manager(self.scene_manager)

        self.scene_manager.current_room = main_menu
        main_menu.enter()

        self.scene_manager.navigation_ui.build_buttons(
            self.scene_manager.get_room_names()
        )
        self.scene_manager.navigation_ui.set_room(main_menu.name)

    def run(self):
        self.running = True
        while self.running:
            self._handle_events()
            self._update()
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

    def _update(self) -> None:
        self.scene_manager.update()

    def _render(self) -> None:
        self.screen.fill((0, 0, 0))
        self.scene_manager.render()
        pygame.display.flip()

    def _save_on_exit(self) -> None:
        affinity = self.npc_registry.get_all_affinity()
        self.save_manager.save_affinity(affinity)
        # Phase 7: save dialogue tracker
        tracker_data = self.dialogue_tracker.get_save_data()
        self.save_manager.save_dialogue_tracker(tracker_data)
        print("[Game] Save on exit complete")