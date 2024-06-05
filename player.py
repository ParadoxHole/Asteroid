import pygame
from pygame.math import Vector2
from models import Spaceship

class Player:
    MAX_LIVES = 3
    INVULNERABILITY_TIME = 2000  # 3 seconds

    def __init__(self, position, color, controls,joystick=None):
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
                if not self.shooting:
                    self.spaceship.shoot()
                    self.shooting = True
            else:
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
                if pygame.time.get_ticks() % 500 < 350:
                    self.spaceship.draw(surface)
            else:
                self.spaceship.draw(surface)
            self.spaceship.draw_projectiles(surface)

    def reset_lives(self):
        self.lives = self.MAX_LIVES
        self.active = True

    def lose_life(self):
        
        self.lives -= 1
        if self.lives <= 0:
            self.active = False
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

    def draw_lives(self, surface, player_index):
        player = self
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        life_offset = Vector2(player.spaceship.SIZE + 5, player.spaceship.SIZE + 5)

        if player_index == 0:
            for i in range(player.lives):
                life_position = Vector2(screen_width - life_offset.x - (i+1) * life_offset.x, screen_height - life_offset.y) 
                player.spaceship.draw_small(surface, life_position)
        elif player_index == 1:
            for i in range(player.lives):
                life_position = Vector2(life_offset.x, screen_height - life_offset.x - (i+1) * life_offset.y) 
                player.spaceship.draw_small(surface, life_position, Vector2(1, 0))
        elif player_index == 2:
            for i in range(player.lives):
                life_position = Vector2(life_offset.x + (i+1) * life_offset.x, life_offset.y) 
                player.spaceship.draw_small(surface, life_position, Vector2(0, 1))
        elif player_index == 3:
            for i in range(player.lives):
                life_position = Vector2(screen_width - life_offset.x, life_offset.y + (i+1) * life_offset.y) 
                player.spaceship.draw_small(surface, life_position, Vector2(-1, 0))
