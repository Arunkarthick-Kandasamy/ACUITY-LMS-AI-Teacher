from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str) -> str:
    try:
        import pdfminer.high_level as pdfminer

        text = pdfminer.extract_text(file_path)
        if text and text.strip():
            return text.strip()
    except ImportError:
        logger.warning("pdfminer not installed, trying PyMuPDF")
    except Exception as e:
        logger.warning("pdfminer extraction failed: %s", e)

    try:
        import fitz

        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        if text and text.strip():
            return text.strip()
    except ImportError:
        logger.warning("PyMuPDF not installed")
    except Exception as e:
        logger.warning("PyMuPDF extraction failed: %s", e)

    raise RuntimeError(
        "No PDF parser available. Install pdfminer.six or PyMuPDF (fitz)."
    )
