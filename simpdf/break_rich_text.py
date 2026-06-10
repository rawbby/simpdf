from simpdf.rich_text import RichText, RichTextStyle, _RichContent
from simpdf.stretch_rich_text import stretch_rich_text

__all__ = ["break_rich_text", "break_block_rich_text"]


def _make_rich_text(rc: _RichContent, style: RichTextStyle) -> RichText:
    rt = RichText.__new__(RichText)
    rt.content_left = rc
    rt.content_center = _RichContent(None)
    rt.content_right = _RichContent(None)
    rt.style = style
    return rt


def _rich_content_breaker(rc: _RichContent, line_width: float, style: RichTextStyle) -> list[_RichContent]:
    """Greedy word-level line breaker for a parsed _RichContent.

    Works on char positions in the flat text so segment/link metadata is
    preserved intact via _RichContent.slice.
    """
    if not rc.segments:
        return [rc]

    text = rc.text

    def width_of_slice(a: int, b: int) -> float:
        total = 0.0
        for beg, end, mode in rc.segments:
            sa, sb = max(beg, a), min(end, b)
            if sa < sb:
                total += style.get_style(mode).text_width(text[sa:sb])
        return total

    words = text.split(" ")
    word_starts: list[int] = []
    pos = 0
    for word in words:
        word_starts.append(pos)
        pos += len(word) + 1

    lines: list[tuple[int, int]] = []
    i = 0
    while i < len(words):
        line_start = word_starts[i]
        last_j = i  # always include at least the first word on a line

        for j in range(i + 1, len(words)):
            test_end = word_starts[j] + len(words[j])
            if width_of_slice(line_start, test_end) <= line_width:
                last_j = j
            else:
                break

        line_end = word_starts[last_j] + len(words[last_j])
        lines.append((line_start, line_end))
        i = last_j + 1

    return [rc.slice(a, b) for a, b in lines]


def break_rich_text(rich_text: str | None, line_width: float, style: RichTextStyle) -> list[RichText]:
    """Break a rich-text string into RichText lines that fit within *line_width*."""
    rc = _RichContent(rich_text)
    if rc.is_empty:
        return [_make_rich_text(rc, style)]
    return [_make_rich_text(piece, style) for piece in _rich_content_breaker(rc, line_width, style)]


def break_block_rich_text(
        rich_text: str | None,
        line_width: float,
        style: RichTextStyle,
        min_word_space_factor: float = 0.95,
        min_char_space_factor: float = 0.995,
        min_horizontal_scale: float = 99.0,
        max_word_space_factor: float = 1.1,
        max_char_space_factor: float = 1.01,
        max_horizontal_scale: float = 102.0) -> list[RichText]:
    """Break a rich-text string into fully-justified RichText lines.

    All lines except the last are stretched to *line_width* by adjusting spacing
    and horizontal scale within the given bounds.  The last line is only
    compressed (never expanded beyond neutral).
    """
    rc = _RichContent(rich_text)
    if rc.is_empty:
        return [_make_rich_text(rc, style)]

    assert min_char_space_factor <= max_char_space_factor
    assert min_word_space_factor <= max_word_space_factor
    assert min_horizontal_scale <= max_horizontal_scale

    s = style.style
    fs = s.font_size
    dense_style = RichTextStyle(
        font=s.font,
        font_italic=style.style_italic.font if style.style_italic is not style.style else None,
        font_bold=style.style_bold.font if style.style_bold is not style.style else None,
        font_bold_italic=style.style_bold_italic.font if style.style_bold_italic is not style.style else None,
        font_size=fs,
        line_height_factor=s.line_height_factor,
        char_space=fs * (min_char_space_factor - 1.0),
        word_space=fs * (min_word_space_factor - 1.0),
        horizontal_scale=min_horizontal_scale,
        color=s.color,
    )

    target_width = line_width - 1e-6
    pieces = _rich_content_breaker(rc, line_width, dense_style)

    result = []
    for piece in pieces[:-1]:
        result.append(_make_rich_text(piece, stretch_rich_text(
            piece, target_width, style,
            min_word_space_factor=min_word_space_factor,
            min_char_space_factor=min_char_space_factor,
            min_horizontal_scale=min_horizontal_scale,
            max_word_space_factor=max_word_space_factor,
            max_char_space_factor=max_char_space_factor,
            max_horizontal_scale=max_horizontal_scale)))

    last = pieces[-1]
    result.append(_make_rich_text(last, stretch_rich_text(
        last, target_width, style,
        min_word_space_factor=min_word_space_factor,
        min_char_space_factor=min_char_space_factor,
        min_horizontal_scale=min_horizontal_scale,
        max_word_space_factor=1.0,
        max_char_space_factor=1.0,
        max_horizontal_scale=100.0)))

    return result
