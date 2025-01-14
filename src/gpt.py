from openai import OpenAI

from constants import API_KEY

client = OpenAI(api_key=API_KEY)

def ask_ai(message_history: list[str]) -> str:
    """Return ChatGPT completion for given message history.

    It is assumed that the last message in `message_history` is the user's.
    """
    header = """
    You are a chatbot for the game Yahtzee. A user will talk to you about the game.

    If the user's message is not related to the game Yahtzee, you will answer promptly with `I cannot answer to that.`
    and stop the answer there.
    Otherwise, you will answer with a short message (about 2-3 phrases), keeping the information concise and 
    game-related.
    """

    message_history_with_roles = list(
        map(
            lambda indexed_msg: {
                "role": "assistant" if (indexed_msg[0] % 2 == len(message_history) % 2) else "user",
                "content": indexed_msg[1]
            },
            enumerate(message_history)
        )
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": header},
                *message_history_with_roles,
            ]
        )

        message = completion.choices[0].message.content

        if not message:
            raise

        return message
    except (Exception,):
        return "An error occured. Try again."


