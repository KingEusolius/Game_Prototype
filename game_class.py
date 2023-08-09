from abc import ABC, abstractmethod
import pygame


class GameClass(ABC):
    def __init__(self, state_switch):
        self.overlay_image = pygame.Surface((64 * 16, 64 * 10), pygame.SRCALPHA, 32)
        self.overlay_image = self.overlay_image.convert_alpha()
        self.overlay_image.fill((0, 0, 0, 0))
        self.overlay_alpha = 0
        self.bool_increment_overlay = False
        self.fade_out = True
        self.fade_in = False
        self.state_switch = state_switch
        self.input_handling_allowed = True

    @abstractmethod
    def input_handling(self):
        raise NotImplementedError("Subclass must implement this method")

    @abstractmethod
    def update(self):
        raise NotImplementedError("Subclass must implement this method")

    @abstractmethod
    def draw(self):
        raise NotImplementedError("Subclass must implement this method")

    def trigger_transition(self):
        self.bool_increment_overlay = True
        self.fade_out = True
        self.fade_in = False
        self.input_handling_allowed = False

    def transition(self):
        if self.fade_out:
            if not self.fade_out_overlay():
                self.fade_out = False
                self.fade_in = True
                self.state_switch()

        if self.fade_in:
            if not self.fade_in_overlay():
                self.fade_in = False
                self.bool_increment_overlay = False
                self.input_handling_allowed = True

    def fade_out_overlay(self):
        increment = 3
        if self.overlay_alpha < 255 - increment:
            self.overlay_alpha += increment
        return self.overlay_alpha < 255 - increment

    def fade_in_overlay(self):
        decrement = 3
        if self.overlay_alpha > decrement:
            self.overlay_alpha -= decrement
        return self.overlay_alpha > decrement

    def transition_drawing(self, screen):
        if self.bool_increment_overlay:
            self.transition()
            self.overlay_image.fill((0, 0, 0, self.overlay_alpha))
            screen.blit(self.overlay_image, (0, 0))
