import pygame
import os


class Particle_Player:
    def __init__(self):
        print('In particle player constructor')
        particles = ['inferno', 'update']
        self.particles = {}
        for pl in particles:
            self.particles[f'{pl}'] = []
            for pic in os.listdir(f'graphics/particles/{pl}'):
                current_img = pygame.image.load(f'graphics/particles/{pl}/{pic}').convert_alpha()
                current_img = pygame.transform.scale(current_img, (64, 64))
                self.particles[f'{pl}'].append(current_img)

    def get_particle_image(self, particle_name, index):
        return self.particles[particle_name][index]

    def is_animation_over(self, index):
        if int(index) >= 4:
            return True
        return False


class Particle:
    def __init__(self, particle_player, particle_type, position, clear_particle):
        self.particle_player = particle_player
        self.animation_index = 0
        self.particle_type = particle_type
        self.img = particle_player.get_particle_image(particle_type, self.animation_index)
        self.position_x = position[0] * 64
        self.position_y = position[1] * 64
        self.clear_particle = clear_particle

    def play_animation(self):
        self.animation_index += 0.2
        if self.particle_player.is_animation_over(self.animation_index):
            self.animation_index = 0
            return True
        return False

    def update(self):
        self.img = self.particle_player.get_particle_image(self.particle_type, int(self.animation_index))
        finished = self.play_animation()

        if finished:
            self.clear_particle()

    def draw(self, screen):
        screen.blit(self.img, (self.position_x, self.position_y))