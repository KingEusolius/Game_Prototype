import pygame

class Mouse:
    def __init__(self):
        pygame.mouse.set_visible(False)
        mouse_pos = pygame.mouse.get_pos()
        self.position_x = mouse_pos[0]
        self.position_y = mouse_pos[1]

        self.img = pygame.image.load(f'graphics/mouse/Cursor_1.png').convert_alpha()
        self.img = pygame.transform.scale(self.img, (32, 32))

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.position_x = mouse_pos[0]
        self.position_y = mouse_pos[1]

    def draw(self, screen, offset_x=0, offset_y=0):
        screen.blit(self.img, (self.position_x, self.position_y))

