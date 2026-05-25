import pygame, os
from Room.Room import Room
from Constant import SCREEN_WIDTH, SCREEN_HEIGHT, BAKING_BG, COLOR_BG_CREAM, COLOR_DARK_BROWN, FONT_HEADING_SIZE, FONT_BODY_SIZE, FONT_NAME, OVEN_CLOSE_IMAGE

class BakingRoom(Room):
    def __init__(self):
        super().__init__(name="Baking")
        self._bg_image = None
        self._oven_image = None
        self._font_heading = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)

    def enter(self):
        if os.path.exists(BAKING_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(BAKING_BG).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
          # Load oven image
        if os.path.exists(OVEN_CLOSE_IMAGE):
            img = pygame.image.load(OVEN_CLOSE_IMAGE).convert_alpha()  # convert_alpha untuk transparency
            # Scale sesuai kebutuhan, misal jadi lebar 200px dengan aspect ratio tetap
            original_width, original_height = img.get_size()
            new_width = 520
            new_height = int(original_height * (new_width / original_width))
            self._oven_image = pygame.transform.smoothscale(img, (new_width, new_height))

    def update(self): pass

    def render(self):
        if not self.screen: return
        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))
        else:
            self.screen.fill(COLOR_BG_CREAM)
            t = self._font_heading.render("~ Cashier ~", True, COLOR_DARK_BROWN)
            self.screen.blit(t, t.get_rect(centerx=SCREEN_WIDTH//2, centery=SCREEN_HEIGHT//3))

        if self._oven_image:
            oven_rect = self._oven_image.get_rect(centerx=SCREEN_WIDTH - 550,
                bottom=SCREEN_HEIGHT + 5)
            self.screen.blit(self._oven_image, oven_rect)

    def handle_event(self, event): pass