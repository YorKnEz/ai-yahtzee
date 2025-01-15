from enum import Enum

import pygame
from pygame import Surface

from gui.dialogue.textbox import Textbox
from gui.dialogue.gpt import GptResponse
from state import GameState


def render_text_box(
    text, font, max_width, text_color=(0, 0, 0), bg_color=(255, 255, 255), right_align=False
) -> Surface:
    """
    Render a rectangle containing the given text with word wrapping, splitting words if needed.
    The width of the rectangle will be as small as needed but no larger than max_width.

    :param text: The text to render.
    :param font: A pygame.font.Font object.
    :param max_width: The maximum width of the rectangle.
    :param text_color: The color of the text.
    :param bg_color: The background color of the rectangle.
    :param right_align: If True, align text to the right; otherwise, align to the left.
    :return: A pygame.Surface with the rendered text, and the rectangle size.
    """
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        # Split word if it's too long to fit max_width
        while font.size(word)[0] > max_width:
            # Find the maximum number of characters that fit
            for i in range(1, len(word) + 1):
                if font.size(word[:i])[0] > max_width:
                    # Add the chunk that fits and update the word
                    current_line.append(word[:i - 1])
                    lines.append(' '.join(current_line))
                    current_line = []
                    word = word[i - 1:]
                    break
        # Test the current line with the new word
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            # Finalize the current line and start a new one
            lines.append(' '.join(current_line))
            current_line = [word]

    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))

    # Calculate the width of the rectangle
    line_widths = [font.size(line)[0] for line in lines]
    text_width = min(max(line_widths), max_width) if line_widths else max_width
    line_height = font.get_linesize()
    text_height = line_height * len(lines)

    surface = pygame.Surface((text_width + 10, text_height + 10))
    surface.fill(bg_color)

    # Render the text line by line
    y_offset = 5
    for line in lines:
        rendered_line = font.render(line, True, text_color)
        if right_align:
            x_offset = text_width + 5 - rendered_line.get_width()
        else:
            x_offset = 5
        surface.blit(rendered_line, (x_offset, y_offset))
        y_offset += line_height

    return surface


class MessageSender(Enum):
    Player = "user"
    AI = "assistant"


class Chat:

    def __init__(self, rect: pygame.Rect, input_box_height: int, font: pygame.font.Font):
        self.rect = rect
        self.input_box = Textbox(
            pygame.Rect(rect.left, rect.top + rect.height - input_box_height, rect.width, input_box_height),
            font,
            empty_text="Write to our AI here",
            character_limit=306
        )
        self.messages: list[tuple[Surface, MessageSender]] = []
        self.message_history: list[dict[str, str]] = []
        self.building_response = False
        self.ai_response = None
        self.feedback_response = None

    def handle_event(self, event: pygame.event.Event, game_state: GameState):
        if self.building_response:
            return

        text = self.input_box.handle_event(event)
        if text is None or not text.strip():
            return
        self.messages.append((
            render_text_box(text, self.input_box.font, self.rect.width * 4 // 5, right_align=True),
            MessageSender.Player
        ))
        self.message_history.append({"role": MessageSender.Player.value, "content": text})
        self.building_response = True
        self.ai_response = GptResponse.chat(self.message_history, game_state)

    def update(self, dt):
        self.input_box.update(dt)

        if not self.building_response:
            return
        if self.ai_response is not None:
            if self.__check_response(self.ai_response):
                self.ai_response = None
            return
        if self.feedback_response is not None:
            if self.__check_response(self.feedback_response):
                self.feedback_response = None
            return
        self.building_response = False

    def __check_response(self, response):
        if not response.is_response_ready:
            return False
        text = response.response
        self.messages.append((
            render_text_box(text, self.input_box.font, self.rect.width * 4 // 5),
            MessageSender.AI
        ))
        self.message_history.append({"role": MessageSender.AI.value, "content": text})
        return True

    def generate_feedback(self, game_state: GameState):
        self.feedback_response = GptResponse.feedback(self.message_history, game_state)
        self.building_response = True

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (20, 20, 20), self.rect)
        self.input_box.draw(screen)
        height = self.input_box.rect.top
        for message, sender in reversed(self.messages):
            height -= message.get_height() + 7
            left_shift = int(sender == MessageSender.Player) * (self.rect.width - message.get_width())
            screen.blit(message, (self.rect.left + left_shift, height))
