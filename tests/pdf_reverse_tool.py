import fitz

class PDFReverseTool:
    def __init__(self, pdf_path: str | bytes):
        self.doc = fitz.open(pdf_path)

    def get_text_bboxes(self, page_index: int = 0):
        """Returns a list of dicts with text and bbox."""
        page = self.doc[page_index]
        blocks = page.get_text("dict")["blocks"]
        results = []
        for b in blocks:
            if b.get("type") == 0:  # text block
                for l in b["lines"]:
                    for s in l["spans"]:
                        results.append({
                            "text": s["text"],
                            "bbox": s["bbox"]  # (x0, y0, x1, y1)
                        })
        return results

    def get_image_bboxes(self, page_index: int = 0):
        """Returns a list of dicts with image bboxes."""
        page = self.doc[page_index]
        blocks = page.get_text("dict")["blocks"]
        results = []
        for b in blocks:
            if b.get("type") == 1:  # image block
                results.append({
                    "bbox": b["bbox"]
                })
        return results

    def get_drawings(self, page_index: int = 0):
        """Returns a list of vector drawings (like lines/separators)."""
        page = self.doc[page_index]
        return page.get_drawings()
