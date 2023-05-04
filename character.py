import pygame


class Character:
    def __init__(self, anim_player, clear_path):
        self.class_name = 'Cavalier'
        self.state = 'idle'
        self.direction = 'down'
        self.animation_index = 0
        self.anim_player = anim_player

        self.direction_x = 0
        self.direction_y = 0

        self.waypoints = []

        self.img = anim_player.get_image(self.class_name, self.state, self.animation_index)
        self.img = pygame.transform.scale(self.img, (64, 64))

        self.position_x = 2 * 64
        self.position_y = 2 * 64

        self.target_position_x = 400
        self.target_position_y = 100

        self.clear_path_for_game = clear_path

    def update(self):
        self.img = self.anim_player.get_image(self.class_name, self.state, int(self.animation_index))
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
                self.change_state('idle')

        elif self.state == 'attack':
            if finished:
                self.change_state('idle')

        elif self.state == 'take_hit':
            if finished:
                self.change_state('idle')

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

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y))
