import os
import struct
from tempfile import NamedTemporaryFile
from tkinter import messagebox

import matplotlib.colors
import pygame
from matplotlib import pyplot as plt
import tkinter as tk

from ai import QAI
from constants import FPS, ScoreCategory
from gui import AIPlayer, Button, Dice, Sheet
from gui.dialogue import Chat
from state import GameState, PlayerState

pygame.init()
pygame.display.set_caption("Yahtzee")
pygame.key.set_repeat(500, 40)

size = width, height = 1280, 720
screen = pygame.display.set_mode((1600, 720))

screen_bounds = pygame.Rect(0, 0, width, height)
# screen has two parts: game and scoresheet
game_bounds = pygame.Rect(0, 0, int(0.75 * width), height)  # 75% of screen
sheet_bounds = pygame.Rect(game_bounds.right, 0, int(0.25 * width), height)  # 25% of screen

clock = pygame.time.Clock()
running = True
dt = 0

font = pygame.font.Font("assets/ldfcomicsans.ttf", 16)
dialogues_font = pygame.font.Font("assets/ComicMono.ttf", 16)

state = GameState()
dice = Dice(game_bounds, state.dice)

roll_dice_button_bounds = pygame.Rect(0, dice.dice[1].bounds.top - 64 - 16, 200, 64)
roll_dice_button_bounds.center = (game_bounds.center[0], roll_dice_button_bounds.center[1])
roll_dice_button = Button(roll_dice_button_bounds, "Roll dice", font)

replay_button_bounds = pygame.Rect((width - 300) // 2 + 50, (height - 200) // 2 + 120, 200, 50)
replay_button_bounds.center = game_bounds.center[0], replay_button_bounds.center[1]
replay_button = Button(replay_button_bounds, "Replay", font)

statistics_button_bounds = pygame.Rect(0, 0, 100, 50)
statistics_button_bounds.center = (game_bounds.bottomright[0] - 60, game_bounds.bottomright[1] - 30)
statistics_button = Button(statistics_button_bounds, "Statistics", font)
statistics_file = "yahtzee-stats.bin"

sheet = Sheet(sheet_bounds, font)
final_scores: tuple[int, int] | None = None

ai: AIPlayer = AIPlayer(QAI("7"), sheet, dice)
ai2: AIPlayer = AIPlayer(QAI("bomberman"), sheet, dice)

textbox = Chat(pygame.Rect(1280, 0, 320, 720), 200, dialogues_font)
generated_feedback = False


def show_statistics():
    if not os.path.isfile(statistics_file):
        return None
    if not os.access(statistics_file, os.R_OK):
        return None
    struct_size = struct.calcsize("14i")
    with open(statistics_file, "rb") as file:
        fdata = file.read()
        player_states = [
            PlayerState.from_array(list(struct.unpack("14i", fdata[i:i + struct_size])))
            for i in range(0, len(fdata), struct_size)
        ]

    total_scores = [player_state.total_score() for player_state in player_states]
    category_scores = list(zip(*[player_state.scores for player_state in player_states]))
    rerolls = [player_state.rerolls for player_state in player_states]
    games = range(1, len(player_states) + 1)

    # Create the figure and subplots
    fig, ax = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Plot total score evolution
    ax[0].plot(games, total_scores, marker='o', label="Total Score", color="blue")
    ax[0].set_title("Total Score Evolution")
    ax[0].set_ylabel("Total Score")
    ax[0].legend()
    ax[0].grid(True)

    # Plot category score evolution
    cmap = matplotlib.colormaps["tab20"]
    colors = [cmap(i / len(category_scores)) for i in range(len(category_scores))]
    for category_data, category_type, color in zip(category_scores, list(ScoreCategory)[1:], colors):
        ax[1].plot(
            games, category_data, marker='o', label=category_type.name.capitalize().replace("_", " "), color=color
        )
    ax[1].set_title("Category Score Evolution")
    ax[1].set_ylabel("Score per Category")
    ax[1].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[1].grid(True)

    # Plot reroll evolution
    ax[2].plot(games, rerolls, marker='o', label="Rerolls Used", color="red")
    ax[2].set_title("Reroll Evolution")
    ax[2].set_xlabel("Game Number")
    ax[2].set_ylabel("Rerolls Used")
    ax[2].set_xticks(games)
    # ax[2].xaxis.get_major_locator().set_params(integer=True)
    ax[2].yaxis.get_major_locator().set_params(integer=True)
    ax[2].legend()
    ax[2].grid(True)

    # Adjust layout to fit the category legend
    plt.tight_layout(rect=(0, 0, 0.85, 1))

    try:
        with open("statistics.png", "wt+") as file:
            plt.savefig(file.name)
            plt.close()
            os.startfile(file.name)
    except (Exception,) as e:
        try:
            with NamedTemporaryFile(delete=True, suffix='.png') as temp_file:
                plt.savefig(temp_file.name)
                plt.close()
                os.startfile(temp_file.name)
        except (Exception,):
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))


