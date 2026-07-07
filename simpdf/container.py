from reportlab.pdfgen.canvas import *

from simpdf.line import Line

__all__ = ["Container"]


class Container(Line):
    """Keeps a group of lines together on the same page.

    ``unpack()`` returns ``[self]`` so the paginator treats the whole group
    as one indivisible unit.  Height properties sum the children's natural
    (infinite-width) dimensions.  ``draw()`` renders each child in sequence
    using those same natural metrics for baseline advancement.

    Children that produce multiple lines when word-wrapped (e.g. ``BreakText``)
    will be drawn as a single overflowing line inside a Container; place them
    at the top level instead if wrapping is needed.
    """

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
