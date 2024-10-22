from copy import deepcopy

from constants import UNSELECTED_CATEGORY_VALUE, ScoreCategory
from utils import reroll, score_roll


class GameState:

    # The first reroll is forced
    REROLLS_PER_ROUND = 3

    def __init__(self, player_count: int = 2) -> None:
        self.player_states: list[PlayerState] = [
            PlayerState() for _ in range(player_count)
        ]
        self.current_player = 0
        self.dice = [1, 2, 3, 4, 5]
        self.rerolls = GameState.REROLLS_PER_ROUND

    def __next_turn(self):
        self.current_player = (self.current_player + 1) % len(self.player_states)
        self.rerolls = GameState.REROLLS_PER_ROUND

    def __is_valid_reroll_by_unpicked_dice(self, unpicked_dice: list[int]) -> bool:
        # if self.rerolls == 0:
        #     return False
        if len(unpicked_dice) == 0:
            return False
        if not all(0 <= die_index < len(self.dice) for die_index in unpicked_dice):
            return False

        return True

    def apply_reroll_by_unpicked_dice(self, unpicked_dice: list[int]) -> "GameState":
        if not self.__is_valid_reroll_by_unpicked_dice(unpicked_dice):
            raise ValueError(f"Invalid reroll {unpicked_dice}")

        new_state = deepcopy(self)
        new_state.dice = reroll(new_state.dice, unpicked_dice)
        new_state.rerolls -= 1
        return new_state

    def is_valid_category(self, category: int, player_index: int = None) -> bool:
        """
        Determine whether the current player can choose the specified category
        to claim their score for.
        """
        if player_index is None:
            player_index = self.current_player

        if player_index != self.current_player:
            return False

        category_ints = [enum_obj.value for enum_obj in ScoreCategory]
        if category not in category_ints:
            return False

        player_state = self.player_states[player_index]
        if player_state.scores[category] != UNSELECTED_CATEGORY_VALUE:
            return False

        predicted_scores = score_roll(self.dice)

        is_0_only_obtainable_score = all(
            obtained_score == 0
            for obtained_score, player_score in
            zip(predicted_scores, self.player_states[player_index].scores)
            if player_score == UNSELECTED_CATEGORY_VALUE
        )

        if not is_0_only_obtainable_score and predicted_scores[category] == 0:
            return False

        return True

    def apply_category(self, category: int, player_index: int = None) -> "GameState":
        """
        Return a new GameState with the given category transition applied
        (along with updated bonus, if it is the case).
        """
        if player_index is None:
            player_index = self.current_player

        if not self.is_valid_category(category, player_index):
            raise ValueError(f"Invalid category {category} or player {player_index}")

        new_state = deepcopy(self)
        player_state = new_state.player_states[player_index]

        # multi-yahtzee
        if (
                all(self.dice[0] == die for die in self.dice)
                and player_state.scores[ScoreCategory.YAHTZEE.value] > 0
        ):
            player_state.scores[ScoreCategory.YAHTZEE.value] += 100  # yahtzee bonus

        predicted_scores = score_roll(new_state.dice)
        player_state.scores[category] = predicted_scores[category]

        new_state.__next_turn()

        return new_state

    def is_final(self):
        """
        Return whether the current GameState is final.
        """
        if any(any(score == UNSELECTED_CATEGORY_VALUE for score in player.scores) for player in self.player_states):
            return False

        return True


class PlayerState:
    """
    Class representing the state of a player.
    """

    CATEGORY_COUNT = 13

    def __init__(self) -> None:
        self.scores = [UNSELECTED_CATEGORY_VALUE] * PlayerState.CATEGORY_COUNT

    @staticmethod
    def from_array(player_scores: list[int]) -> "PlayerState":
        assert len(player_scores) == PlayerState.CATEGORY_COUNT
        new_state = PlayerState()
        new_state.scores = deepcopy(player_scores)
        return new_state

    def to_array(self) -> list[int]:
        """
        Transform player state into array of integers.
        """
        return self.scores

    def total_score(self):
        return sum(self.scores) + 35 if sum(self.scores[:6]) > 63 else 0
