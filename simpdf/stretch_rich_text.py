from simpdf.rich_text import RichTextStyle, RichContent

__all__ = ["stretch_rich_text"]


def stretch_rich_text(
        rich_text: str | None | RichContent,
        target_width: float,
        style: RichTextStyle,
        min_word_space_factor: float = 0.95,
        min_char_space_factor: float = 0.995,
        min_horizontal_scale: float = 99.0,
        max_word_space_factor: float | None = None,
        max_char_space_factor: float | None = None,
        max_horizontal_scale: float | None = None) -> RichTextStyle:
    """Returns a RichTextStyle that stretches *rc* to fill *target_width*.

    Applies the same six-step optimization as stretch_text.  Model coefficients
    are derived by sampling the width function at reference points rather than
    replicating internal font metrics, so the same ws/cs/hs solve works uniformly
    across all bold/italic segment variants.
    """
    assert min_horizontal_scale > 0.0
    if not isinstance(rich_text, RichContent):
        rich_text = RichContent(rich_text)

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

    w_neutral = make_style(0.0, 0.0, 100.0).text_width(rich_text)
    d_ws = make_style(1.0, 0.0, 100.0).text_width(rich_text) - w_neutral
    d_cs = make_style(0.0, 1.0, 100.0).text_width(rich_text) - w_neutral

    min_ws = style.style.font_size * (min_word_space_factor - 1.0)
    min_cs = style.style.font_size * (min_char_space_factor - 1.0)
    min_hs = min_horizontal_scale

    norm_ws = max(0.0, min_ws)
    norm_cs = max(0.0, min_cs)
    norm_hs = max(100.0, min_hs)

    max_ws = style.style.font_size * (max_word_space_factor - 1.0) if max_word_space_factor is not None else None
    max_cs = style.style.font_size * (max_char_space_factor - 1.0) if max_char_space_factor is not None else None
    max_hs = max_horizontal_scale

    def text_width(ws: float, cs: float, hs: float) -> float:
        return (w_neutral + d_ws * ws + d_cs * cs) * hs / 100.0

    def solve_hs(ws: float, cs: float) -> float:
        base = w_neutral + d_ws * ws + d_cs * cs
        return target_width / base * 100.0 if base > 0 else norm_hs

    def solve_cs(ws: float, hs: float) -> float:
        return (target_width * 100.0 / hs - w_neutral - d_ws * ws) / d_cs if d_cs > 0 else norm_cs

    def solve_ws(cs: float, hs: float) -> float:
        return (target_width * 100.0 / hs - w_neutral - d_cs * cs) / d_ws if d_ws > 0 else norm_ws

    if text_width(min_ws, min_cs, min_hs) >= target_width:
        return make_style(min_ws, min_cs, min_hs)

    if text_width(min_ws, min_cs, norm_hs) >= target_width:
        return make_style(min_ws, min_cs, solve_hs(min_ws, min_cs))

    if text_width(min_ws, norm_cs, norm_hs) >= target_width:
        return make_style(min_ws, solve_cs(min_ws, norm_hs), norm_hs)

    if text_width(norm_ws, norm_cs, norm_hs) >= target_width:
        return make_style(solve_ws(norm_cs, norm_hs), norm_cs, norm_hs)

    if max_ws is None or text_width(max_ws, norm_cs, norm_hs) >= target_width:
        return make_style(solve_ws(norm_cs, norm_hs), norm_cs, norm_hs)

    if max_cs is None or text_width(max_ws, max_cs, norm_hs) >= target_width:
        return make_style(max_ws, solve_cs(max_ws, norm_hs), norm_hs)

    if max_hs is None or text_width(max_ws, max_cs, max_hs) >= target_width:
        return make_style(max_ws, max_cs, solve_hs(max_ws, max_cs))

    return make_style(max_ws, max_cs, max_hs)
