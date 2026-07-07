# simpdf

A simple, pixel-perfect PDF layout library built on top of ReportLab, providing easy interfaces for text and block breaking, styling, and basic document structure.

## Features

- **Simplicity:** Minimal, intuitive interface to generate PDF documents programmatically.
- **Pixel Perfection:** Precise control over layout, typography spacing, and margins without unexpected overlaps.
- **Text & Block Breaking:** Automatic adjustment of word and character spacing, and horizontal scaling to perfectly fit texts.
- **Hyperlinks Support:** Easily define interactive links in your layout.
- **Machine Readable:** Generated PDFs are optimized to be understood by machines, allowing content to be easily extracted automatically.
- **Bullet Points:** Hierarchical bullet lists with per-level style, custom glyphs, and automatic indentation.
- **Indentation:** Shift any line element by a fixed horizontal indent.
- **Background Images:** Reusable image references for direct canvas rendering (e.g. page watermarks or banners via `on_new_page`).
- **Page Callbacks:** `on_new_page` hook called at the start of each page with the canvas and content area.

## Installation

```bash
pip install git+https://github.com/rawbby/simpdf.git@v0.1.8
```

## Example

```python
from pathlib import Path
from simpdf import PDF, Text, TextStyle, Separator, InlineImage, Container, Indentation, BulletPoints, BulletStyle, BackgroundImage

pdf = PDF(Path("example.pdf"))
style = TextStyle(font="Helvetica", font_size=12)

# Background image on every page
bg = BackgroundImage(Path("banner.png"), image_height=40.0)
pdf.on_new_page = lambda canvas, x, y, cw, ch: bg.draw(canvas, x, y + ch - 40.0, width=cw)

# Text line
line = Text(content_left="Hello", content_right="World!", style=style)
pdf.add_line(line)

# Image
img = InlineImage(image_path_center=Path("logo.png"), image_height=50.0)
pdf.add_line(img)

# Separator
sep = Separator(thickness=1)
pdf.add_line(sep)

# Indented line
pdf.add_line(Indentation(Text("indented text", style=style), indent=20.0))

# Keep lines together on the same page
pdf.add_line(Container([Text("Header", style=style), sep, Text("Body", style=style)]))

# Bullet points
bp = BulletPoints(
    points=[(0, "Top-level item"), (1, "Sub-item"), (0, "Another item")],
    text_style=style,
    styles={0: BulletStyle("•"), 1: BulletStyle("–")},
)
for line in bp.lines(pdf.line_width):
    pdf.add_line(line)

pdf.save()
```
