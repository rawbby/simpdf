from reportlab.pdfbase.pdfmetrics import *

from simpdf.text_style import TextStyle
from simpdf.text import Text
from simpdf.stretch_text import stretch_text

__all__ = ["break_text", "break_block_text"]


def _text_breaker(text: str | None, line_width: float, style: "TextStyle") -> list[str]:
    if text is None:
        return []
    if not text:
        return [""]

    words = text.split(" ")
    lines = []
    curr_line = words[:1]

    for word in words[1:]:
        test_line = curr_line + [word]
        if style.text_width(" ".join(test_line)) <= line_width:
            curr_line = test_line
        else:
            lines.append(curr_line)
            curr_line = [word]

    result = []
    for line_words in lines:
        result.append(" ".join(line_words))
    if curr_line:
        result.append(" ".join(curr_line))
    return result


def break_text(text: str | None, line_width: float, style: TextStyle,
               links: dict[str, str] | None = None) -> list[Text]:
    """
    Breaks a single string of text into multiple TextLine objects that fit within the specified width.
    """
    return [Text(line, style=style, links=links) for line in _text_breaker(text, line_width, style)]


def break_block_text(text: str | None, line_width: float, style: TextStyle,
                     min_word_space_factor: float = 0.95,
                     min_char_space_factor: float = 0.995,
                     min_horizontal_scale: float = 99.0,
                     max_word_space_factor: float = 1.1,
                     max_char_space_factor: float = 1.01,
                     max_horizontal_scale: float = 102.0,
                     links: dict[str, str] | None = None) -> list[Text]:
    """
    Breaks a text block into multiple TextLine objects, attempting to fully justify them
    by adjusting spacing and horizontal scaling within the specified minimum and maximum bounds.
    """
    if text is None:
        return []
    if not text:
        return [Text("", style=style)]

    assert min_char_space_factor <= max_char_space_factor
    assert min_word_space_factor <= max_word_space_factor
    assert min_horizontal_scale <= max_horizontal_scale

    dense_style = TextStyle(
        font=style.font,
        font_size=style.font_size,
        line_height_factor=style.line_height_factor,
        char_space=style.font_size * (min_char_space_factor - 1.0),
        word_space=style.font_size * (min_word_space_factor - 1.0),
        horizontal_scale=min_horizontal_scale)

    lines = _text_breaker(text, line_width, dense_style)

    target_width = line_width - 1e-5

    result = []
    for line in lines[:-1]:
        line_style = stretch_text(
            line, target_width, style,
            min_word_space_factor=min_word_space_factor,
            min_char_space_factor=min_char_space_factor,
            min_horizontal_scale=min_horizontal_scale,
            max_word_space_factor=max_word_space_factor,
            max_char_space_factor=max_char_space_factor,
            max_horizontal_scale=max_horizontal_scale)
        result.append(Text(content_left=line, style=line_style, links=links))

    last_line = lines[-1]
    if style.text_width(last_line) > line_width:
        unscaled_width = stringWidth(last_line, style.font, style.font_size)
        required_hs = target_width * 100.0 / unscaled_width if unscaled_width != 0 else style.horizontal_scale
        last_line_style = TextStyle(
            font=style.font,
            font_size=style.font_size,
            line_height_factor=style.line_height_factor,
            horizontal_scale=min(style.horizontal_scale, required_hs))
        result.append(Text(content_left=last_line, style=last_line_style, links=links))
    else:
        result.append(Text(content_left=last_line, style=style, links=links))

    return result
