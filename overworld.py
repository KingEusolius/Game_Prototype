from pygame.math import clamp

from game_class import GameClass
import pygame, sys
import numpy as np
from buildings import *


class Overworld(GameClass):
    def __init__(self, avatar, enemies, set_fight):
        super().__init__(set_fight)
        self.avatar = avatar
        self.enemies = enemies
        self.running = True
        self.selected_enemy = None
        self.buildings_player = Building_Player()
        self.buildings = [Building(self.buildings_player, 3 * 64, 6 * 64, "windmill"), Building(self.buildings_player, 13 * 64, 2 * 64, "watermill")]
        self.buildings.append(Building(self.buildings_player, 5 * 64, 1 * 64, "tradingpost"))
        self.buildings.append(Building(self.buildings_player, 11 * 64, 5 * 64, "stables"))
        self.background_image = None
        # debug code
        self.enemies[0].mobs[0].set_items(['sword', 'crossbow'])
        self.enemies[1].mobs[0].set_items(['book'])
        self.enemies[2].mobs[1].set_items(['horse'])
        # test for camera
        self.camera_img = pygame.Surface((64 * 16, 64 * 10), pygame.SRCALPHA, 32)
        self.fog_img = pygame.Surface((64 * 16, 64 * 10), pygame.SRCALPHA, 32)
        self.detected_img = pygame.Surface((64 * 16, 64 * 10), pygame.SRCALPHA, 32)
        self.color = (0, 0, 0)
        self.fog_img.fill(self.color)
        k = 100
        self.detected_img.fill((k, k, k))

        self.circle_img = pygame.Surface((32, 32), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.circle_img, (255, 255, 255), (16, 16), 16)
        self.circle_img = pygame.transform.scale(self.circle_img, (256, 256))


    def set_img(self, img):
        self.background_image = img

    def input_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if self.input_handling_allowed:
                # debug code
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.trigger_transition()

                keys = pygame.key.get_pressed()
                self.avatar.handle_input(keys)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # pack into own function
                    for enemy in self.enemies:
                        if enemy.rect.collidepoint(pygame.mouse.get_pos()) and not enemy.defeated and enemy.in_range:
                            self.trigger_transition()
                            self.selected_enemy = enemy

    def update(self):
        self.avatar.update()
        for enemy in self.enemies:
            enemy.update()
            enemy.in_range = self.check_distance(enemy)

        for building in self.buildings:
            building.update()
            building.is_selected(pygame.mouse.get_pos())

    def draw(self, screen):
        self.draw_background(self.camera_img)

        self.avatar.draw(self.camera_img)
        for enemy in self.enemies:
            enemy.draw(self.camera_img)
            if enemy.in_range:
                enemy.draw_outline(self.camera_img)

        for building in self.buildings:
            building.draw(self.camera_img)

        self.transition_drawing(self.camera_img)

        # if we want to center the player
        # x_offset = self.avatar.position_x - 64 * 8
        # y_offset = self.avatar.position_y - 64 * 5
        # screen.blit(self.camera_img, (-x_offset, -y_offset))

        # if we want to use fog of war - still needs a lot of improvement
        self.fog_img.blit(self.detected_img, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.fog_img.blit(self.circle_img, (self.avatar.position_x - (256 / 2 - 32 / 2), self.avatar.position_y - (256 / 2 - 32 / 2)))
        #pygame.draw.circle(self.fog_img, (255, 255, 255), (self.avatar.position_x, self.avatar.position_y), 150)

        self.camera_img.blit(self.fog_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)



        screen.blit(self.camera_img, (0, 0))



    def draw_background(self, screen):
        screen.blit(self.background_image, (0, 0))

    def check_distance(self, mob):
        return np.sqrt((self.avatar.position_x - mob.position_x) ** 2 + (
                    self.avatar.position_y - mob.position_y) ** 2) < 100 and not mob.defeated
