import pygame
from pygame.math import Vector2
import random

class Superpower:
    SIZE = 20

    def __init__(self, position):
        self.position = Vector2(position)
        self.color = (255, 0, 255)  # Purple color for superpower
        self.active = True
        self.superpowers = ['faster_shot', 'bigger_shot', 'faster_spaceship', 'invincibility', 'boomerang_projectiles', 'shield', 'double_shot', 'heal']
        weights = [0, 0, 0, 0, 0, 1, 0, 0]
        self.duration = [5000, 5000, 5000, 5000, 5000, 60000, 5000, 5000]

        # Use random.choices to select a superpower based on weights
        self.type = random.choices(self.superpowers, weights, k=1)[0]
        print(self.type)

    def draw(self, surface):
        if self.active:
            pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.SIZE)

    def apply_effect(self, player):
        player.superpower_active = True
        player.superpower_time = pygame.time.get_ticks()
        player.superpower_duration = self.duration[self.superpowers.index(self.type)]
        player.superpower_type = self.type 
