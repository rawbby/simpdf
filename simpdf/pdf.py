from pathlib import Path

from reportlab.lib.pagesizes import *
from reportlab.lib.units import *
from reportlab.pdfgen.canvas import *

from simpdf._common import _apply_constraints
from simpdf.line import Line

__all__ = ["PDF"]


class PDF:
    """A straightforward PDF generator that organizes content as lines and separators."""

    """Default page width."""
    default_page_width: float = A4[0]

    """Default page height."""
    default_page_height: float = A4[1]

    """Default left margin."""
    default_margin_left: float = inch

    """Default right margin."""
    default_margin_right: float = inch

    """Default top margin."""
    default_margin_top: float = inch

    """Default bottom margin."""
    default_margin_bottom: float = inch

    """Current page width."""
    page_width: float

    """Current page height."""
    page_height: float

    """Current left margin."""
    margin_left: float

    """Current right margin."""
    margin_right: float

    """Current top margin."""
    margin_top: float

    """Current bottom margin."""
    margin_bottom: float

    """The underlying ReportLab canvas."""
    canvas: Canvas

    """List of elements to be rendered."""
    lines: list[Line]

    def __init__(
            self,
            output_path: Path,
            page_width: float | None = None,
            page_height: float | None = None,
            margin_left: float | None = None,
            margin_right: float | None = None,
            margin_top: float | None = None,
            margin_bottom: float | None = None,
            content_x: float | None = None,
            content_y: float | None = None,
            content_width: float | None = None,
            content_height: float | None = None):
        sym_params = [
            ("page_width", page_width),
            ("page_height", page_height),
            ("margin_left", margin_left),
            ("margin_right", margin_right),
            ("margin_top", margin_top),
            ("margin_bottom", margin_bottom),
            ("content_x", content_x),
            ("content_y", content_y),
            ("content_width", content_width),
            ("content_height", content_height)
        ]

        sym_defaults = [
            ("page_width", self.default_page_width),
            ("page_height", self.default_page_height),
            ("margin_left", self.default_margin_left),
            ("margin_right", self.default_margin_right),
            ("margin_top", self.default_margin_top),
            ("margin_bottom", self.default_margin_bottom)
        ]

        relations = [
            ("page_width", ["margin_left", "content_width", "margin_right"], lambda l, cw, r: l + cw + r),
            ("margin_left", ["page_width", "content_width", "margin_right"], lambda pw, cw, r: pw - cw - r),
            ("content_width", ["page_width", "margin_left", "margin_right"], lambda pw, l, r: pw - l - r),
            ("margin_right", ["page_width", "margin_left", "content_width"], lambda pw, l, cw: pw - l - cw),
            ("page_height", ["margin_bottom", "content_height", "margin_top"], lambda b, ch, t: b + ch + t),
            ("margin_bottom", ["page_height", "content_height", "margin_top"], lambda ph, ch, t: ph - ch - t),
            ("content_height", ["page_height", "margin_bottom", "margin_top"], lambda ph, b, t: ph - b - t),
            ("margin_top", ["page_height", "margin_bottom", "content_height"], lambda ph, b, ch: ph - b - ch),
            ("content_x", ["margin_left"], lambda l: l),
            ("margin_left", ["content_x"], lambda x: x),
            ("content_y", ["margin_bottom"], lambda b: b),
            ("margin_bottom", ["content_y"], lambda y: y),
        ]

        _apply_constraints(self, sym_params, sym_defaults, relations)

        self.canvas = Canvas(
            filename=str(output_path),
            pagesize=(self.page_width, self.page_height),
            pdfVersion=(1, 4),
            pageCompression=1,
            invariant=True)

        self.lines = []

    @property
    def content_x(self) -> float:
        """Gets the X coordinate of the starting content area."""
        return self.margin_left

    @property
    def content_y(self) -> float:
        """Gets the Y coordinate of the bottom content area."""
        return self.margin_bottom

    @property
    def content_width(self) -> float:
        """Gets the usable width for content."""
        return self.page_width - self.margin_left - self.margin_right

    @property
    def content_height(self) -> float:
        """Gets the usable height for content."""
        return self.page_height - self.margin_bottom - self.margin_top

    @property
    def line_width(self) -> float:
        """Gets the current line width available for text."""
        return self.content_width

    def add_line(self, line: Line):
        """Appends a line or separator to the PDF document."""
        self.lines.append(line)

    def save(self, max_pages: int = -1):
        """Renders the collected lines onto the canvas and saves the PDF file."""
        if not self.lines:
            self.canvas.save()
            return

        pages = []
        page = [self.lines[0]]
        page_height = self.lines[0].line_height - self.lines[0].space_top

        for line in self.lines[1:]:
            page_height += line.line_height - line.space_bottom

            # trivial case: line fits page
            if page_height <= self.content_height:
                page_height += line.space_bottom
                page.append(line)
                continue

            # start new page
            pages.append(page)

            page = [line]
            page_height = line.line_height - line.space_top

        if page:
            pages.append(page)

        assert max_pages < 0 or len(pages) <= max_pages

        for i, page in enumerate(pages):
            if i > 0:
                self.canvas.showPage()

            baseline = self.page_height - self.margin_top - page[0].ascent
            beg = self.content_x
            end = beg + self.content_width

            page[0].draw(self.canvas, baseline, beg, end)
            for j, line in enumerate(page[1:], 1):
                baseline -= page[j - 1].line_height_lower + line.line_height_upper
                line.draw(self.canvas, baseline, beg, end)

        self.canvas.save()
