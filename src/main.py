import math
import random
from copy import deepcopy

import pygame

from button import Button
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
fps = 144
running = True
dt = 0

font = pygame.font.Font("assets/ldfcomicsans.ttf", 16)

dice_size = 64
dice_space = 16

dice_faces = [
    pygame.transform.scale(
        pygame.image.load(f"assets/dice/dice{i}.png").convert_alpha(),
        (dice_size, dice_size),
    )
    for i in range(1, 7)
]
dies = [dice_faces[i] for i in range(5)]

dice_start_x = game_bounds.center[0] - (dice_size * 5 + dice_space * 4) // 2
dice_pos = [
    (
        dice_start_x + i * (dice_size + dice_space),
        game_bounds.bottom - 30 + 4 - dice_size,
    )
    for i in range(5)
]
dice_bottom_pos = deepcopy(dice_pos)
dice_top_pos = [(x, game_bounds.top + 30 - 4 + dice_size) for x, _ in dice_pos]

button_bounds = pygame.Rect(0, dice_pos[0][1] - 64 - 16, 200, 64)
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


# dice animation stuff
animate = False
# the keyframes of the animation (a tuple of form (duration in seconds, duration in frames)):
# - first item: off screen animation
# - second item: "dice throw" animation
keyframes = [(0.5, 0.5 * fps), (0.3, 0.3 * fps)]
frame_count = 0
curr_keyframe = 0

off_screen_pos = (dice_pos[2][0], game_bounds.bottom + dice_size + 256)


# generate 5 throws in the space defined by throw_bounds such that the dies are not overlapping
# the returned value is an array of tuples of form (x, y, rotation)
def get_random_dice_throw(throw_bounds: pygame.Rect, dice_size: int):
    dice_diag = math.ceil((dice_size * (2**0.5)))

    # normalize throw_bounds such that if dices are rotated they wont be drawn outside of the
    # original throw bounds
    throw_bounds_copy = throw_bounds.copy()
    throw_bounds_copy.x += dice_diag // 2
    throw_bounds_copy.y += dice_diag // 2
    throw_bounds_copy.width -= dice_diag
    throw_bounds_copy.height -= dice_diag

    # generate random (x, y, rotation) tuples
    def get_spots():
        return [
            (
                throw_bounds_copy.x + throw_bounds_copy.width * random.random(),
                throw_bounds_copy.y + throw_bounds_copy.height * random.random(),
                360 * random.random(),
            )
            for _ in range(5)
        ]

    # pick 5 random spots in this space until they are non overlapping
    overlapping = True
    spots = []

    while overlapping:
        spots = get_spots()
        overlapping = False

        for i in range(5):
            for j in range(i + 1, 5):
                # check if distance between points < dice_diag
                if (
                    math.sqrt(
                        (spots[j][0] - spots[i][0]) ** 2
                        + (spots[j][1] - spots[i][1]) ** 2
                    )
                    < dice_diag
                ):
                    overlapping = True

    # the (x, y) picked above are assumed to be the center of the dice, so we need to subtract
    # half of the diagonal
    return [
        (x - dice_diag / 2, y - dice_diag / 2, rotation) for x, y, rotation in spots
    ]


throw_bounds = pygame.Rect(
    game_bounds.x,
    game_bounds.y + game_bounds.height // 4,
    game_bounds.width,
    game_bounds.height // 2,
)

dice_vectors = [(0, 0)] * 5
dice_throw_pos = [(0.0, 0.0, 0.0)] * 5


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

                animate = not animate

                dice_pos = deepcopy(dice_bottom_pos)
                dice_throw_pos = get_random_dice_throw(throw_bounds, dice_size)
                fx, fy = off_screen_pos
                dice_vectors = [(fx - x, fy - y) for x, y in dice_bottom_pos]

            sheet.clicked(mouse_pos)

    if animate:
        duration, total_frames = keyframes[curr_keyframe]

        if curr_keyframe == 0:
            off_x, off_y = off_screen_pos

            if frame_count < total_frames:
                dice_pos = [
                    (
                        x + (dx * dt / duration),
                        y + (dy * dt / duration),
                    )
                    for (x, y), (dx, dy) in zip(dice_pos, dice_vectors)
                ]

                frame_count += 1
            else:
                dice_pos = [off_screen_pos] * 5

                frame_count = 0
                curr_keyframe += 1

                dice_vectors = [
                    (fx - x, fy - y)
                    for (x, y), (fx, fy, _) in zip(dice_pos, dice_throw_pos)
                ]
        else:
            if frame_count < total_frames:
                dice_pos = [
                    (
                        x + (dx * dt / duration),
                        y + (dy * dt / duration),
                    )
                    for (x, y), (dx, dy) in zip(dice_pos, dice_vectors)
                ]

                frame_count += 1
            else:
                dice_pos = [(x, y) for x, y, _ in dice_throw_pos]
                dies = [
                    pygame.transform.rotate(dice_faces[i], rotation)
                    for i, (_, _, rotation) in enumerate(dice_throw_pos)
                ]

                frame_count = 0
                curr_keyframe = 0
                animate = False

    screen.fill("purple")

    pygame.draw.rect(screen, "blue", game_bounds)
    pygame.draw.rect(screen, "green", throw_bounds)

    button.draw(screen)

    for i in range(5):
        screen.blit(dies[i], dice_pos[i])

    sheet.draw(screen)

    pygame.display.flip()

    dt = clock.tick(fps) / 1000

pygame.quit()
