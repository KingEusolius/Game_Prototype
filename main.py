import numpy as np
import random
import sys
import time
import pygame

pygame.init()
pygame.font.init()  # you have to call this at the start,

TILESIZE = 64
GRIDWIDTH = 14
GRIDHEIGHT = 8
WIDTH = TILESIZE * GRIDWIDTH
HEIGHT = TILESIZE * GRIDHEIGHT
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)
LIGHTGRAY = (140, 140, 140)
my_font = pygame.font.SysFont('New Times Roman', 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

last_time = time.time()
while True:
    # delta time
    dt = time.time() - last_time
    last_time = time.time()
    if dt:
        pygame.display.set_caption(str(int(1 / dt)))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    clock.tick(FPS)
    pygame.display.flip()
