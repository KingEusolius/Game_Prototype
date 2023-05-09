import pygame

pygame.font.init()
my_font = pygame.font.SysFont('New Times Roman', 30)

class Character:
    def __init__(self, anim_player, clear_path, pos, class_name):
        self.class_name = class_name
        self.state = 'idle'
        self.direction = 'down'
        self.animation_index = 0
        self.anim_player = anim_player
        self.health = 2

        if class_name == 'cavalier':
            self.direction_x = 0
        else:
            self.direction_x = -1
        self.direction_y = 0

        self.waypoints = []

        self.img = anim_player.get_image(self.class_name, self.state, self.animation_index)
        self.stats_img = pygame.Surface((64, 64 // 4))
        self.color = (0, 0, 255)
        self.stats_img.fill(self.color)
        text_surface = my_font.render(f'{self.health} / {self.health}', True, (0, 0, 0))
        text_width = text_surface.get_width()
        text_pos = (64 - text_width) // 2
        self.stats_img.blit(text_surface, (text_pos, 0))

        self.outline = anim_player.get_outline(self.class_name, self.state, self.animation_index)

        self.position_x = pos.x * 64
        self.position_y = pos.y * 64

        self.target_position_x = 400
        self.target_position_y = 100

        self.clear_path_for_game = clear_path

        self.selected = False



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
                self.is_selected(False)
                self.change_state('idle')

        elif self.state == 'attack':
            if finished:
                self.change_state('idle')

        elif self.state == 'take_hit':
            if finished:
                self.health -= 1
                self.update_status()
                self.change_state('idle')
                if self.health <= 0:
                    self.change_state('death')

        elif self.state == 'death':
            if finished:
                self.change_state('dead')

        elif self.state == 'dead':
            self.animation_index = 0

    def play_animation(self):
        self.animation_index += 0.1
        if self.anim_player.is_animation_over(self.animation_index):
            self.animation_index = 0
            return True
        return False

    def move(self, amount):
        self.position_x += amount.x * 2
        self.position_y += amount.y * 2
        if int(self.position_x) == int(self.waypoints[0][0]) and int(self.position_y) == int(self.waypoints[0][1]):
            del self.waypoints[0]
            if len(self.waypoints):
                self.set_target_position(self.waypoints[0][0], self.waypoints[0][1])

    def set_target_position(self, x, y):
        self.get_direction(x, y)

    def change_state(self, state):
        self.animation_index = 0
        self.state = state

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
        text_surface = my_font.render(f'{self.health} / {self.health}', True, (0, 0, 0))
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

        screen.blit(self.stats_img, (self.position_x, self.position_y - 16))
