import pygame
import numpy as np
import os


class Avatar_Player:
    def __init__(self):
        print('In avatar player constructor')
        classes = ['men']
        state_list = ['right']
        self.classes = {}
        # self.classes_outlines = {}
        for cl in classes:
            self.classes[f'{cl}'] = {}
            # self.classes_outlines[f'{cl}'] = {}
            for state in state_list:
                self.classes[f'{cl}'][f'{state}'] = []
                # self.classes_outlines[f'{cl}'][f'{state}'] = []
                for pic in os.listdir(f'graphics/heroes/{cl}/{state}'):
                    current_img = pygame.image.load(f'graphics/heroes/{cl}/{state}/{pic}').convert_alpha()
                    current_img = pygame.transform.scale(current_img, (32, 32))
                    self.classes[f'{cl}'][f'{state}'].append(current_img)
                    # self.classes_outlines[f'{cl}'][f'{state}'].append(pygame.mask.from_surface(current_img))

        # print(self.classes)

    def get_image(self, class_name, class_state, index):
        return self.classes[class_name][class_state][index]


class Avatar:
    def __init__(self, avatar_player, class_name, chars):
        self.size = 32
        self.position_x = 1 * self.size
        self.position_y = 1 * self.size
        self.avatar_player = avatar_player
        self.class_name = class_name
        self.state = 'right'
        self.animation_index = 0
        self.img = avatar_player.get_image(self.class_name, self.state, self.animation_index)
        self.direction_x = 0
        self.direction_y = 0
        self.speed = 2
        self.image_direction = self.direction_x
        self.dir_length = 0.01
        self.inventory = [None] * 4
        self.chars = chars

    def check_characters(self):
        for idx, char in enumerate(self.chars):
            if not char.alive:
                # test if works as intended
                self.chars.pop(idx)

    def handle_input(self, keys):
        direction_x = 0
        direction_y = 0

        if keys[pygame.K_d]:
            direction_x = 1
        if keys[pygame.K_a]:
            direction_x = -1
        if keys[pygame.K_s]:
            direction_y = 1
        if keys[pygame.K_w]:
            direction_y = -1

        self.dir_length = np.sqrt(direction_x ** 2 + direction_y ** 2)

        if self.dir_length:
            self.direction_x = direction_x / self.dir_length
            self.direction_y = direction_y / self.dir_length
            self.check_image_direction()
        else:
            self.direction_x = 0
            self.direction_y = 0
            self.animation_index = 0

    def handle_input_mouse(self, pressed, mouse_pos):
        self.dir_length = np.sqrt((self.position_x - mouse_pos[0]) ** 2 + (self.position_y - mouse_pos[1]) ** 2)
        if pressed:
            direction_x = mouse_pos[0] - self.position_x
            direction_y = mouse_pos[1] - self.position_y
            self.direction_x = direction_x / self.dir_length
            self.direction_y = direction_y / self.dir_length
            self.check_image_direction()
            self.play_animation()
        else:
            self.direction_x = 0
            self.direction_y = 0
            self.animation_index = 0

    def update(self, collision_rects):
        if self.dir_length != 0:
            self.play_animation()
        self.img = self.avatar_player.get_image(self.class_name, self.state, int(self.animation_index))
        if self.image_direction < 0:
            self.img = pygame.transform.flip(self.img, True, False)
        self.position_x += (self.direction_x * self.speed)
        self.check_collisions(collision_rects, 'horizontal')
        self.position_y += (self.direction_y * self.speed)
        self.check_collisions(collision_rects, 'vertical')

    def check_image_direction(self):
        if self.direction_x != 0:
            self.image_direction = self.direction_x

    def play_animation(self):
        self.animation_index += 0.1
        if self.animation_index >= 4:
            self.animation_index = 0

    def draw(self, screen, x_offset=0, y_offset=0):
        screen.blit(self.img, (self.position_x + x_offset, self.position_y + y_offset))
        #rect = self.img.get_rect().scale_by(0.5)

        #rect.top = self.position_y + 8
        #rect.left = self.position_x + 8
        #pygame.draw.rect(screen, (0, 0, 255), rect)

    def check_collisions(self, collision_rects, dir):
        self_rect = self.img.get_rect().scale_by(0.5)
        self_rect.top = self.position_y + 8
        self_rect.left = self.position_x + 8
        if dir == 'horizontal':
            for rect in collision_rects:
                if self_rect.colliderect(rect):
                    if self.direction_x > 0:
                        self.position_x = rect.rect.left - 24
                    if self.direction_x < 0:
                        self.position_x = rect.rect.right - 8

        if dir == "vertical":
            for rect in collision_rects:
                if self_rect.colliderect(rect):
                    if self.direction_y > 0:
                        self.position_y = rect.rect.top - 24
                    if self.direction_y < 0:
                        self.position_y = rect.rect.bottom - 8



