import pygame
from os import path
from collections import deque
import numpy as np

vec = pygame.math.Vector2


class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.obstacles = []
        self.connections = [vec(1, 0), vec(-1, 0), vec(0, 1), vec(0, -1)]

    def in_bounds(self, node):
        return 0 <= node.x < self.width and 0 <= node.y < self.height

    def passable(self, node):
        return node not in self.walls

    def is_obstacle(self, node):
        return node not in self.obstacles

    def find_neighbors(self, node):
        neighbors = [node + connection for connection in self.connections]
        neighbors = filter(self.in_bounds, neighbors)
        neighbors = filter(self.passable, neighbors)
        neighbors = filter(self.is_obstacle, neighbors)
        return neighbors

    def find_neighbors_for_attack(self, node):
        neighbors = [node + connection for connection in self.connections]
        neighbors = filter(self.in_bounds, neighbors)
        neighbors = filter(self.passable, neighbors)
        return neighbors

    # def draw(self):
    #    for wall in self.walls:
    #        rect = pygame.Rect(wall * TILESIZE, (TILESIZE, TILESIZE))
    #        pygame.draw.rect(screen, LIGHTGRAY, rect)


def vec2int(v):
    return (int(v.x), int(v.y))


def breadth_first_search(graph, start, max_cost):
    frontier = deque()
    frontier.append(start)
    path = {}
    path[vec2int(start)] = None
    while len(frontier) > 0:
        current = frontier.popleft()
        for next in graph.find_neighbors(current):
            if vec2int(next) not in path and heuristic(start, next) <= max_cost:
                frontier.append(next)
                path[vec2int(next)] = current - next
    return path


def breadth_first_search_attack(graph, start, max_cost):
    frontier = deque()
    frontier.append(start)
    path = {}
    path[vec2int(start)] = None
    while len(frontier) > 0:
        current = frontier.popleft()
        for next in graph.find_neighbors_for_attack(current):
            if vec2int(next) not in path and heuristic(start, next) <= max_cost:
                frontier.append(next)
                path[vec2int(next)] = current - next
    return path


def breadth_first_search_with_end(graph, start, end, allowed_graph):
    frontier = deque()
    frontier.append(start)
    path = {}
    path[vec2int(start)] = None
    if vec2int(start) == vec2int(end):
        return None
    if vec2int(start) not in allowed_graph:
        return None
    while len(frontier) > 0:
        current = frontier.popleft()
        if current == end:
            break
        for next in graph.find_neighbors(current):
            if vec2int(next) not in path and vec2int(next) in allowed_graph:
                frontier.append(next)
                path[vec2int(next)] = current - next
    return path


def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)
