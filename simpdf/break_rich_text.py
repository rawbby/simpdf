from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line
from simpdf.rich_text import RichText, RichTextStyle, RichContent
from simpdf.stretch_rich_text import StretchRichText

__all__ = ["BreakRichText", "BreakRichBlockText"]


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


class BreakRichText(Line):
    """Word-wraps a rich-text string into multiple ``RichText`` lines.

    ``unpack(line_width)`` performs the break and returns the individual
    ``RichText`` lines.  Height properties reflect a single line using the
    worst-case metrics across all style variants (infinite-width assumption).
    ``draw()`` renders the content as-is without wrapping.
    """

    rich_text: RichContent
    style: RichTextStyle

    def __init__(self, rich_text: str | None | RichContent, style: RichTextStyle | None = None):
        self.rich_text = rich_text if isinstance(rich_text, RichContent) else RichContent(rich_text)
        self.style = style or RichTextStyle()

    def _make_lines(self, line_width: float) -> list[RichText]:
        if not self.rich_text:
            return [_rich_text(self.rich_text, self.style)]
        return [_rich_text(piece, self.style)
                for piece in _rich_breaker(self.rich_text, line_width, self.style)]

    def unpack(self, line_width: float) -> list[Line]:
        return self._make_lines(line_width)

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        lines = self._make_lines(end - start)
        lines[0].draw(canvas, baseline, start, end)
        for i, line in enumerate(lines[1:], 1):
            baseline -= lines[i - 1].line_height_lower + line.line_height_upper
            line.draw(canvas, baseline, start, end)

    @property
    def space_top(self) -> float:
        return max(0.5 * s.line_spacing for s in self.style.styles)

    @property
    def space_bottom(self) -> float:
        return max(0.5 * s.line_spacing for s in self.style.styles)

    @property
    def ascent(self) -> float:
        return max(s.ascent for s in self.style.styles)

    @property
    def descent(self) -> float:
        return min(s.descent for s in self.style.styles)

    @property
    def line_height_upper(self) -> float:
        return self.space_top + self.ascent

    @property
    def line_height_lower(self) -> float:
        return self.space_bottom - self.descent

    @property
    def line_height(self) -> float:
        return self.line_height_upper + self.line_height_lower


class BreakRichBlockText(BreakRichText):
    """Word-wraps a rich-text string into fully justified lines.

    All lines except the last are wrapped in ``StretchRichText`` so they fill
    the available width at draw time.  The last line uses conservative
    maximums and does not stretch significantly.
    """

    def __init__(
            self,
            rich_text: str | None | RichContent,
            style: RichTextStyle | None = None,
            min_word_space_factor: float = 0.95,
            min_char_space_factor: float = 0.995,
            min_horizontal_scale: float = 99.0,
            max_word_space_factor: float = 1.1,
            max_char_space_factor: float = 1.01,
            max_horizontal_scale: float = 102.0):
        super().__init__(rich_text, style)
        self._min_wsf = min_word_space_factor
        self._min_csf = min_char_space_factor
        self._min_hs = min_horizontal_scale
        self._max_wsf = max_word_space_factor
        self._max_csf = max_char_space_factor
        self._max_hs = max_horizontal_scale

    def _make_lines(self, line_width: float) -> list[Line]:
        if not self.rich_text:
            return [_rich_text(self.rich_text, self.style)]

        assert self._min_csf <= self._max_csf
        assert self._min_wsf <= self._max_wsf
        assert self._min_hs <= self._max_hs

        dense_style = RichTextStyle(
            font=self.style.style.font,
            font_italic=self.style.style_italic.font if self.style.style_italic is not self.style.style else None,
            font_bold=self.style.style_bold.font if self.style.style_bold is not self.style.style else None,
            font_bold_italic=self.style.style_bold_italic.font if self.style.style_bold_italic is not self.style.style else None,
            font_size=self.style.style.font_size,
            line_height_factor=self.style.style.line_height_factor,
            char_space=self.style.style.font_size * (self._min_csf - 1.0),
            word_space=self.style.style.font_size * (self._min_wsf - 1.0),
            horizontal_scale=self._min_hs,
            color=self.style.style.color)

        pieces = _rich_breaker(self.rich_text, line_width, dense_style)

        result: list[Line] = []
        for piece in pieces[:-1]:
            result.append(StretchRichText(piece, self.style,
                                          min_word_space_factor=self._min_wsf,
                                          min_char_space_factor=self._min_csf,
                                          min_horizontal_scale=self._min_hs,
                                          max_word_space_factor=self._max_wsf,
                                          max_char_space_factor=self._max_csf,
                                          max_horizontal_scale=self._max_hs))

        last = pieces[-1]
        result.append(StretchRichText(last, self.style,
                                       min_word_space_factor=self._min_wsf,
                                       min_char_space_factor=self._min_csf,
                                       min_horizontal_scale=self._min_hs,
                                       max_word_space_factor=1.0,
                                       max_char_space_factor=1.0,
                                       max_horizontal_scale=100.0))
        return result
