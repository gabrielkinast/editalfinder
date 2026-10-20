"""Verify passive text-view reproduction locally; no network or opportunity extraction.

Run from backend/V2: .venv/bin/python -B data/m3/provenance/verify_derivation.py
Requires the existing Poppler pdftotext for PDF views. Never changes evidence.
"""

import json
import subprocess
from email.message import Message
from pathlib import Path

from freeze_selected import derive_html

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "corpus_manifest.json").read_text())
checked = []
for doc in manifest["documents"]:
    raw = (root / doc["raw_path"]).read_bytes()
    frozen = (root / doc["text_path"]).read_bytes()
    if doc["content_type"] == "text/html":
        headers = json.loads(
            (root / "provenance" / (doc["document_id"] + ".headers.json")).read_text()
        )
        message = Message()
        message["content-type"] = next(
            (v for k, v in headers.items() if k.lower() == "content-type"), "text/html"
        )
        charset = message.get_content_charset() or "utf-8"
        reproduced = derive_html(raw, charset).encode("utf-8")
    else:
        reproduced = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(root / doc["raw_path"]), "-"],
            capture_output=True,
            check=True,
            timeout=30,
        ).stdout
    if reproduced != frozen:
        raise ValueError("View derivation mismatch: " + doc["document_id"])
    checked.append(doc["document_id"])
print(json.dumps({"status": "PASS", "documents": len(checked), "checked_ids": checked}))
