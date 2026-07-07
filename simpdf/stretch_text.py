from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line
from simpdf.text import Text
from simpdf.text_style import TextStyle

__all__ = ["StretchText"]


class StretchText(Line):
    """A single text line that stretches to fill the available width at draw time.

    The six-step algorithm (decompress hs → cs → ws, then expand ws → cs → hs)
    runs inside ``draw()`` using ``end - start`` as the target width.
    ``unpack()`` returns ``[self]``.  Height properties use the natural
    (unstretched) style metrics.
    """

    text: str
    style: TextStyle

    def __init__(
            self,
            text: str,
            style: TextStyle | None = None,
            min_word_space_factor: float = 0.95,
            min_char_space_factor: float = 0.995,
            min_horizontal_scale: float = 99.0,
            max_word_space_factor: float | None = None,
            max_char_space_factor: float | None = None,
            max_horizontal_scale: float | None = None):
        self.text = text
        self.style = style or TextStyle()
        self._min_wsf = min_word_space_factor
        self._min_csf = min_char_space_factor
        self._min_hs = min_horizontal_scale
        self._max_wsf = max_word_space_factor
        self._max_csf = max_char_space_factor
        self._max_hs = max_horizontal_scale

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        def stretched_style(target_width: float) -> TextStyle:
            assert self._min_hs > 0.0

            num_ws = self.text.count(" ")
            num_cs = len(self.text)
            unscaled = stringWidth(self.text, self.style.font, self.style.font_size)

            min_ws = self.style.font_size * (self._min_wsf - 1.0)
            min_cs = self.style.font_size * (self._min_csf - 1.0)
            min_hs = self._min_hs
            norm_ws = max(0.0, min_ws)
            norm_cs = max(0.0, min_cs)
            norm_hs = max(100.0, min_hs)
            max_ws = self.style.font_size * (self._max_wsf - 1.0) if self._max_wsf is not None else None
            max_cs = self.style.font_size * (self._max_csf - 1.0) if self._max_csf is not None else None
            max_hs = self._max_hs

            def tw(ws_, cs_, hs_):
                return (unscaled + num_ws * ws_ + num_cs * cs_) * hs_ / 100.0

            def ms(ws_, cs_, hs_):
                return TextStyle(
                    font=self.style.font,
                    font_size=self.style.font_size,
                    line_height_factor=self.style.line_height_factor,
                    word_space=ws_, char_space=cs_, horizontal_scale=hs_)

            def solve_hs(ws, cs):
                total = unscaled + num_ws * ws + num_cs * cs
                return target_width * 100.0 / total if total > 0 else norm_hs

            def solve_cs(ws, hs):
                return (target_width * 100.0 / hs - unscaled - num_ws * ws) / num_cs if num_cs > 0 else norm_cs

            def solve_ws(cs, hs):
                return (target_width * 100.0 / hs - unscaled - num_cs * cs) / num_ws if num_ws > 0 else norm_ws

            if tw(min_ws, min_cs, min_hs) >= target_width:
                return ms(min_ws, min_cs, min_hs)
            if tw(min_ws, min_cs, norm_hs) >= target_width:
                return ms(min_ws, min_cs, solve_hs(min_ws, min_cs))
            if tw(min_ws, norm_cs, norm_hs) >= target_width:
                return ms(min_ws, solve_cs(min_ws, norm_hs), norm_hs)
            if tw(norm_ws, norm_cs, norm_hs) >= target_width:
                return ms(solve_ws(norm_cs, norm_hs), norm_cs, norm_hs)
            if max_ws is None or tw(max_ws, norm_cs, norm_hs) >= target_width:
                return ms(solve_ws(norm_cs, norm_hs), norm_cs, norm_hs)
            if max_cs is None or tw(max_ws, max_cs, norm_hs) >= target_width:
                return ms(max_ws, solve_cs(max_ws, norm_hs), norm_hs)
            if max_hs is None or tw(max_ws, max_cs, max_hs) >= target_width:
                return ms(max_ws, max_cs, solve_hs(max_ws, max_cs))
            return ms(max_ws, max_cs, max_hs)

        Text(content_left=self.text, style=stretched_style(end - start - 1e-6)).draw(canvas, baseline, start, end)

    @property
    def space_top(self) -> float:
        return 0.5 * self.style.line_spacing

    @property
    def space_bottom(self) -> float:
        return 0.5 * self.style.line_spacing

    @property
    def ascent(self) -> float:
        return self.style.ascent

    @property
    def descent(self) -> float:
        return self.style.descent

    @property
    def line_height_upper(self) -> float:
        return self.space_top + self.ascent

    @property
    def line_height_lower(self) -> float:
        return self.space_bottom - self.descent

    @property
    def line_height(self) -> float:
        return self.style.line_height
