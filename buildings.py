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

    def get_outline(self, class_name, index):
        return self.classes_outlines[class_name][index].outline()


class Building:
    def __init__(self, building_player, pos_x, pos_y, class_name):
        self.position_x = pos_x
        self.position_y = pos_y
        self.building_player = building_player
        self.class_name = class_name
        self.animation_index = 0
        self.img = building_player.get_image(self.class_name, int(self.animation_index))
        self.outline = building_player.get_outline(self.class_name, int(self.animation_index))
        self.selected = False

    def update(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.building_player.classes[self.class_name]):
            self.animation_index = 0
        self.img = self.building_player.get_image(self.class_name, int(self.animation_index))
        self.outline = self.building_player.get_outline(self.class_name, int(self.animation_index))

    def is_selected(self, mouse_pos, x_offset, y_offset):
        self.selected = (self.position_x + x_offset <= mouse_pos[0] < self.position_x + x_offset + 64 and self.position_y + y_offset <= mouse_pos[
            1] < self.position_y + y_offset + 64)

    def draw(self, screen, x_offset=0, y_offset=0):
        screen.blit(self.img, (self.position_x + x_offset, self.position_y + y_offset))

        if self.selected:
            for point in self.outline:
                x = point[0] + self.position_x
                y = point[1] + self.position_y
                pygame.draw.line(screen, (255, 0, 0), (x + x_offset, y + y_offset), (x + x_offset, y + y_offset), 2)