import pygame, os
from Room.Room import Room
from Constant import SCREEN_WIDTH, SCREEN_HEIGHT, BAKING_BG, COLOR_BG_CREAM, COLOR_DARK_BROWN, FONT_HEADING_SIZE, FONT_BODY_SIZE, FONT_NAME

class BakingRoom(Room):
    def __init__(self):
        super().__init__(name="Baking")
        self._bg_image = None
        self._font_heading = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)

    def enter(self):
        if os.path.exists(BAKING_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(BAKING_BG).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    def update(self): pass

    def render(self):
        if not self.screen: return
        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))
        else:
            self.screen.fill(COLOR_BG_CREAM)
            t = self._font_heading.render("~ Cashier ~", True, COLOR_DARK_BROWN)
            self.screen.blit(t, t.get_rect(centerx=SCREEN_WIDTH//2, centery=SCREEN_HEIGHT//3))

    def handle_event(self, event): pass

    