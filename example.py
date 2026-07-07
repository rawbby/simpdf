import tempfile
from pathlib import Path

from PIL import Image as PILImage

from simpdf import *


def main() -> None:
    unsafe_remove_reportlab_signature()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        grey_path = Path(f.name)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        white_path = Path(f.name)

    PILImage.new("RGB", (1, 1), (220, 220, 220)).save(grey_path)
    PILImage.new("RGB", (1, 1), (255, 255, 255)).save(white_path)

    bg_page = Image(grey_path)
    bg_content = Image(white_path)

    font = "Helvetica"
    font_italic = "Helvetica-Oblique"
    font_bold = "Helvetica-Bold"
    font_bold_italic = "Helvetica-BoldOblique"
    fonts = {
        "font": font,
        "font_italic": font_italic,
        "font_bold": font_bold,
        "font_bold_italic": font_bold_italic
    }

    pdf = PDF(Path("example.pdf"))
    w = pdf.line_width

    def on_new_page(canvas, x, y, cw, ch):
        bg_page.draw(canvas, 0, 0, pdf.page_width, pdf.page_height)
        bg_content.draw(canvas, x, y, cw, ch)

    pdf.on_new_page = on_new_page

    title_style = TextStyle(font_bold, font_size=22.0, line_height_factor=1.0)
    pdf.add_line(Text(content_center="SimplePDF Feature Demo", style=title_style))
    pdf.add_line(Separator(thickness=2.0))

    head = TextStyle(font_bold, font_size=14.0)
    body = TextStyle(font_size=11.0)
    small = TextStyle(font_size=9.0, color=RGB(0.4))

    pdf.add_line(Text("1  Text & Alignment", style=head))
    pdf.add_line(Text("Left-aligned", "Centered", "Right-aligned", style=body))
    pdf.add_line(Text("Small gray caption", style=small))

    pdf.add_line(Separator())
    pdf.add_line(Text("2  Colors (RGB)", style=head))
    pdf.add_line(Text("Named hex color  #C00000", style=TextStyle(color=RGB("#C00000"))))
    pdf.add_line(Text("Short hex  #0A0", style=TextStyle(color=RGB("#0A0"))))
    pdf.add_line(Text("RGB tuple (0, 80, 160)", style=TextStyle(color=RGB((0, 80, 160)))))
    pdf.add_line(Text("Grayscale float 0.5", style=TextStyle(color=RGB(0.5))))
    pdf.add_line(Text("Grayscale int 128", style=TextStyle(color=RGB(128))))

    pdf.add_line(Separator())
    pdf.add_line(Text("3  Separator Variants", style=head))
    pdf.add_line(Separator())
    pdf.add_line(Separator(length_center=1.0 / 3.0))
    pdf.add_line(Separator(length_left=1.0 / 3.0))
    pdf.add_line(Separator(length_right=1.0 / 3.0))
    pdf.add_line(Separator(length_left=1.0 / 3.0, length_right=1.0 / 3.0))
    pdf.add_line(Separator(thickness=2.0, color=RGB("#0044AA"), line_spacing=8.0))

    pdf.add_line(Separator())
    pdf.add_line(Text("4  BreakText  (word-wrap)", style=head))
    long = (
        "SimplePDF lays out content as a vertical sequence of Line objects. "
        "Each line reports its own ascent, descent, and spacing so the engine "
        "can pack them onto pages automatically without any manual positioning. "
        "BreakText splits a long string into individual Text lines "
        "that each fit within the available column width.")
    pdf.add_line(BreakText(long, w, body))

    pdf.add_line(Separator())
    pdf.add_line(Text("5  BreakBlockText  (full justification)", style=head))
    pdf.add_line(BreakBlockText(long, w, body))

    pdf.add_line(Separator())
    pdf.add_line(Text("6  RichText  (bold / italic / links)", style=head))
    rich = RichTextStyle(**fonts, font_size=11.0)
    pdf.add_line(RichText("normal <b>bold</b> <i>italic</i> <b><i>bold-italic</i></b>", style=rich))
    pdf.add_line(VerticalSpace(20.0))
    pdf.add_line(RichText(
        content_left='<a href="https://example.com">Linked rich text</a>  —  '
                     '<b><a href="https://example.com">bold link</a></b>.',
        style=rich))
    pdf.add_line(VerticalSpace(20.0))
    pdf.add_line(RichText("left <b>bold</b>", "center <i>italic</i>", "right <b><i>bold-italic</i></b>", style=rich))

    pdf.add_line(Separator())
    pdf.add_line(Text("7  BreakRichText  (word-wrap with markup)", style=head))
    rich_long = (
        "SimplePDF supports <b>bold</b>, <i>italic</i>, and "
        "<b><i>bold-italic</i></b> text in the same paragraph. "
        "Long runs of mixed markup are broken at word boundaries just like "
        "plain text, and <a href=\"https://example.com\">hyperlinks that "
        "span a line break are <b>split cleanly</b> so the clickable region "
        "covers only the visible portion on each line.</a> "
        "The <i>segment metadata</i> travels with each piece after the split."
    )
    pdf.add_line(BreakRichText(rich_long, w, rich))

    pdf.add_line(Separator())
    pdf.add_line(Text("8  BreakRichBlockText  (justified with markup)", style=head))
    pdf.add_line(BreakRichBlockText(rich_long, w, rich))

    pdf.add_line(Separator())
    pdf.add_line(Text("9  Container  (keep-together)", style=head))
    pdf.add_line(Container([
        Text("This Text + wrapped lines are kept on the same page:", style=body),
        BreakText(
            "Container wraps several lines and reports a single line_height to the "
            "layout engine, so either every wrapped line fits on the current page or "
            "they all flow to the next one together.",
            w, body),
    ]))

    pdf.add_line(Separator())
    pdf.add_line(Text("10  Indentation", style=head))
    pdf.add_line(Text("No indent", style=body))
    pdf.add_line(Indentation(Text("Indented by 20pt", style=body), indent=20.0))
    pdf.add_line(Indentation(Text("Indented by 40pt", style=body), indent=40.0))
    pdf.add_line(Indentation(Separator(length_left=0.5), indent=40.0))

    pdf.add_line(Separator())
    pdf.add_line(Text("11  BulletPoints", style=head))
    pdf.add_line(BulletPoints(
        points=[
            (0, Text("• Top-level item.", style=body)),
            (1, Text("– Sub-item, indented one level.", style=body)),
            (1, Text("– Another sub-item at the same level.", style=body)),
            (2, Text("◦ Deeply nested item, two levels down.", style=body)),
            (0, Text("• Second top-level item.", style=body)),
            (1, Text("– Sub-item under the second top-level item.", style=body)),
        ],
        styles={
            0: BulletStyle("• "),
            1: BulletStyle("– "),
            2: BulletStyle("◦ "),
        },
    ))

    pdf.add_line(Separator())
    pdf.add_line(Text("12  Image & on_new_page", style=head))
    pdf.add_line(BreakText(
        "The grey margin and white content area visible on every page of this document "
        "are drawn by two Image instances registered on pdf.on_new_page.",
        w, body))

    pdf.add_line(PageFlush())

    pdf.add_line(Text(content_center="Page 2  —  PageFlush demo", style=title_style))
    pdf.add_line(Separator(thickness=2.0))
    page2_text = (
        "This page was started by a PageFlush sentinel on the previous page. "
        "PageFlush has an effectively infinite line_height so the layout engine "
        "always opens a new page when it encounters one."
    )
    pdf.add_line(BreakText(page2_text, w, body))

    pdf.save()
    grey_path.unlink()
    white_path.unlink()


if __name__ == "__main__":
    main()
