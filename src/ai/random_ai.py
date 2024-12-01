from random import choice, random
from time import time

import matplotlib.pyplot as plt

from ai import AI
from constants import CATEGORY_COUNT
from state import GameState


class RandomAI(AI):

    REROLL_TRANSITIONS_LIST = list(AI.REROLL_TRANSITIONS.values())

    def wants_reroll(self, state: GameState) -> bool:
        return state.rerolls == state.REROLLS_PER_ROUND or (state.rerolls > 0 and random() < 0.5)

    def reroll(self, state: GameState) -> GameState:
        self.unpicked_dice = (
            RandomAI.REROLL_TRANSITIONS_LIST[30]
            if state.rerolls == state.REROLLS_PER_ROUND
            else choice(RandomAI.REROLL_TRANSITIONS_LIST)
        )

        return state.apply_reroll_by_unpicked_dice(self.unpicked_dice)

    def pick_category(self, state: GameState) -> GameState:
        selected_category = choice(
            [category for category in range(CATEGORY_COUNT) if state.is_valid_category(category)]
        )
        self.unpicked_dice = AI.REROLL_TRANSITIONS[30]
        return state.apply_category(selected_category)


class R:

    REROLL_TRANSITIONS_LIST = list(AI.REROLL_TRANSITIONS.values())
    REROLL_CONFIGURATIONS_COUNT = len(REROLL_TRANSITIONS_LIST)

    def __init__(self):
        self.ai = RandomAI()

    def __train(self):
        """Train for a single game/epoch."""
        state = GameState(1)
        state = state.apply_reroll_by_unpicked_dice(AI.REROLL_TRANSITIONS[30])

        while not state.is_final():
            if self.ai.wants_reroll(state):
                state = self.ai.reroll(state)
            else:
                state = self.ai.pick_category(state)

        return state.player_states[0].total_score()

    def train(self, *, epochs=100):
        """Train for a number of games/epochs."""
        results = []
        start = time()
        for _ in range(epochs):
            results.append(self.__train())
        end = time()

        # stats
        plt.plot(results, ".-g")
        plt.savefig("qai_acc.png")
        print(f"QAI Avg Score: {sum(results) / len(results)} in {end - start:.2f} seconds")

        return results
