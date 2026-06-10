from reportlab.pdfgen.canvas import *

from simpdf.line import Line
from simpdf.rgb import RGB, ColorType

__all__ = ["Separator"]


class Separator(Line):
    """Represents a horizontal separator line."""

    """Length of the separator aligned to the left in (0.0, 1.0]."""
    length_left: float | None

    """Length of the separator aligned to the center in (0.0, 1.0]."""
    length_center: float | None

    """Length of the separator aligned to the right in (0.0, 1.0]."""
    length_right: float | None

    """Total spacing around the separator."""
    line_spacing: float

    """Thickness of the separator line."""
    thickness: float

    """Color of the separator."""
    color: RGB

    def __init__(
            self,
            line_spacing: float | None = None,
            thickness: float | None = None,
            color: ColorType | None = None,
            length_left: float | None = None,
            length_center: float | None = None,
            length_right: float | None = None):
        """Initializes a Separator with specific spacing, thickness, and segment lengths."""

        self.line_spacing = line_spacing or 10.0
        self.thickness = thickness or 1.0
        self.color = RGB(color or 0.0)
        self.length_left = length_left
        self.length_center = length_center
        self.length_right = length_right

        assert self.line_spacing >= 0.0
        assert self.thickness >= 0.0

        if None in [self.length_left, self.length_center, self.length_right]:
            self.length_center = 1.0

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        """Draws the separator line on the given canvas."""
        canvas.saveState()
        canvas.setLineWidth(self.thickness)
        canvas.setStrokeColor(self.color)
        pt_total = end - start

        if self.length_left:
            assert 0.0 < self.length_left <= 1.0
            pt_left = self.length_left * pt_total
            canvas.line(start, baseline, start + pt_left, baseline)

        if self.length_center:
            assert 0.0 < self.length_center <= 1.0
            pt_center = self.length_center * pt_total
            mid = start + 0.5 * pt_total
            canvas.line(mid - 0.5 * pt_center, baseline, mid + 0.5 * pt_center, baseline)

        if self.length_right:
            assert 0.0 < self.length_right <= 1.0
            pt_right = self.length_right * pt_total
            canvas.line(end - pt_right, baseline, end, baseline)

        if self.length_left is not None and self.length_center is not None:
            assert self.length_left + 0.5 * self.length_center <= 0.5

        if self.length_center is not None and self.length_right is not None:
            assert self.length_right + 0.5 * self.length_center <= 0.5

        if self.length_left is not None and self.length_right is not None:
            assert self.length_left + self.length_right <= 1.0

        canvas.restoreState()

    @property
    def space_top(self) -> float:
        """Gets the top spacing for the separator."""
        return 0.5 * self.line_spacing

    @property
    def space_bottom(self) -> float:
        """Gets the bottom spacing for the separator."""
        return 0.5 * self.line_spacing

    @property
    def ascent(self) -> float:
        """Gets the upward extent of the separator."""
        return 0.5 * self.thickness

    @property
    def descent(self) -> float:
        """Gets the downward extent of the separator."""
        return -0.5 * self.thickness

    @property
    def line_height_upper(self) -> float:
        """Gets the upper line height including spacing."""
        return 0.5 * (self.thickness + self.line_spacing)

    @property
    def line_height_lower(self) -> float:
        """Gets the lower line height including spacing."""
        return 0.5 * (self.thickness + self.line_spacing)

    @property
    def line_height(self) -> float:
        """Gets the total line height of the separator."""
        return self.thickness + self.line_spacing

    def __repr__(self):
        """Returns a string representation of the separator."""
        return "<separator>"
