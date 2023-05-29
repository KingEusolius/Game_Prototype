import pygame
import os

class UI:
    def __init__(self, inventory, spawn_particle):
        screen = pygame.display.get_surface()
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.nr_item_slots = 4
        self.nr_resource_slots = 4
        self.item_slots = []
        self.resource_slots = []
        self.inventory = inventory
        self.char = None
        self.gray_img = pygame.Surface((64, 64))
        self.gray_img.fill((80, 80, 80))
        for i in range(self.nr_item_slots):
            self.item_slots.append(UI_Skill(self.screen_width // 2 - (self.nr_item_slots // 2 - i) * 64, self.screen_height - 64, spawn_particle, i, 64))
        for idx, item in enumerate(self.inventory):
            if item:
                self.item_slots[idx].occupy_spot(item.particle_type)

        for i in range(self.nr_resource_slots):
            self.resource_slots.append(UI_Skill(self.screen_width - 64, self.screen_height // 2 - (self.nr_resource_slots // 2 - i) * 64, spawn_particle, i, 64))

    def on_mouse_click(self, mouse_pos):
        for rect in self.item_slots:
            if rect.on_mouse_click(mouse_pos):
                self.inventory[rect.index] = None
                return True
        for rect in self.resource_slots:
            if rect.on_mouse_click(mouse_pos):
                self.char.can_attack = False
                index = rect.index
                self.char.skills_available_this_turn[index] = False
                return True
        return False

    def set_spot_occupied(self, index, particle_type):
        self.item_slots[index].occupy_spot(particle_type)

    def draw(self, screen, char):
        for idx, item in enumerate(self.inventory):
            if item:
                screen.blit(item.inventory_img, (self.screen_width // 2 - (self.nr_item_slots // 2 - idx) * 64, self.screen_height - 64))
        for rect in self.item_slots:
            rect.draw(screen)
        self.char = char
        if char:
            for idx, item in enumerate(char.skills):
                if item:
                    screen.blit(item.inventory_img, (self.screen_width - 64, self.screen_height // 2 - (self.nr_resource_slots // 2 - idx) * 64))
                    if char.skills_available_this_turn[idx]:
                        self.resource_slots[idx].occupy_spot(char.skills[idx].particle_type)
                    else:
                        screen.blit(self.gray_img, (self.screen_width - 64, self.screen_height // 2 - (self.nr_resource_slots // 2 - idx) * 64), special_flags=pygame.BLEND_RGBA_SUB)
                else:
                    self.resource_slots[idx].free_spot()
        for rect in self.resource_slots:
            rect.draw(screen)


class UI_Skill:
    def __init__(self, x, y, spawn_particle, index, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.position_x = x
        self.position_y = y
        self.active = False
        self.occupied = False
        self.particle_type = ''
        self.index = index
        self.color = (255, 255, 200)
        self.border_width = 4
        self.spawn_particle = spawn_particle

    def on_mouse_click(self, mouse_pos):
        if self.active and self.occupied:
            self.spawn_particle(self.particle_type)
            self.free_spot()
            self.active = False
            self.color = (255, 255, 200)
            return True

        if self.rect.collidepoint(mouse_pos):
            self.active = True
            self.color = (255, 0, 0)
        else:
            self.active = False
            self.color = (255, 255, 200)
        return False

    def occupy_spot(self, particle_type):
        self.occupied = True
        self.particle_type = particle_type

    def free_spot(self):
        self.occupied = False
        self.particle_type = ''

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, self.border_width)