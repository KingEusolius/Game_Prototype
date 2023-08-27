from abc import ABC
import numpy as np
from pathfinding import heuristic, vec


def from_screenspace_to_gridspace(screen_coordinates):
    x_grid = screen_coordinates[0] // 64
    y_grid = screen_coordinates[1] // 64
    return x_grid, y_grid


def decision_method_nearest_target(x_self, y_self, x_char, y_char, health=None):
    return heuristic(vec(x_self, y_self), vec(x_char, y_char))


def decision_method_nearest_and_strongest_target(x_self, y_self, x_char, y_char, health):
    return heuristic(vec(x_self, y_self), vec(x_char, y_char)) - health


def decision_method_nearest_and_weakest_target(x_self, y_self, x_char, y_char, health):
    return heuristic(vec(x_self, y_self), vec(x_char, y_char)) + health


class TargetFinder(ABC):
    def __init__(self):
        self.decision_func = None

    def execute(self, own_pos, targets):
        nearest_char = None
        nearest_char_distance = np.inf
        x_self, y_self = from_screenspace_to_gridspace((own_pos[0], own_pos[1]))
        for target in targets:
            if target.health > 0:
                x_char, y_char = from_screenspace_to_gridspace((target.position_x, target.position_y))
                decision_value = self.decision_func(x_self, y_self, x_char, y_char, target.health)
                if decision_value < nearest_char_distance:
                    nearest_char = target
                    nearest_char_distance = decision_value
        return nearest_char


class NearestTarget(TargetFinder):
    def __init__(self):
        self.decision_func = decision_method_nearest_target


class NearestAndStrongestTarget(TargetFinder):
    def __init__(self):
        self.decision_func = decision_method_nearest_and_strongest_target


class NearestAndWeakestTarget(TargetFinder):
    def __init__(self):
        self.decision_func = decision_method_nearest_and_weakest_target
