import threading

from openai import OpenAI

from constants import ScoreCategory
from state import GameState

client = OpenAI()


class ChatResponse:
    def __init__(self, message_history: list[str], state: GameState):
        self._is_response_ready = False
        self._response = None
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

        self.header = f"""
You are a chatbot for the game Yahtzee. A user will talk to you about the game. 
{dice_values}
The unfilled categories are: {', '.join(remaining_categories)},

If the user's message is not related in any way to the game Yahtzee, you will answer promptly with 
`I cannot answer to that.` and stop the answer there.
Otherwise, you will answer with a short message (about 30 words), keeping the information concise and game-related.
"""
        self.message_history_with_roles = list(
            map(
                lambda indexed_msg: {
                    "role": "assistant" if (indexed_msg[0] % 2 == len(message_history) % 2) else "user",
                    "content": indexed_msg[1]
                },
                enumerate(message_history)
            )
        )
        self._start_request()

    def _start_request(self):
        threading.Thread(target=self._request_ai).start()

    def _request_ai(self):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.header},
                    *self.message_history_with_roles
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
