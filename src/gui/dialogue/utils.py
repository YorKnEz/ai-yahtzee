def wrap_text(text, font, width) -> tuple[list[str], list[bool]]:
    max_text_width = width + font.size(" ")[0]
    separated_text = []
    word_index = 0
    for word in text.split(" "):
        if font.size(word + " ")[0] <= max_text_width:
            separated_text.append((word, word_index))
        else:
            current_word = ""
            for ch in word:
                test_word = current_word + ch
                if font.size(test_word + " ")[0] <= max_text_width:
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
        if font.size(test_line)[0] <= max_text_width:
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
