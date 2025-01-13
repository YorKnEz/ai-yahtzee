import pygame

from ai import QAI
from constants import FPS
from gui import AIPlayer, Button, Dice, Sheet
from gui.dialogue.chat import Chat
from gui.dialogue.textbox import Textbox
from state import GameState

pygame.init()
pygame.display.set_caption("Yahtzee")
pygame.key.set_repeat(500, 40)

size = width, height = 1280, 720
screen = pygame.display.set_mode(size)

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

sheet = Sheet(sheet_bounds, font)
final_scores: tuple[int, int] | None = None

ai: AIPlayer = AIPlayer(QAI("7"), sheet, dice)
ai2: AIPlayer = AIPlayer(QAI("bomberman"), sheet, dice)

textbox = Chat(pygame.Rect(100, 100, 200, 400), 200, dialogues_font)


def render():
    dice.update(dt)
    textbox.update(dt)
    screen.fill("purple")

    pygame.draw.rect(screen, "blue", game_bounds)
    pygame.draw.rect(screen, "green", dice.play_area_bounds)

    roll_dice_button.draw(screen)

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
        textbox.handle_event(event)
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if state.is_final():
                if replay_button.clicked(mouse_pos):
                    state = GameState()
                    dice.reset()
                    sheet.update_score(state)
                    final_scores = None

                    ai.reset()
                    ai2.reset()

                continue

            # if state.current_player != 0:
            #     continue
            #
            # if roll_dice_button.clicked(mouse_pos) and not dice.in_animation():
            #     try:
            #         state = state.apply_reroll_by_unpicked_dice(dice.unpicked_indexes())
            #         dice.throw(state.dice)
            #         sheet.update_score(state, after_roll=True)
            #     except ValueError as _:
            #         pass
            #
            # dice.click(mouse_pos)
            #
            # sheet_cell = sheet.clicked(mouse_pos)
            # if sheet_cell:
            #     category, player = sheet_cell
            #
            #     try:
            #         state = state.apply_category(category, player)
            #         dice.reset()
            #         sheet.update_score(state)
            #     except ValueError as _:
            #         pass

    # if not state.is_final() and state.current_player == 0 and not dice.in_animation():
    #     state = ai.play(dt, state)
    #
    # if not state.is_final() and state.current_player == 1 and not dice.in_animation():
    #     state = ai2.play(dt, state)
    #
    # if state.is_final():
    #     final_scores = (
    #         state.player_states[0].total_score(),
    #         state.player_states[1].total_score(),
    #     )

    render()

    dt = clock.tick(FPS) / 1000

pygame.quit()
