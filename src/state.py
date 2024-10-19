from copy import deepcopy

from constants import UNSELECTED_CATEGORY_VALUE, ScoreCategory
from utils import reroll, score_roll

# each reroll transition is encoded into a number
REROLL_TRANSITIONS = {
    0: [0],
    1: [1],
    2: [2],
    3: [3],
    4: [4],
    5: [0, 1],
    6: [0, 2],
    7: [0, 3],
    8: [0, 4],
    9: [1, 2],
    10: [1, 3],
    11: [1, 4],
    12: [2, 3],
    13: [2, 4],
    14: [3, 4],
    15: [0, 1, 2],
    16: [0, 1, 3],
    17: [0, 1, 4],
    18: [0, 2, 3],
    19: [0, 2, 4],
    20: [0, 3, 4],
    21: [1, 2, 3],
    22: [1, 2, 4],
    23: [1, 3, 4],
    24: [2, 3, 4],
    25: [0, 1, 2, 3],
    26: [0, 1, 2, 4],
    27: [0, 1, 3, 4],
    28: [0, 2, 3, 4],
    29: [1, 2, 3, 4],
    30: [0, 1, 2, 3, 4],
}


class GameState:

    # The first reroll is forced
    REROLLS_PER_ROUND = 3

    def __init__(self, player_count: int = 2) -> None:
        self.player_states: list[PlayerState] = [PlayerState()] * player_count
        self.current_player = 0
        self.dice = [1, 2, 3, 4, 5]
        self.rerolls = GameState.REROLLS_PER_ROUND

    def is_valid_reroll_by_transition(self, transition: int) -> bool:
        if self.rerolls == 0:
            return False
        if 0 <= transition < len(REROLL_TRANSITIONS):
            return True  # can reroll dice

        return False  # invalid transition number

    def is_valid_reroll_by_unpicked_dice(self, unpicked_dice: list[int]) -> bool:
        if self.rerolls == 0:
            return False
        if len(unpicked_dice) == 0:
            return False
        if not all(0 <= die_index < len(self.dice) for die_index in unpicked_dice):
            return False

        return True

    def apply_reroll_by_unpicked_dice(self, unpicked_dice: list[int]) -> "GameState":
        new_state = deepcopy(self)
        new_state.dice = reroll(new_state.dice, unpicked_dice)
        new_state.rerolls -= 1
        return new_state

    def apply_reroll_by_transition(self, transition: int) -> "GameState":
        return self.apply_reroll_by_unpicked_dice(REROLL_TRANSITIONS[transition])

    def is_valid_category(self, category: int, player_index: int = None) -> bool:
        """
        Determine whether the current player can choose the specified category
        to claim their score for.
        """
        if player_index is None:
            player_index = self.current_player

        category_ints = [enum_obj.value for enum_obj in ScoreCategory]
        if category not in category_ints:
            return False

        player_state = self.player_states[player_index]
        if player_state.scores[category] != UNSELECTED_CATEGORY_VALUE:
            return False

        predicted_scores = score_roll(self.dice)
        if any(score > 0 for score in predicted_scores) and predicted_scores[category] == 0:
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
            raise ValueError(f"Invalid category {category}")

        new_state = deepcopy(self)
        player_state = new_state.player_states[player_index]

        predicted_scores = score_roll(new_state.dice)
        player_state.scores[category] = predicted_scores

        # multi-yahtzee
        if all(self.dice[0] == die for die in self.dice) and player_state.scores[ScoreCategory.YAHTZEE.value] > 0:
            player_state.scores[ScoreCategory.YAHTZEE.value] += 100  # yahtzee bonus

        new_state.current_player = (new_state.current_player + 1) % len(self.player_states)

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

    # def reset_turn(self) -> "PlayerState":
    #     new_state = PlayerState.from_array(self.to_array())
    #     new_state.rerolls = self.MAX_ROLLS
    #     return new_state