def render():
    dice.update(dt)
    textbox.update(dt)
    screen.fill("purple")

    pygame.draw.rect(screen, "blue", game_bounds)
    pygame.draw.rect(screen, "green", dice.play_area_bounds)

    roll_dice_button.draw(screen)
    statistics_button.draw(screen)

    sheet.draw(screen)
    dice.draw(screen)

    if final_scores:
        player_score, ai_score = final_scores
        rect_width, rect_height = 300, 200
        rect_x = game_bounds.center[0] - rect_width // 2
        rect_y = (height - rect_height) // 2
        pygame.draw.rect(screen, "pink", (rect_x, rect_y, rect_width, rect_height))
        pygame.draw.rect(screen, "black", (rect_x, rect_y, rect_width, rect_height), 2)
        player_score_text = font.render(f"Your score: {player_score}", True, "black")
        ai_score_text = font.render(f"AI score: {ai_score}", True, "black")

        screen.blit(player_score_text, (rect_x + rect_width // 2 - 50, rect_y + 20))
        screen.blit(ai_score_text, (rect_x + rect_width // 2 - 50, rect_y + 60))
        replay_button.draw(screen)

    textbox.draw(screen)
    pygame.display.flip()


while running:
    for event in pygame.event.get():
        textbox.handle_event(event, state)
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if state.is_final():
                if replay_button.clicked(mouse_pos):
                    state = GameState()
                    dice.reset()
                    sheet.update_score(state)
                    final_scores = None
                    generated_feedback = False

                    ai.reset()
                    # ai2.reset()

                continue

            if statistics_button.clicked(mouse_pos):
                show_statistics()

            if state.current_player != 0:
                continue

            if roll_dice_button.clicked(mouse_pos) and not dice.in_animation():
                try:
                    state = state.apply_reroll_by_unpicked_dice(dice.unpicked_indexes())
                    dice.throw(state.dice)
                    sheet.update_score(state, after_roll=True)
                except ValueError as _:
                    pass

            dice.click(mouse_pos)

            sheet_cell = sheet.clicked(mouse_pos)
            if sheet_cell:
                category, player = sheet_cell

                try:
                    state = state.apply_category(category, player)
                    dice.reset()
                    sheet.update_score(state)
                except ValueError as _:
                    pass

    if not state.is_final() and state.current_player == 1 and not dice.in_animation():
        state = ai.play(dt, state)

    # if not state.is_final() and state.current_player == 1 and not dice.in_animation():
    #     state = ai2.play(dt, state)

    if state.is_final():
        if not generated_feedback:
            textbox.generate_feedback(state)
            generated_feedback = True
        state.save_statistics(statistics_file)
        final_scores = (
            state.player_states[0].total_score(),
            state.player_states[1].total_score(),
        )

    render()

    dt = clock.tick(FPS) / 1000

pygame.quit()
