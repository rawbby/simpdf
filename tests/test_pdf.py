from simpdf import PDF, Separator

def test_pdf_init(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf = PDF(output_path=pdf_path)
    assert pdf.page_width > 0
    assert pdf.page_height > 0
    assert pdf.content_width > 0
    assert pdf.content_height > 0
    assert len(pdf.lines) == 0

def test_pdf_add_line(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf = PDF(output_path=pdf_path)
    sep = Separator()
    pdf.add_line(sep)
    assert len(pdf.lines) == 1
    assert pdf.lines[0] == sep
