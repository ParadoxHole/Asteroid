import pygame
from pygame.math import Vector2
from models import Spaceship
import firebase_listener

class Player:
    MAX_LIVES = 3
    INVULNERABILITY_TIME = 2000  # 3 seconds

    def __init__(self, position, color, controls, user_id='Guest', arcadeId = None, playerSeat = None, joystick=None):
        self.spaceship = Spaceship(position, color)
        self.controls = controls
        self.joystick = joystick

        self.initial_position = position
        self.lives = self.MAX_LIVES
        self.shooting = False
        self.active = True
        self.invulnerable = True
        self.respawn_key = self.controls['respawn']
        self.respawn_time = 0
        self.waiting_to_respawn = False
        self.trail = Trail(self)
        
        self.score = 0
        self.userId = user_id 
        self.arcadeId = arcadeId
        self.player_seat = playerSeat

        self.superpower_duration = 0
        self.superpower_active = False
        self.superpower_time = 0
        self.superpower_type = None

    def update(self):
        self.trail.update()

        if self.superpower_active: 
            if self.superpower_duration < pygame.time.get_ticks() - self.superpower_time or self.active == False:
                self.superpower_active = False
                self.color = (255, 0, 0)
                # Reset spaceship attributes to default values
                self.spaceship.ACCELERATION = 0.1
                self.spaceship.SHOOT_DELAY = 200
                self.spaceship.projectileSize = 2
                self.spaceship.DOUBLE_SHOT = False
                self.invulnerable = False
                self.spaceship.deactivate_shield()
                self.spaceship.shootType = "single"
            else:
                if self.superpower_type =='faster_spaceship':
                    self.spaceship.ACCELERATION = 0.14
                elif self.superpower_type == 'invincibility':
                    self.invulnerable = True
                    self.respawn_time = pygame.time.get_ticks()
                elif self.superpower_type == 'shield':
                    if not self.spaceship.shield_active:
                        self.spaceship.activate_shield()
                elif self.superpower_type == 'double_shot':
                    self.spaceship.shootType = "double"
                elif self.superpower_type == 'boomerang_projectiles':
                    self.spaceship.shootType = "boomerang"
                elif self.superpower_type == 'faster_shot':
                    self.spaceship.SHOOT_DELAY = 10
                elif self.superpower_type == 'bigger_shot':
                    self.spaceship.projectileSize = 10
                    self.spaceship.SHOOT_DELAY = 500
                elif self.superpower_type == 'heal':
                    self.lives += 1
                    self.superpower_active = False

    def handle_input(self):
        if not self.active:
            return
        
        is_key_pressed = pygame.key.get_pressed()

        if not self.joystick:
            if is_key_pressed[self.controls['left']]:
                self.spaceship.rotate(clockwise=False)
            if is_key_pressed[self.controls['right']]:
                self.spaceship.rotate(clockwise=True)
            if is_key_pressed[self.controls['up']]:
                self.spaceship.accelerate()
            if is_key_pressed[self.controls['shoot']]:
                if not self.shooting and (pygame.time.get_ticks() - self.spaceship.last_shot_time >= self.spaceship.SHOOT_DELAY or self.spaceship.last_shot_time == 0):
                    self.spaceship.shoot()
                    self.spaceship.last_shot_time = pygame.time.get_ticks()
                    self.shooting = True
            elif pygame.time.get_ticks() - self.spaceship.last_shot_time >= self.spaceship.SHOOT_DELAY:
                self.shooting = False

        # Handle joystick input if available
        if self.joystick:
            hat = self.joystick.get_hat(0)
            if hat[0] == -1:  # Left
                self.spaceship.rotate(clockwise=False)
            if hat[0] == 1:   # Right
                self.spaceship.rotate(clockwise=True)
            if self.joystick.get_button(2):
                self.spaceship.accelerate()
            if self.joystick.get_button(3):  
                if not self.shooting:
                    self.spaceship.shoot()
                    self.shooting = True
            else :
                self.shooting = False

    def move(self, surface):
        if self.active:
            self.spaceship.move(surface)

    def draw(self, surface):
        if self.active:
            if self.invulnerable:
                # Blink effect to show invulnerability
                if pygame.time.get_ticks() % 200 < 150: # COORECT THE BLINKING TIME HERE !!!!!!
                    self.spaceship.draw(surface)
            else:
                self.spaceship.draw(surface)
            self.trail.draw(surface)
            self.spaceship.draw_projectiles(surface)

    def reset_lives(self):
        self.lives = self.MAX_LIVES
        self.active = True

    def lose_life(self):
        
        self.lives -= 1
        if self.lives <= 0:
            self.active = False
            if self.userId:
                firebase_listener.save_score(self.userId, self.arcadeId, self.player_seat, self.score)
        else:
            self.active = False
            self.waiting_to_respawn = True

    def spawn(self):
        self.active = True
        self.waiting_to_respawn = False
        self.spaceship.position = self.initial_position
        self.spaceship.velocity = Vector2(0)
        self.spaceship.direction = Vector2(0, -1)
        self.spaceship.projectiles = []
        self.invulnerable = True
        self.respawn_time = pygame.time.get_ticks()

    def update_invulnerability(self):
        if self.invulnerable and pygame.time.get_ticks() - self.respawn_time >= self.INVULNERABILITY_TIME:
            self.invulnerable = False

    def draw_lives(self, surface, player_color):
        player = self
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        life_offset = Vector2(player.spaceship.SIZE + 5, player.spaceship.SIZE + 5)

        if player_color == "green":
            for i in range(player.lives):
                life_position = Vector2(screen_width - life_offset.x - (i+1) * life_offset.x, screen_height - life_offset.y) 
                player.spaceship.draw_small(surface, life_position)
        elif player_color == "red":
            for i in range(player.lives):
                life_position = Vector2(life_offset.x, screen_height - life_offset.x - (i+1) * life_offset.y) 
                player.spaceship.draw_small(surface, life_position, Vector2(1, 0))
        elif player_color == "yellow":
            for i in range(player.lives):
                life_position = Vector2(life_offset.x + (i+1) * life_offset.x, life_offset.y) 
                player.spaceship.draw_small(surface, life_position, Vector2(0, 1))
        elif player_color == "blue":
            for i in range(player.lives):
                life_position = Vector2(screen_width - life_offset.x, life_offset.y + (i+1) * life_offset.y) 
                player.spaceship.draw_small(surface, life_position, Vector2(-1, 0))

class TrailParticle:
    def __init__(self, position, color, max_lifetime):
        self.position = position
        self.color = color
        self.max_lifetime = max_lifetime
        self.lifetime = max_lifetime

    def update(self):
        self.lifetime -= 1
        if self.lifetime < 0:
            self.lifetime = 0

    def draw(self, surface):
        alpha = self.lifetime / self.max_lifetime * 255
        pygame.draw.circle(surface, (self.color[0], self.color[1], self.color[2], alpha), (int(self.position.x), int(self.position.y)), 3)

class Trail:
    def __init__(self, player, length=10 , max_lifetime=5):
        self.player = player
        self.length = length
        self.max_lifetime = max_lifetime
        self.particles = []

    def update(self):
        if self.player.spaceship.velocity.length() > 2:
            self.create_particle()

    
        for particle in self.particles:
            particle.update()
            if particle.lifetime == 0 or self.player.spaceship.velocity.length() < 2:
                self.particles.remove(particle)

    def create_particle(self):
        position = self.player.spaceship.position - self.player.spaceship.direction * (self.player.spaceship.SIZE * 0.6)
        color = self.player.spaceship.color
        particle = TrailParticle(position, color, self.max_lifetime)
        self.particles.append(particle)

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)