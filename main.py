import numpy as np
import random
import sys
import time
from enum import Enum
import math
import pygame
from character import *
from animation_player import *
from item_player import *
from pathfinding import *
from projectiles import *
from avatar import *
from fight import *
from overworld import *

pygame.init()
pygame.font.init()  # you have to call this at the start,

TILESIZE = 64
GRIDWIDTH = 16
GRIDHEIGHT = 10
WIDTH = TILESIZE * GRIDWIDTH
HEIGHT = TILESIZE * GRIDHEIGHT
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARKRED = (127, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (71, 117, 191)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)
LIGHTGRAY = (140, 140, 140)
my_font = pygame.font.SysFont('New Times Roman', 30)


# class syntax
class GameState(Enum):
    AVATAR = 1
    COMBAT = 2


class Game:
    def __init__(self):
        self.game_state = GameState.AVATAR
        self.occupied_spots_by_ai = []
        self.game_celebration = False
        self.Figures = []
        self.running = True
        self.g = SquareGrid(GRIDWIDTH, GRIDHEIGHT)
        self.path = None
        self.attack_path = None
        self.reachable_tiles = []
        self.shortest_path_tiles = []
        self.attack_tiles = []
        self.calculate_new_path = True
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        self.characters = []
        self.mobs = []
        self.particles = []
        self.items = []
        self.projectiles = []
        self.inventory = [None] * 4
        self.selected_char = None
        self.selected_mob = None
        self.can_ai_turn = False

        self.player_turn = True
        self.level = 1
        self.background_image = pygame.image.load("First_Level.png").convert_alpha()
        self.background_image = pygame.transform.scale(self.background_image, (WIDTH, HEIGHT))

        self.level_two_image = pygame.image.load("Second_Level.png").convert_alpha()
        self.level_two_image = pygame.transform.scale(self.level_two_image, (WIDTH, HEIGHT))

        self.level_three_image = pygame.image.load("Third_Level.png").convert_alpha()
        self.level_three_image = pygame.transform.scale(self.level_three_image, (WIDTH, HEIGHT))

        self.overlay_image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
        self.overlay_image = self.overlay_image.convert_alpha()
        self.overlay_image.fill((0, 0, 0, 0))
        self.overlay_alpha = 0
        self.bool_increment_overlay = False
        self.fade_out = True
        self.fade_in = False

        self.fight = Fight(self.set_overworld)

        self.avatar = Avatar(avatar_player, 'men', [
            Character(animation_player, self.fight.clear_path, pygame.math.Vector2(4, 3), 'peasant_minor',
                      self.fight.spawn_item,
                      char_dictionary, self.fight.calculate_possible_attack_tiles, False, self.fight.create_projectile,
                      None), Character(animation_player, self.fight.clear_path, pygame.math.Vector2(4, 5), 'peasant_minor',
                      self.fight.spawn_item,
                      char_dictionary, self.fight.calculate_possible_attack_tiles, False, self.fight.create_projectile,
                      None)])
        self.avatar_enemies = [Avatar_Enemies(avatar_enemies_player, 320, 320, 'imp_minor', [
            Character(animation_player, self.fight.clear_path, pygame.math.Vector2(7, 3), 'skeleton_minor',
                      self.fight.spawn_item,
                      char_dictionary, self.fight.calculate_possible_attack_tiles, True, self.fight.create_projectile,
                      None)]),
                               Avatar_Enemies(avatar_enemies_player, 480, 320, 'imp_minor', [
                                   Character(animation_player, self.fight.clear_path, pygame.math.Vector2(10, 3),
                                             'skeleton_minor', self.fight.spawn_item,
                                             char_dictionary, self.fight.calculate_possible_attack_tiles, True,
                                             self.fight.create_projectile, None)]),
                               Avatar_Enemies(avatar_enemies_player, 320, 480, 'imp_major', [
                                   Character(animation_player, self.fight.clear_path, pygame.math.Vector2(10, 6),
                                             'skeleton_minor', self.fight.spawn_item,
                                             char_dictionary, self.fight.calculate_possible_attack_tiles, True,
                                             self.fight.create_projectile, None), Character(animation_player, self.fight.clear_path, pygame.math.Vector2(10, 4),
                                             'lich_minor', self.fight.spawn_item,
                                             char_dictionary, self.fight.calculate_possible_attack_tiles, True,
                                             self.fight.spawn_particle, None)])]

        self.overworld = Overworld(self.avatar, self.avatar_enemies, self.set_fight)
        self.fight.set_img(self.background_image)
        self.fight.set_avatar(self.avatar)
        self.fight.set_player_chars(self.avatar.chars)
        self.game = self.overworld

    def set_overworld(self):
        self.fight.overlay_alpha = 255
        self.fight.fade_in = True
        self.fight.fade_out = False
        self.fight.bool_increment_overlay = True
        if self.fight.game_celebration:
            self.overworld.selected_enemy.set_defeated()
        self.game = self.overworld

    def set_fight(self):
        self.fight.overlay_alpha = 255
        self.fight.fade_in = True
        self.fight.fade_out = False
        self.fight.bool_increment_overlay = True
        self.fight.clear_mobs()
        self.fight.clear_items()
        self.fight.set_mobs(self.overworld.selected_enemy.mobs)
        self.fight.set_player_chars(self.avatar.chars)
        self.fight.game_celebration = False

        self.game = self.fight

    def re_init(self):
        self.level = 1
        self.characters.clear()
        self.mobs.clear()
        self.particles.clear()
        self.items.clear()
        self.projectiles.clear()

        self.characters.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(4, 3), 'cavalier_minor', self.spawn_item,
                      char_dictionary, self.calculate_possible_attack_tiles, False, self.create_projectile, None))
        self.characters.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(4, 5), 'archer_minor', self.spawn_item,
                      char_dictionary, self.calculate_possible_attack_tiles, False, self.create_projectile, None))
        self.selected_char = None

        self.mobs.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(10, 3), 'skeleton_minor', self.spawn_item,
                      char_dictionary, self.calculate_possible_attack_tiles, True, self.create_projectile, None))
        self.mobs.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(10, 5), 'skeleton_minor', self.spawn_item,
                      char_dictionary, self.calculate_possible_attack_tiles, True, self.create_projectile, None))
        self.selected_mob = None
        self.can_ai_turn = False
        self.game_celebration = False
        self.fight = Fight(self.mobs, self.background_image)

    def input_handling(self):
        self.game.input_handling()

    def level_update(self):
        self.mobs.clear()
        self.particles.clear()
        self.projectiles.clear()
        self.items.clear()
        self.selected_char = None
        self.selected_mob = None
        self.can_ai_turn = False
        self.game_celebration = False

        for char in self.characters:
            char.position_x = 4 * 64
            char.reset_for_new_turn()
            char.get_stats(char.dictionary)

        if self.level == 2:
            self.mobs.append(
                Character(animation_player, self.clear_path, pygame.math.Vector2(7, 3), 'skeleton_major',
                          self.spawn_item,
                          char_dictionary, self.calculate_possible_attack_tiles, True, self.create_projectile, None))
            self.mobs.append(
                Character(animation_player, self.clear_path, pygame.math.Vector2(7, 5), 'skeleton_major',
                          self.spawn_item,
                          char_dictionary, self.calculate_possible_attack_tiles, True, self.create_projectile, None))

        elif self.level == 3:
            self.mobs.append(
                Character(animation_player, self.clear_path, pygame.math.Vector2(9, 3), 'lich_minor',
                          self.spawn_item,
                          char_dictionary, self.calculate_possible_attack_tiles, True, self.spawn_particle, None))
            self.mobs.append(
                Character(animation_player, self.clear_path, pygame.math.Vector2(7, 5), 'imp_minor',
                          self.spawn_item,
                          char_dictionary, self.calculate_possible_attack_tiles, True, self.create_projectile, None))

    def update(self):
        self.game.update()

    def draw_inventory(self):
        screen.blit(self.inventory_ui, (TILESIZE * 2, TILESIZE * 5))

    def draw(self):
        self.game.draw(screen)


