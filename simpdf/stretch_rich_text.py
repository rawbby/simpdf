from reportlab.pdfgen.canvas import Canvas

from simpdf.line import Line
from simpdf.rich_text import RichText, RichTextStyle, RichContent

__all__ = ["StretchRichText"]


class StretchRichText(Line):
    """A single rich-text line that stretches to fill the available width at draw time.

    Model coefficients are derived by sampling the width function at reference
    points rather than replicating internal font metrics, so the same ws/cs/hs
    solve works uniformly across bold/italic segment variants.
    ``unpack()`` returns ``[self]``.  Height properties use the worst-case
    metrics across all style variants.
    """

    rich_text: RichContent
    style: RichTextStyle

    def __init__(
            self,
            rich_text: str | None | RichContent,
            style: RichTextStyle | None = None,
            min_word_space_factor: float = 0.95,
            min_char_space_factor: float = 0.995,
            min_horizontal_scale: float = 99.0,
            max_word_space_factor: float | None = None,
            max_char_space_factor: float | None = None,
            max_horizontal_scale: float | None = None):
        self.rich_text = rich_text if isinstance(rich_text, RichContent) else RichContent(rich_text)
        self.style = style or RichTextStyle()
        self._min_wsf = min_word_space_factor
        self._min_csf = min_char_space_factor
        self._min_hs = min_horizontal_scale
        self._max_wsf = max_word_space_factor
        self._max_csf = max_char_space_factor
        self._max_hs = max_horizontal_scale

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        def stretched_style(target_width: float) -> RichTextStyle:
            assert self._min_hs > 0.0

            def ms(ws: float, cs: float, hs: float) -> RichTextStyle:
                return RichTextStyle(
                    font=self.style.style.font,
                    font_italic=self.style.style_italic.font if self.style.style_italic is not self.style.style else None,
                    font_bold=self.style.style_bold.font if self.style.style_bold is not self.style.style else None,
                    font_bold_italic=self.style.style_bold_italic.font if self.style.style_bold_italic is not self.style.style else None,
                    font_size=self.style.style.font_size,
                    line_height_factor=self.style.style.line_height_factor,
                    word_space=ws, char_space=cs, horizontal_scale=hs,
                    color=self.style.style.color)

            w_neutral = ms(0.0, 0.0, 100.0).text_width(self.rich_text)
            d_ws = ms(1.0, 0.0, 100.0).text_width(self.rich_text) - w_neutral
            d_cs = ms(0.0, 1.0, 100.0).text_width(self.rich_text) - w_neutral

            min_ws = self.style.style.font_size * (self._min_wsf - 1.0)
            min_cs = self.style.style.font_size * (self._min_csf - 1.0)
            min_hs = self._min_hs
            norm_ws = max(0.0, min_ws)
            norm_cs = max(0.0, min_cs)
            norm_hs = max(100.0, min_hs)
            max_ws = self.style.style.font_size * (self._max_wsf - 1.0) if self._max_wsf is not None else None
            max_cs = self.style.style.font_size * (self._max_csf - 1.0) if self._max_csf is not None else None
            max_hs = self._max_hs

            def tw(ws_, cs_, hs_):
                return (w_neutral + d_ws * ws_ + d_cs * cs_) * hs_ / 100.0

            def solve_hs(ws, cs):
                base = w_neutral + d_ws * ws + d_cs * cs
                return target_width / base * 100.0 if base > 0 else norm_hs

            def solve_cs(ws, hs):
                return (target_width * 100.0 / hs - w_neutral - d_ws * ws) / d_cs if d_cs > 0 else norm_cs

            def solve_ws(cs, hs):
                return (target_width * 100.0 / hs - w_neutral - d_cs * cs) / d_ws if d_ws > 0 else norm_ws

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

        rt = RichText.__new__(RichText)
        rt.content_left = self.rich_text
        rt.content_center = RichContent(None)
        rt.content_right = RichContent(None)
        rt.style = stretched_style(end - start - 1e-6)
        rt.draw(canvas, baseline, start, end)

    @property
    def space_top(self) -> float:
        return max(0.5 * s.line_spacing for s in self.style.styles)

    @property
    def space_bottom(self) -> float:
        return max(0.5 * s.line_spacing for s in self.style.styles)

    @property
    def ascent(self) -> float:
        return max(s.ascent for s in self.style.styles)

    @property
    def descent(self) -> float:
        return min(s.descent for s in self.style.styles)

    @property
    def line_height_upper(self) -> float:
        return self.space_top + self.ascent

    @property
    def line_height_lower(self) -> float:
        return self.space_bottom - self.descent

    @property
    def line_height(self) -> float:
        return self.line_height_upper + self.line_height_lower
