"""
Извлечение текста из PDF в cache/ с записью в logs/ (зачаток урока 6 из гайда AiManual).
Без unstructured — только pypdf; для сканов без текстового слоя извлечённый текст может быть пустым.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
LOGS_DIR = PROJECT_ROOT / "logs"
INBOX = PROJECT_ROOT / "docs-inbox"


def setup_logging() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / "extract-pdf.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def extract_text(pdf_path: Path) -> tuple[str, int]:
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n\n".join(parts), len(reader.pages)


def default_pdf() -> Path | None:
    pdfs = sorted(INBOX.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pdfs[0] if pdfs else None


def list_inbox_pdfs() -> list[Path]:
    return sorted(INBOX.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)


def process_one_pdf(pdf_path: Path, *, skip_existing: bool) -> int:
    """Write cache artifacts for one PDF. Returns 0 on success, 1 on failure."""
    if not pdf_path.is_file():
        logging.error("Not a file: %s", pdf_path)
        return 1

    stem = pdf_path.stem
    out_dir = CACHE_DIR / stem
    txt_path = out_dir / f"{stem}.txt"
    meta_path = out_dir / f"{stem}.meta.json"

    if skip_existing and txt_path.is_file() and meta_path.is_file():
        logging.info("Skip existing cache: %s", txt_path)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    logging.info("Reading %s", pdf_path)
    try:
        text, page_count = extract_text(pdf_path)
    except Exception:
        logging.exception("Failed to read PDF")
        return 1

    txt_path.write_text(text, encoding="utf-8")
    meta = {
        "source_pdf": str(pdf_path.relative_to(PROJECT_ROOT)) if pdf_path.is_relative_to(PROJECT_ROOT) else str(pdf_path),
        "output_txt": str(txt_path.relative_to(PROJECT_ROOT)),
        "pages": page_count,
        "chars_extracted": len(text),
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    logging.info("Wrote %s (%s chars, %s pages)", txt_path, len(text), page_count)
    logging.info("Meta %s", meta_path)
    if not text.strip():
        logging.warning(
            "No text extracted — possible image-only PDF; нужен OCR или другой пайплайн."
        )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from PDF(s) into cache/")
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        help=f"Path to PDF (default: newest in {INBOX})",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help=f"Process every *.pdf in {INBOX} (newest first)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip PDF if cache already has .txt and .meta.json",
    )
    args = parser.parse_args()

    setup_logging()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if args.all:
        pdfs = list_inbox_pdfs()
        if not pdfs:
            logging.error("No *.pdf in %s", INBOX)
            sys.exit(1)
        failures = 0
        for p in pdfs:
            failures += process_one_pdf(p.resolve(), skip_existing=args.skip_existing)
        if failures:
            logging.error("Finished with %s failure(s)", failures)
            sys.exit(1)
        logging.info("Processed %s file(s)", len(pdfs))
        return

    pdf_path = args.pdf.expanduser().resolve() if args.pdf else None
    if pdf_path is None:
        candidate = default_pdf()
        if candidate is None:
            logging.error("No PDF specified and no *.pdf in %s", INBOX)
            sys.exit(1)
        pdf_path = candidate

    sys.exit(process_one_pdf(pdf_path, skip_existing=args.skip_existing))


if __name__ == "__main__":
    main()
