from itertools import zip_longest

import pygame

from constants import UNSELECTED_CATEGORY_VALUE
from utils import score_roll
from state import GameState


class Sheet:
    row_labels = [
        "Ones",
        "Twos",
        "Threes",
        "Fours",
        "Fives",
        "Sixes",
        "Three of a kind",
        "Four of a kind",
        "Full house",
        "Small straight",
        "Large straight",
        "Chance",
        "YAHTZEE",
        "Total score",
    ]
    col_labels = ["You", "AI"]

    def __init__(self, bounds: pygame.Rect, font: pygame.font.Font):
        self.bounds = bounds.copy()
        self.font = font

        border_padding = 2

        # add exterior borders
        bounds.x += border_padding
        bounds.y += border_padding
        bounds.width -= 3 * border_padding
        bounds.height -= 3 * border_padding
        self.lines = [
            (bounds.topleft, bounds.topright),
            (bounds.topright, bounds.bottomright),
            (bounds.bottomright, bounds.bottomleft),
            (bounds.bottomleft, bounds.topleft),
        ]
        bounds.x += border_padding
        bounds.y += border_padding
        bounds.width -= border_padding
        bounds.height -= border_padding

        # from now on, bounds represents the box without the borders, math is easier this way
        self.text = [
            font.render(label, True, "black")
            for label in (Sheet.row_labels + Sheet.col_labels)
        ]
        self.text_rect: list[pygame.Rect] = []

        row_labels_len = len(Sheet.row_labels)

        cell_height = bounds.height // 15  # there are 15 rows
        cell_width = bounds.width // 2  # cell width for first col

        self.cells_bounds = bounds.copy()
        self.cells_bounds.x += cell_width
        self.cells_bounds.y += cell_height
        self.cells_bounds.width -= cell_width
        self.cells_bounds.height -= cell_height

        # init rects for row_labels
        for i in range(row_labels_len):
            rect = self.text[i].get_rect()
            rect.x = bounds.x + 8
            rect.center = (
                rect.center[0],
                bounds.y + (i + 1) * cell_height + cell_height // 2,
            )
            self.text_rect.append(rect)

            # add horizontal borders
            self.lines.append(
                (
                    (
                        bounds.x,
                        bounds.y + (i + 1) * cell_height,
                    ),
                    (
                        bounds.x + bounds.width,
                        bounds.y + (i + 1) * cell_height,
                    ),
                ),
            )

        # init rects for col_labels
        for i in range(row_labels_len, row_labels_len + 2):
            rect = self.text[i].get_rect()
            rect.x = bounds.x + cell_width + (i - 14) * (cell_width // 2) + 8
            rect.center = (rect.center[0], bounds.y + cell_height // 2)
            self.text_rect.append(rect)

            # add vertical borders
            self.lines.append(
                (
                    (
                        bounds.x + cell_width + (i - 14) * (cell_width // 2),
                        bounds.y,
                    ),
                    (
                        bounds.x + cell_width + (i - 14) * (cell_width // 2),
                        bounds.y + bounds.height,
                    ),
                ),
            )

        self.cell_width = cell_width // 2
        self.cell_height = cell_height

        self.score_text = []
        self.score_text_rect = []

    def __score_for_player(self, column_index: int, player_scores: list[int], obtained_scores: list[int] = None):

        if obtained_scores is None:
            obtained_scores = []

        is_0_only_obtainable_score = all(
            player_score == UNSELECTED_CATEGORY_VALUE and obtained_score == 0
            for obtained_score, player_score in (zip_longest(obtained_scores, player_scores))
        )

        for i, (existing_score, possible_score) in enumerate(zip_longest(player_scores, obtained_scores, fillvalue=0)):

            color = "black"
            display_number = existing_score
            if display_number == UNSELECTED_CATEGORY_VALUE:
                display_number = possible_score
                color = "red"

                if not is_0_only_obtainable_score and display_number == 0:
                    display_number = None

            self.score_text.append(
                self.font.render(
                    str(display_number) if display_number else "",
                    True,
                    color
                )
            )
            rect = self.score_text[i].get_rect()
            rect.x = self.cells_bounds.x + self.cell_width * column_index + 8
            rect.center = (
                rect.center[0],
                self.cells_bounds.y + i * self.cell_height + self.cell_height // 2,
            )
            self.score_text_rect.append(rect)

    def update_score(self, state: GameState):
        self.score_text.clear()
        self.score_text_rect.clear()

        obtained_scores = score_roll(state.dice)
        for player_index, player_state in enumerate(state.player_states):
            self.__score_for_player(
                player_index, player_state.scores, obtained_scores if player_index == state.current_player else None
            )

    def draw(self, screen):
        pygame.draw.rect(screen, "white", self.bounds)

        for i, (start_pos, end_pos) in enumerate(self.lines):
            # make the exterior borders (i < 4), border after the first six rows (i == 10) and
            # border before total score (i == 17) bold
            pygame.draw.line(
                screen,
                "black",
                start_pos,
                end_pos,
                2 if i < 4 or i == 10 or i == 17 else 1,
            )

        for text, text_rect in zip(self.text, self.text_rect):
            screen.blit(text, text_rect)

        for text, text_rect in zip(self.score_text, self.score_text_rect):
            screen.blit(text, text_rect)

    def clicked(self, pos):
        x, y = pos
        if self.cells_bounds.collidepoint(x, y):
            row = (y - self.cells_bounds.y) // self.cell_height
            col = (x - self.cells_bounds.x) // self.cell_width
            return row, col
        return None
