from reportlab.pdfgen.canvas import *
from reportlab.pdfbase.pdfmetrics import *

from simpdf._common import _apply_constraints
from simpdf.rgb import RGB, ColorType

__all__ = ["TextStyle"]


class TextStyle:
    """Defines typographic styles and spacing constraints for text lines."""

    """Default font family."""
    default_font: str = "Helvetica"

    """Default font size in points."""
    default_font_size: float = 11.0

    """Default factor for line height calculation."""
    default_line_height_factor: float = 1.2

    """Default character spacing factor."""
    default_char_space_factor: float = 0.0

    """Default word spacing factor."""
    default_word_space_factor: float = 0.0

    """Default horizontal scaling percentage."""
    default_horizontal_scale: float = 100.0

    """Default text color."""
    default_color: RGB = RGB(0.0)

    """Current font family."""
    font: str

    """Current font size in points."""
    font_size: float

    """Current line height factor."""
    line_height_factor: float

    """Current character spacing factor."""
    char_space_factor: float

    """Current word spacing factor."""
    word_space_factor: float

    """Current horizontal scaling percentage."""
    horizontal_scale: float

    """Current text color."""
    color: RGB

    def __init__(
            self,
            font: str | None = None,
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
        """Initializes a LineStyle, automatically resolving typographic constraints."""
        self.font = font if font is not None else self.default_font
        self.color = RGB(color) if color is not None else self.default_color
        font_ascent_10 = getAscent(self.font, 10.0)
        font_descent_10 = getDescent(self.font, 10.0)

        sym_params = [
            ("font_size", font_size),
            ("font_ascent", font_ascent),
            ("font_descent", font_descent),
            ("font_height", font_height),
            ("line_height_factor", line_height_factor),
            ("line_height", line_height),
            ("line_spacing", line_spacing),
            ("char_space_factor", char_space_factor),
            ("word_space_factor", word_space_factor),
            ("horizontal_scale", horizontal_scale),
            ("char_space", char_space),
            ("word_space", word_space)
        ]

        sym_defaults = [
            ("font_size", self.default_font_size),
            ("line_height_factor", self.default_line_height_factor),
            ("char_space_factor", self.default_char_space_factor),
            ("word_space_factor", self.default_word_space_factor),
            ("horizontal_scale", self.default_horizontal_scale)
        ]

        relations = [
            ("font_height", ["font_ascent", "font_descent"], lambda a, d: a - d),
            ("font_ascent", ["font_height", "font_descent"], lambda h, d: h + d),
            ("font_descent", ["font_ascent", "font_height"], lambda a, h: a - h),

            ("line_spacing", ["line_height", "font_height"], lambda lh, fh: lh - fh),
            ("line_height", ["line_spacing", "font_height"], lambda ls, fh: ls + fh),
            ("font_height", ["line_height", "line_spacing"], lambda lh, ls: lh - ls),

            ("line_height", ["font_size", "line_height_factor"], lambda f, lf: f * lf),
            ("font_size", ["line_height", "line_height_factor"], lambda lh, lf: lh / lf if lf else None),
            ("line_height_factor", ["line_height", "font_size"], lambda lh, f: lh / f if f else None),

            ("font_ascent", ["font_descent"],
             lambda d: d * font_ascent_10 / font_descent_10 if font_descent_10 else None),
            ("font_descent", ["font_ascent"],
             lambda a: a * font_descent_10 / font_ascent_10 if font_ascent_10 else None),

            ("font_size", ["font_height"],
             lambda h: h * 10.0 / (font_ascent_10 - font_descent_10) if (font_ascent_10 - font_descent_10) else None),
            ("font_height", ["font_size"], lambda f: f * (font_ascent_10 - font_descent_10) / 10.0),

            ("font_size", ["font_descent"], lambda d: d * 10.0 / font_descent_10 if font_descent_10 else None),
            ("font_descent", ["font_size"], lambda f: f * font_descent_10 / 10.0),

            ("font_ascent", ["font_size"], lambda f: f * font_ascent_10 / 10.0),
            ("font_size", ["font_ascent"], lambda a: a * 10.0 / font_ascent_10 if font_ascent_10 else None),

            ("char_space", ["font_size", "char_space_factor"], lambda f, cf: f * cf),
            ("font_size", ["char_space", "char_space_factor"], lambda cs, cf: cs / cf if cf else None),
            ("char_space_factor", ["char_space", "font_size"], lambda cs, f: cs / f if f else None),

            ("word_space", ["font_size", "word_space_factor"], lambda f, wf: f * wf),
            ("font_size", ["word_space", "word_space_factor"], lambda ws, wf: ws / wf if wf else None),
            ("word_space_factor", ["word_space", "font_size"], lambda ws, f: ws / f if f else None),
        ]

        _apply_constraints(self, sym_params, sym_defaults, relations)

    @property
    def font_ascent(self):
        """Gets the font ascent based on the current font and size."""
        return getAscent(self.font, self.font_size)

    @property
    def font_descent(self):
        """Gets the font descent based on the current font and size."""
        return getDescent(self.font, self.font_size)

    @property
    def font_height(self):
        """Gets the total height of the font (ascent minus descent)."""
        return self.font_ascent - self.font_descent

    @property
    def line_height(self):
        """Gets the total line height."""
        return self.font_size * self.line_height_factor

    @property
    def line_spacing(self):
        """Gets the extra spacing between lines."""
        return self.line_height - self.font_height

    @property
    def char_space(self):
        """Gets the absolute character spacing."""
        return self.char_space_factor * self.font_size

    @property
    def word_space(self):
        """Gets the absolute word spacing."""
        return self.word_space_factor * self.font_size

    def text_width(self, text: str | None) -> float:
        """Calculates the total width of the given text with this style applied."""
        text = "" if text is None else text
        if not text:
            return 0.0

        total_text_width = stringWidth(text, self.font, self.font_size)
        total_text_width += text.count(" ") * self.word_space
        total_text_width += len(text) * self.char_space
        return total_text_width * self.horizontal_scale / 100.0

    def draw_text(self, canvas: Canvas, x: float, y: float, text: str):
        """Draws the text onto the given canvas at the specified coordinates using this style."""
        canvas.saveState()
        canvas.setFillColor(self.color)
        text_object = canvas.beginText(x, y, "LTR")
        text_object.setFont(self.font, self.font_size, self.line_height)
        text_object.setHorizScale(self.horizontal_scale)
        text_object.setCharSpace(self.char_space)
        text_object.setWordSpace(self.word_space)
        text_object.textLine(text)
        canvas.drawText(text_object)
        canvas.restoreState()
