from typing import Literal

from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line
from simpdf.text_style import TextStyle
from simpdf.rgb import ColorType

__all__ = ["RichTextStyle", "RichText"]


class _RichContent:
    """Parsed rich-text content with mixed bold/italic styling and inline links.

    Recognized tags: <b>...</b>, <i>...</i>, <a href="URL">...</a>.

    Segment mode bits: bit 0 = italic, bit 1 = bold.
    So 0 = normal, 1 = italic, 2 = bold, 3 = bold + italic.
    """

    """the raw string content including all tags"""
    # e.g. 'Hello <b>User</b>, please <i>look</i> <a href="http://example.com">here</a>!'
    rich_text: str

    """the parsed segments as structured data as (start, end, mode)"""
    # e.g. [...] todo
    segments: list[tuple[int, int, int]]

    """maps each raw-string index to the content position with tags removed"""
    # e.g. [0, 1, 2, 3, 4, 5, 6, 6, 6, 6, 7, 8, 9, 10, 10, 10, 10, 10, 11, ...]
    positions: list[int]

    """the links as (start, end, url) referencing character positions of content without tags"""
    # e.g. [(19, 23, "http://example.com")]
    links: list[tuple[int, int, str]]

    """the tag-stripped flat text (concatenated segment text)"""
    text: str

    def __init__(self, rich_text: str | None):
        self.rich_text = rich_text or ""
        self.segments = []
        self.positions = []
        self.links = []
        self.text = ""

        if not self.rich_text:
            return

        buffer: list[str] = []
        link_start: int | None = None
        link_url: str | None = None

        code_link: Literal["a"] = "a"
        code_bold: Literal["b"] = "b"
        code_italic: Literal["i"] = "i"
        stack: list[Literal["a", "b", "i"]] = []

        def flush() -> None:
            if buffer:
                mode = (1 if code_italic in stack else 0) | (2 if code_bold in stack else 0)
                self.segments.append((mode, "".join(buffer)))
                buffer.clear()

        p, i, n = 0, 0, len(self.rich_text)
        while i < n:
            if self.rich_text.startswith("<b>", i):
                assert code_bold not in stack
                flush()
                stack.append(code_bold)
                self.positions.extend([p] * 3)
                i += 3
            elif self.rich_text.startswith("</b>", i):
                assert stack and stack[-1] == code_bold
                flush()
                stack.pop()
                self.positions.extend([p] * 4)
                i += 4
            elif self.rich_text.startswith("<i>", i):
                assert code_italic not in stack
                flush()
                stack.append(code_italic)
                self.positions.extend([p] * 3)
                i += 3
            elif self.rich_text.startswith("</i>", i):
                assert stack and stack[-1] == code_italic
                flush()
                stack.pop()
                self.positions.extend([p] * 4)
                i += 4
            elif self.rich_text.startswith('<a href="', i):
                assert code_link not in stack
                url_start = i + 9
                url_end = self.rich_text.index('"', url_start)
                assert self.rich_text.startswith('">', url_end), \
                    f"expected '\">' after URL at position {url_end}"
                tag_end = url_end + 2
                stack.append(code_link)
                link_url = self.rich_text[url_start:url_end]
                link_start = p
                self.positions.extend([p] * (tag_end - i))
                i = tag_end
            elif self.rich_text.startswith("</a>", i):
                assert stack and stack[-1] == code_link
                assert link_start is not None and link_url is not None
                stack.pop()
                self.links.append((link_start, p, link_url))
                link_start = None
                link_url = None
                self.positions.extend([p] * 4)
                i += 4
            else:
                buffer.append(self.rich_text[i])
                self.positions.append(p)
                p += 1
                i += 1
        flush()
        assert not stack, f"unclosed tags: {stack}"
        self.text = "".join(t for _, t in self.segments)

    @property
    def is_empty(self) -> bool:
        return not self.segments


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
        return self.style, self.style_italic, self.style_bold, self.style_bold_italic

    def get_style(self, mode: int) -> TextStyle:
        return self.styles[mode]

    def text_width(self, rich_text: str | None | _RichContent) -> float:
        if not isinstance(rich_text, _RichContent):
            rich_text = _RichContent(rich_text)
        return sum(self.get_style(mode).text_width(text) for mode, text in rich_text.segments)

    def draw_text(self, canvas: Canvas, x: float, y: float,
                  rich_text: str | None | _RichContent) -> None:
        """Draws rich text onto the canvas, switching fonts per segment."""
        if not isinstance(rich_text, _RichContent):
            rich_text = _RichContent(rich_text)

        for mode, text in rich_text.segments:
            style = self.get_style(mode)
            style.draw_text(canvas, x, y, text)
            x += style.text_width(text)


