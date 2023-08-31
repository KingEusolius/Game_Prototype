import pygame
import numpy as np
from pathfinding import heuristic, vec, vec2int
from states import *
from target_finder import *

pygame.font.init()
my_font = pygame.font.SysFont('New Times Roman', 30)
game_over_font = pygame.font.SysFont('Verdana', 60)


def from_screenspace_to_gridspace(screen_coordinates):
    x_grid = screen_coordinates[0] // 64
    y_grid = screen_coordinates[1] // 64
    return x_grid, y_grid


class Character_Dictionary:
    def __init__(self):
        first_line = True
        character_information = []
        self.char_dict = {}
        with open('character_stats.ini') as f:
            for line in f.readlines():
                x = line.split(";")
                if first_line:
                    first_line = False
                    for word in x:
                        if '\n' in word:
                            character_information.append(word.replace('\n', ''))
                        else:
                            character_information.append(word)
                else:
                    for idx, word in enumerate(x):
                        if idx == 0:
                            self.char_dict[word] = {}
                            key = word
                        else:
                            self.char_dict[key][character_information[idx]] = int(word)


class Character:
    def __init__(self, anim_player, clear_path, pos, class_name, spawn_item, dictionary, calc_attack_path, is_mob,
                 create_projectile, item):
        self.class_name = class_name
        self.state = 'idle'
        self.direction = 'down'
        self.animation_index = 0
        self.anim_player = anim_player

        self.attack_after_walk = False
        self.deselect_after_action = False
        self.in_range = False
        self.target = None
        self.alive = True
        self.can_attack = True
        self.can_walk = True
        self.dictionary = dictionary
        self.get_stats(dictionary)
        if is_mob:
            self.direction_x = -1
        else:
            self.direction_x = 0
        self.direction_y = 0

        self.waypoints = []
        self.skills = [None] * 4
        self.skills_available_this_turn = [True] * 4
        self.skills[0] = item
        self.skills[3] = item
        self.items = []

        self.img = anim_player.get_image(self.class_name, self.state, self.animation_index)
        self.stats_img = pygame.Surface((64, 64 // 4))
        self.color = (0, 0, 255)
        self.stats_img.fill(self.color)
        text_surface = my_font.render(f'{self.attack_power} / {self.health}', True, (0, 0, 0))
        text_width = text_surface.get_width()
        text_pos = (64 - text_width) // 2
        self.stats_img.blit(text_surface, (text_pos, 0))

        self.outline = anim_player.get_outline(self.class_name, self.state, self.animation_index)

        self.position_x = pos.x * 64
        self.position_y = pos.y * 64

        self.target_position_x = 400
        self.target_position_y = 100

        self.clear_path_for_game = clear_path
        self.spawn_item = spawn_item
        self.calc_attack_path = calc_attack_path
        self.create_projectile = create_projectile

        self.selected = False
        self.is_mob = is_mob

        self.ai_turn = False
        self.actions = []
        self.finished = False

        self.turn_over = False
        self.notify_fight = None
        self.nr_max_actions = 1
        self.nr_actions = 1
        # init state machine
        self.state_machine = State_machine(self)
        # init target finder
        self.target_finder = NearestTarget()
        self.create_particle = False
        self.particle_create = None
        self.particle = None

    def get_stats(self, dictionary):
        self.health = dictionary.char_dict[self.class_name]['health']
        self.attack_power = dictionary.char_dict[self.class_name]['attack_power']
        self.speed = dictionary.char_dict[self.class_name]['speed']
        self.long_range = dictionary.char_dict[self.class_name]['long_range']
        self.attack_range = dictionary.char_dict[self.class_name]['attack_range']
        self.move_range = dictionary.char_dict[self.class_name]['move_range']
        self.max_move_range = self.move_range * 1

    def set_items(self, items):
        self.items = items

    def set_nr_max_actions(self, nr_max_actions):
        self.nr_max_actions = nr_max_actions

    def set_notify_fight(self, ai_turn):
        self.notify_fight = ai_turn

    def set_particle_create(self, func, particle):
        self.particle_create = func
        self.particle = particle

    def update(self):
        # check if animation should be over and update
        finished = self.play_animation()
        transition = self.state_machine.current_state.update(finished)
        self.state_machine.trigger_transition(transition)
        # TO DO: refactor code
        if self.ai_turn and not self.actions:
            if self.nr_actions != self.nr_max_actions:
                self.nr_actions += 1
                self.notify_fight()
            else:
                self.ai_turn = False
                self.turn_over = True

        if not self.ai_turn and not self.check_if_turn_is_over():
            self.finished = True

    def play_animation(self):
        self.animation_index += 0.1
        if self.anim_player.is_animation_over(self.animation_index):
            self.animation_index = 0
            return True
        return False

    def reset_for_new_turn(self):
        self.can_attack = True
        self.can_walk = True
        self.move_range = self.max_move_range
        for i in range(len(self.skills_available_this_turn)):
            self.skills_available_this_turn[i] = True

    def check_if_turn_is_over(self):
        return self.can_attack or self.can_walk

    def move(self, amount):
        self.position_x += amount.x * self.speed
        self.position_y += amount.y * self.speed
        if int(self.position_x) == int(self.waypoints[0][0]) and int(self.position_y) == int(self.waypoints[0][1]):
            del self.waypoints[0]
            if len(self.waypoints):
                self.set_target_position(self.waypoints[0][0], self.waypoints[0][1])

    def set_target_position(self, x, y):
        self.get_direction(x, y)

    def take_damage(self, amount):
        self.health -= amount

    def get_direction(self, target_x, target_y):
        if target_x == self.position_x:
            self.direction_x = 0

        if target_x < self.position_x:
            self.direction_x = -1
        if target_x > self.position_x:
            self.direction_x = 1

        if target_y == self.position_y:
            self.direction_y = 0

        if target_y < self.position_y:
            self.direction_y = -1
        if target_y > self.position_y:
            self.direction_y = 1

    def is_selected(self, value):
        self.selected = value

    def update_status(self):
        self.stats_img.fill(self.color)
        text_surface = my_font.render(f'{self.attack_power} / {self.health}', True, (0, 0, 0))
        text_width = text_surface.get_width()
        text_pos = (64 - text_width) // 2
        self.stats_img.blit(text_surface, (text_pos, 0))

    def draw(self, screen):
        self.img = self.anim_player.get_image(self.class_name, self.state, int(self.animation_index))

        if self.direction_x < 0:
            self.img = pygame.transform.flip(self.img, True, False)
        screen.blit(self.img, (self.position_x, self.position_y))

        if self.selected:
            self.outline = self.anim_player.get_outline(self.class_name, self.state, int(self.animation_index))
            self.calc_outline(screen, (255, 0, 0))

        if self.in_range:
            self.outline = self.anim_player.get_outline(self.class_name, self.state, int(self.animation_index))
            self.calc_outline(screen, (255, 215, 0))

        screen.blit(self.stats_img, (self.position_x, self.position_y - 16))

    def calc_outline(self, screen, color):
        for point in self.outline:
            if self.direction_x < 0:
                x = -point[0] + 64 + self.position_x
            else:
                x = point[0] + self.position_x
            y = point[1] + self.position_y
            pygame.draw.line(screen, color, (x, y), (x, y), 4)
