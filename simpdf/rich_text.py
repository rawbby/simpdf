from typing import Literal

from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line
from simpdf.rgb import ColorType
from simpdf.text_style import TextStyle

__all__ = ["RichContent", "RichTextStyle", "RichText"]


class RichContent:
    """Parsed rich-text content with mixed bold/italic styling and inline links.

    Recognized tags: <b>...</b>, <i>...</i>, <a href="URL">...</a>.

    Segment mode bits: bit 0 = italic, bit 1 = bold.
    So 0 = normal, 1 = italic, 2 = bold, 3 = bold + italic.
    """

    """the parsed segments as (start, end, mode) char positions into `text`"""
    segments: list[tuple[int, int, int]]

    """the links as (start, end, url) referencing char positions in `text`"""
    links: list[tuple[int, int, str]]

    """the tag-stripped flat text"""
    text: str

    def __init__(self, rich_text: str | None):
        self.segments = []
        self.links = []
        self.text = ""

        if not rich_text:
            return

        text_buf: list[str] = []
        seg_buf: list[str] = []
        link_start: int = 0
        link_url: str = ""
        stack: list[Literal["a", "b", "i"]] = []

        def flush():
            if seg_buf:
                mode = (1 if "i" in stack else 0) | (2 if "b" in stack else 0)
                beg = len(text_buf)
                text_buf.extend(seg_buf)
                self.segments.append((beg, len(text_buf), mode))
                seg_buf.clear()

        p, i, n = 0, 0, len(rich_text)
        while i < n:
            if rich_text.startswith("<b>", i):
                assert "b" not in stack
                flush()
                stack.append("b")
                i += 3
            elif rich_text.startswith("</b>", i):
                assert stack and stack[-1] == "b"
                flush()
                stack.pop()
                i += 4
            elif rich_text.startswith("<i>", i):
                assert "i" not in stack
                flush()
                stack.append("i")
                i += 3
            elif rich_text.startswith("</i>", i):
                assert stack and stack[-1] == "i"
                flush()
                stack.pop()
                i += 4
            elif rich_text.startswith('<a href="', i):
                assert "a" not in stack
                url_start = i + 9
                url_end = rich_text.index('"', url_start)
                assert rich_text[url_end + 1] == '>'
                stack.append("a")
                link_url = rich_text[url_start:url_end]
                link_start = p
                i = url_end + 2
            elif rich_text.startswith("</a>", i):
                assert stack and stack[-1] == "a"
                stack.pop()
                self.links.append((link_start, p, link_url))
                i += 4
            else:
                seg_buf.append(rich_text[i])
                p += 1
                i += 1
        flush()
        assert not stack
        self.text = "".join(text_buf)

    def __bool__(self) -> bool:
        return bool(self.segments)

    @property
    def is_empty(self) -> bool:
        return not self.segments

    def slice(self, beg: int, end: int) -> "RichContent":
        """Return a new object containing only the characters from *slice_beg* to *slice_end*."""

        # noinspection PyTypeChecker
        result = RichContent.__new__(RichContent)
        result.text = self.text[beg:end]
        result.segments = []
        result.links = []

        for seg_beg, seg_end, mode in self.segments:
            seg_beg = max(seg_beg, beg)
            seg_end = min(seg_end, end)
            if seg_beg < seg_end:
                result.segments.append((seg_beg - beg, seg_end - beg, mode))

        for lnk_beg, lnk_end, url in self.links:
            lnk_beg = max(lnk_beg, beg)
            lnk_end = min(lnk_end, end)
            if lnk_beg < lnk_end:
                result.links.append((lnk_beg - beg, lnk_end - beg, url))

        return result


class RichTextStyle:
    """TextStyle that carries all four bold/italic font variants."""

    style: TextStyle
    style_italic: TextStyle
    style_bold: TextStyle
    style_bold_italic: TextStyle

    def __init__(
            self,
            font: str | None = None,
            font_italic: str | None = None,
            font_bold: str | None = None,
            font_bold_italic: str | None = None,
            font_size: float | None = None,
            font_ascent: float | None = None,
            font_descent: float | None = None,
            font_height: float | None = None,
            line_height_factor: float | None = None,
            line_height: float | None = None,
            line_spacing: float | None = None,
            char_space_factor: float | None = None,
            word_space_factor: float | None = None,
            horizontal_scale: float | None = None,
            char_space: float | None = None,
            word_space: float | None = None,
            color: ColorType | None = None):
        kwargs = {
            "font_size": font_size,
            "font_ascent": font_ascent,
            "font_descent": font_descent,
            "font_height": font_height,
            "line_height_factor": line_height_factor,
            "line_height": line_height,
            "line_spacing": line_spacing,
            "char_space_factor": char_space_factor,
            "word_space_factor": word_space_factor,
            "horizontal_scale": horizontal_scale,
            "char_space": char_space,
            "word_space": word_space,
            "color": color
        }
        self.style = TextStyle(font=font, **kwargs)
        self.style_italic = TextStyle(font=font_italic, **kwargs) if font_italic else self.style
        self.style_bold = TextStyle(font=font_bold, **kwargs) if font_bold else self.style
        self.style_bold_italic = TextStyle(font=font_bold_italic, **kwargs) if font_bold_italic else self.style

    @property
    def styles(self) -> tuple[TextStyle, TextStyle, TextStyle, TextStyle]:
        """Returns the four style variants as (normal, italic, bold, bold-italic)."""
        return self.style, self.style_italic, self.style_bold, self.style_bold_italic

    def get_style(self, mode: int) -> TextStyle:
        """Returns the TextStyle corresponding to the given mode bitmask (0=normal, 1=italic, 2=bold, 3=bold-italic)."""
        return self.styles[mode]

    def text_width(self, rich_text: str | None | RichContent) -> float:
        """Calculates the total rendered width of the given rich text string."""
        if not isinstance(rich_text, RichContent):
            rich_text = RichContent(rich_text)

        return sum(self.get_style(mode).text_width(rich_text.text[beg:end])
                   for beg, end, mode in rich_text.segments)

    def draw_text(self, canvas: Canvas, x: float, y: float, rich_text: str | None | RichContent):
        """Draws rich text onto the canvas, switching fonts per segment."""
        if not isinstance(rich_text, RichContent):
            rich_text = RichContent(rich_text)

        for beg, end, mode in rich_text.segments:
            text = rich_text.text[beg:end]
            style = self.get_style(mode)
            style.draw_text(canvas, x, y, text)
            x += style.text_width(text)


