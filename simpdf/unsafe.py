from reportlab.pdfbase.pdfdoc import *

__all__ = ["unsafe_remove_reportlab_signature"]


def unsafe_remove_reportlab_signature():
    """
    Removes the default ReportLab signature from generated PDF files.
    
    WARNING: This is an invasive and unsafe operation that modifies global 
    ReportLab internals (`PDFDocument` and `PDFFile`) via monkey-patching. 
    It alters the PDF generation process to remove metadata signatures, 
    which might lead to unexpected behavior or break in future ReportLab versions.
    """

    def _pdf_document_id(self):
        if not self._ID:
            dig = self.signature.digest()
            ids = PDFText(dig, enc='raw').format(DummyDoc())
            self._ID = b'\n[' + ids + ids + b']\n'
        return self._ID

    PDFDocument.ID = _pdf_document_id

    # noinspection PyPep8Naming
    def _pdf_file_init(self, pdfVersion=PDF_VERSION_DEFAULT):
        self.strings = []
        self.write = self.strings.append
        self.offset = 0
        clean_header = pdfdocEnc("%%PDF-%s.%s" % pdfVersion) + b'\n%\223\214\213\236\n'
        self.add(clean_header)

    PDFFile.__init__ = _pdf_file_init
