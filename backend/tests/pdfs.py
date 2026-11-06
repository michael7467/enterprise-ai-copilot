"""Small real PDFs for tests, made with reportlab."""
import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def make_pdf(pages: list[str], image_only_pages: set[int] = frozenset()) -> bytes:
    """One PDF page per string; lines wrap at about 90 characters. Pages in image_only_pages get
    only a drawn rectangle and no text layer, like a scanned page."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    for i, text in enumerate(pages, start=1):
        if i in image_only_pages:
            c.rect(100, 400, 300, 200, fill=1)
        else:
            y = 800
            for para in text.split("\n\n"):
                words, line = para.split(), ""
                for w in words:
                    if len(line) + len(w) > 90:
                        c.drawString(50, y, line); y -= 14; line = ""
                    line += w + " "
                c.drawString(50, y, line); y -= 24
        c.showPage()
    c.save()
    return buf.getvalue()
