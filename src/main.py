import random

import pygame

from button import Button
from constants import FPS
from dies import Dies
from sheet import Sheet

pygame.init()

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)

screen_bounds = pygame.Rect(0, 0, width, height)
# screen has two parts: game and score sheet
game_bounds = pygame.Rect(0, 0, int(0.75 * width), height)  # 75% of screen
sheet_bounds = pygame.Rect(
    game_bounds.right, 0, int(0.25 * width), height
)  # 25% of screen

clock = pygame.time.Clock()
running = True
dt = 0

font = pygame.font.Font("assets/ldfcomicsans.ttf", 16)

dies = Dies(game_bounds)

button_bounds = pygame.Rect(0, dies.dice_pos[0][1] - 64 - 16, 200, 64)
button_bounds.center = (game_bounds.center[0], button_bounds.center[1])
button = Button(button_bounds, "Roll dice", font)

sheet = Sheet(
    pygame.Rect(
        sheet_bounds.x,
        sheet_bounds.y + 32 - 4,
        sheet_bounds.width - 32,
        sheet_bounds.height - 60 + 8,
    ),
    font,
)




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

                throw = [int(random.random() * 6) % 6 + 1 for _ in range(5)]
                print(throw)
                dies.throw(throw)

            for dice in dies.rotated_dies:
                if point_in_convex_polygon(mouse_pos, dice):
                    print("clicked")

            sheet.clicked(mouse_pos)

    if dies.animate:
        dies.throw_animation_frame(dt)

    screen.fill("purple")

    pygame.draw.rect(screen, "blue", game_bounds)
    pygame.draw.rect(screen, "green", dies.throw_bounds)

    button.draw(screen)

    sheet.draw(screen)

    dies.draw(screen)

    pygame.display.flip()

    dt = clock.tick(FPS) / 1000

pygame.quit()
