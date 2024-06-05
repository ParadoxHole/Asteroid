import pygame

pygame.init()

done = False

pygame.joystick.init()
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    joystick = pygame.joystick.Joystick(0)

    hat = pygame.joystick.Joystick(0).get_hat(0)
    print(hat)

    pygame.time.Clock().tick(30)
    