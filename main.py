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
LIGHTBLUE = (71, 117, 191)
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
        self.g = SquareGrid(GRIDWIDTH, GRIDHEIGHT)
        self.path = None
        self.reachable_tiles = []
        self.shortest_path_tiles = []
        self.calculate_new_path = True
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        self.characters = []
        self.characters.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(2, 2), 'cavalier', self.spawn_item))
        self.characters.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(4, 4), 'cavalier', self.spawn_item))
        self.characters.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(6, 4), 'cavalier', self.spawn_item))
        self.selected_char = None

        self.mobs = []
        self.mobs.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(10, 2), 'imp', self.spawn_item))
        self.mobs.append(
            Character(animation_player, self.clear_path, pygame.math.Vector2(10, 5), 'imp', self.spawn_item))
        self.selected_mob = None
        self.can_ai_turn = False

        self.particles = []
        self.items = []

    def ai_turn(self):
        occupied_spots_by_ai = []
        for mob in self.mobs:
            character = mob
            self.reachable_tiles.clear()
            x_fig, y_fig = from_screenspace_to_gridspace((character.position_x, character.position_y))
            self.g.walls = []
            self.g.obstacles = []
            for oc in occupied_spots_by_ai:
                self.g.obstacles.append(oc)
            for char in self.characters:
                x, y = from_screenspace_to_gridspace((char.position_x, char.position_y))
                #self.g.obstacles.append((x, y))
            for mobster in self.mobs:
                if mobster != character:
                    x, y = from_screenspace_to_gridspace((mobster.position_x, mobster.position_y))
                    self.g.obstacles.append((x, y))
            self.path = breadth_first_search(self.g, vec(x_fig, y_fig), 18)
            self.reachable_tiles.append((x_fig * TILESIZE, y_fig * TILESIZE))
            for node, dir in self.path.items():
                if dir:
                    x, y = node
                    x = x * TILESIZE
                    y = y * TILESIZE
                    self.reachable_tiles.append((x, y))

            x_end, y_end = from_screenspace_to_gridspace((game.characters[0].position_x, game.characters[0].position_y))
            shortest_path = breadth_first_search_with_end(self.g, vec(x_end, y_end), vec(x_fig, y_fig),
                                                          self.path)
            goal = vec(x_end, y_end)
            # draw path from start to goal
            start = vec(x_fig, y_fig)
            if shortest_path:
                self.shortest_path_tiles.clear()
                current = start + shortest_path[vec2int(start)]
                while current != goal and heuristic(start, current) <= 4:
                    x = current.x * TILESIZE
                    y = current.y * TILESIZE
                    self.shortest_path_tiles.append((x, y))
                    # find next in path
                    current = current + shortest_path[vec2int(current)]
                last_x, last_y = x / TILESIZE, y / TILESIZE
                occupied_spots_by_ai.append((last_x, last_y))
                #self.shortest_path_tiles.append((goal.x * TILESIZE, goal.y * TILESIZE))

                mob.waypoints = game.get_shortest_path() * 1
                #print(mob.waypoints)
                if mob.waypoints:
                    mob.change_state('walk')
                    mob.set_target_position(mob.waypoints[0][0],
                                                           mob.waypoints[0][1])
                    if heuristic(vec(last_x, last_y), goal) == 1:
                        mob.attack_after_walk = True
                        mob.target = game.characters[0]
                    else:
                        mob.attack_after_walk = False
                else:
                    mob.target = game.characters[0]
                    mob.change_state('attack')

        self.can_ai_turn = False
        self.clear_path()

    def character_selection(self):
        self.selected_char = None
        self.mouse_position = from_screenspace_to_gridspace(pygame.mouse.get_pos())
        for char in self.characters:
            char_position = from_screenspace_to_gridspace((char.position_x, char.position_y))
            if char_position == self.mouse_position:
                char.is_selected(True)
                self.selected_char = char
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
        self.items.append(Item(item_player, 'spell', pos))

    def update(self):
        for char in self.characters:
            char.update()

        for mob in self.mobs:
            mob.update()

        for part in self.particles:
            part.update()

        for it in self.items:
            it.update()

    def draw_characters(self):
        for char in self.characters:
            char.draw(screen)

        for mob in self.mobs:
            mob.draw(screen)

        for part in self.particles:
            part.draw(screen)

        for it in self.items:
            it.draw(screen)

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
            while current != goal and heuristic(start, current) <= 4:
                x = current.x * TILESIZE
                y = current.y * TILESIZE
                self.shortest_path_tiles.append((x, y))
                # find next in path
                current = current + shortest_path[vec2int(current)]
            self.shortest_path_tiles.append((current.x * TILESIZE, current.y * TILESIZE))

    def get_shortest_path(self):
        self.calculate_new_path = False
        return self.shortest_path_tiles

    def clear_path(self):
        self.path = None
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

        character = self.selected_char
        self.reachable_tiles.clear()
        x_fig, y_fig = from_screenspace_to_gridspace((character.position_x, character.position_y))
        self.g.walls = []
        self.g.obstacles = []
        for char in self.characters:
            if char != character:
                x, y = from_screenspace_to_gridspace((char.position_x, char.position_y))
                self.g.obstacles.append((x, y))
        for mob in self.mobs:
            x, y = from_screenspace_to_gridspace((mob.position_x, mob.position_y))
            self.g.obstacles.append((x, y))
        self.path = breadth_first_search(self.g, vec(x_fig, y_fig), 8)
        self.reachable_tiles.append((x_fig * TILESIZE, y_fig * TILESIZE))
        for node, dir in self.path.items():
            if dir:
                x, y = node
                x = x * TILESIZE
                y = y * TILESIZE
                self.reachable_tiles.append((x, y))

    def draw_reachable_tiles(self):
        for tile in self.reachable_tiles:
            rect = pygame.Rect(tile[0], tile[1], TILESIZE, TILESIZE)
            pygame.draw.rect(screen, LIGHTGRAY, rect)
        for tile in self.shortest_path_tiles:
            rect = pygame.Rect(tile[0], tile[1], TILESIZE, TILESIZE)
            pygame.draw.rect(screen, LIGHTBLUE, rect)


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

