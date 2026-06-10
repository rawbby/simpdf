from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line

__all__ = ["PageFlush"]


class PageFlush(Line):
    """A sentinel line that forces a page break when the PDF layout engine encounters it."""

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        return

    @property
    def space_top(self) -> float:
        return 1.0e9

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
        return 0.0

    @property
    def line_height_lower(self) -> float:
        return 0.0

    @property
    def line_height(self) -> float:
        return 1.0e9
