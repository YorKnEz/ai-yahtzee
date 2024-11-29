from ai import AI
from . import Dice, Sheet
from state import GameState


class AIPlayer:
    def __init__(self, ai: AI, sheet: Sheet, dice: Dice):
        self.ai = ai
        self.sheet = sheet
        self.dice = dice

        self.state = 0
        self.wait_time = 0

    def play(self, dt, state: GameState) -> GameState:
        match self.state:
            case 0:  # picking dice
                if self.ai.wants_reroll(state):
                    state = self.ai.reroll(state)
                    self.dice.pick([i for i in range(5) if i not in self.ai.unpicked_dice])
                    self.wait_time = 0
                    self.state = 3
                else:
                    self.state = 2
            case 1:  # throw dice
                self.dice.throw(state.dice)
                self.sheet.update_score(state, after_roll=True)
                self.wait_time = 0
                self.state = 4
            case 2:  # select category
                state = self.ai.pick_category(state)
                self.dice.reset()
                self.sheet.update_score(state)
                self.state = 0
            case 3:  # thinking time after pick
                self.wait_time += dt
                if self.wait_time > 1.5:
                    self.state = 1
            case 4:  # thinking time after reroll
                self.wait_time += dt
                if self.wait_time > 1.5:
                    self.state = 0

        return state
