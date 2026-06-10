from pathlib import Path

from PIL import Image
from reportlab.pdfgen.canvas import *

from simpdf.line import Line

__all__ = ["InlineImage"]


def _scale_image(img: Image.Image, min_height: float) -> Image.Image:
    k = 1
    while img.size[1] // (k + 1) >= min_height:
        k += 1
    if k == 1:
        return img
    rem_w = img.size[0] % k
    rem_h = img.size[1] % k
    x0 = rem_w // 2
    y0 = rem_h // 2
    x1 = img.size[0] - (rem_w - x0)
    y1 = img.size[1] - (rem_h - y0)
    return img.reduce(k, (x0, y0, x1, y1))


class InlineImage(Line):
    """Represents an image element."""

    default_line_spacing: float = 10.0

    image_path_left: Path | None
    image_path_center: Path | None
    image_path_right: Path | None
    image_height: float
    line_spacing: float
    dpi: float | None

    def __init__(
            self, image_height: float,
            image_path_left: Path | None,
            image_path_center: Path | None,
            image_path_right: Path | None,
            line_spacing: float | None = None,
            dpi: float | None = None):
        self.image_path_left = image_path_left
        self.image_path_center = image_path_center
        self.image_path_right = image_path_right
        self.image_height = image_height
        self.line_spacing = line_spacing or self.default_line_spacing
        self.dpi = dpi

    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        kwargs = {"y": baseline, "height": self.image_height, "preserveAspectRatio": True, "anchorAtXY": True}
        line_width = end - start

        def get_image(path: Path | None) -> str | Image.Image | None:
            if path is None:
                return None
            if not self.dpi:
                return str(path)

            min_height = (self.image_height / 72.0) * self.dpi
            with Image.open(path) as img:
                if img.height <= min_height:
                    return str(path)

                img.load()
                scaled_img = _scale_image(img, min_height)
                if scaled_img is img:
                    return str(path)
                return scaled_img

        image_l = get_image(self.image_path_left)
        image_c = get_image(self.image_path_center)
        image_r = get_image(self.image_path_right)

        width_l = 0.0
        width_c = 0.0
        width_r = 0.0

        if image_l:
            width_l = canvas.drawInlineImage(image_l, start, anchor="sw", **kwargs)[0]
            assert width_l <= line_width

        if image_c:
            width_c = canvas.drawInlineImage(image_c, start + 0.5 * line_width, anchor="s", **kwargs)[0]
            assert width_c <= line_width

        if image_r:
            width_r = canvas.drawInlineImage(image_r, start + line_width, anchor="se", **kwargs)[0]
            assert width_r <= line_width

        if image_l and image_c:
            assert width_l + 0.5 * width_c <= 0.5 * line_width

        if image_c and image_r:
            assert width_r + 0.5 * width_c <= 0.5 * line_width

        if image_l and image_r:
            assert width_l + width_r <= line_width

    @property
    def space_top(self) -> float:
        return 0.5 * self.line_spacing

    @property
    def space_bottom(self) -> float:
        return 0.5 * self.line_spacing

    @property
    def ascent(self) -> float:
        return self.image_height

    @property
    def descent(self) -> float:
        return 0.0

    @property
    def line_height_upper(self) -> float:
        return self.space_top + self.image_height

    @property
    def line_height_lower(self) -> float:
        return 0.5 * self.line_spacing

    @property
    def line_height(self) -> float:
        return self.image_height + self.line_spacing
