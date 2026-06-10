from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line

__all__ = ["PageFlush"]


class PageFlush(Line):
    """A sentinel line that forces a page break when the PDF layout engine encounters it."""

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float) -> None:
        """Does nothing; PageFlush is a layout sentinel, not a drawable element."""
        return None

    @property
    def space_top(self) -> float:
        """Returns an effectively infinite top spacing to trigger a page break."""
        return 1.0e9

    @property
    def space_bottom(self) -> float:
        """Returns zero bottom spacing."""
        return 0.0

    @property
    def ascent(self) -> float:
        """Returns zero ascent."""
        return 0.0

    @property
    def descent(self) -> float:
        """Returns zero descent."""
        return 0.0

    @property
    def line_height_upper(self) -> float:
        """Returns zero upper line height."""
        return 0.0

    @property
    def line_height_lower(self) -> float:
        """Returns zero lower line height."""
        return 0.0

    @property
    def line_height(self) -> float:
        """Returns an effectively infinite line height to force a page break."""
        return 1.0e9
