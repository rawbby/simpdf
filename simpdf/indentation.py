from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line

__all__ = ["Indentation"]


class Indentation(Line):
    """Shifts the start position of an inner line by a fixed indent.

    ``end`` is unchanged, so the available width for the inner line shrinks
    by ``indent``.  ``unpack()`` forwards the reduced width to the inner
    line and wraps each result in its own ``Indentation``, so a
    ``BreakText`` inner line word-wraps correctly at the top level.
    """

    indent: float
    line: Line

    def __init__(self, line: Line, indent: float):
        self.line = line
        self.indent = indent

    def unpack(self, line_width: float) -> list["Line"]:
        return [Indentation(l, self.indent) for l in self.line.unpack(line_width - self.indent)]

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        self.line.draw(canvas, baseline, start + self.indent, end)

    @property
    def space_top(self) -> float:
        return self.line.space_top

    @property
    def space_bottom(self) -> float:
        return self.line.space_bottom

    @property
    def ascent(self) -> float:
        return self.line.ascent

    @property
    def descent(self) -> float:
        return self.line.descent

    @property
    def line_height_upper(self) -> float:
        return self.line.line_height_upper

    @property
    def line_height_lower(self) -> float:
        return self.line.line_height_lower

    @property
    def line_height(self) -> float:
        return self.line.line_height
