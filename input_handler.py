import pygame

def initialize_player_controls(joystick=None):
    player1_controls = {
        'left': pygame.K_q,
        'right': pygame.K_d,
        'up': pygame.K_z,
        'shoot': pygame.K_SPACE,
        'respawn': pygame.K_r
    }

    player2_controls = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'up': pygame.K_UP,
        'shoot': pygame.K_RETURN,
        'respawn': pygame.K_RSHIFT
    }

    player3_controls = {
        'left': pygame.K_a,
        'right': pygame.K_f,
        'up': pygame.K_s,
        'shoot': pygame.K_g,
        'respawn': pygame.K_h
    }

    player4_controls = {
        'left': pygame.K_j,
        'right': pygame.K_l,
        'up': pygame.K_i,
        'shoot': pygame.K_k,
        'respawn': pygame.K_o
    }

    return player1_controls, player2_controls, player3_controls, player4_controls, joystick

def get_controls_for_seat(player_seat):
    # Define controls for each seat here
    controls = {
        "blue": {
            "up": pygame.K_w,
            "left": pygame.K_a,
            "right": pygame.K_d,
            "shoot": pygame.K_SPACE,
            'respawn': pygame.K_r
        },
        "red": {
            "up": pygame.K_UP,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "shoot": pygame.K_RETURN,
            'respawn': pygame.K_RSHIFT
        },
        "yellow": {
            'left': pygame.K_a,
            'right': pygame.K_f,
            'up': pygame.K_s,
            'shoot': pygame.K_g,
            'respawn': pygame.K_h
        },
        "green": {
            'left': pygame.K_j,
            'right': pygame.K_l,
            'up': pygame.K_i,
            'shoot': pygame.K_k,
            'respawn': pygame.K_o
        }
    }

    return controls.get(player_seat, {})

def handle_start_input(state):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:  # Press Enter to start the game
        state = "playing"
    return state

def handle_game_over_input(state):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:  # Press Enter to return to start screen
        state = "start"
    return state

def handle_respawn_input(players):
    for player in players.values():
        keys = pygame.key.get_pressed()
        if player.waiting_to_respawn:
            if keys[player.respawn_key]:  # Press the respawn key to respawn the player
                player.spawn()
            if player.joystick:
                if player.joystick.get_button(0):
                    player.spawn()
