import pygame
from pygame.math import Vector2
from utils import wrap_position
import random
import math
from pygame.mask import Mask

import pgeng

UP = Vector2(0, -1)

class GameObject:
    def __init__(self, position, velocity):
        self.position = Vector2(position)
        self.velocity = Vector2(velocity)
        self.mask = None  # Add mask attribute

    def draw(self, surface):
        pass

    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

class Spaceship(GameObject):
    ROTATION_SPEED = 3
    ACCELERATION = 0.1
    FRICTION = 0.99
    SIZE = 20
    INITIAL_LIVES = 3

    def __init__(self, position, color):
        self.direction = Vector2(UP)
        super().__init__(position, Vector2(0))
        self.projectiles = []
        self.color = color
        self.lives = self.INITIAL_LIVES
        self.update_mask()

    def update_mask(self):
        pass

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.ROTATION_SPEED * sign
        self.direction.rotate_ip(angle)
        self.update_mask()

    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION

    def apply_friction(self):
        self.velocity *= self.FRICTION

    def shoot(self):
        projectile_velocity = self.direction * 5
        projectile = Projectile(self.position, projectile_velocity, self.color)
        self.projectiles.append(projectile)

    def draw(self, surface):
        points = [
            self.position + self.direction.rotate(0) * self.SIZE,
            self.position + self.direction.rotate(135) * self.SIZE,
            self.position + self.direction.rotate(0) * self.SIZE // 10,
            self.position + self.direction.rotate(-135) * self.SIZE,
        ]

        # Create a mask from the temporary surface
        self.mask = pgeng.collision.create_mask_from_surface(surface, points)

        # Draw the polygon on the original surface
        pygame.draw.polygon(surface, self.color, points)


    def draw_small(self, surface, position, orientation=UP):
        small_size = self.SIZE // 2
        fixed_direction = orientation.normalize()
        points = [
            position + fixed_direction.rotate(0) * small_size,
            position + fixed_direction.rotate(135) * small_size,
            position + fixed_direction.rotate(0) * small_size // 10,
            position + fixed_direction.rotate(-135) * small_size,
        ]
        pygame.draw.polygon(surface, self.color, points)

    def move(self, surface):
        self.apply_friction()
        super().move(surface)
        for projectile in self.projectiles:
            projectile.move(surface)

    def draw_projectiles(self, surface):
        for projectile in self.projectiles:
            projectile.draw(surface)


class Projectile(GameObject):
    SIZE = 2

    def __init__(self, position, velocity, color, lifespan=60):
        super().__init__(position, velocity)
        self.lifespan = lifespan
        self.color = color
        self.create_mask()

    def create_mask(self):
        pass

    def update(self):
        self.lifespan -= 1

    def is_alive(self):
        return self.lifespan > 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.SIZE)

class Circle(GameObject):
    SIZE_MAP = {
        "large": 50,
        "medium": 30,
        "small": 15
    }
    MAX_SPEED = 2

    def __init__(self, position, size_category):
        self.size_category = size_category
        self.size = self.SIZE_MAP[size_category]

        velocity = Vector2(random.uniform(-self.MAX_SPEED, self.MAX_SPEED), random.uniform(-self.MAX_SPEED, self.MAX_SPEED))
        super().__init__(position, velocity)

        self.vertices = self.generate_vertices(self.size)
        self.create_mask()

    def generate_vertices(self, size):
        verts = 20
        vertices = []
        for i in range(verts):
            noise = random.uniform(0.9, 1.2)  # Adjust noise to shape
            angle = (i / verts) * 2 * math.pi
            x = noise * size * math.sin(angle)
            y = noise * size * math.cos(angle)
            vertices.append((x, y))
        return vertices

    def create_mask(self):
        pass

    def draw(self, surface):
        points = [(self.position[0] + x, self.position[1] + y) for x, y in self.vertices]
        pygame.draw.lines(surface, (255, 255, 255), True, points)

    def split(self):
        if self.size_category == "large":
            new_size_category = "medium"
        elif self.size_category == "medium":
            new_size_category = "small"
        else:
            return []

        angle = random.uniform(0, 360)
        velocity_1 = self.velocity.rotate(angle)
        velocity_2 = self.velocity.rotate(-angle)

        new_circle_1 = Circle(self.position, new_size_category)
        new_circle_1.velocity = velocity_1

        new_circle_2 = Circle(self.position, new_size_category)
        new_circle_2.velocity = velocity_2

        return [new_circle_1, new_circle_2]