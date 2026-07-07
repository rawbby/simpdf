from typing import Callable

from reportlab.pdfgen.canvas import Canvas

from simpdf.indentation import Indentation
from simpdf.line import Line
from simpdf.text_style import TextStyle

__all__ = ["BulletStyle", "BulletPoints"]


class _GlyphLine(Line):
    """One atomic content line with a glyph drawn to its left."""

    def __init__(self, line: Line, content_indent: float, glyph_x: float, glyph: str, style: TextStyle):
        self._line = line
        self._content_indent = content_indent
        self._glyph_x = glyph_x
        self._glyph = glyph
        self._style = style

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        self._style.draw_text(canvas, start + self._glyph_x, baseline, self._glyph)
        self._line.draw(canvas, baseline, start + self._content_indent, end)

    @property
    def space_top(self) -> float:
        return self._line.space_top

    @property
    def space_bottom(self) -> float:
        return self._line.space_bottom

    @property
    def ascent(self) -> float:
        return self._line.ascent

    @property
    def descent(self) -> float:
        return self._line.descent

    @property
    def line_height_upper(self) -> float:
        return self._line.line_height_upper

    @property
    def line_height_lower(self) -> float:
        return self._line.line_height_lower

    @property
    def line_height(self) -> float:
        return self._line.line_height


class BulletStyle:
    """Glyph, text style, column width, and margins for one bullet level."""

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
        """Returns the glyph column width for indices 1..max_index.

        When ``width`` is set it is returned directly after asserting that
        every glyph fits within it.  Otherwise the width is computed from
        the rendered glyph text.  Returns 0.0 when ``max_index`` < 1.
        """
        if max_index < 1:
            return 0.0
        if self.width is not None:
            for i in range(1, max_index + 1):
                gw = self.style.text_width(self._glyph_str(i))
                assert gw <= self.width, \
                    f"glyph '{self._glyph_str(i)}' at index {i} (width {gw:.3f}) exceeds column width {self.width:.3f}"
            return self.width
        if isinstance(self.glyph, str):
            return self.style.text_width(self.glyph)
        return max(self.style.text_width(self._glyph_str(i)) for i in range(1, max_index + 1))


class BulletPoints(Line):
    """A flat list of ``(level, Line)`` bullet points rendered with glyphs and indentation.

    ``default_style`` is the fallback ``BulletStyle`` used when ``styles``
    has no entry for a given level.

    ``styles`` can be:

    * ``None`` — every level uses ``default_style``
    * ``dict[int, BulletStyle]`` — lookup by level, ``default_style`` for
      missing keys
    * ``Callable[[int], BulletStyle]`` — called with the level index;
      includes ``defaultdict`` accessed via a lambda, or any custom mapping
      function

    ``unpack(line_width)`` expands each bullet's inner line via its own
    ``unpack()``, returning one ``_GlyphLine`` for the first inner line and
    plain ``Indentation`` wrappers for any continuation lines.  Height
    properties use each bullet's natural (infinite-width) single-line metrics.
    ``draw()`` renders every bullet as a single line with glyph.
    """

    default_style: BulletStyle = BulletStyle()

    points: list[tuple[int, Line]]
    styles: dict[int, BulletStyle] | Callable[[int], BulletStyle] | None

    def __init__(
            self,
            points: list[tuple[int, Line]],
            styles: dict[int, BulletStyle] | Callable[[int], BulletStyle] | None = None):
        assert points, "BulletPoints requires at least one point"
        self.points = points
        self.styles = styles

    def _iter_positions(self):
        """Yields (glyph_x, content_indent, glyph_str, text_style, line) per point."""
        def lookup(level: int) -> BulletStyle:
            if self.styles is None:
                return BulletPoints.default_style
            if callable(self.styles):
                return self.styles(level)
            return self.styles.get(level, BulletPoints.default_style)

        level_indices: dict[int, int] = {}
        for level, line in self.points:
            style = lookup(level)

            indent = 0.0
            for l in range(level):
                ps = lookup(l)
                pl = sum(1 for li, _ in self.points if li == l)
                indent += (ps.left_margin or 0.0) + ps.max_width(pl) + (ps.right_margin or 0.0)

            level_index = level_indices.get(level, 1)
            level_indices[level] = level_index + 1

            pl = sum(1 for li, _ in self.points if li == level)
            glyph_x = indent + (style.left_margin or 0.0)
            content_indent = glyph_x + style.max_width(pl) + (style.right_margin or 0.0)
            glyph_str = style._glyph_str(level_index)

            yield glyph_x, content_indent, glyph_str, style.style, line

    def unpack(self, line_width: float) -> list[Line]:
        result = []
        for glyph_x, content_indent, glyph_str, text_style, line in self._iter_positions():
            inner = list(line.unpack(line_width - content_indent))
            result.append(_GlyphLine(inner[0], content_indent, glyph_x, glyph_str, text_style))
            for extra in inner[1:]:
                result.append(Indentation(extra, content_indent))
        return result

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        prev_line = None
        for glyph_x, content_indent, glyph_str, text_style, line in self._iter_positions():
            if prev_line is not None:
                baseline -= prev_line.line_height_lower + line.line_height_upper
            text_style.draw_text(canvas, start + glyph_x, baseline, glyph_str)
            line.draw(canvas, baseline, start + content_indent, end)
            prev_line = line

    @property
    def space_top(self) -> float:
        return self.points[0][1].space_top

    @property
    def space_bottom(self) -> float:
        return self.points[-1][1].space_bottom

    @property
    def ascent(self) -> float:
        return self.points[0][1].ascent

    @property
    def descent(self) -> float:
        return self.ascent + self.space_top + self.space_bottom - self.line_height

    @property
    def line_height_upper(self) -> float:
        return self.points[0][1].line_height_upper

    @property
    def line_height_lower(self) -> float:
        return self.line_height - self.line_height_upper

    @property
    def line_height(self) -> float:
        return sum(line.line_height for _, line in self.points)
