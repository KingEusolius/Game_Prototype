import pygame
import os
import numpy as np
my_font = pygame.font.SysFont('New Times Roman', 20)


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
        x = np.random.randint(-6, 6) / 10.0
        y = np.random.randint(-4, 2) / 10.0
        self.x_vel = x * self.max_speed
        self.y_vel = y * self.max_speed
        self.z_vel = 6
        self.z_vel_init = 6
        self.bounces = 5

        if item_type == 'book':
            self.particle_type = 'update'
        else:
            self.particle_type = 'inferno'

        self.inventory_img = pygame.image.load(f'graphics/icons/{self.particle_type}.png').convert_alpha()
        self.inventory_img = pygame.transform.scale(self.inventory_img, (64, 64))

        self.upgrades = ["Damage: +5", "Health: +10", "Immune to fire"]
        max_width = 0
        text_surfaces = []
        for up in self.upgrades:
            text_surf = my_font.render(up, True, (0, 0, 0))
            text_surfaces.append(text_surf)
            if text_surf.get_width() > max_width:
                max_width = text_surf.get_width()
        self.stats_img = pygame.Surface((max_width + 5, len(self.upgrades) * 15))
        self.stats_img.fill((200, 200, 200))
        for idx, surf in enumerate(text_surfaces):
            self.stats_img.blit(surf, (0, idx * 15))


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
        return self.selected

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y - self.position_z))
        if self.selected:
            for point in self.outline:
                x = point[0] + self.position_x
                y = point[1] + self.position_y - self.position_z
                pygame.draw.line(screen, (255, 0, 0), (x, y), (x, y), 4)
            screen.blit(self.stats_img, (self.position_x, self.position_y - 64))
