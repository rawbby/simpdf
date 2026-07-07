from functools import cached_property
from typing import Callable

from reportlab.pdfgen.canvas import Canvas

from simpdf.indentation import Indentation
from simpdf.line import Line
from simpdf.text_style import TextStyle

__all__ = ["BulletStyle", "BulletPoints"]


class _GlyphLine(Line):
    """Draws a glyph at a fixed x offset, then delegates to an indented inner line."""

    def __init__(self, line: Line, content_indent: float, glyph_x: float, glyph: str, style: TextStyle):
        self._inner = Indentation(line, content_indent)
        self._glyph_x = glyph_x
        self._glyph = glyph
        self._style = style

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        self._style.draw_text(canvas, start + self._glyph_x, baseline, self._glyph)
        self._inner.draw(canvas, baseline, start, end)

    @property
    def space_top(self) -> float:
        return self._inner.space_top

    @property
    def space_bottom(self) -> float:
        return self._inner.space_bottom

    @property
    def ascent(self) -> float:
        return self._inner.ascent

    @property
    def descent(self) -> float:
        return self._inner.descent

    @property
    def line_height_upper(self) -> float:
        return self._inner.line_height_upper

    @property
    def line_height_lower(self) -> float:
        return self._inner.line_height_lower

    @property
    def line_height(self) -> float:
        return self._inner.line_height


class BulletStyle:
    """Defines the glyph, its text style, column width, and margins for one bullet level.

    The *style* attribute controls both the rendered appearance of the glyph and the
    width computation used to size the glyph column.  Set it to match the desired
    bullet appearance; it does not affect how the caller-supplied ``Line`` objects
    are rendered.
    """

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
        """Returns the glyph column width for indices 0..max_index.

        When *width* is set it is returned directly (and each glyph is validated
        against any margin constraints).  Otherwise the width is computed from
        the rendered glyph text.  Returns 0.0 when *max_index* < 0 (no items at
        this level).
        """
        if max_index < 0:
            return 0.0
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
    """A flat list of (level, Line) bullet points that unpacks into indented lines.

    Each entry is a ``(level, line)`` pair where *level* is a zero-based nesting
    depth and *line* is any ``Line`` instance (``Text``, ``RichText``, etc.).
    The glyph defined in ``BulletStyle`` is drawn automatically at the left edge of
    each bullet's indent column; callers should *not* embed the glyph in the supplied
    line.  Pass a ``styles`` mapping to customise glyph, margins, or width per level.
    """

    default_style: BulletStyle = BulletStyle()

    points: list[tuple[int, Line]]
    styles: dict[int, BulletStyle]

    def __init__(
            self,
            points: list[tuple[int, Line]],
            styles: dict[int, BulletStyle] | None = None):
        assert points, "BulletPoints requires at least one point"
        self.points = points
        self.styles = styles or {}

    def _style(self, level: int) -> BulletStyle:
        return self.styles.get(level, self.default_style)

    @cached_property
    def _unpacked(self) -> list[Line]:
        result = []
        level_indices: dict[int, int] = {}
        for level, line in self.points:
            style = self._style(level)

            indent = 0.0
            for l in range(level):
                ps = self._style(l)
                pl = sum(1 for li, _ in self.points if li == l)
                indent += (ps.left_margin or 0.0) + ps.max_width(pl - 1) + (ps.right_margin or 0.0)

            level_index = level_indices.get(level, 0)
            level_indices[level] = level_index + 1

            pl = sum(1 for li, _ in self.points if li == level)
            glyph_x = indent + (style.left_margin or 0.0)
            content_indent = glyph_x + style.max_width(pl - 1) + (style.right_margin or 0.0)
            glyph_str = style._glyph_str(level_index)

            result.append(_GlyphLine(line, content_indent, glyph_x, glyph_str, style.style))
        return result

    def unpack(self) -> list[Line]:
        """Returns one indented Line per bullet point."""
        return list(self._unpacked)

    # --- Line interface, delegating to the unpacked lines ---

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        lines = self._unpacked
        lines[0].draw(canvas, baseline, start, end)
        for i, line in enumerate(lines[1:], 1):
            baseline -= lines[i - 1].line_height_lower + line.line_height_upper
            line.draw(canvas, baseline, start, end)

    @property
    def space_top(self) -> float:
        return self._unpacked[0].space_top

    @property
    def space_bottom(self) -> float:
        return self._unpacked[-1].space_bottom

    @property
    def ascent(self) -> float:
        return self._unpacked[0].ascent

    @property
    def descent(self) -> float:
        return self.ascent + self.space_top + self.space_bottom - self.line_height

    @property
    def line_height_upper(self) -> float:
        return self._unpacked[0].line_height_upper

    @property
    def line_height_lower(self) -> float:
        return self.line_height - self.line_height_upper

    @property
    def line_height(self) -> float:
        return sum(line.line_height for line in self._unpacked)
