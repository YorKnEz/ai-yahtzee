from random import choice, random

from ai import AI
from constants import CATEGORY_COUNT
from state import GameState


class RandomAI(AI):

    REROLL_TRANSITIONS_LIST = list(AI.REROLL_TRANSITIONS.values())

    def wants_reroll(self, state: GameState) -> bool:
        return state.rerolls == state.REROLLS_PER_ROUND or (state.rerolls > 0 and random() < 0.5)

    def reroll(self, state: GameState) -> GameState:
        if state.rerolls == state.REROLLS_PER_ROUND:
            return state.apply_reroll_by_unpicked_dice(self.unpicked_dice)

        self.unpicked_dice = choice(RandomAI.REROLL_TRANSITIONS_LIST)
        return state.apply_reroll_by_unpicked_dice(self.unpicked_dice)

    def pick_category(self, state: GameState) -> GameState:
        self.selected_category = choice(
            [category for category in range(CATEGORY_COUNT) if state.is_valid_category(category)]
        )
        self.unpicked_dice = AI.REROLL_TRANSITIONS[30]
        return state.apply_category(self.selected_category)
