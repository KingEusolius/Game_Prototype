import pygame
import os
import numpy as np


class Item_Player:
    def __init__(self):
        print('In item player constructor')
        items = ['spell', 'book']
        self.items = {}
        self.items_outline = {}
        for it in items:
            self.items[f'{it}'] = []
            self.items_outline[f'{it}'] = []
            for pic in os.listdir(f'graphics/items/{it}'):
                current_img = pygame.image.load(f'graphics/items/{it}/{pic}').convert_alpha()
                current_img = pygame.transform.scale(current_img, (48, 48))
                self.items[f'{it}'].append(current_img)
                self.items_outline[f'{it}'].append(pygame.mask.from_surface(current_img))

    def get_item_image(self, item_name):
        return self.items[item_name][0]

    def get_outline(self, item_name):
        return self.items_outline[item_name][0].outline()


class Item:
    def __init__(self, item_player, item_type, position):
        self.item_player = item_player
        self.item_type = item_type
        self.img = item_player.get_item_image(item_type)
        self.outline = item_player.get_outline(self.item_type)
        self.selected = False
        self.position_x = position[0] * 64 + np.random.randint(-32, 32)
        self.position_y = position[1] * 64 + np.random.randint(-32, 32)
        self.position_z = 5
        self.velocity_z = -0.2
        self.max_speed = 4
        self.x_vel = -0.2 * self.max_speed
        self.y_vel = 0.1 * self.max_speed
        self.z_vel = 8
        self.z_vel_init = 8
        self.bounces = 5

    def update(self):
        if self.position_z < 0 and self.bounces > 0:
            self.position_z = 0
            self.z_vel_init /= 2
            self.z_vel = 1 * self.z_vel_init
            self.position_z += self.z_vel
            self.x_vel /= 2
            self.y_vel /= 2
            self.bounces -= 1
        if self.bounces == 0:
            self.position_z = 0

        if self.position_z != 0:
            self.position_z += self.z_vel
            self.z_vel -= 0.25
            self.position_x += self.x_vel
            self.position_y += self.y_vel

        self.check_overlap(pygame.mouse.get_pos())

    def check_overlap(self, position):
        self.selected = (self.position_x <= position[0] < self.position_x + 48 and self.position_y <= position[
            1] < self.position_y + 48)

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y - self.position_z))
        if self.selected:
            for point in self.outline:
                x = point[0] + self.position_x
                y = point[1] + self.position_y - self.position_z
                pygame.draw.line(screen, (255, 0, 0), (x, y), (x, y), 4)
