import pygame


class Character:
    def __init__(self, anim_player):
        self.class_name = 'Rider'
        self.state = 'Idle'
        self.direction = 'down'
        self.animation_index = 0
        self.anim_player = anim_player
        self.img = anim_player.get_image(self.class_name, self.direction, self.animation_index)
        self.img = pygame.transform.scale(self.img, (64, 64))
        self.play_anim = False

        self.position_x = 100
        self.position_y = 100

        self.target_position_x = 400
        self.target_position_y = 100

    def update(self):
        self.img = self.anim_player.get_image(self.class_name, self.direction, int(self.animation_index))
        self.img = pygame.transform.scale(self.img, (64, 64))

        if self.state == 'Moving' and self.direction == 'right':
            if self.play_anim:
                self.play_animation()

            if self.position_x != self.target_position_x:
                self.move(pygame.math.Vector2(1, 0))
            else:
                self.state = 'Idle'
                self.play_anim = False

        elif self.state == 'Moving' and self.direction == 'down':
            if self.play_anim:
                if self.play_animation():
                    self.state = 'Idle'
                    self.play_anim = False

    def play_animation(self):
        self.animation_index += 0.1
        if self.anim_player.is_animation_over(self.animation_index):
            self.animation_index = 0
            return True

    def move(self, amount):
        self.position_x += amount.x
        self.position_y += amount.y

    def set_target_position(self, x):
        self.target_position_x = x

    def change_state(self, direction):
        self.animation_index = 0
        self.direction = direction

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y))