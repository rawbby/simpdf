from simpdf.vertical_space import VerticalSpace

__all__ = ["PageFlush"]


class PageFlush(VerticalSpace):
    """A sentinel line that forces a page break when the PDF layout engine encounters it."""

    def __init__(self):
        super().__init__(1.0e9)
