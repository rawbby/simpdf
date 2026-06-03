from reportlab.pdfgen.canvas import *

from simpdf.line import Line
from simpdf.text_style import TextStyle

__all__ = ["Text"]


class Text(Line):
    """Represents a line of text divided into left, center, and right alignments."""

    """Default style for the text line."""
    default_style: TextStyle = TextStyle()

    """Text content aligned to the left."""
    content_left: str | None

    """Text content aligned to the center."""
    content_center: str | None

    """Text content aligned to the right."""
    content_right: str | None

    """Dictionary mapping text labels to URL links."""
    links: dict[str, str]

    """Style applied to the text line."""
    style: TextStyle

    def __init__(
            self,
            content_left: str | None = None,
            content_center: str | None = None,
            content_right: str | None = None,
            style: TextStyle | None = None,
            links: dict[str, str] | None = None):
        """Initializes a TextLine with optional content for different alignments and a style."""
        self.content_left = content_left
        self.content_center = content_center
        self.content_right = content_right
        self.links = links or dict()
        self.style = style or self.default_style

    @property
    def min_text_width(self):
        """Calculates the minimum width required to fit the text."""
        text_width_sum = self.style.text_width(self.content_left)
        text_width_sum += self.style.text_width(self.content_center)
        text_width_sum += self.style.text_width(self.content_right)
        return text_width_sum

    def add_link(self, label: str, url: str):
        """Adds a hyperlink to a specific text label in the line."""
        self.links[label] = url

    def _draw(self, canvas: Canvas, baseline: float, start: float, text: str):
        self.style.draw_text(canvas, start, baseline, text)
        # draw links
        for label, url in self.links.items():
            index = 0
            while True:
                index = text.find(label, index)
                if index == -1:
                    break
                margin = 0.5 * self.style.line_spacing
                x0 = start + self.style.text_width(text[:index]) - margin
                x1 = start + self.style.text_width(text[:index + len(label)]) + margin
                y0 = baseline + self.descent - margin
                y1 = baseline + self.ascent + margin
                canvas.linkURL(url, (x0, y0, x1, y1))
                print(f">>> linking {label} to {url}")
                index += len(label)

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

    @property
    def space_top(self) -> float:
        """Gets the top spacing for the line."""
        return 0.5 * self.style.line_spacing

    @property
    def space_bottom(self) -> float:
        """Gets the bottom spacing for the line."""
        return 0.5 * self.style.line_spacing

    @property
    def ascent(self) -> float:
        """Gets the ascent of the line."""
        return self.style.font_ascent

    @property
    def descent(self) -> float:
        """Gets the descent of the line."""
        return self.style.font_descent

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
        return self.style.line_height

    def __repr__(self):
        """Returns a string representation of the text line."""
        parts = []
        if self.content_left:
            parts.append(self.content_left)
        if self.content_center:
            parts.append(self.content_center)
        if self.content_right:
            parts.append(self.content_right)
        return " ".join(parts)
