# simpdf

A simple, pixel-perfect PDF layout library built on top of ReportLab, providing easy interfaces for text and block breaking, styling, and basic document structure.

## Features

- **Simplicity:** Minimal, intuitive interface to generate PDF documents programmatically.
- **Pixel Perfection:** Precise control over layout, typography spacing, and margins without unexpected overlaps.
- **Text & Block Breaking:** Automatic adjustment of word and character spacing, and horizontal scaling to perfectly fit texts.
- **Hyperlinks Support:** Easily define interactive links in your layout.
- **Machine Readable:** Generated PDFs are optimized to be understood by machines, allowing content to be easily extracted automatically.

## Installation

```bash
pip install git+https://github.com/rawbby/simpdf.git@v0.1.6
```

## Example

```python
from pathlib import Path
from simpdf import PDF, Text, TextStyle, Separator, InlineImage

pdf = PDF(Path("example.pdf"))
style = TextStyle(font="Helvetica", font_size=12)

# Create a text line
line = Text(content_left="Hello", content_right="World!", style=style)
pdf.add_line(line)

# Create an image
img = InlineImage(image_path_center=Path("logo.png"), image_height=50.0)
pdf.add_line(img)

# Create a separator
sep = Separator(thickness=1)
pdf.add_line(sep)

pdf.save()
```
