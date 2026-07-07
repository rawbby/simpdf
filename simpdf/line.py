from abc import ABC, abstractmethod

from reportlab.pdfgen.canvas import *

__all__ = ["Line"]


class Line(ABC):
    """Base class for all layout elements in SimplePDF.

    Three-method contract:

    ``unpack(line_width)``
        Pure function — no side effects, no stored state.  Returns a flat list
        of lines that fit within ``line_width``.  Compound elements (e.g.
        ``BreakText``) override this to split themselves into multiple atomic
        lines.  The default returns ``[self]``.

    ``draw(canvas, baseline, start, end)``
        Draws the element.  Assumes the content fits within ``[start, end]``
        and asserts layout constraints.  Does no layout logic.

    Height properties (``line_height``, ``space_top``, etc.)
        Stateless, pure.  Assume infinite line width — i.e. they reflect the
        element as a single undivided line regardless of actual available width.
        ``PDF.save()`` uses these only on the atomic lines returned by
        ``unpack()``, so they are always called in a context where the element
        genuinely fits.
    """

    @abstractmethod
    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        pass

    @property
    @abstractmethod
    def space_top(self) -> float:
        pass

    @property
    @abstractmethod
    def space_bottom(self) -> float:
        pass

    @property
    @abstractmethod
    def ascent(self) -> float:
        pass

    @property
    @abstractmethod
    def descent(self) -> float:
        pass

    @property
    @abstractmethod
    def line_height_upper(self) -> float:
        pass

    @property
    @abstractmethod
    def line_height_lower(self) -> float:
        pass

    @property
    @abstractmethod
    def line_height(self) -> float:
        pass

    def unpack(self, line_width: float) -> list["Line"]:
        return [self]
