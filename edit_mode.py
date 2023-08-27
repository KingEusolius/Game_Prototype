import pygame, sys
from game_class import GameClass


class CollisionRectangle:
    def __init__(self, rect, position):
        self.rect = rect
        self.selected = False
        self.color = (255, 0, 0)
        self.position = position

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 4)

    def is_selected(self, selected):
        if selected:
            self.color = (0, 255, 0)
            self.selected = True
        else:
            self.color = (255, 0, 0)
            self.selected = False

    def collision(self):
        self.is_selected(self.rect.collidepoint(pygame.mouse.get_pos()))


class Editmode(GameClass):
    def __init__(self, set_overworld):
        super().__init__(set_overworld)
        self.buildings_player = None
        self.buildings = []
        self.enemies = None
        self.collision_rectangles = []
        self.img = None

    def input_handling(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    print("set overworld")
                    self.trigger_transition()

            keys = pygame.mouse.get_pressed(num_buttons=3)
            keyboard_keys = pygame.key.get_pressed()
            if event.type == pygame.MOUSEBUTTONDOWN and keys[1]:
                mouse_position = pygame.mouse.get_pos()
                rect = CollisionRectangle(pygame.Rect(mouse_position, (40, 40)), mouse_position)

                self.collision_rectangles.append(rect)
            elif event.type == pygame.MOUSEBUTTONDOWN and keys[2]:
                for rect in self.collision_rectangles:
                    rect.collision()

            for rect in self.collision_rectangles:
                if rect.selected and keys[0]:
                    rect.rect.topleft = pygame.mouse.get_pos()

                if rect.selected and keyboard_keys[pygame.K_RIGHT]:
                    rect.rect.width += 5

                if rect.selected and keyboard_keys[pygame.K_LEFT]:
                    rect.rect.width -= 5

                if rect.selected and keyboard_keys[pygame.K_UP]:
                    rect.rect.height -= 5

                if rect.selected and keyboard_keys[pygame.K_DOWN]:
                    rect.rect.height += 5



    def update(self):
        for building in self.buildings:
            building.update()
        for enemy in self.enemies:
            enemy.update()

    def draw(self, screen):
        self.draw_background(screen)

        for building in self.buildings:
            building.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for rect in self.collision_rectangles:
            rect.draw(screen)

        self.transition_drawing(screen)

    def set_buildings(self, building_player, buildings):
        self.buildings = buildings
        self.buildings_player = building_player

    def set_enemies(self, enemies):
        self.enemies = enemies

    def set_img(self, img):
        self.img = img

    def draw_background(self, screen):
        screen.blit(self.img, (0, 0))