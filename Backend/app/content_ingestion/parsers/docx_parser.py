from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def parse_docx(file_path: str) -> str:
    try:
        import docx

        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs)
        if text.strip():
            return text.strip()
    except ImportError:
        logger.warning("python-docx not installed")
    except Exception as e:
        logger.warning("python-docx extraction failed: %s", e)

    raise RuntimeError(
        "No DOCX parser available. Install python-docx."
    )
