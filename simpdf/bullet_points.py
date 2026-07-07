from typing import Callable

from reportlab.pdfgen.canvas import Canvas

from simpdf.indentation import Indentation
from simpdf.line import Line
from simpdf.text_style import TextStyle

__all__ = ["BulletStyle", "BulletPoints"]


class BulletStyle:
    """Defines the glyph column width and margins for one bullet level."""

    default_style: TextStyle = TextStyle()

    glyph: str | Callable[[int], str]
    style: TextStyle
    left_margin: float | None
    right_margin: float | None
    width: float | None

    def __init__(
            self,
            glyph: str | Callable[[int], str] = "•",
            style: TextStyle | None = None,
            left_margin: float | None = None,
            right_margin: float | None = None,
            width: float | None = None):
        assert not (width is not None and left_margin is not None and right_margin is not None), \
            "width, left_margin, and right_margin cannot all be specified simultaneously"
        self.glyph = glyph
        self.style = style or self.default_style
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.width = width

    def _glyph_str(self, index: int) -> str:
        return self.glyph if isinstance(self.glyph, str) else self.glyph(index)

    def max_width(self, max_index: int) -> float:
        """Returns the glyph column width, validating per-glyph constraints when width is fixed."""
        if self.width is not None:
            for i in range(max_index + 1):
                gw = self.style.text_width(self._glyph_str(i))
                if self.left_margin is not None:
                    assert gw + self.left_margin <= self.width, \
                        f"glyph at index {i} with left_margin exceeds width"
                if self.right_margin is not None:
                    assert gw + self.right_margin <= self.width, \
                        f"glyph at index {i} with right_margin exceeds width"
            return self.width
        if isinstance(self.glyph, str):
            return self.style.text_width(self.glyph)
        return max(self.style.text_width(self._glyph_str(i)) for i in range(max_index + 1))


class BulletPoints(Line):
    """A flat list of (level, Line) bullet points that unpacks into indented lines."""

    default_style: BulletStyle = BulletStyle()

    points: list[tuple[int, Line]]
    styles: dict[int, BulletStyle]

    def __init__(
            self,
            points: list[tuple[int, Line]],
            styles: dict[int, BulletStyle] | None = None):
        self.points = points
        self.styles = styles or {}

    def _style(self, level: int) -> BulletStyle:
        return self.styles.get(level, self.default_style)

    def unpack(self) -> list[Line]:
        """Returns one indented line per bullet point."""
        result = []
        for index, (level, line) in enumerate(self.points):
            style = self._style(level)
            level_count = sum(1 for l, _ in self.points if l == level)

            indent = 0.0
            for l in range(level):
                ps = self._style(l)
                pl = sum(1 for li, _ in self.points if li == l)
                indent += (ps.left_margin or 0.0) + ps.max_width(pl - 1) + (ps.right_margin or 0.0)

            result.append(Indentation(line, indent + (style.left_margin or 0.0)))
        return result

    # --- Line interface, delegating to the unpacked lines ---

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        lines = self.unpack()
        lines[0].draw(canvas, baseline, start, end)
        for i, line in enumerate(lines[1:], 1):
            baseline -= lines[i - 1].line_height_lower + line.line_height_upper
            line.draw(canvas, baseline, start, end)

    @property
    def space_top(self) -> float:
        return self.unpack()[0].space_top

    @property
    def space_bottom(self) -> float:
        return self.unpack()[-1].space_bottom

    @property
    def ascent(self) -> float:
        return self.unpack()[0].ascent

    @property
    def descent(self) -> float:
        return self.ascent + self.space_top + self.space_bottom - self.line_height

    @property
    def line_height_upper(self) -> float:
        return self.unpack()[0].line_height_upper

    @property
    def line_height_lower(self) -> float:
        return self.line_height - self.line_height_upper

    @property
    def line_height(self) -> float:
        return sum(line.line_height for line in self.unpack())
