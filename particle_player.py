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
        return int(index) >= 4


class Particle:
    def __init__(self, particle_player, particle_type, position, clear_particle, enemy_list, player_list):
        self.particle_player = particle_player
        self.animation_index = 0
        self.particle_type = particle_type
        self.img = particle_player.get_particle_image(particle_type, self.animation_index)
        self.position_x = position[0] * 64
        self.position_y = position[1] * 64
        self.clear_particle = clear_particle
        if particle_type == 'inferno':
            for enemy in enemy_list:
                if self.position_x == enemy.position_x and self.position_y == enemy.position_y:
                    enemy.change_state('take_hit')
                    enemy.take_damage(2)

        elif particle_type == 'update':
            for player in player_list:
                if self.position_x == player.position_x and self.position_y == player.position_y:
                    player.change_state('take_hit')
                    player.class_name = player.class_name.replace("minor", "major")
                    player.get_stats(player.dictionary)
                    print(player.class_name)

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
