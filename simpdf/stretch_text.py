from reportlab.pdfbase.pdfmetrics import stringWidth

from simpdf.text_style import TextStyle

__all__ = ["stretch_text"]


def stretch_text(
        text: str,
        target_width: float,
        style: TextStyle,
        min_word_space_factor: float = 0.95,
        min_char_space_factor: float = 0.995,
        min_horizontal_scale: float = 99.0,
        max_word_space_factor: float | None = None,
        max_char_space_factor: float | None = None,
        max_horizontal_scale: float | None = None) -> TextStyle:
    """Returns a TextStyle that stretches *text* to fill *target_width*.

    Steps 1–3 relax any compression back to neutral (hs → 100 %, cs → 0, ws → 0).
    Steps 4–6 expand beyond neutral (ws → max, cs → max, hs → max).
    Each step is solved analytically: if the full boundary would overshoot, the
    exact value is computed and returned immediately.  Passing ``None`` for any
    maximum removes the cap on that axis.

    The caller must ensure the text fits within *target_width* at the minimum
    settings.
    """
    assert min_horizontal_scale > 0.0

    num_ws = text.count(" ")
    num_cs = len(text)
    unscaled = stringWidth(text, style.font, style.font_size)

    fs = style.font_size
    min_ws = fs * (min_word_space_factor - 1.0)
    min_cs = fs * (min_char_space_factor - 1.0)
    min_hs = min_horizontal_scale

    norm_ws = max(0.0, min_ws)
    norm_cs = max(0.0, min_cs)
    norm_hs = max(100.0, min_hs)

    max_ws = fs * (max_word_space_factor - 1.0) if max_word_space_factor is not None else None
    max_cs = fs * (max_char_space_factor - 1.0) if max_char_space_factor is not None else None
    max_hs = max_horizontal_scale

    def text_width(ws_: float, cs_: float, hs_: float) -> float:
        return (unscaled + num_ws * ws_ + num_cs * cs_) * hs_ / 100.0

    def make_style(ws_: float, cs_: float, hs_: float) -> TextStyle:
        return TextStyle(
            font=style.font,
            font_size=fs,
            line_height_factor=style.line_height_factor,
            word_space=ws_,
            char_space=cs_,
            horizontal_scale=hs_)

    def solve_hs(ws_: float, cs_: float) -> float:
        total = unscaled + num_ws * ws_ + num_cs * cs_
        if total > 0:
            return target_width * 100.0 / total
        return norm_hs

    def solve_cs(ws_: float, hs_: float) -> float:
        if num_cs > 0:
            return (target_width * 100.0 / hs_ - unscaled - num_ws * ws_) / num_cs
        return norm_cs

    def solve_ws(cs_: float, hs_: float) -> float:
        if num_ws > 0:
            return (target_width * 100.0 / hs_ - unscaled - num_cs * cs_) / num_ws
        return norm_ws

    if text_width(min_ws, min_cs, min_hs) >= target_width:
        return make_style(min_ws, min_cs, min_hs)

    # Step 1: relax hs from min_hs to norm_hs
    if text_width(min_ws, min_cs, norm_hs) > target_width:
        return make_style(min_ws, min_cs, solve_hs(min_ws, min_cs))

    # Step 2: relax cs from min_cs to norm_cs
    if num_cs > 0 and text_width(min_ws, norm_cs, norm_hs) > target_width:
        return make_style(min_ws, solve_cs(min_ws, norm_hs), norm_hs)

    # Step 3: relax ws from min_ws to norm_ws
    if num_ws > 0 and text_width(norm_ws, norm_cs, norm_hs) > target_width:
        return make_style(solve_ws(norm_cs, norm_hs), norm_cs, norm_hs)

    # Step 4: stretch ws from norm_ws toward max_ws
    if max_ws is None or text_width(max_ws, norm_cs, norm_hs) > target_width:
        return make_style(solve_ws(norm_cs, norm_hs), norm_cs, norm_hs)

    # Step 5: stretch cs from norm_cs toward max_cs
    if max_cs is None or text_width(max_ws, max_cs, norm_hs) > target_width:
        return make_style(max_ws, solve_cs(max_ws, norm_hs), norm_hs)

    # Step 6: stretch hs from norm_hs toward max_hs
    if max_hs is None or text_width(max_ws, max_cs, max_hs) > target_width:
        return make_style(max_ws, max_cs, solve_hs(max_ws, max_cs))

    return make_style(max_ws, max_cs, max_hs)
