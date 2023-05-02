import pygame


class Animation_Player:
    def __init__(self):
        self.classes = {}
        self.classes['Rider'] = {'down': [pygame.image.load(
            'graphics/hero/down/CastleSpriteMale-Down (Frame 1).png').convert_alpha(),
                                          pygame.image.load(
                                              'graphics/hero/down/CastleSpriteMale-Down (Frame 2).png').convert_alpha(),
                                          pygame.image.load(
                                              'graphics/hero/down/CastleSpriteMale-Down (Frame 3).png').convert_alpha(),
                                          pygame.image.load(
                                              'graphics/hero/down/CastleSpriteMale-Down (Frame 4).png').convert_alpha()
                                          ],
                                 'right': [pygame.image.load(
                                     'graphics/hero/right/CastleSpriteMale-Right (Frame 1).png').convert_alpha(),
                                           pygame.image.load(
                                               'graphics/hero/right/CastleSpriteMale-Right (Frame 2).png').convert_alpha(),
                                           pygame.image.load(
                                               'graphics/hero/right/CastleSpriteMale-Right (Frame 3).png').convert_alpha(),
                                           pygame.image.load(
                                               'graphics/hero/right/CastleSpriteMale-Right (Frame 4).png').convert_alpha()
                                           ]}

    def get_image(self, class_name, class_state, index):
        return self.classes[class_name][class_state][index]

    def is_animation_over(self, index):
        if int(index) >= 4:
            return True
        return False
