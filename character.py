import pygame
import numpy as np
from pathfinding import heuristic, vec, vec2int

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
    def __init__(self, anim_player, clear_path, pos, class_name, spawn_item, dictionary, calc_attack_path, is_mob, create_projectile, item):
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

    def get_stats(self, dictionary):
        self.health = dictionary.char_dict[self.class_name]['health']
        self.attack_power = dictionary.char_dict[self.class_name]['attack_power']
        self.speed = dictionary.char_dict[self.class_name]['speed']
        self.long_range = dictionary.char_dict[self.class_name]['long_range']
        self.attack_range = dictionary.char_dict[self.class_name]['attack_range']
        self.move_range = dictionary.char_dict[self.class_name]['move_range']
        self.max_move_range = self.move_range * 1

    def update(self):
        self.img = self.anim_player.get_image(self.class_name, self.state, int(self.animation_index))
        self.outline = self.anim_player.get_outline(self.class_name, self.state, int(self.animation_index))
        if self.direction_x < 0:
            self.img = pygame.transform.flip(self.img, True, False)
        finished = self.play_animation()

        self.state_transition_handling(finished)
        if self.ai_turn and not self.actions:
            self.ai_turn = False

        if not self.ai_turn and not self.check_if_turn_is_over():
            self.finished = True



    def state_transition_handling(self, finished):
        if self.state == 'walk':
            if len(self.waypoints) > 0:
                self.move(pygame.math.Vector2(self.direction_x, self.direction_y))
            else:
                if self.is_mob:
                    self.actions.pop(0)
                self.clear_path_for_game()
                if self.move_range <= 0:
                    self.can_walk = False
                if self.deselect_after_action:
                    self.is_selected(False)

                if self.attack_after_walk:
                    self.change_state('attack')
                    self.attack_after_walk = False
                else:
                    self.change_state('idle')
                    if self.can_attack and not self.is_mob:
                        self.calc_attack_path(self)

        elif self.state == 'attack':
            if finished:
                if self.is_mob:
                    self.actions.pop(0)
                self.can_attack = False
                self.change_state('idle')

        elif self.state == 'take_hit':
            if finished:
                self.update_status()
                self.change_state('idle')
                if self.health <= 0:
                    self.change_state('death')

        elif self.state == 'death':
            if finished:
                self.change_state('dead')
                self.alive = False

        elif self.state == 'dead':
            self.animation_index = 0

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

    def change_state(self, state):
        self.animation_index = 0
        self.state = state
        if self.state == 'attack':
            self.get_direction(self.target.position_x, self.target.position_y)
            if self.long_range == 0:
                self.target.change_state('take_hit')
                self.target.take_damage(self.attack_power)
                self.target = None
            else:
                if "lich" in self.class_name:
                    self.create_projectile("death_ripple", (self.target.position_x, self.target.position_y))
                else:
                    self.create_projectile(self.position_x, self.position_y, self.target, self.attack_power)

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

    def find_nearest_target(self, characters):
        nearest_char = None
        nearest_char_distance = np.inf
        x_self, y_self = from_screenspace_to_gridspace((self.position_x, self.position_y))
        for char in characters:
            if char.health > 0:
                x_char, y_char = from_screenspace_to_gridspace((char.position_x, char.position_y))
                decision_value = heuristic(vec(x_self, y_self), vec(x_char, y_char))
                if decision_value < nearest_char_distance:
                    nearest_char = char
                    nearest_char_distance = decision_value
        return nearest_char

    def find_nearest_and_strongest_target(self, characters):
        nearest_char = None
        nearest_char_distance = np.inf
        x_self, y_self = from_screenspace_to_gridspace((self.position_x, self.position_y))
        for char in characters:
            if char.health > 0:
                x_char, y_char = from_screenspace_to_gridspace((char.position_x, char.position_y))
                decision_value = heuristic(vec(x_self, y_self), vec(x_char, y_char)) - char.health
                if decision_value < nearest_char_distance:
                    nearest_char = char
                    nearest_char_distance = decision_value
        return nearest_char

    def find_nearest_and_weakest_target(self, characters):
        nearest_char = None
        nearest_char_distance = np.inf
        x_self, y_self = from_screenspace_to_gridspace((self.position_x, self.position_y))
        for char in characters:
            if char.health > 0:
                x_char, y_char = from_screenspace_to_gridspace((char.position_x, char.position_y))
                decision_value = heuristic(vec(x_self, y_self), vec(x_char, y_char)) + char.health
                if decision_value < nearest_char_distance:
                    nearest_char = char
                    nearest_char_distance = decision_value
        return nearest_char

    def update_status(self):
        self.stats_img.fill(self.color)
        text_surface = my_font.render(f'{self.attack_power} / {self.health}', True, (0, 0, 0))
        text_width = text_surface.get_width()
        text_pos = (64 - text_width) // 2
        self.stats_img.blit(text_surface, (text_pos, 0))

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y))

        if self.selected:
            for point in self.outline:
                if self.direction_x < 0:
                    x = -point[0] + 64 + self.position_x
                else:
                    x = point[0] + self.position_x
                y = point[1] + self.position_y
                pygame.draw.line(screen, (255, 0, 0), (x, y), (x, y), 4)

        if self.in_range:
            for point in self.outline:
                if self.direction_x < 0:
                    x = -point[0] + 64 + self.position_x
                else:
                    x = point[0] + self.position_x
                y = point[1] + self.position_y
                pygame.draw.line(screen, (255, 215, 0), (x, y), (x, y), 4)

        screen.blit(self.stats_img, (self.position_x, self.position_y - 16))
