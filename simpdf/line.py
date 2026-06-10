from abc import ABC, abstractmethod

from reportlab.pdfgen.canvas import *

__all__ = ["Line"]


class Line(ABC):
    """Interface defining the methods expected by SimplePDF for layout elements."""

    @abstractmethod
    def draw(self, canvas: Canvas, baseline: float, start: float, end: float):
        """Draws the element on the canvas."""
        pass

    @property
    @abstractmethod
    def space_top(self) -> float:
        """Gets the top spacing for the element."""
        pass

    @property
    @abstractmethod
    def space_bottom(self) -> float:
        """Gets the bottom spacing for the element."""
        pass

    @property
    @abstractmethod
    def ascent(self) -> float:
        """Gets the ascent of the element."""
        pass

    @property
    @abstractmethod
    def descent(self) -> float:
        """Gets the descent of the element."""
        pass

    @property
    @abstractmethod
    def line_height_upper(self) -> float:
        """Gets the upper portion of the line height."""
        pass

    @property
    @abstractmethod
    def line_height_lower(self) -> float:
        """Gets the lower portion of the line height."""
        pass

    @property
    @abstractmethod
    def line_height(self) -> float:
        """Gets the total line height."""
        pass
