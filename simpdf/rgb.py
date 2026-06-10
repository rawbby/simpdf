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
        def norm(v: int | float) -> float:
            if isinstance(v, int):
                v = float(v) / 255.0
            return max(0.0, min(1.0, v))

        if isinstance(value, Color):
            r, g, b = value.red, value.green, value.blue
        elif isinstance(value, (int, float)):
            r = g = b = norm(value)
        elif isinstance(value, tuple):
            if len(value) != 3:
                raise TypeError(f"Color tuple must have 3 elements, got {len(value)}")
            r = norm(value[0])
            g = norm(value[1])
            b = norm(value[2])
        elif isinstance(value, str):
            if value[0] != "#" or len(value) not in [4, 7]:
                raise TypeError(f"Invalid color string: {value}")
            if len(value) == 4:
                r = norm(int(value[1], 16) / 15)
                g = norm(int(value[2], 16) / 15)
                b = norm(int(value[3], 16) / 15)
            else:
                r = norm(int(value[1:3], 16) / 255)
                g = norm(int(value[3:5], 16) / 255)
                b = norm(int(value[5:7], 16) / 255)
        else:
            raise TypeError(f"Invalid color type: {type(value)}")

        Color.__init__(self, r, g, b)
