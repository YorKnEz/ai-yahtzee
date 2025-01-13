from functools import partial

import pygame


class Textbox:

    CURSOR_BLINK_PERIOD = 500
    LINE_SPACING = 3

    def __init__(
        self,
        rect: pygame.Rect,
        font: pygame.font.Font,
        *,
        text="",
        text_color=(255, 255, 255),
        empty_text="",
        empty_text_color=pygame.Color("gray"),
        background_color=(0, 0, 0),
        border_width=1,
        border_color=(0, 0, 0)
    ):
        self.rect = rect
        self.font = font
        self.text = text
        self.lines = []
        self.is_line_word_continuation = []
        self.line_pos_to_text_pos = []
        self.__wrap_text_and_set_pos()
        self.text_color = text_color
        self.empty_text_lines = self.__wrap_text(empty_text)[0]
        self.empty_text_color = empty_text_color
        self.background_color = background_color
        self.border_width = border_width
        self.border_color = border_color
        self.active = False
        self.cursor_index = (0, 0)
        self.cursor_update_counter = 0
        self.is_cursor_visible = False

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            return

        if event.type == pygame.KEYDOWN and self.active:
            match event.key:
                case pygame.K_ESCAPE:
                    self.active = False
                case pygame.K_KP_ENTER:
                    txt = self.text
                    self.text = ""
                    self.__wrap_text_and_set_pos()
                    return txt
                case pygame.K_DOWN:
                    self.is_cursor_visible = True
                    self.cursor_update_counter = 0
                    if self.cursor_index[0] + 1 < len(self.lines):
                        self.cursor_index = (self.cursor_index[0] + 1, self.cursor_index[1])
                        if self.cursor_index[1] >= len(self.lines[self.cursor_index[0]]):
                            self.cursor_index = (self.cursor_index[0], len(self.lines[self.cursor_index[0]]) - 1)
                case pygame.K_RIGHT:
                    self.is_cursor_visible = True
                    self.cursor_update_counter = 0
                    self.__move_cursor_right()
                case pygame.K_UP:
                    self.is_cursor_visible = True
                    self.cursor_update_counter = 0
                    if self.cursor_index[0] > 0:
                        self.cursor_index = (self.cursor_index[0] - 1, self.cursor_index[1])
                case pygame.K_LEFT:
                    self.is_cursor_visible = True
                    self.cursor_update_counter = 0
                    self.__move_cursor_left()
                case _editing_event:
                    self.is_cursor_visible = True
                    self.cursor_update_counter = 0
                    self.__handle_editing_event(event)

    def __move_cursor_left(self):
        if self.cursor_index[1] > 0:
            self.cursor_index = (self.cursor_index[0], self.cursor_index[1] - 1)
        elif self.cursor_index[0] > 0:
            self.cursor_index = (self.cursor_index[0] - 1, len(self.lines[self.cursor_index[0] - 1]) - 1)

    def __handle_backspace(self):
        self.__move_cursor_left()
        if self.cursor_index[0] >= len(self.lines):
            self.cursor_index = (self.cursor_index[0] - 1, len(self.lines[self.cursor_index[0] - 1]) - 1)

    def __move_cursor_right(self, prev_text_pos=None):
        if self.cursor_index[1] + 1 < len(self.lines[self.cursor_index[0]]):
            self.cursor_index = (self.cursor_index[0], self.cursor_index[1] + 1)
        elif self.cursor_index[0] + 1 < len(self.lines):
            if prev_text_pos is None:
                self.cursor_index = (self.cursor_index[0] + 1, 0)
            else:
                current_pos = self.line_pos_to_text_pos[self.cursor_index[0] + 1][0]
                self.cursor_index = (self.cursor_index[0] + 1, prev_text_pos - current_pos)

        if self.cursor_index[0] != 0 and self.cursor_index[1] == 0 and len(self.lines[self.cursor_index[0]]) == 0:
            self.cursor_index = (self.cursor_index[0] - 1, len(self.lines[self.cursor_index[0] - 1]) - 1)

    def __wrap_text(self, text) -> tuple[list[str], list[bool]]:
        max_text_width = self.rect.width - 10 + self.font.size(" ")[0]
        separated_text = []
        word_index = 0
        for word in text.split(" "):
            if self.font.size(word + " ")[0] <= max_text_width:
                separated_text.append((word, word_index))
            else:
                current_word = ""
                for ch in word:
                    test_word = current_word + ch
                    if self.font.size(test_word + " ")[0] <= max_text_width:
                        current_word = test_word
                    else:
                        separated_text.append((current_word, word_index))
                        current_word = ch
                if current_word != "":
                    separated_text.append((current_word, word_index))
            word_index += 1

        lines = []
        is_line_word_continuation = []
        current_line = ""
        for i, (word, word_index) in enumerate(separated_text):
            test_line = f"{current_line}{word} "
            if self.font.size(test_line)[0] <= max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                if len(lines) >= 1 and separated_text[i - 1][1] == word_index:
                    is_line_word_continuation.append(True)
                else:
                    is_line_word_continuation.append(False)
                current_line = f"{word} "
        if current_line != "":
            lines.append(current_line)
            if len(lines) >= 1 and separated_text[-1][1] == word_index:
                is_line_word_continuation.append(True)
            else:
                is_line_word_continuation.append(False)

        return lines, is_line_word_continuation

    def __set_line_pos_to_text_pos(self):
        self.line_pos_to_text_pos.clear()
        pos = 0
        for (line, is_continuation) in zip(self.lines, self.is_line_word_continuation):
            self.line_pos_to_text_pos.append(list(range(pos, pos + len(line))))
            pos += len(line) - int(is_continuation)

    def __wrap_text_and_set_pos(self):
        self.lines, self.is_line_word_continuation = self.__wrap_text(self.text)
        self.__set_line_pos_to_text_pos()

    def __handle_editing_event(self, event: pygame.event.Event):
        text_index = self.line_pos_to_text_pos[self.cursor_index[0]][self.cursor_index[1]]
        move_cursor = None
        if event.key == pygame.K_BACKSPACE:
            if text_index > 0:
                self.text = self.text[:text_index - 1] + self.text[text_index:]
                move_cursor = self.__handle_backspace
        elif len(repr(event.unicode)) > 2:
            self.text = self.text[:text_index] + event.unicode + self.text[text_index:]
            move_cursor = partial(self.__move_cursor_right, prev_text_pos=text_index + 1)

        self.__wrap_text_and_set_pos()
        if move_cursor:
            move_cursor()

    def update(self, dt):
        if self.active:
            self.cursor_update_counter += dt * 1000
            if self.cursor_update_counter >= Textbox.CURSOR_BLINK_PERIOD:
                self.cursor_update_counter = 0
                self.is_cursor_visible = not self.is_cursor_visible

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.background_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)

        y_offset = self.rect.y + 5

        for i, line in enumerate(self.lines):
            text_surface = self.font.render(line, True, self.text_color)
            screen.blit(text_surface, (self.rect.x + 5, y_offset))

            if self.active and self.is_cursor_visible and i == self.cursor_index[0]:
                cursor_x = self.rect.x + 5 + self.font.size(line[:self.cursor_index[1]])[0]
                cursor_y = y_offset
                cursor_height = text_surface.get_height()
                pygame.draw.line(screen, self.text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

            y_offset += text_surface.get_height() + Textbox.LINE_SPACING
