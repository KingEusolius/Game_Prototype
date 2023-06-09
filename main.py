import numpy as np
import random
import sys
import time
import pygame
from character import *
from animation_player import *
from particle_player import *
from item_player import *
from pathfinding import *
from projectiles import *
from ui import *

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


class Game:
    def __init__(self):
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
        # self.inventory[0] = (Item(item_player, 'book', (0, 0), item_dictionary))
        # self.inventory[1] = (Item(item_player, 'spell', (0, 0), item_dictionary))
        self.selected_char = None
        self.selected_mob = None
        self.can_ai_turn = False
        self.re_init()
        self.ui = UI(self.inventory, self.spawn_particle)
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

    def re_init(self):
        self.level = 1
        self.characters.clear()
        self.mobs.clear()
        self.particles.clear()
        self.items.clear()
        self.projectiles.clear()

        self.characters.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(4, 3), 'peasant_minor', self.spawn_item,
                      char_dictionary, self.calculate_possible_attack_tiles, False, self.create_projectile, None))
        self.characters.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(4, 5), 'peasant_minor', self.spawn_item,
                      char_dictionary, self.calculate_possible_attack_tiles, False, self.create_projectile, None))
        self.selected_char = None

        self.mobs.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(7, 3), 'skeleton_minor', self.spawn_item,
                      char_dictionary, self.calculate_possible_attack_tiles, True, self.create_projectile, None))
        self.mobs.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(7, 5), 'skeleton_minor', self.spawn_item,
                      char_dictionary, self.calculate_possible_attack_tiles, True, self.create_projectile, None))
        self.selected_mob = None
        self.can_ai_turn = False
        self.game_celebration = False

    def input_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and self.player_turn:

                if self.game_celebration:
                    self.item_pick_up()

                if self.ui.on_mouse_click(pygame.mouse.get_pos()):
                    pass
                elif self.selected_char and event.button == 1:
                    state = self.mouse_selection()
                    # click on terrain
                    if state == 0:
                        if self.selected_char.can_walk:
                            self.selected_char.change_state('walk')
                            self.selected_char.waypoints = self.get_shortest_path()
                            if self.selected_char.waypoints:
                                self.selected_char.set_target_position(self.selected_char.waypoints[0][0],
                                                                       self.selected_char.waypoints[0][1])
                                self.selected_char.move_range -= len(self.selected_char.waypoints)
                    # click on other character
                    elif state == 1:
                        self.clear_path()
                        self.character_selection()
                        if self.selected_char:
                            if self.selected_char.can_walk:
                                self.calculate_possible_paths_character()
                            elif self.selected_char.can_attack:
                                self.calculate_possible_attack_tiles(self.selected_char)
                        self.calc_if_enemy_in_range()
                    # click on enemy
                    elif state == 2 and self.selected_char.can_attack:
                        self.mob_selection()
                        # short range units
                        if self.selected_char.long_range == 0:
                            self.selected_char.change_state('walk')
                            self.selected_char.waypoints = self.get_shortest_path()
                            if self.selected_char.waypoints:
                                self.selected_char.set_target_position(self.selected_char.waypoints[0][0],
                                                                       self.selected_char.waypoints[0][1])
                                self.selected_char.move_range -= len(self.selected_char.waypoints)
                            length_waypoints = len(self.selected_char.waypoints)
                            # unit must walk up to enemy
                            if length_waypoints:
                                last_x, last_y = self.selected_char.waypoints[length_waypoints - 1][0], \
                                                 self.selected_char.waypoints[length_waypoints - 1][1]
                                mob_x, mob_y = self.selected_mob.position_x, self.selected_mob.position_y
                                last_x, last_y = from_screenspace_to_gridspace((last_x, last_y))
                                mob_x, mob_y = from_screenspace_to_gridspace((mob_x, mob_y))
                                if heuristic(vec(last_x, last_y), vec(mob_x, mob_y)) <= self.selected_char.attack_range:
                                    self.selected_char.attack_after_walk = True
                                    self.selected_char.target = self.selected_mob
                                    self.selected_mob.in_range = False
                                    self.selected_char.deselect_after_action = True
                                    self.selected_char.is_selected(False)
                                    self.selected_char = None
                            else:
                                char_x, char_y = self.selected_char.position_x, \
                                                 self.selected_char.position_y
                                mob_x, mob_y = self.selected_mob.position_x, self.selected_mob.position_y
                                char_x, char_y = from_screenspace_to_gridspace((char_x, char_y))
                                mob_x, mob_y = from_screenspace_to_gridspace((mob_x, mob_y))
                                if heuristic(vec(char_x, char_y), vec(mob_x, mob_y)) <= self.selected_char.attack_range:
                                    self.selected_char.target = self.selected_mob
                                    self.selected_mob.in_range = False
                                    self.selected_char.change_state('attack')
                                    self.selected_char.deselect_after_action = True
                                    self.selected_char.is_selected(False)
                                    self.clear_path()
                                    self.selected_char = None
                        # long range unit
                        else:
                            char_x, char_y = self.selected_char.position_x, \
                                             self.selected_char.position_y
                            mob_x, mob_y = self.selected_mob.position_x, self.selected_mob.position_y
                            char_x, char_y = from_screenspace_to_gridspace((char_x, char_y))
                            mob_x, mob_y = from_screenspace_to_gridspace((mob_x, mob_y))
                            if heuristic(vec(char_x, char_y), vec(mob_x, mob_y)) <= self.selected_char.attack_range:
                                self.selected_char.target = self.selected_mob
                                self.selected_char.change_state('attack')

                                self.selected_char.deselect_after_action = True
                                self.selected_char.is_selected(False)
                                self.clear_path()
                                self.selected_mob.in_range = False
                                self.selected_char = None

                elif event.button == 3:
                    self.clear_path()
                    self.selected_char = None
                    self.selected_mob = None
                    for char in self.characters:
                        char.is_selected(False)
                    for mob in self.mobs:
                        mob.in_range = False
                else:
                    self.clear_path()
                    self.character_selection()
                    if self.selected_char:
                        if self.selected_char.can_walk:
                            self.calculate_possible_paths_character()
                        elif self.selected_char.can_attack:
                            self.calculate_possible_attack_tiles(self.selected_char)
                    self.calc_if_enemy_in_range()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pos = from_screenspace_to_gridspace(pygame.mouse.get_pos())
                    self.particles.append(Particle(particle_player, 'inferno', pos, self.clear_particle))
                if event.key == pygame.K_u:
                    pos = from_screenspace_to_gridspace(pygame.mouse.get_pos())
                    self.particles.append(Particle(particle_player, 'update', pos, self.clear_particle))
                if event.key == pygame.K_a:
                    self.player_turn = False
                    self.ai_turn()
                if event.key == pygame.K_r:
                    self.re_init()
                if event.key == pygame.K_b:
                    pos = (self.characters[2].position_x + 32, self.characters[2].position_y + 32)
                    self.characters[2].change_state('attack')
                    self.projectiles.append(Arrow(pos, self.mobs[1], self.characters[2].attack_power))
                if event.key == pygame.K_n:
                    self.level += 1
                    self.bool_increment_overlay = True
                    self.fade_out = True
                    self.fade_in = False

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

    def mob_decision(self, mob, nearest_char):
        x_fig, y_fig = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
        x_end, y_end = from_screenspace_to_gridspace((nearest_char.position_x, nearest_char.position_y))
        shortest_path = breadth_first_search_with_end(self.g, vec(x_end, y_end), vec(x_fig, y_fig),
                                                      self.path)
        goal = vec(x_end, y_end)
        start = vec(x_fig, y_fig)

        self.shortest_path_tiles.clear()
        current = start + shortest_path[vec2int(start)]
        x = None
        y = None
        while current != goal and heuristic(start, current) <= mob.move_range and heuristic(current,
                                                                                            goal) >= mob.attack_range:
            x = current.x * TILESIZE
            y = current.y * TILESIZE
            self.shortest_path_tiles.append((x, y))
            # find next in path
            current = current + shortest_path[vec2int(current)]
        if x is not None and y is not None:
            last_x, last_y = x / TILESIZE, y / TILESIZE
            self.occupied_spots_by_ai.append((last_x, last_y))

        mob.waypoints = game.get_shortest_path() * 1
        # mob has to walk
        if mob.waypoints:
            mob.change_state('walk')
            mob.actions.append('walk')
            mob.set_target_position(mob.waypoints[0][0],
                                    mob.waypoints[0][1])
            # mob can attack directly after walking
            if heuristic(vec(last_x, last_y), goal) <= mob.attack_range:
                mob.attack_after_walk = True
                mob.target = nearest_char
                mob.actions.append('attack')
            else:
                mob.attack_after_walk = False
        else:
            # mob can attack directly
            mob.target = nearest_char
            mob.change_state('attack')
            mob.actions.append('attack')

    def ai_turn(self):
        self.selected_mob = None
        self.selected_char = None
        self.occupied_spots_by_ai.clear()
        for mob in self.mobs:
            mob_ready = not mob.actions
            if mob.alive and mob_ready:
                mob.ai_turn = True
                self.reachable_tiles.clear()
                self.g.walls = []
                self.g.obstacles = []
                for oc in self.occupied_spots_by_ai:
                    self.g.obstacles.append(oc)
                for mobster in self.mobs:
                    if mobster != mob:
                        x, y = from_screenspace_to_gridspace((mobster.position_x, mobster.position_y))
                        self.g.obstacles.append((x, y))

                self.calculate_path(mob, 18)

                nearest_char = mob.find_nearest_and_weakest_target(self.characters)

                if nearest_char:
                    self.mob_decision(mob, nearest_char)

        self.can_ai_turn = False
        self.clear_path()
        for char in self.characters:
            char.reset_for_new_turn()

    def check_if_ai_is_finished(self):
        finished = True
        for mob in self.mobs:
            if mob.ai_turn:
                finished = False
        if finished:
            self.player_turn = True

    def create_projectile(self, start_position_x, start_position_y, target, attack_power):
        pos = (start_position_x + 32, start_position_y + 16)
        self.projectiles.append(Arrow(pos, target, attack_power))

    def mouse_selection(self):
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        for char in self.characters:
            char_position = from_screenspace_to_gridspace((char.position_x, char.position_y))
            if char_position == self.mouse_position:
                return 1

        for mob in self.mobs:
            mob_position = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
            if mob_position == self.mouse_position:
                return 2

        for rect in self.ui.resource_slots:
            rect_position = from_screenspace_to_gridspace((rect.position_x, rect.position_y))
            if rect_position == self.mouse_position:
                return 3

        return 0

    def character_selection(self):
        self.selected_char = None
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        for char in self.characters:
            char_position = from_screenspace_to_gridspace((char.position_x, char.position_y))
            if char_position == self.mouse_position:
                char.is_selected(True)
                self.selected_char = char
                char.deselect_after_action = False
            else:
                char.is_selected(False)

    def mob_selection(self):
        self.selected_mob = None
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        for mob in self.mobs:
            mob_position = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
            if mob_position == self.mouse_position:
                self.selected_mob = mob

    def spawn_item(self, position):
        pos = from_screenspace_to_gridspace(position)
        self.items.append(Item(item_player, 'sword', pos, item_dictionary))
        self.items.append(Item(item_player, 'crossbow', pos, item_dictionary))

    def spawn_particle(self, particle_type, position):
        pos = from_screenspace_to_gridspace(position)
        self.particles.append(
            Particle(particle_player, particle_type, pos, self.clear_particle, self.mobs, self.characters))

    def item_pick_up(self):
        for it in self.items:
            if it.check_overlap(pygame.mouse.get_pos()):
                i = self.inventory_find_free_spot()
                if i <= len(self.inventory) - 1:
                    self.inventory[i] = it
                    self.ui.set_spot_occupied(i, it.particle_type, it.inventory_img)
                    self.items.remove(it)

    def inventory_find_free_spot(self):
        for i in range(len(self.inventory)):
            if not self.inventory[i]:
                return i
        return len(self.inventory)

    def update(self):
        for char in self.characters:
            if char.alive:
                char.update()

        for mob in self.mobs:
            if mob.alive:
                mob.update()

        for part in self.particles:
            part.update()

        for it in self.items:
            it.update()

        for pr in self.projectiles:
            pr.update()
            if pr.hit:
                self.projectiles.remove(pr)

    def draw_characters(self):
        for char in self.characters:
            char.draw(screen)

        for mob in self.mobs:
            mob.draw(screen)

        for part in self.particles:
            part.draw(screen)

        for it in self.items:
            it.draw(screen)

        for pr in self.projectiles:
            pr.draw(screen)

    def draw_ui(self):
        self.ui.draw(screen, self.selected_char)

    def calculate_shortest_path_character(self):
        if not self.path:
            return
        if not self.selected_char:
            self.clear_path()
            return

        character = self.selected_char
        x_fig, y_fig = from_screenspace_to_gridspace((character.position_x, character.position_y))
        x_end, y_end = from_screenspace_to_gridspace(pygame.mouse.get_pos())

        shortest_path = breadth_first_search_with_end(self.g, vec(x_end, y_end), vec(x_fig, y_fig),
                                                      self.path)
        goal = vec(x_end, y_end)
        # draw path from start to goal
        start = vec(x_fig, y_fig)
        if shortest_path:
            self.shortest_path_tiles.clear()
            current = start + shortest_path[vec2int(start)]
            while current != goal and heuristic(start, current) <= character.move_range and len(
                    self.shortest_path_tiles) < character.move_range - 1:
                x = current.x * TILESIZE
                y = current.y * TILESIZE
                self.shortest_path_tiles.append((x, y))
                # find next in path
                current = current + shortest_path[vec2int(current)]
            self.shortest_path_tiles.append((current.x * TILESIZE, current.y * TILESIZE))

    def calc_if_enemy_in_range(self):
        if self.selected_char:
            length = len(self.shortest_path_tiles)
            if length:
                x_pos = self.shortest_path_tiles[length - 1][0]
                y_pos = self.shortest_path_tiles[length - 1][1]
                x_fig, y_fig = from_screenspace_to_gridspace((x_pos, y_pos))
            else:
                x_pos = self.selected_char.position_x
                y_pos = self.selected_char.position_y
                x_fig, y_fig = from_screenspace_to_gridspace((x_pos, y_pos))

            for mob in self.mobs:
                mob.in_range = False
                if mob.alive:
                    x_mob, y_mob = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
                    char_pos = vec(x_fig, y_fig)
                    mob_pos = vec(x_mob, y_mob)
                    mob.in_range = heuristic(char_pos, mob_pos) <= self.selected_char.attack_range

    def get_shortest_path(self):
        self.calculate_new_path = False
        return self.shortest_path_tiles

    def clear_path(self):
        self.path = None
        self.attack_path = None
        self.attack_tiles.clear()
        self.reachable_tiles.clear()
        self.shortest_path_tiles.clear()
        self.calculate_new_path = True

    def clear_particle(self):
        cur_particle = self.particles.pop(0)
        del cur_particle

    def calculate_possible_paths_character(self):
        if not self.selected_char:
            self.clear_path()
            return

        if not self.selected_char.can_walk:
            self.clear_path()
            return

        self.reachable_tiles.clear()
        self.g.walls.clear()
        self.g.obstacles.clear()

        character = self.selected_char
        for char in self.characters:
            if char != character:
                x, y = from_screenspace_to_gridspace((char.position_x, char.position_y))
                self.g.obstacles.append((x, y))
        for mob in self.mobs:
            x, y = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
            self.g.obstacles.append((x, y))

        self.calculate_path(character)

    def calculate_path(self, character, move_range=None):
        x_fig, y_fig = from_screenspace_to_gridspace((character.position_x, character.position_y))
        if not move_range:
            movement_range = character.move_range
        else:
            movement_range = move_range
        self.path = breadth_first_search(self.g, vec(x_fig, y_fig), movement_range)
        self.reachable_tiles.append((x_fig * TILESIZE, y_fig * TILESIZE))
        for node, dir in self.path.items():
            if dir:
                x, y = node
                x = x * TILESIZE
                y = y * TILESIZE
                self.reachable_tiles.append((x, y))

    def calculate_possible_attack_tiles(self, character):
        self.clear_path()
        self.g.walls.clear()
        self.g.obstacles.clear()
        x_fig, y_fig = from_screenspace_to_gridspace((character.position_x, character.position_y))
        self.attack_path = breadth_first_search(self.g, vec(x_fig, y_fig), character.attack_range)
        self.attack_tiles.append((x_fig * TILESIZE, y_fig * TILESIZE))
        for node, dir in self.attack_path.items():
            if dir:
                x, y = node
                x = x * TILESIZE
                y = y * TILESIZE
                self.attack_tiles.append((x, y))

    def draw_reachable_tiles(self):
        for tile in self.reachable_tiles:
            rect = pygame.Rect(tile[0], tile[1], TILESIZE, TILESIZE)
            pygame.draw.line(screen, DARKGRAY, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, DARKGRAY, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(screen, DARKGRAY, rect.topright, rect.bottomright, 2)
            pygame.draw.line(screen, DARKGRAY, rect.bottomleft, rect.bottomright, 2)
        for idx, tile in enumerate(self.shortest_path_tiles):
            rect = pygame.Rect(tile[0], tile[1], TILESIZE, TILESIZE)
            pygame.draw.line(screen, LIGHTBLUE, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, LIGHTBLUE, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(screen, LIGHTBLUE, rect.topright, rect.bottomright, 2)
            pygame.draw.line(screen, LIGHTBLUE, rect.bottomleft, rect.bottomright, 2)
        for tile in self.attack_tiles:
            rect = pygame.Rect(tile[0], tile[1], TILESIZE, TILESIZE)
            pygame.draw.line(screen, DARKRED, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, DARKRED, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(screen, DARKRED, rect.topright, rect.bottomright, 2)
            pygame.draw.line(screen, DARKRED, rect.bottomleft, rect.bottomright, 2)

    def draw_inventory(self):
        screen.blit(self.inventory_ui, (TILESIZE * 2, TILESIZE * 5))

    def draw_background(self):
        screen.blit(self.background_image, (0, 0))

    def fade_out_overlay(self):
        increment = 3
        if self.overlay_alpha < 255 - increment:
            self.overlay_alpha += increment
        return self.overlay_alpha < 255 - increment

    def fade_in_overlay(self):
        decrement = 3
        if self.overlay_alpha > decrement:
            self.overlay_alpha -= decrement
        return self.overlay_alpha > decrement

    def handle_level_transition(self):
        if self.fade_out:
            if not self.fade_out_overlay():
                self.fade_out = False
                self.fade_in = True
                if self.level == 2:
                    self.background_image = self.level_two_image
                elif self.level == 3:
                    self.background_image = self.level_three_image
                self.level_update()
        if self.fade_in:
            if not self.fade_in_overlay():
                self.fade_in = False
                self.bool_increment_overlay = False



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
item_dictionary = Item_Dictionary()
animation_player = Animation_Player(char_dictionary)
particle_player = Particle_Player()
item_player = Item_Player(item_dictionary)







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
last_time = time.time()
while game.running:
    # delta time
    dt = time.time() - last_time
    last_time = time.time()
    if dt:
        pygame.display.set_caption(str(int(1 / dt)))

    game.input_handling()

    current_mouse_pos = from_screenspace_to_gridspace(pygame.mouse.get_pos())

    if game.mouse_position != current_mouse_pos and game.calculate_new_path:
        game.calculate_shortest_path_character()
        game.calc_if_enemy_in_range()
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
    game.mouse_position = current_mouse_pos

    game.update()
    clock.tick(FPS)
    screen.fill(DARKGRAY)
    game.draw_background()
    game.draw_reachable_tiles()

    game.draw_characters()

    if game.bool_increment_overlay:
        game.handle_level_transition()
        game.overlay_image.fill((0, 0, 0, game.overlay_alpha))
        screen.blit(game.overlay_image, (0, 0))

    game.draw_ui()

    if mouse_down:
        pygame.mouse.set_visible(False)
    else:
        pygame.mouse.set_visible(True)

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
