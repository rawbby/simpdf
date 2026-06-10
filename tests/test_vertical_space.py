import pytest
from simpdf import PDF, Text, TextStyle, VerticalSpace
from tests.pdf_reverse_tool import PDFReverseTool


@pytest.fixture
def style():
    return TextStyle(font="Helvetica", font_size=12)


def _line1_y0(tool: PDFReverseTool) -> float:
    return next(t for t in tool.get_text_bboxes() if "Line1" in t["text"])["bbox"][1]


def _line2_y0(tool: PDFReverseTool) -> float:
    return next(t for t in tool.get_text_bboxes() if "Line2" in t["text"])["bbox"][1]


def test_vertical_space_between_lines(tmp_path, style):
    """VerticalSpace(extra) widens the gap between two text lines by exactly extra."""
    extra = 50.0

    pdf_ref = PDF(output_path=tmp_path / "ref.pdf")
    pdf_ref.add_line(Text(content_left="Line1", style=style))
    pdf_ref.add_line(Text(content_left="Line2", style=style))
    pdf_ref.save()

    pdf_vs = PDF(output_path=tmp_path / "vs.pdf")
    pdf_vs.add_line(Text(content_left="Line1", style=style))
    pdf_vs.add_line(VerticalSpace(extra))
    pdf_vs.add_line(Text(content_left="Line2", style=style))
    pdf_vs.save()

    ref = PDFReverseTool(str(tmp_path / "ref.pdf"))
    vs = PDFReverseTool(str(tmp_path / "vs.pdf"))

    # Line1 must be at the same vertical position in both PDFs.
    assert abs(_line1_y0(ref) - _line1_y0(vs)) < 0.5

    gap_ref = _line2_y0(ref) - _line1_y0(ref)
    gap_vs = _line2_y0(vs) - _line1_y0(vs)

    assert abs((gap_vs - gap_ref) - extra) < 0.5, (
        f"VerticalSpace({extra}) should add {extra} pts to the gap, "
        f"but added {gap_vs - gap_ref:.2f}"
    )


def test_vertical_space_ignored_as_first_line(tmp_path, style):
    """VerticalSpace at the top of a page is dropped entirely from page layout (property 1)."""
    extra = 50.0

    # VerticalSpace first, then Line1 and Line2
    pdf_vs_first = PDF(output_path=tmp_path / "vs_first.pdf")
    pdf_vs_first.add_line(VerticalSpace(extra))
    pdf_vs_first.add_line(Text(content_left="Line1", style=style))
    pdf_vs_first.add_line(Text(content_left="Line2", style=style))
    pdf_vs_first.save()

    # No VerticalSpace at top
    pdf_ref = PDF(output_path=tmp_path / "ref.pdf")
    pdf_ref.add_line(Text(content_left="Line1", style=style))
    pdf_ref.add_line(Text(content_left="Line2", style=style))
    pdf_ref.save()

    vs_first = PDFReverseTool(str(tmp_path / "vs_first.pdf"))
    ref = PDFReverseTool(str(tmp_path / "ref.pdf"))

    # Both lines must land at exactly the same positions — leading VerticalSpace is a no-op.
    assert abs(_line1_y0(vs_first) - _line1_y0(ref)) < 0.5, (
        f"Line1 y shifted by {_line1_y0(vs_first) - _line1_y0(ref):.2f} with leading VerticalSpace"
    )
    assert abs(_line2_y0(vs_first) - _line2_y0(ref)) < 0.5, (
        f"Line2 y shifted by {_line2_y0(vs_first) - _line2_y0(ref):.2f} with leading VerticalSpace"
    )
