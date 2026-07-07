from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line

__all__ = ["Indentation"]


class Indentation(Line):
    """Wraps a line and shifts its start position by a fixed indentation amount."""

    indent: float
    line: Line

    def __init__(self, line: Line, indent: float):
        self.line = line
        self.indent = indent

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
