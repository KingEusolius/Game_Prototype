import pygame
import os


class Animation_Player:
    def __init__(self):
        print('In animation player constructor')
        state_list = ['idle', 'walk', 'attack', 'take_hit', 'death', 'dead']
        self.classes = {'Cavalier': {}}
        for state in state_list:
            self.classes['Cavalier'][f'{state}'] = []
            for pic in os.listdir(f'graphics/human/cavalier/{state}'):
                current_img = pygame.image.load(f'graphics/human/cavalier/{state}/{pic}').convert_alpha()
                self.classes['Cavalier'][f'{state}'].append(pygame.transform.scale(current_img, (64, 64)))

    def get_image(self, class_name, class_state, index):
        return self.classes[class_name][class_state][index]

    def is_animation_over(self, index):
        if int(index) >= 4:
            return True
        return False
