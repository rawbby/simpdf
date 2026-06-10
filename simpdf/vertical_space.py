from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line

__all__ = ["VerticalSpace"]


class VerticalSpace(Line):
    """A blank line that inserts a fixed amount of vertical space."""

    def __init__(self, space: float):
        self._space = space

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        return

    @property
    def space_top(self) -> float:
        return self._space

    @property
    def space_bottom(self) -> float:
        return 0.0

    @property
    def ascent(self) -> float:
        return 0.0

    @property
    def descent(self) -> float:
        return 0.0

    @property
    def line_height_upper(self) -> float:
        return self._space

    @property
    def line_height_lower(self) -> float:
        return 0.0

    @property
    def line_height(self) -> float:
        return self._space
