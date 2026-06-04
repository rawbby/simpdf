from reportlab.lib.colors import Color

__all__ = ["ColorType", "RGB"]

ColorType = Color | str | int | float | tuple[int | float, int | float, int | float]


class RGB(Color):
    """
    Represents an RGB color without an alpha channel.
    Accepts ReportLab colors, scalars (grayscale), 3-tuples (RGB), or color strings like "#RRGGBB" or "#RGB".
    Ints are interpreted as 0-255, floats as 0.0-1.0.
    """

    def __init__(self, value: ColorType):
        """Initializes a Color from a variety of formats."""
        r = 0.0
        g = 0.0
        b = 0.0
        if isinstance(value, int) or isinstance(value, float):
            r = g = b = self._norm(value)
        elif isinstance(value, tuple):
            r = self._norm(value[0])
            g = self._norm(value[1])
            b = self._norm(value[2])
        elif isinstance(value, str):
            if value[0] != "#" or len(value) not in [4, 7]:
                raise ValueError(f"Invalid color string: {value}")
            if len(value) == 4:
                r = self._norm(int(value[1], 16) / 15)
                g = self._norm(int(value[2], 16) / 15)
                b = self._norm(int(value[3], 16) / 15)
            else:
                r = self._norm(int(value[1:3], 16) / 255)
                g = self._norm(int(value[3:5], 16) / 255)
                b = self._norm(int(value[5:7], 16) / 255)
        Color.__init__(self, r, g, b)

    @staticmethod
    def _norm(v: int | float) -> float:
        if isinstance(v, float) and (v < 0.0 or v > 1.0):
            raise ValueError(f"Float color value must be between 0 and 1, got {v}")

        if isinstance(v, int):
            if v < 0 or v > 255:
                raise ValueError(f"Integer color value must be between 0 and 255, got {v}")
            v = float(v) / 255.0

        return v

    def __repr__(self) -> str:
        return f"Color(r={self.red}, g={self.green}, b={self.blue})"
