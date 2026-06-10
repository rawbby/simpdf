from simpdf.rich_text import RichText, RichTextStyle, RichContent
from simpdf.stretch_rich_text import stretch_rich_text

__all__ = ["break_rich_text", "break_rich_block_text"]


def _rich_text(rich_text: RichContent, style: RichTextStyle) -> RichText:
    # noinspection PyTypeChecker
    result = RichText.__new__(RichText)
    result.content_left = rich_text
    result.content_center = RichContent(None)
    result.content_right = RichContent(None)
    result.style = style
    return result


def _rich_breaker(rich_text: RichContent, line_width: float, style: RichTextStyle) -> list[RichContent]:
    if not rich_text.segments:
        return [rich_text]

    def width_of_slice(a: int, b: int) -> float:
        total = 0.0
        for beg, end, mode in rich_text.segments:
            sa, sb = max(beg, a), min(end, b)
            if sa < sb:
                total += style.get_style(mode).text_width(rich_text.text[sa:sb])
        return total

    words = rich_text.text.split(" ")
    word_starts: list[int] = []
    pos = 0
    for word in words:
        word_starts.append(pos)
        pos += len(word) + 1

    lines: list[tuple[int, int]] = []
    i = 0
    while i < len(words):
        line_start = word_starts[i]
        last_j = i

        for j in range(i + 1, len(words)):
            test_end = word_starts[j] + len(words[j])
            if width_of_slice(line_start, test_end) > line_width:
                break
            last_j = j

        line_end = word_starts[last_j] + len(words[last_j])
        lines.append((line_start, line_end))
        i = last_j + 1

    return [rich_text.slice(a, b) for a, b in lines]


def break_rich_text(rich_text: str | None | RichContent, line_width: float, style: RichTextStyle) -> list[RichText]:
    """Break a rich-text string into RichText lines that fit within *line_width*."""
    if not isinstance(rich_text, RichContent):
        rich_text = RichContent(rich_text)
    if not rich_text:
        return [_rich_text(rich_text, style)]
    return [_rich_text(piece, style) for piece in _rich_breaker(rich_text, line_width, style)]


def break_rich_block_text(
        rich_text: str | None | RichContent,
        line_width: float,
        style: RichTextStyle,
        min_word_space_factor: float = 0.95,
        min_char_space_factor: float = 0.995,
        min_horizontal_scale: float = 99.0,
        max_word_space_factor: float = 1.1,
        max_char_space_factor: float = 1.01,
        max_horizontal_scale: float = 102.0) -> list[RichText]:
    """Break a rich-text string into fully justified RichText lines.

    All lines except the last are stretched to *line_width* by adjusting spacing
    and horizontal scale within the given bounds.  The last line is only
    compressed (never expanded beyond neutral).
    """
    if not isinstance(rich_text, RichContent):
        rich_text = RichContent(rich_text)

    if not rich_text:
        return [_rich_text(rich_text, style)]

    assert min_char_space_factor <= max_char_space_factor
    assert min_word_space_factor <= max_word_space_factor
    assert min_horizontal_scale <= max_horizontal_scale

    dense_style = RichTextStyle(
        font=style.style.font,
        font_italic=style.style_italic.font if style.style_italic is not style.style else None,
        font_bold=style.style_bold.font if style.style_bold is not style.style else None,
        font_bold_italic=style.style_bold_italic.font if style.style_bold_italic is not style.style else None,
        font_size=style.style.font_size,
        line_height_factor=style.style.line_height_factor,
        char_space=style.style.font_size * (min_char_space_factor - 1.0),
        word_space=style.style.font_size * (min_word_space_factor - 1.0),
        horizontal_scale=min_horizontal_scale,
        color=style.style.color)

    target_width = line_width - 1e-6
    pieces = _rich_breaker(rich_text, line_width, dense_style)

    result = []
    for piece in pieces[:-1]:
        result.append(_rich_text(piece, stretch_rich_text(
            piece, target_width, style,
            min_word_space_factor=min_word_space_factor,
            min_char_space_factor=min_char_space_factor,
            min_horizontal_scale=min_horizontal_scale,
            max_word_space_factor=max_word_space_factor,
            max_char_space_factor=max_char_space_factor,
            max_horizontal_scale=max_horizontal_scale)))

    last = pieces[-1]
    result.append(_rich_text(last, stretch_rich_text(
        last, target_width, style,
        min_word_space_factor=min_word_space_factor,
        min_char_space_factor=min_char_space_factor,
        min_horizontal_scale=min_horizontal_scale,
        max_word_space_factor=1.0,
        max_char_space_factor=1.0,
        max_horizontal_scale=100.0)))

    return result
