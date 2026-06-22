from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_TYPES = frozenset({"txt", "pdf", "docx"})

FILE_TYPE_MAP: dict[str, str] = {
    ".txt": "txt",
    ".pdf": "pdf",
    ".docx": "docx",
}


def get_file_type(filename: str) -> str | None:
    ext = Path(filename).suffix.lower()
    return FILE_TYPE_MAP.get(ext)


def parse_file(file_path: str, file_type: str) -> str:
    if file_type == "txt":
        from app.content_ingestion.parsers.txt_parser import parse_txt

        return parse_txt(file_path)
    if file_type == "pdf":
        from app.content_ingestion.parsers.pdf_parser import parse_pdf

        return parse_pdf(file_path)
    if file_type == "docx":
        from app.content_ingestion.parsers.docx_parser import parse_docx

        return parse_docx(file_path)
    raise ValueError(f"Unsupported file type: {file_type}")
