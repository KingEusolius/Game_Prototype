import pygame
import os


class Animation_Player:
    def __init__(self):
        print('In animation player constructor')
        state_list = ['idle', 'walk', 'attack', 'take_hit', 'death', 'dead']
        classes = ['cavalier', 'imp']
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
                    current_img = pygame.transform.scale(current_img, (64, 64))
                    self.classes[f'{cl}'][f'{state}'].append(current_img)
                    self.classes_outlines[f'{cl}'][f'{state}'].append(pygame.mask.from_surface(current_img))

        #print(self.classes)

    def get_image(self, class_name, class_state, index):
        return self.classes[class_name][class_state][index]

    def get_outline(self, class_name, class_state, index):
        return self.classes_outlines[class_name][class_state][index].outline()

    def is_animation_over(self, index):
        return int(index) >= 4

