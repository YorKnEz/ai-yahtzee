
import pygame

pygame.init()

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

running = True
dt = 0


dice_size = (64, 64)
dice_space = 16

dice_faces = [
    pygame.transform.scale(
        pygame.image.load(f"assets/dice/dice{i}.png").convert_alpha(), dice_size
    )
    for i in range(1, 7)
]

dice_start_x = width // 2 - (dice_size[0] * 5 + dice_space * 4) // 2
dice_pos = [
    (dice_start_x + i * (dice_size[0] + dice_space), height - 30 + 4 - dice_size[1])
    for i in range(5)
]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("purple")

    [screen.blit(dice_faces[i], dice_pos[i]) for i in range(5)]

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
