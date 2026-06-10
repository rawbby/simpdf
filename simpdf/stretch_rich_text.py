from reportlab.pdfbase.pdfmetrics import stringWidth

from simpdf.rich_text import RichTextStyle, _RichContent

__all__ = ["stretch_rich_text"]


def stretch_rich_text(
        rc: _RichContent,
        target_width: float,
        style: RichTextStyle,
        min_word_space_factor: float = 0.95,
        min_char_space_factor: float = 0.995,
        min_horizontal_scale: float = 99.0,
        max_word_space_factor: float | None = None,
        max_char_space_factor: float | None = None,
        max_horizontal_scale: float | None = None) -> RichTextStyle:
    """Returns a RichTextStyle that stretches *rc* to fill *target_width*.

    Applies the same six-step optimization as stretch_text but aggregates unscaled
    widths across all bold/italic segments so the same ws/cs/hs delta is applied
    uniformly to all four style variants.
    """
    assert min_horizontal_scale > 0.0

    fs = style.style.font_size
    total_unscaled = sum(stringWidth(rc.text[beg:end], style.get_style(mode).font, fs)
                         for beg, end, mode in rc.segments)
    num_ws = rc.text.count(" ")
    num_cs = len(rc.text)

    min_ws = fs * (min_word_space_factor - 1.0)
    min_cs = fs * (min_char_space_factor - 1.0)
    min_hs = min_horizontal_scale

    norm_ws = max(0.0, min_ws)
    norm_cs = max(0.0, min_cs)
    norm_hs = max(100.0, min_hs)

    max_ws = fs * (max_word_space_factor - 1.0) if max_word_space_factor is not None else None
    max_cs = fs * (max_char_space_factor - 1.0) if max_char_space_factor is not None else None
    max_hs = max_horizontal_scale

    def text_width(ws: float, cs: float, hs: float) -> float:
        return (total_unscaled + num_ws * ws + num_cs * cs) * hs / 100.0

    def make_style(ws: float, cs: float, hs: float) -> RichTextStyle:
        return RichTextStyle(
            font=style.style.font,
            font_italic=style.style_italic.font if style.style_italic is not style.style else None,
            font_bold=style.style_bold.font if style.style_bold is not style.style else None,
            font_bold_italic=style.style_bold_italic.font if style.style_bold_italic is not style.style else None,
            font_size=style.style.font_size,
            line_height_factor=style.style.line_height_factor,
            word_space=ws,
            char_space=cs,
            horizontal_scale=hs,
            color=style.style.color)

    def solve_hs(ws_: float, cs_: float) -> float:
        total = total_unscaled + num_ws * ws_ + num_cs * cs_
        return target_width * 100.0 / total if total > 0 else norm_hs

    def solve_cs(ws_: float, hs_: float) -> float:
        if num_cs > 0:
            return (target_width * 100.0 / hs_ - total_unscaled - num_ws * ws_) / num_cs
        return norm_cs

    def solve_ws(cs_: float, hs_: float) -> float:
        if num_ws > 0:
            return (target_width * 100.0 / hs_ - total_unscaled - num_cs * cs_) / num_ws
        return norm_ws

    if text_width(min_ws, min_cs, min_hs) >= target_width:
        return make_style(min_ws, min_cs, min_hs)

    if text_width(min_ws, min_cs, norm_hs) > target_width:
        return make_style(min_ws, min_cs, solve_hs(min_ws, min_cs))

    if num_cs > 0 and text_width(min_ws, norm_cs, norm_hs) > target_width:
        return make_style(min_ws, solve_cs(min_ws, norm_hs), norm_hs)

    if num_ws > 0 and text_width(norm_ws, norm_cs, norm_hs) > target_width:
        return make_style(solve_ws(norm_cs, norm_hs), norm_cs, norm_hs)

    if max_ws is None or text_width(max_ws, norm_cs, norm_hs) > target_width:
        return make_style(solve_ws(norm_cs, norm_hs), norm_cs, norm_hs)

    if max_cs is None or text_width(max_ws, max_cs, norm_hs) > target_width:
        return make_style(max_ws, solve_cs(max_ws, norm_hs), norm_hs)

    if max_hs is None or text_width(max_ws, max_cs, max_hs) > target_width:
        return make_style(max_ws, max_cs, solve_hs(max_ws, max_cs))

    return make_style(max_ws, max_cs, max_hs)
