import pygame
from pygame import Surface

from gui.dialogue.textbox import Textbox


def render_text_box(text, font, max_width, text_color=(0, 0, 0), bg_color=(255, 255, 255)):
    # TODO: use textbox utils (wrap_text, render, etc.)
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

    line_height = font.get_linesize()
    text_height = line_height * len(lines)
    surface = pygame.Surface((max_width, text_height))
    surface.fill(bg_color)

    # Render the text line by line
    y_offset = 0
    for line in lines:
        rendered_line = font.render(line, True, text_color)
        surface.blit(rendered_line, (0, y_offset))
        y_offset += line_height

    return surface


class Chat:

    def __init__(self, rect: pygame.Rect, input_box_height: int, font: pygame.font.Font):
        self.rect = rect
        self.input_box = Textbox(
            pygame.Rect(rect.left, rect.top + input_box_height, rect.width, input_box_height),
            font,
        )
        self.messages: list[Surface] = []
        self.building_response = False

    def handle_event(self, event: pygame.event.Event):
        if self.building_response:
            # TODO
            return None

        text = self.input_box.handle_event(event)
        if text is None:
            return
        self.messages.append(render_text_box(text, self.input_box.font, self.rect.width * 4 // 5))
        self.messages.append(render_text_box("ai response", self.input_box.font, self.rect.width * 4 // 5))

    def update(self, dt):
        self.input_box.update(dt)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, (20, 20, 20), self.rect)
        self.input_box.draw(screen)
        height = self.input_box.rect.top
        for message in reversed(self.messages):
            height -= message.get_height() + 20
            screen.blit(message, (self.rect.left, height))
