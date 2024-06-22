import pygame
from pygame.math import Vector2
import pgeng
import random

# Define the UFO class
class UFO:
    SIZE = 20
    SPEED_RANGE = (1, 3)

    def __init__(self, position, screen_width, screen_height, color=(255, 0, 0)):
        self.position = Vector2(position)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = color
        self.direction = Vector2(0, -1)
        self.velocity = self.direction * random.uniform(*self.SPEED_RANGE)
        self.update_mask()

    def update_mask(self):
        # Create points for the spaceship polygon
        points = [
            self.position + Vector2(-self.SIZE, -self.SIZE / 2),
            self.position + Vector2(self.SIZE, -self.SIZE / 2),
            self.position + Vector2(self.SIZE, self.SIZE / 2),
            self.position + Vector2(-self.SIZE, self.SIZE / 2),
            self.position + Vector2(0, 0)
        ]
        self.polygon = pgeng.Polygon(points, self.color)
        self.mask = self.polygon.mask

    def draw(self, surface):
        self.polygon.render(surface, width=2)

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("UFO Drawing Test")

# Create a UFO instance
ufo_position = (screen_width // 2, screen_height // 2)
ufo = UFO(ufo_position, screen_width, screen_height)

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the UFO
    ufo.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
