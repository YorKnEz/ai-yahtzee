from time import time

import matplotlib.pyplot as plt
import numpy as np

from ai import AI
from constants import CATEGORY_COUNT, ScoreCategory
from state import GameState
from utils import score_roll


class QState:
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
        dice_id = self.dice_throw_id[tuple(sorted(state.dice))]
        rerolls = state.rerolls
        return rerolls + QState.MAX_REROLLS * dice_id


class Q:
    REROLL_TRANSITIONS_LIST = list(AI.REROLL_TRANSITIONS.values())
    REROLL_CONFIGURATIONS_COUNT = len(REROLL_TRANSITIONS_LIST)

    # 13 possible categories + 31 reroll configurations + 1 for terminal state
    MAX_ACTIONS = CATEGORY_COUNT + REROLL_CONFIGURATIONS_COUNT + 1
    # 252 dice orders * 3 rerolls = 756 states
    MAX_STATES = QState.MAX_DICE_THROWS * QState.MAX_REROLLS

    def __init__(self, q=None, n=None):
        # q table
        self.q = np.zeros(shape=(Q.MAX_STATES, Q.MAX_ACTIONS), dtype=np.float32) if q is None else q
        # freq table
        self.n = np.zeros(shape=(Q.MAX_STATES, Q.MAX_ACTIONS), dtype=np.uint32) if n is None else n

        self.qstate = QState()

    def __next_action(self, state: GameState, state_id, exploration_factor=0.0, test=False):
        """Compute the next action given the current state and its id."""
        # exploration function that is a bit smarter than using an exploration_factor
        # it essentially checks the frequency of the states in order to decide if it should explore
        # the state or not
        #
        # states that were explored less than 5 times will be viewed as potentially offering a
        # reward of 1_000_000 (which is ridiculous) which will encourage the agent to visit
        # unexplored states first

        valid_actions = state.get_valid_categories_optimized_unsafe()

        if state.rerolls > 0:
            valid_actions += [x + CATEGORY_COUNT for x in range(Q.REROLL_CONFIGURATIONS_COUNT)]

        if test:
            return valid_actions[np.argmax(self.q[state_id, valid_actions])]

        # if np.random.rand() < exploration_factor:
        #     return np.random.choice(valid_actions)

        # return valid_actions[
        #     np.argmax(
        #         np.where(
        #             self.n[state_id, valid_actions] < 5,
        #             1_000_000,
        #             self.q[state_id, valid_actions],
        #         )
        #     )
        # ]

        # compute action values favoring less frequent actions (by a lot)
        values = np.where(self.n[state_id, valid_actions] < 5, 1_000, self.q[state_id, valid_actions])

        # compute a probability distributions of the values, use softmax
        #
        # normalize the values before np.exp so that values don't blow up
        exp = np.exp(values / 1_000)
        prob = exp / exp.sum()

        # return an action according to this probability distribution
        return np.random.choice(valid_actions, p=prob)

    def __perform_action(self, state: GameState, action):
        """Compute the next state, its id and the reward retrieved for performing the given action in the given state."""
        if action < CATEGORY_COUNT:
            new_state, new_reward = state.apply_category_optimized_unsafe(action)
            new_state = new_state.apply_reroll_by_unpicked_dice(AI.REROLL_TRANSITIONS[30])
        else:
            new_state = state.apply_reroll_by_unpicked_dice(AI.REROLL_TRANSITIONS[action - CATEGORY_COUNT])
            player_scores = new_state.player_states[0].scores

            scores = score_roll(new_state.dice)

            # see how many categories of the first six are completed
            # if there are five, if we pick the missing category we get a bonus
            # first_six_bonus = (
            #     35 if sum(score != ScoreCategory.UNSELECTED.value for score in player_scores[:6]) == 5 else 0
            # )
            first_six_bonus = (
                35 if sum(score for score in player_scores[:6] if score != ScoreCategory.UNSELECTED.value) >= 63 else 0
            )

            # if yahtzee and yahtzee already selected, then add bonus
            yahtzee_bonus = (
                100
                if all(die == new_state.dice[0] for die in new_state.dice)
                and player_scores[ScoreCategory.YAHTZEE.value] != ScoreCategory.UNSELECTED.value
                else 0
            )

            # a more intuitive way to rewrite this would be:
            # new_reward = (sum((x + 35 if only 5/6 completed and x unpicked) for x = ones, twos, ..., sixes) +
            #               sum(x for x = two of a kind, ..., large straight) +
            #               (yahtzee + yahtzee_bonus))
            #
            # basically we reward the agent by a mean of the possible scores obtainable by each
            # action (even if the action can't actually be selected)
            # new_reward = (sum(scores) + first_six_bonus + yahtzee_bonus) / max(1, sum(score > 0 for score in scores))
            new_reward = (sum(scores) + first_six_bonus + yahtzee_bonus) / CATEGORY_COUNT

        return new_state, self.qstate.state_to_id(new_state), new_reward

    def __train(self, discount_rate, exploration_factor):
        """Train for a single game/epoch."""
        state = GameState(1)
        state = state.apply_reroll_by_unpicked_dice(AI.REROLL_TRANSITIONS[30])  # first roll
        state_id = self.qstate.state_to_id(state)

        while not state.is_final():
            action = self.__next_action(state, state_id, exploration_factor)

            next_state, next_state_id, reward = self.__perform_action(state, action)

            if not next_state.is_final():
                self.n[state_id, action] += 1  # update N
                alpha = 1 / self.n[state_id, action]  # compute learning rate

                # update Q
                self.q[state_id, action] = (1 - alpha) * self.q[state_id, action] + alpha * (
                    reward + discount_rate * np.max(self.q[next_state_id])
                )

            state, state_id = next_state, next_state_id

        return state.player_states[0].total_score()

    def train(
        self,
        *,
        epochs=10_000,
        discount_rate=0.9,
        exploration_factor=1.0,
        exploration_decay=lambda e: e,
        save_state=False,
    ):
        """Train for a number of games/epochs."""
        results = []
        start = time()
        for _ in range(epochs):
            results.append(self.__train(discount_rate, exploration_factor))

            exploration_factor = exploration_decay(exploration_factor)
        end = time()

        # plot results
        plt.title("Training scores")
        plt.plot(results, ".-g")
        plt.savefig("graphs/q_train_scores.png")
        plt.close()

        # plot the mean score over 1_000 epochs
        plt.title("Training average scores over 1_000 epochs")
        plt.plot(np.array(results).reshape(-1, 1_000).mean(axis=1), ".-g")
        plt.savefig("graphs/q_train_avg_scores_1k.png")
        plt.close()

        print(f"Q Train Avg Score: {sum(results) / len(results)} in {end - start:.2f} seconds")

        if save_state:
            print("Saving state...", end=" ")
            self.__save((epochs, discount_rate, exploration_factor))
            print("done!")

        return results

    def __test(self):
        """Test for a single game/epoch."""
        state = GameState(1)
        state = state.apply_reroll_by_unpicked_dice(AI.REROLL_TRANSITIONS[30])  # first roll
        state_id = self.qstate.state_to_id(state)

        # simulate game
        while not state.is_final():
            action = self.__next_action(state, state_id, test=True)

            state, state_id, _ = self.__perform_action(state, action)

        # get the total score obtained
        return state.player_states[0].total_score()

    def test(self, *, epochs=1_000):
        """Test for a number of games/epochs."""
        start = time()
        results = [self.__test() for _ in range(epochs)]
        end = time()

        # plot results
        plt.title("Testing scores")
        plt.plot(results, ".-g")
        plt.savefig("graphs/q_test_scores.png")
        plt.close()

        print(f"Q Test Avg Score: {sum(results) / len(results)} in {end - start:.2f} seconds")

        return results

    def __save(self, params):
        np.savez("states/q_state.npz", params=params, q=self.q, n=self.n)

    @staticmethod
    def from_state_file():
        data = np.load("states/q_state.npz")
        q, n = data["q"], data["n"]
        return Q(q, n), data["params"]


