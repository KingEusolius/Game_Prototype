from game_class import GameClass
import pygame, sys


class Overworld(GameClass):
    def __init__(self, avatar, enemies, set_fight):
        super().__init__(set_fight)
        self.avatar = avatar
        self.enemies = enemies
        self.running = True
        self.selected_enemy = None

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
                        if enemy.rect.collidepoint(pygame.mouse.get_pos()) and not enemy.defeated:
                            self.trigger_transition()
                            self.selected_enemy = enemy

    def update(self):
        self.avatar.update()
        for enemy in self.enemies:
            enemy.update()

    def draw(self, screen):
        self.avatar.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)

        self.transition_drawing(screen)
