# class/file: main.py

import pygame
import sys

pygame.init()

int_screen_width = 1280
int_screen_height = 720

screen = pygame.display.set_mode(
    (int_screen_width, int_screen_height)
)

pygame.display.set_caption("Bakery PBO")

clock = pygame.time.Clock()

bool_is_running = True

while bool_is_running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            bool_is_running = False

    screen.fill((30, 30, 30))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()