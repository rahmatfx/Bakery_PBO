import pygame
import sys
import Constant
from Core.SceneManager import SceneManager
from Core.MainMenu import MainMenu


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(Constant.GAME_TITLE)

        self.screen = pygame.display.set_mode((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = False

        self.scene_manager = SceneManager(self.screen)

        main_menu = MainMenu()
        main_menu._scene_manager = self.scene_manager

        main_menu.screen = self.screen
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

        pygame.QUIT()
        sys.exit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            self.scene_manager.handle_event(event)
            
    def _update(self) -> None:
        self.scene_manager.update()

    def _render(self) -> None:
        self.screen.fill((0, 0, 0))
        self.scene_manager.render()
        pygame.display.flip()