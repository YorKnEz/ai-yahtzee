import random

import pygame
from button import Button
from sheet import Sheet

pygame.init()

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

running = True
dt = 0

font = pygame.font.Font("assets/ldfcomicsans.ttf", 16)

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

button_bounds = pygame.Rect(0, dice_pos[0][1] - 64 - 16, 200, 64)
button_bounds.center = (width // 2, button_bounds.center[1])
button = Button(button_bounds, "Roll dice", font)

sheet = Sheet(pygame.Rect(width - 32 - 304, 32 - 4, 300 + 8, height - 60 + 8), font)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if button.clicked(mouse_pos):
                sheet.update_score(
                    [int(random.random() * 100) for _ in range(14)],
                    [int(random.random() * 100) for _ in range(14)],
                )
            sheet.clicked(mouse_pos)

    screen.fill("purple")

    button.draw(screen)

    [screen.blit(dice_faces[i], dice_pos[i]) for i in range(5)]

    sheet.draw(screen)

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
