import pygame


class Character:
    def __init__(self, anim_player):
        self.class_name = 'Cavalier'
        self.state = 'idle'
        self.direction = 'down'
        self.animation_index = 0
        self.anim_player = anim_player

        self.direction = 1

        self.img = anim_player.get_image(self.class_name, self.state, self.animation_index)
        self.img = pygame.transform.scale(self.img, (64, 64))

        self.position_x = 100
        self.position_y = 100

        self.target_position_x = 400
        self.target_position_y = 100

    def update(self):
        self.img = self.anim_player.get_image(self.class_name, self.state, int(self.animation_index))
        if self.direction < 0:
            self.img = pygame.transform.flip(self.img, True, False)
        finished = self.play_animation()

        self.state_transition_handling(finished)

    def state_transition_handling(self, finished):
        if self.state == 'walk':
            if self.position_x != self.target_position_x:
                self.move(pygame.math.Vector2(self.direction, 0))
            else:
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
        self.position_x += amount.x
        self.position_y += amount.y

    def set_target_position(self, x):
        self.target_position_x = x
        self.get_direction(self.target_position_x)

    def change_state(self, state):
        self.animation_index = 0
        self.state = state

    def get_direction(self, target):
        if target == self.position_x:
            return

        if target < self.position_x:
            self.direction = -1
        else:
            self.direction = 1

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y))