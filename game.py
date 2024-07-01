import pygame, pgeng
from player import Player
import ui
import input_handler
from Spawner import AsteroidSpawner, UFOSpawner
import random
from Superpowers import Superpower
import qrcode
import io
import firebase_listener 

class SpaceRocks:
    def __init__(self):
        self._init_pygame()
        
        self.screen = pygame.display.set_mode((800, 800))
        #self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.clock = pygame.time.Clock()
        self.state = "demo"  # Initial state
        
        self.player_mapping = {}
        self.qr_codes = self.generate_qr_codes()  # Generate QR codes
        self.game_started = False
        self.first_player_login_time = None
        self.login_timer_duration = 2000  # 20 seconds in milliseconds

        # Initialize joystick
        pygame.joystick.init()
        joystick = None
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

        player1_controls, player2_controls, player3_controls, player4_controls, joystick = input_handler.initialize_player_controls(joystick)

        screen_width, screen_height = self.screen.get_size()
        self.player_positions = {
            "blue": pygame.math.Vector2(screen_width // 2 - 60, screen_height // 2 - 60),
            "red": pygame.math.Vector2(screen_width // 2 + 60, screen_height // 2 - 60),
            "yellow": pygame.math.Vector2(screen_width // 2 - 60, screen_height // 2 + 60),
            "green": pygame.math.Vector2(screen_width // 2 + 60, screen_height // 2 + 60)
        }
            
        self.players = {}  # Add player initialization
        self.asteroid = []
        self.superpowers = []
        self.initial_spawn_count = 3
        self.periodic_spawn_count = 2
        self.circle_spawner = AsteroidSpawner(self.screen.get_width(), self.screen.get_height(), self.players)
        self.ufo_spawner = UFOSpawner(self.screen.get_width(), self.screen.get_height(), self.players)
        self.ufos = []  # List to store UFOs

        # Timer events
        self.asteroid_spawn_event = pygame.USEREVENT + 1
        self.superpower_spawn_event = pygame.USEREVENT + 2
        self.ufo_spawn_event = pygame.USEREVENT + 3

        pygame.time.set_timer(self.asteroid_spawn_event, 100000)  # Spawn asteroids every 10 seconds
        pygame.time.set_timer(self.superpower_spawn_event, 15000)  # Spawn superpowers every 15 seconds
        pygame.time.set_timer(self.ufo_spawn_event, 30000, 20000)  # Spawn UFO every 10 seconds after 10 seconds

        self.background = pygame.image.load("img/bg5.jpg")
        
        # Start Firebase listener
        self.listener = firebase_listener.start_listener(self)
        

    def main_loop(self):
        while True:
            self._handle_input()
            self._process_game_logic()
            self._draw()


    def generate_qr_codes(self):
        qr_codes = []
        base_url = "http://localhost:3000/?arcadeId=1&playerSeat=" 

        seats = ["blue", "yellow", "green", "red"]
        for seat in seats:
            qr = qrcode.make(base_url + seat)
            buffered = io.BytesIO()
            qr.save(buffered, format="PNG")
            buffered.seek(0)
            qr_surface = pygame.image.load(buffered, 'PNG')
            qr_codes.append(qr_surface)

        return qr_codes
    
    def add_player(self, user_id, arcadId, player_seat, email):
        if self.state in ["game over", "win"]:
            print("Cannot log in after game over or win.")
            return

        if user_id in self.player_mapping:
            # If the user is already logged in, remove the existing player
            prev_player_seat = self.player_mapping[user_id]
            del self.players[prev_player_seat]
            print(f"Player {email} at seat {prev_player_seat} has been replaced.")

        if player_seat not in self.players:
            player_position = self.player_positions[player_seat]
            controls = input_handler.get_controls_for_seat(player_seat)
            player = Player(player_position, self.get_color_for_seat(player_seat), controls, user_id, arcadId, player_seat)
            self.players[player_seat] = player
            self.player_mapping[user_id] = player_seat  # Update the mapping
            print(f"Added player {email} at seat {player_seat}")
            
            if not self.first_player_login_time:
                self.first_player_login_time = pygame.time.get_ticks()
        else:
            print(f"Seat {player_seat} is already occupied.")

    def get_color_for_seat(self, player_seat):
        colors = {
            "blue": (0, 0, 255),
            "red": (255, 0, 0),
            "yellow": (255, 255, 0),
            "green": (0, 255, 0)
        }
        return colors[player_seat]
    

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Space Rocks")

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            elif event.type == self.asteroid_spawn_event and self.state == "playing":
                self.asteroid.extend(self.circle_spawner.spawn_periodic_circles(self.periodic_spawn_count, len(self.asteroid)))
            elif event.type == self.superpower_spawn_event and self.state == "playing":
                self.spawn_superpower()
                self.set_random_superpower_timer()
            elif event.type == self.ufo_spawner.spawn_timer_event and self.state == "playing":
                self.ufo_spawner.spawn_ufo()
                
        if self.state == "demo" and self.first_player_login_time:
            current_time = pygame.time.get_ticks()
            if current_time - self.first_player_login_time >= self.login_timer_duration:
                self._start_game()
                self.game_started = True
                
        if self.state == "start":
            self._reset_game()
            self.state = input_handler.handle_start_input(self.state)
        elif self.state == "playing": 
            input_handler.handle_respawn_input(self.players)
            for player in self.players.values():
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
        self.asteroid = self.circle_spawner.spawn_initial_circles(min(self.initial_spawn_count, 10))

    def _reset_game(self):
        for player in self.players.values():
            player.reset_lives()
            player.spawn()
        self.asteroid = self.circle_spawner.spawn_initial_circles(self.initial_spawn_count)
        self.first_player_login_time = None
        self.game_started = False
        

    def _process_game_logic(self):
        if self.state == "playing":
            for player in self.players.values():
                player.move(self.screen)
                if player.active:
                    player.update_invulnerability()

            self._move_circles()
            self._check_collisions()
            self._update_projectiles()
            self._check_projectile_collisions()
            self._check_superpower_collisions()
            self.ufo_spawner.update(self.screen)

            if all(player.lives <= 0 for player in self.players.values()):
                self.state = "game over"

    def _move_circles(self):
        for circle in self.asteroid:
            circle.move(self.screen)

    def _check_collisions(self):
        for asteroid  in self.asteroid:
            for player in self.players.values():
                
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
                                self.asteroid.remove(asteroid)
                                new_Asteroids = asteroid.split()
                                self.asteroid.extend(new_Asteroids)
                                if not any(player.spaceship.shields):
                                    player.spaceship.deactivate_shield()
            
                for projectile in player.spaceship.projectiles:
                    if projectile.circle.collidepolygon(asteroid.polygon):
                        player.spaceship.projectiles.remove(projectile)
                        multiplier = 1 + (1000 - projectile.lifespan) / 1000 # Score multiplier based on projectile lifespan
                        player.score += asteroid.score() * multiplier
                        self.asteroid.remove(asteroid)
                        new_circles = asteroid.split()
                        self.asteroid.extend(new_circles)
                
        for ufos in self.ufo_spawner.ufos:
            for player in self.players.values():
                if player.spaceship.polygon.collide(ufos.polygon):
                    if not player.invulnerable and player.active:
                        player.lose_life()
                        self.ufo_spawner.ufos.remove(ufos)
                        continue
                for projectile in player.spaceship.projectiles:
                    if projectile.circle.collidepolygon(ufos.polygon):
                        player.spaceship.projectiles.remove(projectile)
                        self.ufo_spawner.ufos.remove(ufos)
                        player.score += 300
            for projectile in ufos.projectiles:
                if projectile.circle.collidepolygon(player.spaceship.polygon):
                    if not player.invulnerable and player.active:
                        player.lose_life()
                        ufos.projectiles.remove(projectile)
                        continue

    def _check_projectile_collisions(self):
        for player in self.players.values():
            for other_player in self.players.values():
                if player != other_player:
                    for projectile in other_player.spaceship.projectiles[:]:
                        # Check collision between player spaceship and projectile
                        if player.spaceship.polygon.collidecircle(projectile.circle):
                            if not player.invulnerable and player.active:
                                player.lose_life()
                                other_player.spaceship.projectiles.remove(projectile)
                                break

    def _check_superpower_collisions(self):
        for player in self.players.values():
            for superpower in self.superpowers:
                if superpower.active:
                    distance = player.spaceship.position.distance_to(superpower.position)
                    if distance < Superpower.SIZE:
                        superpower.apply_effect(player)
                        superpower.active = False
                        self.superpowers.remove(superpower)

    def _update_projectiles(self):
        for player in self.players.values():
            for projectile in player.spaceship.projectiles[:]:
                projectile.move(self.screen)
                projectile.update()
                if not projectile.is_alive():
                    player.spaceship.projectiles.remove(projectile)
                    
    def _draw(self):
        
        self.screen.blit(self.background, (0, 0))
        if self.state == "demo":
            ui.draw_demo_screen(self.screen, self.qr_codes)
        if self.state == "start":
            ui.draw_start_screen(self.screen)
        elif self.state == "playing":
            for player_index, player in enumerate(self.players.values()):
                player.draw(self.screen)
                player.update()
                player.draw_lives(self.screen, player.player_seat)
                ui.draw_score(self.screen, player, player.player_seat)
                ui.draw_superpower(self.screen, player, player.player_seat)
                if player.waiting_to_respawn:
                    ui.draw_respawn_screen(self.screen, player, player.player_seat)
            for circle in self.asteroid:
                circle.draw(self.screen)
            for superpower in self.superpowers:
                superpower.draw(self.screen)
            self.ufo_spawner.draw(self.screen)
        elif self.state == "game over":
            ui.draw_game_over_screen(self.screen)
        elif self.state == "win":
            ui.draw_win_screen(self.screen)

        self.screen.blit(pygame.font.Font(None, 36).render(f"FPS: {int(self.clock.get_fps())}", True, pygame.Color('white')), (10, 10))

        pygame.display.flip()
        self.clock.tick(60)

if __name__ == "__main__":
    SpaceRocks().main_loop()