animation_player = Animation_Player()
particle_player = Particle_Player()
item_player = Item_Player()
game = Game()

# char = Character(animation_player, game.clear_path)

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

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game.selected_char and event.button == 1:
                game.selected_char.change_state('walk')
                game.selected_char.waypoints = game.get_shortest_path() * 1
                if game.selected_char.waypoints:
                    game.selected_char.set_target_position(game.selected_char.waypoints[0][0],
                                                           game.selected_char.waypoints[0][1])
                game.mob_selection()
                if game.selected_mob:
                    length_waypoints = len(game.selected_char.waypoints)
                    last_x, last_y = game.selected_char.waypoints[length_waypoints - 1][0], game.selected_char.waypoints[length_waypoints - 1][1]
                    mob_x, mob_y = game.selected_mob.position_x, game.selected_mob.position_y
                    last_x, last_y = from_screenspace_to_gridspace((last_x, last_y))
                    mob_x, mob_y = from_screenspace_to_gridspace((mob_x, mob_y))
                if game.selected_mob and heuristic(vec(last_x, last_y), vec(mob_x, mob_y)) == 1:
                    game.selected_char.attack_after_walk = True
                    game.selected_char.target = game.selected_mob
                else:
                    game.selected_char.attack_after_walk = False
                game.selected_char = None
            elif event.button == 3:
                game.clear_path()
                game.selected_char = None
                game.selected_mob = None
                for char in game.characters:
                    char.is_selected(False)
            else:
                game.character_selection()
                game.calculate_possible_paths_character()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pos = from_screenspace_to_gridspace(pygame.mouse.get_pos())
                game.particles.append(Particle(particle_player, 'inferno', pos, game.clear_particle))
            if event.key == pygame.K_u:
                pos = from_screenspace_to_gridspace(pygame.mouse.get_pos())
                game.particles.append(Particle(particle_player, 'update', pos, game.clear_particle))
            if event.key == pygame.K_a:
                game.ai_turn()
        if 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    char.change_state('attack')

                if event.key == pygame.K_w:
                    char.change_state('walk')
                    char.waypoints = game.get_shortest_path()
                    char.set_target_position(char.waypoints[0][0], char.waypoints[0][1])

                if event.key == pygame.K_t:
                    char.change_state('take_hit')

                if event.key == pygame.K_d:
                    char.change_state('death')

                if event.key == pygame.K_p:
                    game.calculate_possible_paths_character(char)

                if event.key == pygame.K_q:
                    print(char.waypoints)

    current_mouse_pos = from_screenspace_to_gridspace(pygame.mouse.get_pos())

    if game.mouse_position != current_mouse_pos and game.calculate_new_path:
        game.calculate_shortest_path_character()
    game.mouse_position = current_mouse_pos

    game.update()
    clock.tick(FPS)
    screen.fill(DARKGRAY)
    game.draw_reachable_tiles()

    draw_grid()
    game.draw_characters()
    pygame.display.flip()
