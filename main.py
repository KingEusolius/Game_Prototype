import numpy as np
import random
import sys
import time
import pygame
from character import *
from animation_player import *

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

class Game:
    def __init__(self):
        self.Figures = []
        self.running = True


screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

game = Game()
animation_player = Animation_Player()
char = Character(animation_player)


last_time = time.time()
while game.running:
    # delta time
    dt = time.time() - last_time
    last_time = time.time()
    if dt:
        pygame.display.set_caption(str(int(1 / dt)))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                char.change_state('down')
            if event.key == pygame.K_s:
                char.change_state('down')
            if event.key == pygame.K_a:
                char.change_state('right')
            if event.key == pygame.K_d:
                char.change_state('right')

            if event.key == pygame.K_u:
                char.state = 'Moving'
                char.direction = 'right'
                char.play_anim = True
                char.set_target_position(pygame.mouse.get_pos()[0])

            if event.key == pygame.K_k:
                char.state = 'Moving'
                char.direction = 'down'
                char.play_anim = True

    char.update()

    clock.tick(FPS)
    screen.fill(DARKGRAY)
    char.draw(screen)
    pygame.display.flip()
