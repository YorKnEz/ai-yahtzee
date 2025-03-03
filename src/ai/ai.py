from state import GameState


class AI:

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

    def __init__(self):
        self.unpicked_dice = AI.REROLL_TRANSITIONS[30]
        pass

    def wants_reroll(self, state: GameState) -> bool:
        raise NotImplementedError()

    def reroll(self, state: GameState) -> GameState:
        raise NotImplementedError()

    def pick_category(self, state: GameState) -> GameState:
        raise NotImplementedError()
