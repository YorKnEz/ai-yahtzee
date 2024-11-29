import numpy as np

from constants import CATEGORY_COUNT, ScoreCategory
from state import GameState

from .ai import AI


class QState:
    MAX_CATEGORY = 1 << 13
    MAX_SUMS = 105
    MAX_DICE_THROWS = 252
    MAX_REROLLS = 3

    def __init__(self):
        # map sorted dice throws to numbers
        self.dice_throw_id = {}
        i = 0
        for i1 in range(1, 7):
            for i2 in range(i1, 7):
                for i3 in range(i2, 7):
                    for i4 in range(i3, 7):
                        for i5 in range(i4, 7):
                            self.dice_throw_id[i1, i2, i3, i4, i5] = i
                            i += 1

    def state_to_id(self, state: GameState):
        """Pack game state to an id."""
        scores = state.player_states[0].to_array()

        categories = sum((1 if score == ScoreCategory.UNSELECTED.value else 0) << i for i, score in enumerate(scores))
        sum_first_six = sum(scores[:6])
        dice_id = self.dice_throw_id[sorted(state.dice)]
        rerolls = state.rerolls

        return rerolls + QState.MAX_REROLLS * (
            dice_id + QState.MAX_DICE_THROWS * (sum_first_six + QState.MAX_SUMS * categories)
        )


class Q:
    # 13 possible categories + 31 reroll configurations + 1 for terminal state
    MAX_ACTIONS = 13 + 31 + 1
    # 2^13 categories choices * 105 max scores (first six categories) * 252 dice orders * 3 rerolls
    MAX_STATES = QState.MAX_CATEGORY * QState.MAX_SUMS * QState.MAX_DICE_THROWS * QState.MAX_REROLLS

    REROLL_TRANSITIONS_LIST = list(AI.REROLL_TRANSITIONS.values())

    def __init__(self, *, epochs=100, discount_rate=0.9):
        # hyper-parameters
        self.epochs, self.discount_rate = epochs, discount_rate
        # q table
        self.q = np.zeros(shape=(Q.MAX_ACTIONS, Q.MAX_STATES), dtype=np.float32)
        # freq table
        self.n = np.zeros(shape=(Q.MAX_ACTIONS, Q.MAX_STATES), dtype=np.uint32)
        self.exploration_factor = 1.0

        self.qstate = QState()

    def __train(self):
        "Train for a single game/epoch."
        state = GameState(1)
        next_state_id, next_reward  = self.qstate.state_to_id(state), 0
        state_id, action, reward = None, None, None

        def next_action():
            valid_actions = [c for c in range(CATEGORY_COUNT) if state.is_valid_category_optimized_unsafe(c)] + [CATEGORY_COUNT]

            if np.random.rand() < self.exploration_factor:
                return np.random.choice(valid_actions)

            return valid_actions[np.argmax(self.q[next_state_id, valid_actions])]

        # handle initial state
        state_id, action, reward = next_state_id, next_action(), next_reward 

        # perform action

        while not state.is_final():
            self.n[state_id, action] += 1
            
            alpha = 1 / self.n[state_id, action]
            self.q[state_id, action] = (1 - alpha) * self.q[state_id, action] + alpha * (reward  + self.discount_rate * np.max(self.q[next_state_id]))

            state_id, action, reward = next_state_id, next_action(), next_reward 

            # perform action

        # handle terminal state
        self.q[state_id, Q.MAX_ACTIONS - 1] = next_reward

        # see results

    def train(self):
        "Train for a number of games/epochs."
        for _ in range(self.epochs):
            self.__train()

    def __save():
        raise NotImplementedError()

    def __load():
        raise NotImplementedError()


class QAI(AI):
    def __init__(self):
        self.q = []

    def wants_reroll(self, state: GameState) -> bool:
        raise NotImplementedError()

    def reroll(self, state: GameState) -> GameState:
        raise NotImplementedError()

    def pick_category(self, state: GameState) -> GameState:
        raise NotImplementedError()
