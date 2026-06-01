#!/usr/bin/env python3
"""Extract text from password-protected NSFC proposal PDFs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_pdf_reader():
    try:
        from pypdf import PdfReader  # type: ignore

        return PdfReader
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore

            return PdfReader
        except Exception as exc:
            raise RuntimeError("Install pypdf or PyPDF2 in env_py3.11 to extract PDFs.") from exc


def collect_pdfs(inputs: list[str]) -> list[Path]:
    pdfs: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser()
        if path.is_dir():
            pdfs.extend(sorted(path.glob("*.pdf")))
        elif path.is_file() and path.suffix.lower() == ".pdf":
            pdfs.append(path)
        else:
            print(f"[WARN] Skipping non-PDF or missing path: {path}", file=sys.stderr)
    return pdfs


def extract_one(pdf_path: Path, password: str | None) -> dict:
    PdfReader = load_pdf_reader()
    result = {
        "file": str(pdf_path),
        "ok": False,
        "encrypted": False,
        "pages": 0,
        "text": "",
        "error": "",
    }
    try:
        reader = PdfReader(str(pdf_path))
        result["encrypted"] = bool(getattr(reader, "is_encrypted", False))
        if result["encrypted"]:
            if not password:
                raise RuntimeError("PDF is encrypted but no password was provided.")
            decrypt_result = reader.decrypt(password)
            if decrypt_result == 0:
                raise RuntimeError("Password was not accepted by the PDF reader.")

        pages = list(reader.pages)
        result["pages"] = len(pages)
        chunks: list[str] = []
        for idx, page in enumerate(pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception as exc:
                page_text = f"\n[PAGE {idx} EXTRACTION ERROR: {exc}]\n"
            chunks.append(f"\n\n===== PAGE {idx} =====\n{page_text.strip()}")
        result["text"] = "".join(chunks).strip()
        result["ok"] = True
    except Exception as exc:
        result["error"] = str(exc)
    return result


def write_outputs(results: list[dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for item in results:
        pdf_path = Path(item["file"])
        stem = pdf_path.stem
        txt_path = output_dir / f"{stem}.txt"
        json_path = output_dir / f"{stem}.json"
        txt_path.write_text(item.get("text", ""), encoding="utf-8")
        json_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        index.append(
            {
                "file": item["file"],
                "ok": item["ok"],
                "encrypted": item["encrypted"],
                "pages": item["pages"],
                "text_file": str(txt_path),
                "json_file": str(json_path),
                "error": item["error"],
            }
        )
    (output_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract text from NSFC proposal PDFs.")
    parser.add_argument("--pdf", nargs="+", required=True, help="PDF files or directories containing PDFs.")
    parser.add_argument("--password", default=None, help="PDF opening password.")
    parser.add_argument("--output", default="extracted_text", help="Output directory.")
    args = parser.parse_args()

    pdfs = collect_pdfs(args.pdf)
    if not pdfs:
        print("[ERROR] No PDF files found.", file=sys.stderr)
        return 2

    results = [extract_one(pdf, args.password) for pdf in pdfs]
    write_outputs(results, Path(args.output))

    failed = [item for item in results if not item["ok"]]
    print(f"Processed {len(results)} PDF(s); succeeded {len(results) - len(failed)}, failed {len(failed)}.")
    for item in failed:
        print(f"[FAILED] {item['file']}: {item['error']}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
