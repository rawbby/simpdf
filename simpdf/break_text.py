from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line
from simpdf.stretch_text import StretchText
from simpdf.text import Text
from simpdf.text_style import TextStyle

__all__ = ["BreakText", "BreakBlockText"]


def _text_breaker(text: str | None, line_width: float, style: TextStyle) -> list[str]:
    if not text:
        return [""]

    words = text.split(" ")
    lines = []
    line = words[:1]

    for word in words[1:]:
        test_line = line + [word]
        if style.text_width(" ".join(test_line)) <= line_width:
            line = test_line
        else:
            lines.append(line)
            line = [word]

    result = []
    for line_words in lines:
        result.append(" ".join(line_words))
    if line:
        result.append(" ".join(line))
    return result


class BreakText(Line):
    """Word-wraps a text string into multiple ``Text`` lines.

    ``unpack(line_width)`` performs the break and returns the individual
    ``Text`` lines.  Height properties reflect a single line of the given
    style (infinite-width assumption).  ``draw()`` renders the text as-is
    without wrapping and asserts that it fits.
    """

    text: str | None
    style: TextStyle

    def __init__(self, text: str | None, style: TextStyle | None = None):
        self.text = text
        self.style = style or TextStyle()

    def _make_lines(self, line_width: float) -> list[Text]:
        return [Text(s, style=self.style) for s in _text_breaker(self.text, line_width, self.style)]

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
        return 0.5 * self.style.line_spacing

    @property
    def space_bottom(self) -> float:
        return 0.5 * self.style.line_spacing

    @property
    def ascent(self) -> float:
        return self.style.ascent

    @property
    def descent(self) -> float:
        return self.style.descent

    @property
    def line_height_upper(self) -> float:
        return self.space_top + self.ascent

    @property
    def line_height_lower(self) -> float:
        return self.space_bottom - self.descent

    @property
    def line_height(self) -> float:
        return self.style.line_height


class BreakBlockText(BreakText):
    """Word-wraps a text string into fully justified lines.

    All lines except the last are wrapped in ``StretchText`` so they fill
    the available width at draw time.  The last line uses conservative
    maximums and does not stretch significantly.
    """

    def __init__(
            self,
            text: str | None,
            style: TextStyle | None = None,
            min_word_space_factor: float = 0.95,
            min_char_space_factor: float = 0.995,
            min_horizontal_scale: float = 99.0,
            max_word_space_factor: float = 1.1,
            max_char_space_factor: float = 1.01,
            max_horizontal_scale: float = 102.0):
        super().__init__(text, style)
        self._min_wsf = min_word_space_factor
        self._min_csf = min_char_space_factor
        self._min_hs = min_horizontal_scale
        self._max_wsf = max_word_space_factor
        self._max_csf = max_char_space_factor
        self._max_hs = max_horizontal_scale

    def _make_lines(self, line_width: float) -> list[Line]:
        if not self.text:
            return [Text("", style=self.style)]

        assert self._min_csf <= self._max_csf
        assert self._min_wsf <= self._max_wsf
        assert self._min_hs <= self._max_hs

        dense_style = TextStyle(
            font=self.style.font,
            font_size=self.style.font_size,
            line_height_factor=self.style.line_height_factor,
            char_space=self.style.font_size * (self._min_csf - 1.0),
            word_space=self.style.font_size * (self._min_wsf - 1.0),
            horizontal_scale=self._min_hs)

        line_strs = _text_breaker(self.text, line_width, dense_style)

        result: list[Line] = []
        for s in line_strs[:-1]:
            result.append(StretchText(s, self.style,
                                      min_word_space_factor=self._min_wsf,
                                      min_char_space_factor=self._min_csf,
                                      min_horizontal_scale=self._min_hs,
                                      max_word_space_factor=self._max_wsf,
                                      max_char_space_factor=self._max_csf,
                                      max_horizontal_scale=self._max_hs))

        last = line_strs[-1]
        result.append(StretchText(last, self.style,
                                   min_word_space_factor=self._min_wsf,
                                   min_char_space_factor=self._min_csf,
                                   min_horizontal_scale=self._min_hs,
                                   max_word_space_factor=1.0,
                                   max_char_space_factor=1.0,
                                   max_horizontal_scale=100.0))
        return result
