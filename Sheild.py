import pygame
from pygame.math import Vector2
import pgeng

class Shield:
    SIZE = 10  # Set an appropriate size for the shield

    def __init__(self, position, direction, color):
        self.position = position
        self.direction = direction
        self.color = color
        self.mask = pgeng.Circle(self.position, self.SIZE, self.color).mask

    def update(self, center_position, angle_offset):
        angle = (pygame.time.get_ticks() / 10) % 360
        self.direction = Vector2(0, -1).rotate(angle + angle_offset)
        self.position = center_position + self.direction * 30
        self.mask = pgeng.Circle(self.position, self.SIZE, self.color).mask
 
    def draw(self, surface):
        for i in range(3):
            angle = (pygame.time.get_ticks() / 10) % 360
            direction = Vector2(0, -1).rotate(angle + 120 * i)
            self.draw_small(surface, self.position + direction * 30, direction)
            # circle collison mask for shield each shield is a circle
            self.mask = pgeng.Circle(self.position + direction * 30, self.SIZE, self.color).mask

        pgeng.draw_circle(surface, self.position, self.SIZE, self.color)        