import pygame

from button import Button
from constants import FPS
from dice import Dice
from sheet import Sheet
from state import GameState

pygame.init()

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)

screen_bounds = pygame.Rect(0, 0, width, height)
# screen has two parts: game and scoresheet
game_bounds = pygame.Rect(0, 0, int(0.75 * width), height)  # 75% of screen
sheet_bounds = pygame.Rect(
    game_bounds.right, 0, int(0.25 * width), height
)  # 25% of screen

clock = pygame.time.Clock()
running = True
dt = 0

font = pygame.font.Font("assets/ldfcomicsans.ttf", 16)

state = GameState()
dice = Dice(game_bounds, state.dice)

roll_dice_button_bounds = pygame.Rect(0, dice.dice[1].bounds.top - 64 - 16, 200, 64)
roll_dice_button_bounds.center = (game_bounds.center[0], roll_dice_button_bounds.center[1])
roll_dice_button = Button(roll_dice_button_bounds, "Roll dice", font)

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
            if roll_dice_button.clicked(mouse_pos):
                state = state.apply_reroll_by_unpicked_dice(dice.unpicked_indexes())
                dice.throw(state.dice)
                sheet.update_score(state)

            dice.click(mouse_pos)
            if sheet.clicked(mouse_pos):
                print(sheet.clicked(mouse_pos))

    dice.update(dt)

    screen.fill("purple")

    pygame.draw.rect(screen, "blue", game_bounds)
    pygame.draw.rect(screen, "green", dice.play_area_bounds)

    roll_dice_button.draw(screen)

    sheet.draw(screen)
    dice.draw(screen)

    pygame.display.flip()

    dt = clock.tick(FPS) / 1000

pygame.quit()