class RichText(Line):
    """Text line that renders mixed bold/italic content using a RichTextStyle."""

    content_left: RichContent
    content_center: RichContent
    content_right: RichContent
    style: RichTextStyle

    def __init__(
            self,
            content_left: str | None = None,
            content_center: str | None = None,
            content_right: str | None = None,
            style: RichTextStyle | None = None):
        self.content_left = RichContent(content_left)
        self.content_center = RichContent(content_center)
        self.content_right = RichContent(content_right)
        self.style = style or RichTextStyle()

    def draw(self, canvas: Canvas, baseline: float, beg: float, end: float):
        def pos(idx: int, rich_text: RichContent, j: int) -> tuple[float, int, float]:
            width: float = 0.0

            for j, (seg_beg, seg_end, seg_mode) in enumerate(rich_text.segments[j:], start=j):
                if seg_beg <= idx < seg_end:
                    return width, j, self.style.get_style(seg_mode).text_width(rich_text.text[seg_beg:idx])
                width += self.style.get_style(seg_mode).text_width(rich_text.text[seg_beg:seg_end])

            if idx == len(rich_text.text):
                return width, idx, 0.0

            raise ValueError(f"Index {idx} is out of range for rich text \"{rich_text.text}\"")

        def drw(x: float, rich_text: RichContent):
            self.style.draw_text(canvas, x, baseline, rich_text)

            for lnk_beg, lnk_end, lnk_url in rich_text.links:
                w0, i, w1 = pos(lnk_beg, rich_text, 0)
                w2, _, w3 = pos(lnk_end, rich_text, i)

                margin = 0.5 * self._line_spacing
                x0 = x + w0 + w1 - margin
                x1 = x + w0 + w2 + w3 + margin
                y0 = baseline + self.descent - margin
                y1 = baseline + self.ascent + margin
                canvas.linkURL(lnk_url, (x0, y0, x1, y1))

        max_text_width = end - beg

        if self.content_left:
            text_width_left = self.style.text_width(self.content_left)
            assert text_width_left <= max_text_width
            drw(beg, self.content_left)

        if self.content_center:
            text_width_center = self.style.text_width(self.content_center)
            assert text_width_center <= max_text_width
            start_center = beg + max_text_width / 2 - text_width_center / 2
            drw(start_center, self.content_center)

        if self.content_right:
            text_width_right = self.style.text_width(self.content_right)
            assert text_width_right <= max_text_width
            drw(end - text_width_right, self.content_right)

        if self.content_left and self.content_center:
            # noinspection PyUnboundLocalVariable
            assert text_width_left + 0.5 * text_width_center <= 0.5 * max_text_width

        if self.content_center and self.content_right:
            # noinspection PyUnboundLocalVariable
            assert text_width_right + 0.5 * text_width_center <= 0.5 * max_text_width

        if self.content_left and self.content_right:
            # noinspection PyUnboundLocalVariable
            assert text_width_left + text_width_right <= max_text_width

    def _unique_styles(self) -> list[TextStyle]:
        all_segments = self.content_left.segments + self.content_center.segments + self.content_right.segments
        all_styles = {self.style.get_style(mode) for _, _, mode in all_segments}
        return list(all_styles) if all_styles else [self.style.style]

    @property
    def _line_spacing(self) -> float:
        return max(style.line_spacing for style in self._unique_styles())

    @property
    def space_top(self) -> float:
        return 0.5 * self._line_spacing

    @property
    def space_bottom(self) -> float:
        return 0.5 * self._line_spacing

    @property
    def ascent(self) -> float:
        return max(style.ascent for style in self._unique_styles())

    @property
    def descent(self) -> float:
        return min(style.descent for style in self._unique_styles())

    @property
    def line_height_upper(self) -> float:
        return self.space_top + self.ascent

    @property
    def line_height_lower(self) -> float:
        return self.space_bottom - self.descent

    @property
    def line_height(self) -> float:
        return self.line_height_lower + self.line_height_upper