class RichText(Line):
    """Text line that renders mixed bold/italic content using a RichTextStyle."""

    content_left: _RichContent
    content_center: _RichContent
    content_right: _RichContent
    style: RichTextStyle

    def __init__(
            self,
            content_left: str | None = None,
            content_center: str | None = None,
            content_right: str | None = None,
            style: RichTextStyle | None = None):
        self.content_left = _RichContent(content_left)
        self.content_center = _RichContent(content_center)
        self.content_right = _RichContent(content_right)
        self.style = style or RichTextStyle()

    def _char_pos(self, index: int, rich_text: _RichContent, segment_skip: int = 0) -> tuple[float, int, float]:
        pre_segments_width: float = 0.0
        for i, (beg, end, mode) in enumerate(rich_text.segments[segment_skip:], start=segment_skip):
            if beg <= index < end:
                return pre_segments_width, i, self.style.get_style(mode).text_width(rich_text.text[beg:index])
            pre_segments_width += self.style.get_style(mode).text_width(rich_text.text[beg:end])
        raise ValueError(f"Index {index} is out of range for rich text \"{rich_text.text}\"")

    def _draw(self, canvas: Canvas, baseline: float, start: float, rich_text: _RichContent):
        self.style.draw_text(canvas, start, baseline, rich_text)

        for link_start, link_end, link_url in rich_text.links:
            w0, i, w1 = self._char_pos(link_start, rich_text)
            w2, _, w3 = self._char_pos(link_end, rich_text, i)

            margin = 0.5 * self._line_spacing
            x0 = start + w0 + w1 - margin
            x1 = start + w0 + w2 + w3 + margin
            y0 = baseline + self.descent - margin
            y1 = baseline + self.ascent + margin
            canvas.linkURL(link_url, (x0, y0, x1, y1))

            print(f">>> linking {rich_text.text[link_start:link_end]} to {link_url}")

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        """Draws the text line on the canvas within the given horizontal boundaries."""
        max_text_width = end - start
        text_width_left = 0.0
        text_width_center = 0.0
        text_width_right = 0.0

        if self.content_left:
            text_width_left = self.style.text_width(self.content_left)
            assert text_width_left <= max_text_width, f"{text_width_left} > {max_text_width}"
            self._draw(canvas, baseline, start, self.content_left)

        if self.content_center:
            text_width_center = self.style.text_width(self.content_center)
            assert text_width_center <= max_text_width, f"{text_width_center} > {max_text_width}"
            start_center = start + (end - start) / 2 - text_width_center / 2
            self._draw(canvas, baseline, start_center, self.content_center)

        if self.content_right:
            text_width_right = self.style.text_width(self.content_right)
            assert text_width_right <= max_text_width, f"{text_width_right} > {max_text_width}"
            self._draw(canvas, baseline, end - text_width_right, self.content_right)

        if self.content_left and self.content_center:
            assert text_width_left + 0.5 * text_width_center <= 0.5 * max_text_width

        if self.content_center and self.content_right:
            assert text_width_right + 0.5 * text_width_center <= 0.5 * max_text_width

        if self.content_left and self.content_right:
            assert text_width_left + text_width_right <= max_text_width

    def _unique_styles(self) -> list[TextStyle]:
        return list({self.style.get_style(mode) for beg, end, mode in self.content_left.segments})

    @property
    def _line_spacing(self) -> float:
        return max(style.line_spacing for style in self._unique_styles())

    @property
    def space_top(self) -> float:
        """Gets the top spacing for the line."""
        return 0.5 * self._line_spacing

    @property
    def space_bottom(self) -> float:
        """Gets the bottom spacing for the line."""
        return 0.5 * self._line_spacing

    @property
    def ascent(self) -> float:
        """Gets the ascent of the line."""
        return max(style.font_ascent for style in self._unique_styles())

    @property
    def descent(self) -> float:
        """Gets the descent of the line."""
        return min(style.font_ascent for style in self._unique_styles())

    @property
    def line_height_upper(self) -> float:
        """Gets the upper portion of the line height (ascent plus top spacing)."""
        return self.ascent + self.space_top

    @property
    def line_height_lower(self) -> float:
        """Gets the lower portion of the line height (descent plus bottom spacing)."""
        return -self.descent + self.space_bottom

    @property
    def line_height(self) -> float:
        """Gets the total line height."""
        return self.line_height_lower + self.line_height_upper

    def __repr__(self):
        return ""