class Avatar_Enemies_Player:
    def __init__(self):
        print('In avatar enemies player constructor')
        classes = ['imp_minor', 'imp_major']
        state_list = ['idle', 'dead']
        self.classes = {}
        self.classes_outlines = {}
        for cl in classes:
            self.classes[f'{cl}'] = {}
            self.classes_outlines[f'{cl}'] = {}
            for state in state_list:
                self.classes[f'{cl}'][f'{state}'] = []
                self.classes_outlines[f'{cl}'][f'{state}'] = []
                for pic in os.listdir(f'graphics/units/{cl}/{state}'):
                    current_img = pygame.image.load(f'graphics/units/{cl}/{state}/{pic}').convert_alpha()
                    current_img = pygame.transform.scale(current_img, (32, 32))
                    self.classes[f'{cl}'][f'{state}'].append(current_img)
                    self.classes_outlines[f'{cl}'][f'{state}'].append(pygame.mask.from_surface(current_img))

        # print(self.classes)

    def get_image(self, class_name, class_state, index):
        return self.classes[class_name][class_state][index]

    def get_outline(self, class_name, class_state, index):
        return self.classes_outlines[class_name][class_state][index].outline()


class Avatar_Enemies:
    def __init__(self, avatar_enemies_player, pos_x, pos_y, class_name, mobs):
        self.position_x = pos_x
        self.position_y = pos_y
        self.state = 'idle'
        self.class_name = class_name
        self.avatar_enemies_player = avatar_enemies_player
        rand_number = np.random.randint(0, 400)
        self.animation_index = rand_number / 400
        rand_number = np.random.randint(0, 4)
        self.img = pygame.image.load(f"graphics/units/{class_name}/idle/{rand_number}.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (32, 32))
        self.rect = self.img.get_rect()
        self.rect.x = self.position_x
        self.rect.y = self.position_y
        self.defeated = False
        self.mobs = mobs
        self.outline = avatar_enemies_player.get_outline(self.class_name, self.state, int(self.animation_index))
        self.in_range = False

    def update(self):
        self.play_animation()
        self.img = self.avatar_enemies_player.get_image(self.class_name, self.state, int(self.animation_index))

    def play_animation(self):
        self.animation_index += 0.025
        if self.animation_index >= len(self.avatar_enemies_player.classes[self.class_name][self.state]):
            self.animation_index = 0

    def set_defeated(self):
        self.defeated = True
        self.state = 'dead'

    def draw(self, screen, x_offset=0, y_offset=0):
        screen.blit(self.img, (self.position_x + x_offset, self.position_y + y_offset))
        if self.in_range:
            self.outline = self.avatar_enemies_player.get_outline(self.class_name, self.state,
                                                                  int(self.animation_index))
            for point in self.outline:
                x = point[0] + self.position_x + x_offset
                y = point[1] + self.position_y + y_offset
                pygame.draw.line(screen, (255, 0, 0), (x, y), (x, y), 1)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect)

    def draw_outline(self, screen, x_offset=0, y_offset=0):
        self.outline = self.avatar_enemies_player.get_outline(self.class_name, self.state, int(self.animation_index))
        for point in self.outline:
            x = point[0] + self.position_x + x_offset
            y = point[1] + self.position_y + y_offset
            pygame.draw.line(screen, (255, 0, 0), (x, y), (x, y), 1)
