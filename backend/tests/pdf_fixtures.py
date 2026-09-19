"""Builds minimal, valid, hand-crafted single-page PDFs for tests.

Avoids adding a PDF-generation library as a dependency just for test
fixtures - PyPDF2 (already a runtime dependency) can read these directly.
"""


def build_pdf_bytes(text: str = "Hello World") -> bytes:
    stream_content = f"BT /F1 24 Tf 10 100 Td ({text}) Tj ET".encode()
    return _build_single_page_pdf(stream_content)


def build_blank_pdf_bytes() -> bytes:
    return _build_single_page_pdf(b"")


def _build_single_page_pdf(stream_content: bytes) -> bytes:
    objs = [
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n",
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n",
        b"3 0 obj<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/MediaBox[0 0 200 200]/Contents 5 0 R>>endobj\n",
        b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n",
        b"5 0 obj<</Length " + str(len(stream_content)).encode() + b">>\nstream\n" + stream_content + b"\nendstream\nendobj\n",
    ]

    body = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objs:
        offsets.append(len(body))
        body += obj

    xref_start = len(body)
    xref = b"xref\n0 " + str(len(objs) + 1).encode() + b"\n0000000000 65535 f \n"
    for offset in offsets[1:]:
        xref += ("%010d 00000 n \n" % offset).encode()

    trailer = (
        b"trailer<</Size " + str(len(objs) + 1).encode() + b"/Root 1 0 R>>\nstartxref\n"
        + str(xref_start).encode()
        + b"\n%%EOF"
    )

    return body + xref + trailer
