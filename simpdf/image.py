from pathlib import Path

from PIL import Image as _PILImage
from reportlab.pdfgen.canvas import Canvas

from simpdf.inline_image import _scale_image

__all__ = ["Image"]


class Image:
    """A reusable image reference for direct canvas rendering, e.g. as a page background or watermark."""

    default_image_height: float = 100.0

    image_path: Path
    image_height: float
    dpi: float | None

    def __init__(self, image_path: Path, image_height: float | None = None, dpi: float | None = None):
        self.image_path = image_path
        self.image_height = image_height if image_height is not None else self.default_image_height
        self.dpi = dpi

    def _resolved_image(self) -> str | _PILImage.Image:
        if not self.dpi:
            return str(self.image_path)
        min_height = (self.image_height / 72.0) * self.dpi
        with _PILImage.open(self.image_path) as img:
            if img.height <= min_height:
                return str(self.image_path)
            img.load()
            scaled = _scale_image(img, min_height)
            if scaled is img:
                return str(self.image_path)
            return scaled

    def draw(self, canvas: Canvas, x: float, y: float, width: float | None = None, height: float | None = None):
        """Draws the image on the canvas with its SW corner at (x, y).

        When both width and height are given the image is stretched to fill the rectangle exactly.
        When only height is given the aspect ratio is preserved.
        """
        image = self._resolved_image()
        h = height if height is not None else self.image_height
        preserve = width is None
        kwargs: dict = {"height": h, "preserveAspectRatio": preserve, "anchor": "sw", "anchorAtXY": True}
        if width is not None:
            kwargs["width"] = width
        canvas.drawImage(image, x, y, **kwargs)
