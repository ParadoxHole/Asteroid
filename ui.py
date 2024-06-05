import pygame

font = "Fonts/Vectorb.ttf"

def draw_start_screen(screen):
    font = pygame.font.Font("Fonts/Vectorb.ttf", 74)
    text = font.render("Press Enter to Start", True, (255, 255, 255))
    screen.blit(text, (150, 300))

def draw_game_over_screen(screen):
    font = pygame.font.Font("Fonts/Vectorb.ttf", 74)
    text = font.render("Game Over", True, (255, 255, 255))
    screen.blit(text, (300, 300))
    text = font.render("Press Enter to Restart", True, (255, 255, 255))
    screen.blit(text, (150, 400))

def draw_respawn_screen(screen, player, player_number):
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    font = pygame.font.Font("Fonts/Vectorb.ttf", 20)
    if player.waiting_to_respawn:
        if player_number == 0:
            text = font.render(f"Press {pygame.key.name(player.respawn_key).upper()} to Respawn", True, player.spaceship.color)
            screen.blit(text, (20, screen_height-30))
        elif player_number == 1:
            text = font.render(f"Press Button 0 to Respawn", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, -90)  # Rotate 90 degrees clockwise
            screen.blit(rotated_text, (10, 20))
        elif player_number == 2:
            text = font.render(f"Press {pygame.key.name(player.respawn_key).upper()} to Respawn", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, 180)  # Rotate 90 degrees counterclockwise
            screen.blit(rotated_text, (screen_width-300, 10))
        elif player_number == 3:
            text = font.render(f"Press {pygame.key.name(player.respawn_key).upper()} to Respawn", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, 90)  # Rotate 180 degrees
            screen.blit(rotated_text, (screen_width-30, screen_height-300))

def draw_win_screen(screen):
    font = pygame.font.Font("Vector.ttf", 74)
    text = font.render("You Win!", True, (255, 255, 255))
    screen.blit(text, (300, 300))
    text = font.render("Press Enter to Restart", True, (255, 255, 255))
    screen.blit(text, (150, 400))