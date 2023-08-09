from game_class import GameClass
import pygame, sys


class Fight(GameClass):
    def __init__(self, set_overworld):
        super().__init__(set_overworld)
        self.mobs = []
        self.player_chars = []
        self.particles = []
        self.items = []
        self.projectiles = []
        self.background_image = None
        self.celebration = False
        self.player_turn = True

    def set_player_chars(self, chars):
        self.player_chars = chars

    def clear_player_chars(self):
        self.player_chars.clear()

    def set_mobs(self, mobs):
        self.mobs = mobs

    def clear_mobs(self):
        self.mobs = []

    def set_img(self, img):
        self.background_image = img

    def clear_img(self):
        self.background_image = None

    def is_fight_over(self, player_characters):
        victory = True
        for mob in self.mobs:
            if mob.alive:
                victory = False

        if victory and not self.celebration and 0:
            self.celebration = True
            for mob in self.mobs:
                self.spawn_item((mob.position_x, mob.position_y))

        defeat = True
        for char in player_characters:
            if char.alive:
                defeat = False

        return victory or defeat

    def input_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if self.input_handling_allowed:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.trigger_transition()

    def update(self):
        for char in self.player_chars:
            if char.alive:
                char.update()

        for mob in self.mobs:
            if mob.alive:
                mob.update()

        for part in self.particles:
            part.update()

        for it in self.items:
            it.update()

        for pr in self.projectiles:
            pr.update()
            if pr.hit:
                self.projectiles.remove(pr)

    def draw(self, screen):
        self.draw_background(screen)

        self.draw_characters(screen)

        self.transition_drawing(screen)

    def draw_background(self, screen):
        screen.blit(self.background_image, (0, 0))

    def draw_characters(self, screen):
        for char in self.player_chars:
            char.draw(screen)

        for mob in self.mobs:
            mob.draw(screen)

        for part in self.particles:
            part.draw(screen)

        for it in self.items:
            it.draw(screen)

        for pr in self.projectiles:
            pr.draw(screen)


