from reportlab.pdfgen.canvas import *

from simpdf.line import Line
from simpdf.rgb import RGB, ColorType

__all__ = ["Separator"]


class Separator(Line):
    """Represents a horizontal separator line."""

    """Default spacing around the separator."""
    default_line_spacing: float = 0.0

    """Default thickness of the separator line."""
    default_thickness: float = 1.0

    """Default color of the separator."""
    default_color: RGB = RGB(0)

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
        self.line_spacing = line_spacing if line_spacing is not None else self.default_line_spacing
        self.thickness = thickness if thickness is not None else self.default_thickness
        self.color = RGB(color or 0.0) if color is not None else self.default_color
        self.length_left = length_left
        self.length_center = length_center
        self.length_right = length_right

        assert self.line_spacing >= 0.0
        assert self.thickness > 0.0

        if all(it is None for it in [self.length_left, self.length_center, self.length_right]):
            self.length_center = 1.0

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
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
        return 0.5 * self.line_spacing

    @property
    def space_bottom(self) -> float:
        return 0.5 * self.line_spacing

    @property
    def ascent(self) -> float:
        return 0.5 * self.thickness

    @property
    def descent(self) -> float:
        return -0.5 * self.thickness

    @property
    def line_height_upper(self) -> float:
        return 0.5 * (self.thickness + self.line_spacing)

    @property
    def line_height_lower(self) -> float:
        return 0.5 * (self.thickness + self.line_spacing)

    @property
    def line_height(self) -> float:
        return self.thickness + self.line_spacing
