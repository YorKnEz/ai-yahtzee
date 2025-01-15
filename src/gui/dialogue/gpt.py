import threading

from openai import OpenAI

from constants import ScoreCategory, CATEGORY_COUNT
from state import GameState

client = OpenAI()


class GptResponse:
    def __init__(self, message_history: list[dict[str, str]]):
        self._is_response_ready = False
        self._response = None
        self.header = ""
        self.message_history = message_history

    @classmethod
    def chat(cls, message_history: list[dict[str, str]], state: GameState):
        obj = cls(message_history)
        remaining_categories = []
        for value, category in zip(state.player_states[0].scores, list(ScoreCategory)[1:]):
            if value == ScoreCategory.UNSELECTED.value:
                remaining_categories.append(category.name.capitalize().replace("_", " "))

        if state.rerolls == 3 or state.current_player != 0:
            dice_values = f"The dice have not yet been rolled this round."
        else:
            dice_values = f"""
        The values of the dice are, in no particular order: {', '.join(map(str, state.dice))}.,
        The number of rerolls left is: {state.rerolls},
        """

        obj.header = f"""
        You are a chatbot for the game Yahtzee. A user will talk to you about the game. 
        {dice_values}
        The unfilled categories are: {', '.join(remaining_categories)},

        If the user's message is not related in any way to the game Yahtzee, you will answer promptly with 
        `I cannot answer to that.` and stop the answer there.
        Otherwise, you will answer with a short message (about 30 words), 
        keeping the information concise and game-related.
        """
        obj._start_request()
        return obj

    @classmethod
    def feedback(cls, message_history: list[dict[str, str]], state: GameState):
        obj = cls(message_history)
        scores = [
            f"{category.name.capitalize().replace("_", " ")} -> {value} points"
            for value, category in zip(state.player_states[0].scores, list(ScoreCategory)[1:])
        ]
        obj.header = f"""
        You are a chatbot for the game Yahtzee. A user has just finished a game.
        The scores obtained for each category are: {', '.join(scores)}.
        The number of used rerolls is {state.player_states[0].rerolls - CATEGORY_COUNT} out of {CATEGORY_COUNT * 2}.
        Answer with a short message (about 30 words), providing feedback on the user's performance during this game.  
        """
        obj._start_request()
        return obj

    def _start_request(self):
        threading.Thread(target=self._request_ai).start()

    def _request_ai(self):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.header},
                    *self.message_history
                ],
                max_tokens=150
            )
            self._response = completion.choices[0].message.content
        except Exception as e:
            self._response = str(e)
        finally:
            self._is_response_ready = True

    @property
    def is_response_ready(self):
        return self._is_response_ready

    @property
    def response(self):
        if self.is_response_ready:
            return self._response

        return "Response is being generated..."
