import os
import struct
import tkinter as tk
from tkinter import messagebox
from typing import overload

from constants import CATEGORY_COUNT, ScoreCategory
from utils import reroll, score_roll


class GameState:
    # The first reroll is forced
    REROLLS_PER_ROUND = 3

    def __init__(self, player_count: int = 2) -> None:
        self.player_states: list[PlayerState] = [PlayerState() for _ in range(player_count)]
        self.current_player = 0
        self.dice = [1, 2, 3, 4, 5]
        self.rerolls = GameState.REROLLS_PER_ROUND
        self.saved = False
        self.__is_final = False

    def __next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.player_states)
        self.rerolls = GameState.REROLLS_PER_ROUND

    def __is_valid_reroll_by_unpicked_dice(self, unpicked_dice: list[int]) -> bool:
        if self.rerolls == 0:
            return False
        if len(unpicked_dice) == 0:
            return False
        if not all(0 <= die_index < len(self.dice) for die_index in unpicked_dice):
            return False

        return True

    def apply_reroll_by_unpicked_dice(self, unpicked_dice: list[int]) -> "GameState":
        if not self.__is_valid_reroll_by_unpicked_dice(unpicked_dice):
            raise ValueError(f"Invalid reroll {unpicked_dice}")
        self.player_states[self.current_player].rerolls += 1
        new_state = self
        new_state.dice = reroll(new_state.dice, unpicked_dice)
        new_state.rerolls -= 1
        return new_state

    def is_valid_category(self, category: int, player_index: int | None = None) -> bool:
        """
        Determine whether the current player can choose the specified category
        to claim their score for.
        """
        if player_index is None:
            player_index = self.current_player

        if player_index != self.current_player:
            return False

        if not (0 <= category < CATEGORY_COUNT):
            return False

        player_state = self.player_states[player_index]
        if player_state.scores[category] != ScoreCategory.UNSELECTED.value:
            return False

        predicted_scores = score_roll(self.dice)

        is_0_only_obtainable_score = all(
            obtained_score == 0
            for obtained_score, player_score in zip(predicted_scores, self.player_states[player_index].scores)
            if player_score == ScoreCategory.UNSELECTED.value
        )

        if not is_0_only_obtainable_score and predicted_scores[category] == 0:
            return False

        return True

    def apply_category_optimized_unsafe(self, category: int, player_index: int = 0) -> tuple["GameState", int]:
        """
        Return a new GameState with the given category transition applied
        (along with updated bonus, if it is the case).
        """

        new_state = self

        player_scores = new_state.player_states[player_index].scores
        scores = score_roll(new_state.dice)

        # see how many categories of the first six are completed
        # if there are five, and if we pick the missing category, we get a bonus
        first_six_sum, first_six_cnt = 0, 0

        for player_score, score in zip(player_scores[:6], scores[:6]):
            first_six_sum += player_score if player_score != ScoreCategory.UNSELECTED.value else score
            first_six_cnt += player_score != ScoreCategory.UNSELECTED.value

        # compute a bonus sum, first add first_six_bonus
        bonus = 35 if first_six_cnt == 5 and first_six_sum >= 63 else 0

        # multi-yahtzee
        if all(self.dice[0] == die for die in self.dice) and player_scores[ScoreCategory.YAHTZEE.value] > 0:
            player_scores[ScoreCategory.YAHTZEE.value] += 100  # yahtzee bonus
            bonus += 100  # add yahtzee bonus

        player_scores[category] = scores[category]

        new_state.__next_turn()

        return new_state, scores[category] + bonus

    def apply_category(self, category: int, player_index: int | None = None) -> "GameState":
        if player_index is None:
            player_index = self.current_player

        if not self.is_valid_category(category, player_index):
            raise ValueError(f"Invalid category {category} or player {player_index}")

        return self.apply_category_optimized_unsafe(category, player_index)[0]

    def get_valid_categories_optimized_unsafe(self, player_index: int = 0) -> list[int]:
        predicted_scores = score_roll(self.dice)

        is_0_only_obtainable_score = all(
            obtained_score == 0
            for obtained_score, player_score in zip(predicted_scores, self.player_states[player_index].scores)
            if player_score == ScoreCategory.UNSELECTED.value
        )

        return [
            c
            for c in range(CATEGORY_COUNT)
            if (predicted_scores[c] == 0) == is_0_only_obtainable_score
            and self.player_states[player_index].scores[c] == ScoreCategory.UNSELECTED.value
        ]

    def is_final(self):
        """
        Return whether the current GameState is final.
        """
        self.__is_final = self.__is_final or not any(
            any(score == ScoreCategory.UNSELECTED.value for score in player.scores) for player in self.player_states
        )
        return self.__is_final

    def save_statistics(self, filepath: str, player_index: int = 0):
        try:
            if self.saved:
                return
            if not self.is_final():
                raise ValueError(f"State must be final to save statistics")
            self.saved = True
            player_stats = self.player_states[player_index]
            with open(filepath, "ab+") as file:
                file.write(struct.pack("14i", *player_stats.scores, player_stats.rerolls - CATEGORY_COUNT))
        except (Exception,) as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", str(e))

    def __repr__(self):
        return f"GameState({self.dice}, {self.current_player}, {self.rerolls}, {self.player_states})"

    def __str__(self):
        return repr(self)


class PlayerState:
    """
    Class representing the state of a player.
    """

    def __init__(self) -> None:
        self.scores = [ScoreCategory.UNSELECTED.value] * CATEGORY_COUNT
        self.rerolls = 0

    @classmethod
    def from_array(cls, array: list[int]) -> "PlayerState":
        state = cls()
        state.scores = array[:CATEGORY_COUNT]
        state.rerolls = array[-1]
        return state

    def total_score(self):
        return sum(self.scores) + (35 if sum(self.scores[:6]) >= 63 else 0)

    def __repr__(self) -> str:
        return f"Player state: {self.scores}"

    def __str__(self) -> str:
        return repr(self)
