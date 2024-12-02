import pygame

from constants import CATEGORY_COUNT, ScoreCategory
from state import GameState
from utils import score_roll


class Sheet:
    row_labels = [
        "Ones",
        "Twos",
        "Threes",
        "Fours",
        "Fives",
        "Sixes",
        "Sum",
        "Bonus",
        "Three of a kind",
        "Four of a kind",
        "Full house",
        "Small straight",
        "Large straight",
        "Chance",
        "YAHTZEE",
        "Total score",
    ]
    row_clickable = [True, True, True, True, True, True, False, False, True, True, True, True, True, True, True, False]

    col_labels = ["You", "AI"]

    def __init__(self, bounds: pygame.Rect, font: pygame.font.Font):
        self.bounds = bounds.copy()
        self.font = font

        border_padding = 2

        # add a margin of 24 pixels around the sheet and 4 pixel padding to take into account borders
        self.bounds.x += 24
        self.bounds.y += 24
        self.bounds.height -= 48 + 4 * border_padding
        self.bounds.width -= 48 + 4 * border_padding

        row_labels_len = len(Sheet.row_labels)

        # compute de width and height so that each row and column is divided evenly
        cell_height = self.bounds.height // (row_labels_len + 1)  # extra row for the header
        cell_width = self.bounds.width // 2  # cell width for first col

        self.bounds.height = cell_height * (row_labels_len + 1) + 4 * border_padding
        self.bounds.width = cell_width * 2 + 4 * border_padding
        self.bounds.center = (bounds.center[0], bounds.y + bounds.height // 2)

        # add exterior borders
        self.bounds.x += border_padding
        self.bounds.y += border_padding
        self.bounds.width -= 3 * border_padding
        self.bounds.height -= 3 * border_padding
        self.lines = [
            (self.bounds.topleft, self.bounds.topright),
            (self.bounds.topright, self.bounds.bottomright),
            (self.bounds.bottomright, self.bounds.bottomleft),
            (self.bounds.bottomleft, self.bounds.topleft),
        ]
        self.bounds.x += border_padding
        self.bounds.y += border_padding
        self.bounds.width -= border_padding
        self.bounds.height -= border_padding

        # from now on, bounds represents the box without the borders, math is easier this way

        self.text = [font.render(label, True, "black") for label in (Sheet.row_labels + Sheet.col_labels)]
        self.text_rect: list[pygame.Rect] = []

        # define clickable area
        self.cells_bounds = self.bounds.copy()
        self.cells_bounds.x += cell_width
        self.cells_bounds.y += cell_height
        self.cells_bounds.width -= cell_width
        self.cells_bounds.height -= cell_height

        # init rects for row_labels
        for i in range(row_labels_len):
            rect = self.text[i].get_rect()
            rect.x = self.bounds.x + 8
            rect.center = (
                rect.center[0],
                self.bounds.y + (i + 1) * cell_height + cell_height // 2,
            )
            self.text_rect.append(rect)

            # add horizontal borders
            self.lines.append(
                (
                    (
                        self.bounds.x,
                        self.bounds.y + (i + 1) * cell_height,
                    ),
                    (
                        self.bounds.x + self.bounds.width,
                        self.bounds.y + (i + 1) * cell_height,
                    ),
                ),
            )

        # init rects for col_labels
        for i in range(row_labels_len, row_labels_len + 2):
            rect = self.text[i].get_rect()
            rect.x = self.bounds.x + cell_width + (i - row_labels_len) * (cell_width // 2) + 8
            rect.center = (rect.center[0], self.bounds.y + cell_height // 2)
            self.text_rect.append(rect)

            # add vertical borders
            self.lines.append(
                (
                    (
                        self.bounds.x + cell_width + (i - row_labels_len) * (cell_width // 2),
                        self.bounds.y,
                    ),
                    (
                        self.bounds.x + cell_width + (i - row_labels_len) * (cell_width // 2),
                        self.bounds.y + self.bounds.height,
                    ),
                ),
            )

        self.cell_width = cell_width // 2
        self.cell_height = cell_height

        self.score_text = []
        self.score_text_rect = []

        # subtract exterior borders
        self.bounds.x -= 2 * border_padding
        self.bounds.y -= 2 * border_padding
        self.bounds.width += 4 * border_padding
        self.bounds.height += 4 * border_padding

    def __update_score_for_player(
        self,
        column_index: int,
        player_scores: list[int],
        obtained_scores: list[int],
    ):
        is_0_only_obtainable_score = all(
            obtained_score == 0
            for obtained_score, player_score in zip(obtained_scores, player_scores)
            if player_score == ScoreCategory.UNSELECTED.value
        )

        are_first_6_rows_completed = all(score != ScoreCategory.UNSELECTED.value for score in player_scores[:6])

        # compute scores for sum and bonus
        if are_first_6_rows_completed:
            sum_first_6_rows = sum(score for score in player_scores[:6] if score != ScoreCategory.UNSELECTED.value)
            bonus_first_6_rows = 35 * (sum_first_6_rows >= 63)
        else:
            sum_first_6_rows = -1
            bonus_first_6_rows = -1

        player_scores = player_scores[:6] + [sum_first_6_rows, bonus_first_6_rows] + player_scores[6:]
        obtained_scores = obtained_scores[:6] + [0, 0] + obtained_scores[6:]

        # update the text elements of the sheet
        for i, (existing_score, possible_score) in enumerate(zip(player_scores, obtained_scores)):
            # black is used for picked fields, red for pickable fields
            color = "black"

            if i == 6 or i == 7:
                # for sum and bonus always render using existing score or display nothing
                display_number = str(existing_score) if existing_score != ScoreCategory.UNSELECTED.value else ""
            elif existing_score != ScoreCategory.UNSELECTED.value:
                # unselected fields should be rendered if the existing_score exists (damn)
                display_number = str(existing_score)
            elif possible_score == -1:
                # ignore values of -1
                # -1 is a marker that esentially says that we are rendering the scores for the other player
                # so no red text should be shown on its column
                display_number = ""
            else:
                # if existing_score is missing, render in red the possible value that can be obtained or nothing
                color = "red"
                # render possible_score in only if it is non zero or if it is zero and zero is the only possible value
                display_number = str(possible_score) if possible_score > 0 or (possible_score == 0 and is_0_only_obtainable_score) else ""

            self.score_text.append(self.font.render(display_number, True, color))
            rect = self.score_text[i].get_rect()
            rect.x = self.cells_bounds.x + self.cell_width * column_index + 8
            rect.center = (
                rect.center[0],
                self.cells_bounds.y + i * self.cell_height + self.cell_height // 2,
            )
            self.score_text_rect.append(rect)

        # update total
        total_score = str(sum(score for score in player_scores[:6] + player_scores[8:] if score != ScoreCategory.UNSELECTED.value))

        self.score_text.append(self.font.render(total_score, True, "black"))
        rect = self.score_text[-1].get_rect()
        rect.x = self.cells_bounds.x + self.cell_width * column_index + 8
        rect.center = (
            rect.center[0],
            self.cells_bounds.y + (len(self.row_labels) - 1) * self.cell_height + self.cell_height // 2,
        )
        self.score_text_rect.append(rect)

    def update_score(self, state: GameState, after_roll=False):
        """
        Updates the scoresheet upon a state change. Updates can come from two places:
        1. A reroll happened, which means `obtained_scores` must be retrieved and rendered on the
        sheet.
        2. A category selection happened, which means no obtained scores should be rendered and
        the picked cell should be drawn using black text.
        """
        self.score_text.clear()
        self.score_text_rect.clear()

        obtained_scores = score_roll(state.dice) if after_roll else [-1] * CATEGORY_COUNT
        for player_index, player_state in enumerate(state.player_states):
            self.__update_score_for_player(
                player_index,
                player_state.scores,
                obtained_scores if player_index == state.current_player else [-1] * CATEGORY_COUNT,
            )

    def draw(self, screen):
        pygame.draw.rect(screen, "white", self.bounds)

        for i, (start_pos, end_pos) in enumerate(self.lines):
            # make the exterior borders (i < 4), border after the first six rows (i == 10),
            # after sum and bonus (i == 12) and the border before total score (i == 19) bold
            pygame.draw.line(
                screen,
                "black",
                start_pos,
                end_pos,
                2 if i < 4 or i == 10 or i == 12 or i == 19 else 1,
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
            if Sheet.row_clickable[row]:
                return row - 2 if row > 7 else row, col
        return None
