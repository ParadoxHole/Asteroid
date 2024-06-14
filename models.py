import pygame
from pygame.math import Vector2
from utils import wrap_position
import random
import math

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
        self.projectileSize = 2
        self.SHOOT_DELAY = 200
        self.last_shot_time = 0

        # superpower attributes
        self.shootType = "single" # single, double, boomerang**
        self.shield_active = False
        self.shields = [False, False, False]

    def update_mask(self):
        # Create points for the spaceship polygon
        points = [
            self.position + self.direction.rotate(0) * self.SIZE,
            self.position + self.direction.rotate(135) * self.SIZE,
            self.position + self.direction.rotate(0) * self.SIZE // 10,
            self.position + self.direction.rotate(-135) * self.SIZE,
        ]
        self.polygon = pgeng.Polygon(points, self.color)
        self.mask = self.polygon.mask

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.ROTATION_SPEED * sign
        self.direction.rotate_ip(angle)

    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION

    def apply_friction(self):
        self.velocity *= self.FRICTION

    def shoot(self):
        if self.shootType == "single":
            projectile_velocity = self.direction * 5
            projectile = Projectile(self.position, projectile_velocity, self.color, self.projectileSize)
            self.projectiles.append(projectile)
        elif self.shootType == "double":
            projectile_velocity = self.direction.rotate(10) * 5
            projectile = Projectile(self.position, projectile_velocity, self.color, self.projectileSize)
            self.projectiles.append(projectile)
            projectile_velocity = self.direction.rotate(-10) * 5
            projectile = Projectile(self.position, projectile_velocity, self.color, self.projectileSize)
            self.projectiles.append(projectile)
        elif self.shootType == "boomerang":
            """Shoot a boomerang projectile #not implemented"""
            projectile_velocity = self.direction * 5
            projectile = Projectile(self.position, projectile_velocity, self.color, self.projectileSize)
            self.projectiles.append(projectile)

    def draw(self, surface):
        self.update_mask()
        self.polygon.render(surface)
        if self.shield_active:
            self.draw_shield(surface)

    def draw_shield(self, surface):
        # Draw shields spinning around the spaceship
        for i in range(3):
            if self.shields[i]:
                angle = (pygame.time.get_ticks() / 10) % 360
                direction = UP.rotate(angle + 120 * i)
                self.draw_small(surface, self.position + direction * 30, direction)
                pygame.draw.circle(surface, (255, 0, 0), (int(self.position.x + direction.x * 30), int(self.position.y + direction.y * 30)), self.SIZE // 2, 2)
                # update mask ^position
                self.shields[i]['mask'] = pgeng.Circle(self.position + direction * 30, self.SIZE // 2, self.color)

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
            projectile.draw(surface, self.projectileSize)

    def activate_shield(self):
        self.shield_active = True
        angle = (pygame.time.get_ticks() / 10) % 360
        self.shields = [
            {
                'position': self.position + UP.rotate(angle + 120 * i) * 30,
                'mask': pgeng.Circle(self.position + UP.rotate(angle + 120 * i) * 30, self.SIZE // 2, self.color),
                'color': self.color
            }
            for i in range(3)
        ]

    def deactivate_shield(self):
        self.shield_active = False
        self.shields = [False, False, False]

class Asteroid(GameObject):
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
            noise = random.uniform(0.9, 1.2)
            angle = (i / verts) * 2 * math.pi
            x = noise * size * math.sin(angle)
            y = noise * size * math.cos(angle)
            vertices.append((x, y))
        return vertices

    def create_mask(self):
        points = [(self.position[0] + x, self.position[1] + y) for x, y in self.vertices]
        self.polygon = pgeng.Polygon(points, (255, 255, 255))
        self.mask = self.polygon.mask

    def draw(self, surface):
        self.polygon.render(surface, width=2)

    def move(self, surface):
        super().move(surface)
        self.create_mask()
        

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
        new_circle_1 = Asteroid(self.position, new_size_category)
        new_circle_1.velocity = velocity_1
        new_circle_2 = Asteroid(self.position, new_size_category)
        new_circle_2.velocity = velocity_2
        return [new_circle_1, new_circle_2]

class Projectile(GameObject):

    def __init__(self, position, velocity, color, size=2, lifespan=60):
        super().__init__(position, velocity)
        self.lifespan = lifespan
        self.color = color
        self.size = size
        self.create_mask()

    def create_mask(self):
        self.circle = pgeng.Circle(self.position, self.size, self.color)
        self.mask = self.circle.mask

    def update(self):
        self.lifespan -= 1
        self.create_mask()

    def is_alive(self):
        return self.lifespan > 0

    def draw(self, surface, size):
        self.circle.render(surface)