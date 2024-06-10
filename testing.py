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
        projectile_velocity = self.direction * 5
        projectile = Projectile(self.position, projectile_velocity, self.color)
        self.projectiles.append(projectile)

    def draw(self, surface):
        self.update_mask()
        self.polygon.render(surface)

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
        self.polygon.render(surface)

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
    SIZE = 2

    def __init__(self, position, velocity, color, lifespan=60):
        super().__init__(position, velocity)
        self.lifespan = lifespan
        self.color = color
        self.create_mask()

    def create_mask(self):
        self.circle = pgeng.Asteroid(self.position, self.SIZE, self.color)
        self.mask = self.circle.mask

    def update(self):
        self.lifespan -= 1

    def is_alive(self):
        return self.lifespan > 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.SIZE)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    spaceship = Spaceship(Vector2(400, 300), (255, 255, 255))
    circles = [Asteroid(Vector2(random.randint(0, 800), random.randint(0, 600)), random.choice(["large", "medium", "small"])) for _ in range(5)]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            spaceship.rotate(clockwise=False)
        if keys[pygame.K_RIGHT]:
            spaceship.rotate(clockwise=True)
        if keys[pygame.K_UP]:
            spaceship.accelerate()
        spaceship.move(screen)
        for circle in circles:
            circle.move(screen)
        for circle in circles:
            if spaceship.polygon.collide(circle.polygon):
                circle.polygon.colour = (255, 0, 0)
            else:
                circle.polygon.colour = (255, 255, 255)
        screen.fill((0, 0, 0))
        spaceship.draw(screen)
        for circle in circles:
            circle.draw(screen)
        spaceship.draw_projectiles(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
