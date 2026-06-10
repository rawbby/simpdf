from reportlab.pdfgen.canvas import *

from simpdf.line import Line

__all__ = ["ContentGroup"]


class ContentGroup(Line):
    """A group of lines that is laid out as a single line and therefore always stays on the same page."""

    """The wrapped lines, drawn one after another."""
    lines: list[Line]

    def __init__(self, lines: list[Line]):
        assert lines
        self.lines = lines

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        self.lines[0].draw(canvas, baseline, start, end)
        for i, line in enumerate(self.lines[1:], 1):
            baseline -= self.lines[i - 1].line_height_lower + line.line_height_upper
            line.draw(canvas, baseline, start, end)

    @property
    def space_top(self) -> float:
        return self.lines[0].space_top

    @property
    def space_bottom(self) -> float:
        return self.lines[-1].space_bottom

    @property
    def ascent(self) -> float:
        return self.lines[0].ascent

    @property
    def descent(self) -> float:
        return self.ascent + self.space_top + self.space_bottom - self.line_height

    @property
    def line_height_upper(self) -> float:
        return self.lines[0].line_height_upper

    @property
    def line_height_lower(self) -> float:
        return self.line_height - self.line_height_upper

    @property
    def line_height(self) -> float:
        return sum(line.line_height for line in self.lines)
