from pathlib import Path
import tempfile

from PIL import Image, ImageDraw

from simpdf import *


def _make_sample_image(path: Path) -> None:
    img = Image.new("RGB", (300, 120), color=(220, 235, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle([4, 4, 295, 115], outline=(60, 100, 160), width=3)
    draw.text((20, 45), "SimplePDF  —  Sample Image", fill=(30, 60, 120))
    img.save(path)


def main() -> None:
    unsafe_remove_reportlab_signature()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img_path = Path(f.name)
    _make_sample_image(img_path)

    pdf = PDF(Path("example.pdf"))
    w = pdf.line_width

    title_style = TextStyle(font="Helvetica-Bold", font_size=22.0)
    pdf.add_line(Text(content_center="SimplePDF Feature Demo", style=title_style))
    pdf.add_line(Separator(thickness=2.0))

    head = TextStyle(font="Helvetica-Bold", font_size=14.0)
    body = TextStyle(font_size=11.0)
    small = TextStyle(font_size=9.0, color=RGB(0.4))

    pdf.add_line(Text("1  Text & Alignment", style=head))
    pdf.add_line(Text(
        content_left="Left-aligned",
        content_center="Centered",
        content_right="Right-aligned",
        style=body))
    pdf.add_line(Text(content_left="Small gray caption", style=small))

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
    pdf.add_line(Separator(length_center=0.5))
    pdf.add_line(Separator(length_left=0.4, length_center=0.0, length_right=0.4))
    pdf.add_line(Separator(length_left=0.45, length_center=0.0, length_right=0.0))
    pdf.add_line(Separator(length_left=0.0, length_center=0.0, length_right=0.45))
    pdf.add_line(Separator(thickness=3.0, color=RGB("#0044AA"), line_spacing=8.0))

    pdf.add_line(Separator())
    pdf.add_line(Text("4  break_text  (word-wrap)", style=head))
    long = (
        "SimplePDF lays out content as a vertical sequence of Line objects. "
        "Each line reports its own ascent, descent, and spacing so the engine "
        "can pack them onto pages automatically without any manual positioning. "
        "The break_text helper splits a long string into individual Text lines "
        "that each fit within the available column width."
    )
    for line in break_text(long, w, body):
        pdf.add_line(line)

    pdf.add_line(Separator())
    pdf.add_line(Text("5  break_block_text  (full justification)", style=head))
    for line in break_block_text(long, w, body):
        pdf.add_line(line)

    pdf.add_line(Separator())
    pdf.add_line(Text("6  RichText  (bold / italic / links)", style=head))
    rich = RichTextStyle(
        font="Helvetica",
        font_italic="Helvetica-Oblique",
        font_bold="Helvetica-Bold",
        font_bold_italic="Helvetica-BoldOblique",
        font_size=11.0)
    pdf.add_line(RichText(
        content_left="Normal, <b>bold</b>, <i>italic</i>, and <b><i>bold-italic</i></b>.",
        style=rich))
    pdf.add_line(RichText(
        content_left='<a href="https://example.com">Linked rich text</a>  —  '
                     '<b><a href="https://example.com">bold link</a></b>.',
        style=rich))
    pdf.add_line(RichText(
        content_left="Left  <b>bold</b>",
        content_center="<i>center italic</i>",
        content_right="right  <b><i>bi</i></b>",
        style=rich))

    pdf.add_line(Separator())
    pdf.add_line(Text("7  InlineImage", style=head))
    pdf.add_line(InlineImage(
        image_height=50.0,
        image_path_left=img_path,
        image_path_center=None,
        image_path_right=None))
    pdf.add_line(InlineImage(
        image_height=50.0,
        image_path_left=None,
        image_path_center=img_path,
        image_path_right=None))
    pdf.add_line(InlineImage(
        image_height=50.0,
        image_path_left=None,
        image_path_center=None,
        image_path_right=img_path))

    pdf.add_line(PageFlush())

    pdf.add_line(Text(content_center="Page 2  —  PageFlush demo", style=title_style))
    pdf.add_line(Separator(thickness=2.0))
    page2_text = (
        "This page was started by a PageFlush sentinel on the previous page. "
        "PageFlush has an effectively infinite line_height so the layout engine "
        "always opens a new page when it encounters one."
    )
    for line in break_text(page2_text, w, body):
        pdf.add_line(line)

    pdf.save()
    img_path.unlink()


if __name__ == "__main__":
    main()
