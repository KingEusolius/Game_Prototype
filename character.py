import pygame

pygame.font.init()
my_font = pygame.font.SysFont('New Times Roman', 30)
game_over_font = pygame.font.SysFont('Verdana', 60)

class Character_Dictionary:
    def __init__(self):
        first_line = True
        character_information = []
        self.char_dict = {}
        with open('character_stats.txt') as f:
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
    def __init__(self, anim_player, clear_path, pos, class_name, spawn_item, dictionary, calc_attack_path):
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
        self.get_stats(dictionary)
        if class_name == 'cavalier' or class_name == 'archer':
            self.direction_x = 0
        else:
            self.direction_x = -1
        self.direction_y = 0

        self.waypoints = []

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

        self.selected = False

    def get_stats(self, dictionary):
        self.health = dictionary.char_dict[self.class_name]['health']
        self.attack_power = dictionary.char_dict[self.class_name]['attack_power']
        self.speed = dictionary.char_dict[self.class_name]['speed']
        self.long_range = dictionary.char_dict[self.class_name]['long_range']
        self.attack_range = dictionary.char_dict[self.class_name]['attack_range']
        self.move_range = dictionary.char_dict[self.class_name]['move_range']

    def update(self):
        self.img = self.anim_player.get_image(self.class_name, self.state, int(self.animation_index))
        self.outline = self.anim_player.get_outline(self.class_name, self.state, int(self.animation_index))
        if self.direction_x < 0:
            self.img = pygame.transform.flip(self.img, True, False)
        finished = self.play_animation()

        self.state_transition_handling(finished)

    def state_transition_handling(self, finished):
        if self.state == 'walk':
            if len(self.waypoints) > 0:
                self.move(pygame.math.Vector2(self.direction_x, self.direction_y))
            else:
                self.clear_path_for_game()
                self.can_walk = False
                if self.deselect_after_action:
                    self.is_selected(False)
                if self.attack_after_walk:
                    self.change_state('attack')

                else:
                    self.change_state('idle')
                    if self.can_attack:
                        self.calc_attack_path(self)

        elif self.state == 'attack':

            if finished:
                self.can_attack = False
                self.change_state('idle')

        elif self.state == 'take_hit':
            if finished:
                #self.health -= 2
                self.update_status()
                self.change_state('idle')
                if self.health <= 0:
                    self.change_state('death')

        elif self.state == 'death':
            if finished:
                #self.spawn_item((self.position_x, self.position_y))
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
            if self.class_name != 'archer':
                self.target.change_state('take_hit')
                self.target.take_damage(self.attack_power)
                self.target = None

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
        #self.stats_img = pygame.Surface((self.width, self.height // 4))
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
