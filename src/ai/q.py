import numpy as np
import matplotlib.pyplot as plt

from ai import AI
from constants import ScoreCategory, CATEGORY_COUNT
from state import GameState
from utils import score_roll


class QState:
    MAX_CATEGORY = 1 << 13
    MAX_SUMS = 106
    MAX_DICE_THROWS = 252
    MAX_REROLLS = 3

    def __init__(self):
        # map sorted dice throws to numbers
        self.dice_throw_id: dict[tuple[int, ...], int] = {}
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
        scores = state.player_states[0].scores

        categories = sum((1 if score == ScoreCategory.UNSELECTED.value else 0) << i for i, score in enumerate(scores))
        sum_first_six = sum(scores[:6])

        dice_id = self.dice_throw_id[tuple(sorted(state.dice))]
        rerolls = state.rerolls

        return rerolls + QState.MAX_REROLLS * (
                dice_id + QState.MAX_DICE_THROWS * (sum_first_six + QState.MAX_SUMS * categories)
        )


class Q:

    REROLL_TRANSITIONS_LIST = list(AI.REROLL_TRANSITIONS.values())
    REROLL_CONFIGURATIONS_COUNT = len(REROLL_TRANSITIONS_LIST)
    # 13 possible categories + 31 reroll configurations + 1 for terminal state
    MAX_ACTIONS = CATEGORY_COUNT + REROLL_CONFIGURATIONS_COUNT + 1
    # 2^13 categories choices * 106 max scores (first six categories) * 252 dice orders * 3 rerolls = 656474112 states
    MAX_STATES = QState.MAX_CATEGORY * QState.MAX_SUMS * QState.MAX_DICE_THROWS * QState.MAX_REROLLS

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
        """Train for a single game/epoch."""
        state = GameState(1)
        state.apply_reroll_by_unpicked_dice(AI.REROLL_TRANSITIONS[30])

        next_state_id, next_reward = self.qstate.state_to_id(state), 0
        state_id, action, reward = None, None, None

        def next_action():
            valid_actions = ([c for c in range(CATEGORY_COUNT) if state.is_valid_category_optimized_unsafe(c)]
                             + [x + CATEGORY_COUNT for x in range(Q.REROLL_CONFIGURATIONS_COUNT)])
            if np.random.rand() < self.exploration_factor:
                return np.random.choice(valid_actions)

            return valid_actions[np.argmax(self.q[next_state_id, valid_actions])]

        def perform_action():
            if action < CATEGORY_COUNT:
                new_state, new_reward = state.apply_category_optimized_unsafe(action)
                new_state = state.apply_reroll_by_unpicked_dice(AI.REROLL_TRANSITIONS[30])
            else:
                new_state = state.apply_reroll_by_unpicked_dice(AI.REROLL_TRANSITIONS[action - CATEGORY_COUNT])
                scores = score_roll(state.dice)

                # ones: x1 + 35 / 21 * fr1 / 5, twos: x2 + 35 / 21 * 2fr2 / 5, ..., large_straight: x10 * b10 / sum(b)
                # 35 = 35 / 21 * 1 + 35 / 21 * 2 + ... + 35 / 21 * 6
                total = sum(
                    val + 35 / 21 * (i + 1) * val / (i + 1) / 5 for i, val in enumerate(scores[:6])
                    if val == ScoreCategory.UNSELECTED.value
                ) + sum(
                    val for val in scores[6:]
                    if val == ScoreCategory.UNSELECTED.value
                )
                cnt = sum(val == ScoreCategory.UNSELECTED.value for val in scores)
                new_reward = total / cnt

            return new_state, self.qstate.state_to_id(new_state), new_reward

        # handle initial state
        state_id, action, reward = next_state_id, next_action(), next_reward
        state, next_state_id, next_reward = perform_action()

        while not state.is_final():
            self.n[state_id, action] += 1

            alpha = 1 / self.n[state_id, action]
            self.q[state_id, action] = ((1 - alpha) * self.q[state_id, action] + alpha *
                                        (reward + self.discount_rate * np.max(self.q[next_state_id])))

            state_id, action, reward = next_state_id, next_action(), next_reward
            state, next_state_id, next_reward = perform_action()

        # TODO?: handle terminal state
        # self.q[next_state_id, Q.MAX_ACTIONS - 1] = next_reward

        return state.player_states[0].total_score()

    def train(self):
        """Train for a number of games/epochs."""
        results = []
        for _ in range(self.epochs):
            results.append(self.__train())

            self.exploration_factor = self.exploration_factor * 0.99

        plt.plot(results, ".-b")
        plt.show()

    def __save(self):
        raise NotImplementedError()

    def __load(self):
        raise NotImplementedError()


class QAI(AI):

    def __init__(self):
        super().__init__()
        self.q = []

    def wants_reroll(self, state: GameState) -> bool:
        raise NotImplementedError()

    def reroll(self, state: GameState) -> GameState:
        raise NotImplementedError()

    def pick_category(self, state: GameState) -> GameState:
        raise NotImplementedError()


if __name__ == "__main__":
    q = Q()
    q.train()