import random
import pygame
from models import Asteroid, UFO
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
        for player in self.players.values():
            player_position = pygame.math.Vector2(player.spaceship.position)
            asteroid_position = pygame.math.Vector2(position)
            distance = player_position.distance_to(asteroid_position)
            if distance < player.spaceship.SIZE + radius:
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

    def spawn_periodic_circles(self, num_circles, current_asteroids_count):
        spawn_count = max(0, 10 - current_asteroids_count)
        return [self.spawn_circle(from_edge=True) for _ in range(min(num_circles, spawn_count))]
    
    def draw(self, surface, asteroids):
        for asteroid in asteroids:
            asteroid.draw(surface)
    
class UFOSpawner:
    def __init__(self, screen_width, screen_height, players):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.players = players
        self.ufos = []
        self.spawn_timer_event = pygame.USEREVENT + 3
        pygame.time.set_timer(self.spawn_timer_event, 20000)  # Spawn a new UFO every 20 seconds

    def spawn_ufo(self):
        position = Vector2(random.choice([0, self.screen_width]), random.randint(0, self.screen_height))
        ufo = UFO(position, self.screen_width, self.screen_height)
        self.ufos.append(ufo)

    def update(self, surface):
        for ufo in self.ufos:
            ufo.move(surface)
            ufo.update(self.players)
            # Remove dead projectiles
            ufo.projectiles = [p for p in ufo.projectiles if p.is_alive()]

    def draw(self, surface):
        for ufo in self.ufos:
            ufo.draw(surface)
