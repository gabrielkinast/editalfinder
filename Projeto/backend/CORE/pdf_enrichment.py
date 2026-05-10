from __future__ import annotations

from io import BytesIO
from typing import Optional

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None  # type: ignore

try:
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover
    pdfplumber = None  # type: ignore


def extract_pdf_text_with_fallback(pdf_bytes: bytes, *, max_pages: int = 10) -> Optional[str]:
    """Extrai texto de PDF com fallback pypdf -> pdfplumber.

    Mantem limite de paginas por seguranca/performance.
    """
    if not pdf_bytes or max_pages <= 0:
        return None

    text = None
    if PdfReader is not None:
        try:
            reader = PdfReader(BytesIO(pdf_bytes), strict=False)
            pages = reader.pages[:max_pages]
            text = "\n".join((p.extract_text() or "") for p in pages).strip()
        except Exception:
            text = None

    if text:
        return text.replace("\x00", "") if "\x00" in text else text

    if pdfplumber is not None:
        try:
            chunks = []
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages[:max_pages]:
                    chunks.append((page.extract_text() or "").strip())
            text = "\n".join(c for c in chunks if c).strip()
        except Exception:
            return None

    if not text:
        return None
    return text.replace("\x00", "") if "\x00" in text else text

