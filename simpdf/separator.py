from reportlab.pdfgen.canvas import *

from simpdf.line import Line
from simpdf.rgb import RGB, ColorType

__all__ = ["Separator"]


class Separator(Line):
    """Represents a horizontal separator line."""

    """Total spacing around the separator."""
    line_spacing: float

    """Thickness of the separator line."""
    thickness: float

    """Color of the separator."""
    color: RGB

    def __init__(self, line_spacing: float = 10.0, thickness: float = 1.0, color: ColorType = 0.0):
        """Initializes a Separator with specific spacing and thickness."""
        assert line_spacing >= 0.0
        assert thickness >= 0.0
        self.line_spacing = line_spacing
        self.thickness = thickness
        self.color = RGB(color)

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        """Draws the separator line on the given canvas."""
        canvas.saveState()
        canvas.setLineWidth(self.thickness)
        canvas.setStrokeColor(self.color)
        canvas.line(start, baseline, end, baseline)
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
