from functools import cached_property

from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line
from simpdf.stretch_text import stretch_text
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
    """Breaks a text string into word-wrapped lines at a fixed width."""

    text: str | None
    line_width: float
    style: TextStyle

    def __init__(self, text: str | None, line_width: float, style: TextStyle | None = None):
        self.text = text
        self.line_width = line_width
        self.style = style or TextStyle()

    @cached_property
    def _lines(self) -> list[Text]:
        return [Text(s, style=self.style) for s in _text_breaker(self.text, self.line_width, self.style)]

    def unpack(self) -> list[Line]:
        return list(self._lines)

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        lines = self._lines
        lines[0].draw(canvas, baseline, start, end)
        for i, line in enumerate(lines[1:], 1):
            baseline -= lines[i - 1].line_height_lower + line.line_height_upper
            line.draw(canvas, baseline, start, end)

    @property
    def space_top(self) -> float:
        return self._lines[0].space_top

    @property
    def space_bottom(self) -> float:
        return self._lines[-1].space_bottom

    @property
    def ascent(self) -> float:
        return self._lines[0].ascent

    @property
    def descent(self) -> float:
        return self.ascent + self.space_top + self.space_bottom - self.line_height

    @property
    def line_height_upper(self) -> float:
        return self._lines[0].line_height_upper

    @property
    def line_height_lower(self) -> float:
        return self.line_height - self.line_height_upper

    @property
    def line_height(self) -> float:
        return sum(line.line_height for line in self._lines)


class BreakBlockText(BreakText):
    """Breaks a text string into fully justified lines at a fixed width."""

    def __init__(
            self,
            text: str | None,
            line_width: float,
            style: TextStyle | None = None,
            min_word_space_factor: float = 0.95,
            min_char_space_factor: float = 0.995,
            min_horizontal_scale: float = 99.0,
            max_word_space_factor: float = 1.1,
            max_char_space_factor: float = 1.01,
            max_horizontal_scale: float = 102.0):
        super().__init__(text, line_width, style)
        self._min_wsf = min_word_space_factor
        self._min_csf = min_char_space_factor
        self._min_hs = min_horizontal_scale
        self._max_wsf = max_word_space_factor
        self._max_csf = max_char_space_factor
        self._max_hs = max_horizontal_scale

    @cached_property
    def _lines(self) -> list[Text]:
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

        target_width = self.line_width - 1e-6
        line_strs = _text_breaker(self.text, self.line_width, dense_style)

        result = []
        for s in line_strs[:-1]:
            result.append(Text(content_left=s, style=stretch_text(
                s, target_width, self.style,
                min_word_space_factor=self._min_wsf,
                min_char_space_factor=self._min_csf,
                min_horizontal_scale=self._min_hs,
                max_word_space_factor=self._max_wsf,
                max_char_space_factor=self._max_csf,
                max_horizontal_scale=self._max_hs)))

        last = line_strs[-1]
        result.append(Text(content_left=last, style=stretch_text(
            last, target_width, self.style,
            min_word_space_factor=self._min_wsf,
            min_char_space_factor=self._min_csf,
            min_horizontal_scale=self._min_hs,
            max_word_space_factor=1.0,
            max_char_space_factor=1.0,
            max_horizontal_scale=100.0)))

        return result
