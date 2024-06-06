import pygame, pgeng
from pygame.math import Vector2
from models import Circle
import random
from player import Player
import ui
import input_handler
from circle_spawner import CircleSpawner


class SpaceRocks:
    def __init__(self):
        self._init_pygame()
        
        self.screen = pygame.display.set_mode((800, 800))
        #self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.clock = pygame.time.Clock()
        self.state = "start"  # Initial state

        # Initialize joystick
        pygame.joystick.init()
        joystick = None
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

        player1_controls, player2_controls, player3_controls, player4_controls, joystick = input_handler.initialize_player_controls(joystick)

        self.players = [
            Player((400, 300), (255, 0, 0), player1_controls),
            Player((500, 300), (0, 255, 0), player2_controls, joystick),
            Player((400, 400), (0, 0, 255), player3_controls),
            Player((500, 400), (255, 255, 0), player4_controls)
        ]

        self.circle_spawner = CircleSpawner(self.screen.get_width(), self.screen.get_height(), self.players)
        self.circles = []
        self.initial_spawn_count = 1
        self.periodic_spawn_count = 1
        self.circle_spawn_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.circle_spawn_event, 5000)  # Spawn new circles every 5 seconds

        self.background = pygame.image.load("img/bg5.jpg")

        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)

        self.bullet = pygame.Surface((4, 4))
        self.col = self.RED
        self.bullet.fill(self.col)
        self.bullet_mask = pygame.mask.from_surface(self.bullet)
        self.pos = pygame.mouse.get_pos()
        
    def main_loop(self):
        while True:
            self._handle_input()
            self._process_game_logic()
            self._draw()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Space Rocks")

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            elif event.type == self.circle_spawn_event and self.state == "playing":
                self.circles.extend(self.circle_spawner.spawn_periodic_circles(self.periodic_spawn_count))

        if self.state == "start":
            self._reset_game()
            self.state = input_handler.handle_start_input(self.state)
        elif self.state == "playing": 
            input_handler.handle_respawn_input(self.players)
            for player in self.players:
                if not player.waiting_to_respawn:
                    player.handle_input()
        elif self.state == "game over" or self.state == "win":
            self.state = input_handler.handle_game_over_input(self.state)

        return self.state

    def _start_game(self):
        self.state = "playing"
        self.circles = self.circle_spawner.spawn_initial_circles(self.initial_spawn_count)

    def _reset_game(self):
        for player in self.players:
            player.reset_lives()
            player.spawn()
        self.circles = self.circle_spawner.spawn_initial_circles(self.initial_spawn_count)

    def _process_game_logic(self):
        if self.state == "playing":
            for player in self.players:
                player.move(self.screen)
                if player.active:
                    player.update_invulnerability()

            self._move_circles()
            self._check_collisions()
            self._update_projectiles()
            self._check_projectile_collisions()

            if all(player.lives <= 0 for player in self.players):
                self.state = "game over"

            if not self.circles:
                self.state = "win"

    def _move_circles(self):
        for circle in self.circles:
            circle.move(self.screen)

    def _check_collisions(self):
        pass

    def _check_projectile_collisions(self):
        pass

    def _check_mouse_collision(self):
        
        for player in self.players:
            offset = (self.pos[0] - player.spaceship.position.x, self.pos[1] - player.spaceship.position.y)
            if player.spaceship.mask.overlap(self.bullet_mask,offset):
                self.col = self.BLUE
                print("Collision" + str(player.color))
            else:
                self.col = self.RED

    def _update_projectiles(self):
        for player in self.players:
            for projectile in player.spaceship.projectiles[:]:
                projectile.move(self.screen)
                projectile.update()
                if not projectile.is_alive():
                    player.spaceship.projectiles.remove(projectile)

    def _draw(self):
        self.screen.blit(self.background, (0, 0))

        if self.state == "start":
            ui.draw_start_screen(self.screen)
        elif self.state == "playing":
            for player_index, player in enumerate(self.players):
                player.draw(self.screen)
                player.draw_lives(self.screen, player_index)
                if player.waiting_to_respawn:
                    ui.draw_respawn_screen(self.screen, player, player_index)
            for circle in self.circles:
                circle.draw(self.screen)
        elif self.state == "game over":
            ui.draw_game_over_screen(self.screen)
        elif self.state == "win":
            ui.draw_win_screen(self.screen)

        self.pos = pygame.mouse.get_pos()
        self.bullet.fill(self.col)
        self.screen.blit(self.bullet, self.pos)

        pygame.display.flip()
        self.clock.tick(60)

if __name__ == "__main__":
    SpaceRocks().main_loop()