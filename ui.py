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

def draw_score(screen, player, player_number):
    if player.active:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        font = pygame.font.Font("Fonts/Vectorb.ttf", 20)
        score = round(player.score)
        if player_number == 0:
            text = font.render(f"{score}", True, player.spaceship.color)
            screen.blit(text, (20, screen_height-30))
        elif player_number == 1:
            text = font.render(f"{score}", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, -90)  # Rotate 90 degrees clockwise
            screen.blit(rotated_text, (10, 20))
        elif player_number == 2:
            text = font.render(f"{score}", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, 180)  # Rotate 90 degrees counterclockwise
            screen.blit(rotated_text, (screen_width-300, 10))
        elif player_number == 3:
            text = font.render(f"{score}", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, 90)  # Rotate 180 degrees
            screen.blit(rotated_text, (screen_width-30, screen_height-300))
            
def draw_superpower(screen, player, player_number):
    if player.superpower_active:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        font = pygame.font.Font("Fonts/Vectorb.ttf", 20)
        
        if player_number == 0:
            text = font.render(f"Superpower: {player.superpower_type}", True, player.spaceship.color)
            screen.blit(text, (20, screen_height-60))
        elif player_number == 1:
            text = font.render(f"Superpower: {player.superpower_type}", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, -90)  # Rotate 90 degrees clockwise
            screen.blit(rotated_text, (10, 40))
        elif player_number == 2:
            text = font.render(f"Superpower: {player.superpower_type}", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, 180)  # Rotate 90 degrees counterclockwise
            screen.blit(rotated_text, (screen_width-300, 30))
        elif player_number == 3:
            text = font.render(f"Superpower: {player.superpower_type}", True, player.spaceship.color)
            rotated_text = pygame.transform.rotate(text, 90)  # Rotate 180 degrees
            screen.blit(rotated_text, (screen_width-30, screen_height-300))
        
def draw_respawn_screen(screen, player, player_number):
    if player.waiting_to_respawn:
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        font = pygame.font.Font("Fonts/Vectorb.ttf", 20)
    
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
    font = pygame.font.Font("Fonts/Vectorb.ttf", 74)
    text = font.render("You Win!", True, (255, 255, 255))
    screen.blit(text, (300, 300))
    text = font.render("Press Enter to Restart", True, (255, 255, 255))
    screen.blit(text, (150, 400))

def draw_demo_screen(screen, qr_codes: list):
    resized_qr_codes = [pygame.transform.scale(qr_code, (100, 100)) for qr_code in qr_codes]  # Resize QR codes to 100x100 pixels

    positions = [
        (screen.get_width() // 2 - resized_qr_codes[0].get_width() // 2, 0),  # Top-center
        (screen.get_width() - resized_qr_codes[1].get_width(), screen.get_height() // 2 - resized_qr_codes[1].get_height() // 2),  # Right-center
        (screen.get_width() // 2 - resized_qr_codes[2].get_width() // 2, screen.get_height() - resized_qr_codes[2].get_height()),  # Bottom-center
        (0, screen.get_height() // 2 - resized_qr_codes[3].get_height() // 2)  # Left-center
    ]
    
    for qr_code, position in zip(resized_qr_codes, positions):
        screen.blit(qr_code, position)