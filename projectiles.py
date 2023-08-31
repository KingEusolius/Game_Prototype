import pygame
import numpy as np


class Arrow:
    def __init__(self, pos, target, attack_power):
        self.position_x = pos[0]
        self.position_y = pos[1]
        self.length = 4
        self.speed = 12
        length = np.sqrt(
            (target.position_x - self.position_x + 32) ** 2 + (target.position_y - self.position_y + 32) ** 2)
        self.direction_x = (target.position_x - self.position_x + 32) / length
        self.direction_y = (target.position_y - self.position_y + 32) / length
        self.target = target
        self.hit = False
        self.attack_power = attack_power
        self.img = pygame.image.load("graphics/mouse/ArrowOrigin 1.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (32, 32))
        norm = pygame.math.Vector2(1, 0)
        perp = pygame.math.Vector2(self.direction_x, self.direction_y)
        angle = norm.angle_to(perp)
        self.img = pygame.transform.rotate(self.img, -45 - angle)
        self.create_particle = False
        self.particle_create = None
        self.particle = None

    def set_particle(self, part):
        self.create_particle = part

    def set_particle_create(self, func, particle):
        self.particle_create = func
        self.particle = particle

    def update(self):
        self.position_x += self.direction_x * self.speed
        self.position_y += self.direction_y * self.speed
        self.check_overlap()

    def check_overlap(self):
        if self.target.position_x + 16 <= self.position_x < self.target.position_x + 48 and self.target.position_y + 16 <= self.position_y < self.target.position_y + 48:
            self.hit = True
            self.target.state_machine.trigger_transition("ACTION::TRANSITION_HIT")
            self.target.take_damage(self.attack_power)
            # create particle here if necessary. use observer pattern. get info from ui/character
            if self.create_particle:
                self.particle_create(self.particle.particle_type, (self.position_x, self.position_y))

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y))
        #pygame.draw.line(screen, (255, 0, 0), (self.position_x, self.position_y),
        #                 (self.position_x + self.direction_x * self.length,
        #                  self.position_y + self.direction_y * self.length), 2)
