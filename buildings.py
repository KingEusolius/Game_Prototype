import pygame
import numpy as np
import os


class Building_Player:
    def __init__(self):
        print('In building player constructor')
        classes = os.listdir(f'graphics/buildings')
        self.classes = {}
        self.classes_outlines = {}
        for cl in classes:
            self.classes[f'{cl}'] = []
            self.classes_outlines[f'{cl}'] = []
            for pic in os.listdir(f'graphics/buildings/{cl}'):
                current_img = pygame.image.load(f'graphics/buildings/{cl}/{pic}').convert_alpha()
                current_img = pygame.transform.scale(current_img, (64, 64))
                self.classes[f'{cl}'].append(current_img)
                self.classes_outlines[f'{cl}'].append(pygame.mask.from_surface(current_img))

    def get_image(self, class_name, index):
        return self.classes[class_name][index]


class Building:
    def __init__(self, building_player, pos_x, pos_y, class_name):
        self.position_x = pos_x
        self.position_y = pos_y
        self.building_player = building_player
        self.class_name = class_name
        self.animation_index = 0
        self.img = building_player.get_image(self.class_name, int(self.animation_index))

    def update(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.building_player.classes[self.class_name]):
            self.animation_index = 0
        self.img = self.building_player.get_image(self.class_name, int(self.animation_index))

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y))