def draw_grid():
    for x in range(0, WIDTH, TILESIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILESIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))


def from_screenspace_to_gridspace(screen_coordinates):
    x_grid = screen_coordinates[0] // TILESIZE
    y_grid = screen_coordinates[1] // TILESIZE
    return x_grid, y_grid


screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

char_dictionary = Character_Dictionary()
animation_player = Animation_Player(char_dictionary)
avatar_player = Avatar_Player()
avatar_enemies_player = Avatar_Enemies_Player()


game = Game()
mouse_down = False
mouse_img_walk = pygame.image.load("graphics/mouse/FeetOriginal 20.png").convert_alpha()
mouse_img_walk = pygame.transform.scale(mouse_img_walk, (32, 32))
mouse_img_attack_1 = pygame.image.load("graphics/mouse/SwordOriginal 5.png").convert_alpha()
mouse_img_attack_1 = pygame.transform.scale(mouse_img_attack_1, (32, 32))
mouse_img_attack_2 = pygame.image.load("graphics/mouse/ArrowOrigin 1.png").convert_alpha()
mouse_img_attack_2 = pygame.transform.scale(mouse_img_attack_2, (32, 32))
# char = Character(animation_player, game.clear_path)
game_celebration = False
fight_over = False
last_time = time.time()
t = 0
while game.running:
    # delta time
    dt = time.time() - last_time
    last_time = time.time()
    if dt:
        pygame.display.set_caption(str(int(1 / dt)))

    game.input_handling()

    if 0:
        if game.mouse_position != current_mouse_pos:
            mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
            mouse_img = mouse_img_walk
            for mob in game.mobs:
                mob_position = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
                if mob_position == mouse_position:
                    if game.selected_char.long_range:
                        mouse_img = mouse_img_attack_2
                    else:
                        mouse_img = mouse_img_attack_1

    game.update()
    clock.tick(FPS)
    screen.fill(DARKGRAY)
    game.draw()

    victory = True

    for mob in game.mobs:
        if mob.alive:
            victory = False

    if victory and not game.game_celebration:
        game.game_celebration = True
        for mob in game.mobs:
            game.spawn_item((mob.position_x, mob.position_y))

    defeat = True
    for char in game.characters:
        if char.alive:
            defeat = False

    if game.game_state == GameState.COMBAT:
        if game.fight.is_fight_over(game.characters):
            game.avatar_enemies[0].set_defeated()

    if 0:
        if victory:
            text_surface = game_over_font.render(f'Victory', True, (0, 255, 0))
            screen.blit(text_surface, (
                screen.get_width() // 2 - text_surface.get_width() // 2,
                screen.get_height() // 2 - text_surface.get_height()))

        if defeat:
            text_surface = game_over_font.render(f'Defeat', True, (255, 0, 0))
            screen.blit(text_surface,
                        (screen.get_width() // 2 - text_surface.get_width() // 2,
                         screen.get_height() // 2 - text_surface.get_height()))

    if not game.player_turn:
        game.check_if_ai_is_finished()

    if mouse_down:
        screen.blit(mouse_img, pygame.mouse.get_pos() - pygame.math.Vector2(16, 16))

    pygame.display.flip()
