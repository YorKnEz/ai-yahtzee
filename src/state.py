from utils import roll_random_dice

# each reroll transition is encoded into a number
REROLL_TRANSITIONS = {
    0: [0], 1: [1], 2: [2], 3: [3], 4: [4],
    5: [0, 1], 6: [0, 2], 7: [0, 3], 8: [0, 4],
    9: [1, 2], 10: [1, 3], 11: [1, 4], 12: [2, 3],
    13: [2, 4], 14: [3, 4], 15: [0, 1, 2], 16: [0, 1, 3],
    17: [0, 1, 4], 18: [0, 2, 3], 19: [0, 2, 4], 20: [0, 3, 4],
    21: [1, 2, 3], 22: [1, 2, 4], 23: [1, 3, 4], 24: [2, 3, 4],
    25: [0, 1, 2, 3], 26: [0, 1, 2, 4], 27: [0, 1, 3, 4],
    28: [0, 2, 3, 4], 29: [1, 2, 3, 4], 30: [0, 1, 2, 3, 4]
}


class GameState:
    def __init__(self) -> None:
        self.player_states: list[PlayerState] = []
        self.current_player = 0
        self.dice = roll_random_dice(5)
    
    def to_array_for_player(self, player_index: int):
        """
        Return an integer array representing the state of the specified player,
        along with the scores of the other player(s).
        """
        raise NotImplementedError()

    def is_valid_reroll(self, player_index: int, transition: int) -> bool:
        player_state = self.player_states[player_index]
        if player_state.rerolls == 0:
            return False
        if 0 <= transition < len(REROLL_TRANSITIONS):
            return True  # can reroll dice
        else:
            return False  # invalid transition number
        
    # I'm not sure if states must/should be immutable
    # or even if these functions belong here
    # but even if the logic gets written here I'm sure it can be moved somewhere else
    def apply_reroll(self, player_index, transition: int) -> "GameState":
        """
        Return a new GameState with the given reroll transition applied
        (along with updated bonus, if it is the case).
        """
        raise NotImplementedError()
    
    def is_valid_category(self, player_index: int, category: int) -> bool:
        """
        Determine whether the current player can choose the specified category
        to claim their score for.
        """
        raise NotImplementedError()
    
    def apply_category(self, player_index: int, category: int) -> "GameState":
        """
        Return a new GameState with the given category transition applied
        (along with updated bonus, if it is the case).
        """
        raise NotImplementedError()
    

class PlayerState:
    """
    Class representing the state of a player.
    """
    MAX_ROLLS = 2

    def __init__(self) -> None:
        self.scores = [-1] * 14  # 13 categories + the bonus at the very end
        self.rerolls = self.MAX_ROLLS

    @staticmethod
    def from_array(player_array: list[int]) -> "PlayerState":
        assert len(player_array) == len(PlayerState().to_array())
        new_state = PlayerState()
        new_state.scores = player_array[:14]
        new_state.rerolls = player_array[14]
        return new_state

    def to_array(self) -> list[int]:
        """
        Transform player state into array of integers.
        """
        return [
            *self.scores,
            self.rerolls
        ]
    
    def reset_turn(self) -> "PlayerState":
        new_state = PlayerState.from_array(self.to_array())
        new_state.rerolls = self.MAX_ROLLS
        return new_state
