import random
import pygame
from models import Asteroid
from pygame.math import Vector2

class AsteroidSpawner:
    def __init__(self, screen_width, screen_height, players):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.players = players

    def _random_position(self):
        return (random.randint(0, self.screen_width), random.randint(0, self.screen_height))

    def _random_edge_position(self):
        # Randomly choose one of the four edges: top, bottom, left, right
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            return Vector2(random.randint(0, self.screen_width), 0)
        elif edge == 'bottom':
            return Vector2(random.randint(0, self.screen_width), self.screen_height)
        elif edge == 'left':
            return Vector2(0, random.randint(0, self.screen_height))
        elif edge == 'right':
            return Vector2(self.screen_width, random.randint(0, self.screen_height))

    def _is_position_valid(self, position, radius):
        for player in self.players:
            if player.active:
                player_x, player_y = player.spaceship.position
                player_size = player.spaceship.SIZE
                player_rect = pygame.Rect(player_x - player_size // 2,
                                        player_y - player_size // 2,
                                        player_size, player_size)
                circle_rect = pygame.Rect(position[0] - radius, position[1] - radius, radius * 2, radius * 2)
                if player_rect.colliderect(circle_rect):
                    return False
        return True

    def spawn_circle(self, from_edge=False):
        size_prob = random.random()
        if size_prob < 0.6:
            size_category = "large"
        elif size_prob < 0.9:
            size_category = "medium"
        else:
            size_category = "small"
        
        if from_edge:
            position = self._random_edge_position()
        else:
            position = self._random_position()
            radius = Asteroid.SIZE_MAP[size_category]
            while not self._is_position_valid(position, radius):
                position = self._random_position()
                
        return Asteroid(position, size_category)

    def spawn_initial_circles(self, num_circles):
        return [self.spawn_circle(from_edge=False) for _ in range(num_circles)]

    def spawn_periodic_circles(self, num_circles):
        return [self.spawn_circle(from_edge=True) for _ in range(num_circles)]
