from simpdf import PDF, Text, TextStyle, InlineImage
from tests.pdf_reverse_tool import PDFReverseTool

def test_pdf_bounding_boxes(tmp_path, generate_image):
    pdf_path = tmp_path / "bbox_test.pdf"
    pdf = PDF(output_path=pdf_path)
    style = TextStyle(font="Helvetica", font_size=12)
    
    # 1. Add Text
    line1 = Text(content_left="LeftText", content_center="CenterText", content_right="RightText", style=style)
    pdf.add_line(line1)
    
    # 2. Add Image
    img_path = generate_image(width=100, height=50)
    img = InlineImage(image_height=50, image_path_left=img_path, image_path_center=None, image_path_right=None)
    pdf.add_line(img)
    
    pdf.save()
    
    # Analyze the generated PDF
    tool = PDFReverseTool(str(pdf_path))
    texts = tool.get_text_bboxes()
    images = tool.get_image_bboxes()
    
    # There should be 3 text spans
    assert len(texts) >= 3
    left_found = any("LeftText" in t["text"] for t in texts)
    center_found = any("CenterText" in t["text"] for t in texts)
    right_found = any("RightText" in t["text"] for t in texts)
    
    assert left_found, "Left text not found"
    assert center_found, "Center text not found"
    assert right_found, "Right text not found"
    
    # There should be 1 image
    assert len(images) == 1
    
    # Let's check some basic geometry expectations
    # Left text x0 should be close to the left margin (which is usually 1 inch = 72)
    left_texts = [t for t in texts if "LeftText" in t["text"]]
    assert len(left_texts) > 0
    left_text_x0 = left_texts[0]["bbox"][0]
    assert abs(left_text_x0 - pdf.margin_left) < 2.0  # Pixel perfect check within margin of error

    # Image x0 should also be close to left margin because image_path_left is set
    img_bbox = images[0]["bbox"]
    img_x0 = img_bbox[0]
    assert abs(img_x0 - pdf.margin_left) < 2.0
