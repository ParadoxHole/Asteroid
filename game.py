import pygame, pgeng
from player import Player
import ui
import input_handler
from AsteroidSpawner import AsteroidSpawner
import random
from Superpowers import Superpower

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
        self.superpowers = []
        self.superpower_spawn_event = pygame.USEREVENT + 2
        pygame.time.set_timer(self.superpower_spawn_event, random.randint(10, 15))
        
        self.circle_spawner = AsteroidSpawner(self.screen.get_width(), self.screen.get_height(), self.players)
        self.asteroid = []
        self.initial_spawn_count = 1
        self.periodic_spawn_count = 1
        self.circle_spawn_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.circle_spawn_event, 5000)  # Spawn new circles every 5 seconds

        self.background = pygame.image.load("img/bg5.jpg")

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
                self.asteroid.extend(self.circle_spawner.spawn_periodic_circles(self.periodic_spawn_count))
            elif event.type == self.superpower_spawn_event and self.state == "playing":
                self.spawn_superpower()
                self.set_random_superpower_timer()

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
    
    def set_random_superpower_timer(self):
        # Random spawn time between 5,000 and 15,000 milliseconds (5 to 15 seconds)
        random_spawn_time = random.randint(10000, 15000)
        pygame.time.set_timer(self.superpower_spawn_event, random_spawn_time)

    def spawn_superpower(self):
        position = (random.randint(0, self.screen.get_width()), random.randint(0, self.screen.get_height()))
        self.superpowers.append(Superpower(position))

    def _start_game(self):
        self.state = "playing"
        self.asteroid = self.circle_spawner.spawn_initial_circles(self.initial_spawn_count)

    def _reset_game(self):
        for player in self.players:
            player.reset_lives()
            player.spawn()
        self.asteroid = self.circle_spawner.spawn_initial_circles(self.initial_spawn_count)

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
            self._check_superpower_collisions()

            if all(player.lives <= 0 for player in self.players):
                self.state = "game over"

            if not self.asteroid:
                self.state = "win"

    def _move_circles(self):
        for circle in self.asteroid:
            circle.move(self.screen)

    def _check_collisions(self):
        for asteroid  in self.asteroid:
            for player in self.players:

                if player.spaceship.polygon.collide(asteroid.polygon):
                    if not player.invulnerable and player.active:
                        player.lose_life()
                        self.asteroid.remove(asteroid)
                        new_Asteroids = asteroid.split()
                        self.asteroid.extend(new_Asteroids)
                    continue

                # Check collision between shields and asteroid
                if player.spaceship.shield_active:
                    for i, shield in enumerate(player.spaceship.shields):
                        if shield:
                            if shield['mask'].collidepolygon(asteroid.polygon):
                                player.spaceship.shields[i] = False
                                print(player.spaceship.shields)
                                self.asteroid.remove(asteroid)
                                new_Asteroids = asteroid.split()
                                self.asteroid.extend(new_Asteroids)
                            if not any(player.spaceship.shields):
                                player.spaceship.deactivate_shield()
            
                for projectile in player.spaceship.projectiles:
                    if projectile.circle.collidepolygon(asteroid.polygon):
                        player.spaceship.projectiles.remove(projectile)
                        self.asteroid.remove(asteroid)
                        new_circles = asteroid.split()
                        self.asteroid.extend(new_circles)

    def _check_projectile_collisions(self):
        for player in self.players:
            for other_player in self.players:
                if player != other_player:
                    for projectile in other_player.spaceship.projectiles[:]:
                        # Check collision between player spaceship and projectile
                        if player.spaceship.polygon.collidecircle(projectile.circle):
                            if not player.invulnerable and player.active:
                                player.lose_life()
                                other_player.spaceship.projectiles.remove(projectile)
                                break

    def _check_superpower_collisions(self):
        for player in self.players:
            for superpower in self.superpowers:
                if superpower.active:
                    distance = player.spaceship.position.distance_to(superpower.position)
                    if distance < Superpower.SIZE:
                        superpower.apply_effect(player)
                        superpower.active = False
                        self.superpowers.remove(superpower)

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
                player.update()
                player.draw_lives(self.screen, player_index)
                if player.waiting_to_respawn:
                    ui.draw_respawn_screen(self.screen, player, player_index)
            for circle in self.asteroid:
                circle.draw(self.screen)
            for superpower in self.superpowers:
                superpower.draw(self.screen)
        elif self.state == "game over":
            ui.draw_game_over_screen(self.screen)
        elif self.state == "win":
            ui.draw_win_screen(self.screen)

        pygame.display.flip()
        self.clock.tick(60)

if __name__ == "__main__":
    SpaceRocks().main_loop()