class QAI(AI):
    REROLL_TRANSITIONS_LIST = list(AI.REROLL_TRANSITIONS.values())

    def __init__(self, state_filename="states/q_state.npz"):
        self.q = np.load(state_filename)["q"]
        self.qstate = QState()

        self.next_action = None  # cache for next action

    def __get_next_action(self, state: GameState):
        # if next action is not cached, compute it
        if self.next_action is None:
            valid_actions = state.get_valid_categories_optimized_unsafe(state.current_player)

            if state.rerolls > 0:
                valid_actions += [x + CATEGORY_COUNT for x in range(Q.REROLL_CONFIGURATIONS_COUNT)]

            self.next_action = valid_actions[np.argmax(self.q[self.qstate.state_to_id(state), valid_actions])]

        return self.next_action

    def wants_reroll(self, state: GameState) -> bool:
        action = self.__get_next_action(state)

        # force reroll if no reroll occurred yet
        return state.rerolls == GameState.REROLLS_PER_ROUND or action >= CATEGORY_COUNT

    def reroll(self, state: GameState) -> GameState:
        # force reroll if no reroll occurred yet or compute the next action otherwise
        action = CATEGORY_COUNT + 30 if state.rerolls == GameState.REROLLS_PER_ROUND else self.__get_next_action(state)
        # reset next action so it will be computed again on next turn
        self.next_action = None

        self.unpicked_dice = AI.REROLL_TRANSITIONS[action - CATEGORY_COUNT]
        return state.apply_reroll_by_unpicked_dice(self.unpicked_dice)

    def pick_category(self, state: GameState) -> GameState:
        action = self.__get_next_action(state)
        self.next_action = None

        self.unpicked_dice = AI.REROLL_TRANSITIONS[30]
        return state.apply_category(action)
