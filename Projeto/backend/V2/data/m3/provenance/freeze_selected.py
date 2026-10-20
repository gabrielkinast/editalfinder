"""Bounded one-document freezing helper, NOT an opportunity extractor/crawler.

Used explicitly during M3.0 curation. Never execute downloaded HTML. Original
response entity bytes are stored before text derivation; Accept-Encoding identity.
Reacquisition must use a NEW directory/version, not overwrite frozen evidence.
"""

import json
import re
import subprocess
import time
from datetime import UTC, datetime
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 5 * 1024 * 1024
HOSTS = {
    "www.gov.br",
    "fapergs.rs.gov.br",
    "www.finep.gov.br",
    "finep.gov.br",
    "www.bndes.gov.br",
    "agenciadenoticias.bndes.gov.br",
    "brde.com.br",
    "www.brde.com.br",
    "criatec4.com",
}


def safe_url(url):
    p = urlsplit(url)
    if p.scheme != "https" or p.hostname not in HOSTS or p.username or p.password:
        raise ValueError("URL outside explicit public HTTPS institutional allowlist")
    if p.port not in (None, 443) or any(c.isspace() for c in url):
        raise ValueError("Invalid transport URL")
    return url


class Redirects(HTTPRedirectHandler):
    max_redirections = 3

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "template"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "template"} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(" ".join(data.split()))


def derive_html(raw, charset):
    parser = Text()
    parser.feed(raw.decode(charset, errors="strict"))
    return "\n".join(parser.parts) + "\n"


def freeze(document_id, url, organization, category):
    safe_url(url)
    raw_dir = ROOT / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    text_dir = ROOT / "text"
    text_dir.mkdir(exist_ok=True)
    if list(raw_dir.glob(document_id + ".*")):
        raise ValueError("Frozen document ID already exists; do not overwrite")
    request = Request(
        url,
        headers={
            "User-Agent": "EditalFinder-M30-OfflinePilot/1.0 (bounded public research snapshot)",
            "Accept-Encoding": "identity",
            "Accept": "text/html, application/pdf",
        },
    )
    now = datetime.now(UTC).isoformat()
    try:
        with build_opener(Redirects()).open(request, timeout=40) as response:
            final_url = safe_url(response.url)
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "application/pdf"}:
                raise ValueError("Unsupported response Content-Type: " + content_type)
            raw = response.read(LIMIT + 1)
            if len(raw) > LIMIT or not raw:
                raise ValueError("Empty or oversized document")
            charset = response.headers.get_content_charset() or "utf-8"
            metadata = dict(response.headers)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        failure = {
            "document_id": document_id,
            "original_url": url,
            "retrieved_at": now,
            "retrieval_status": "failed",
            "reason": str(exc),
        }
        with (ROOT / "provenance" / "retrieval_failures.jsonl").open("a") as f:
            f.write(json.dumps(failure, ensure_ascii=False) + "\n")
        print(json.dumps(failure, ensure_ascii=False))
        return None
    suffix = ".pdf" if content_type == "application/pdf" else ".html"
    raw_path = raw_dir / (document_id + suffix)
    raw_path.write_bytes(raw)
    text_path = text_dir / (document_id + ".txt")
    if suffix == ".pdf":
        if not raw.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF signature")
        # Poppler performs local text conversion only, no embedded actions followed.
        result = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(raw_path), "-"],
            check=True,
            capture_output=True,
            timeout=30,
        )
        text = result.stdout.decode("utf-8")
        method = "poppler-pdftotext-utf8-pages-v1; formfeed page separator"
    else:
        if not re.search(rb"<(?:!doctype\s+html|html)\b", raw[:10000], re.I):
            raise ValueError("Not an HTML document")
        text = derive_html(raw, charset)
        method = (
            "stdlib-HTMLParser-data-whitespace-v1; "
            "excludes script/style/noscript/template; not rendered DOM"
        )
    text_path.write_bytes(text.encode("utf-8"))
    headers_path = ROOT / "provenance" / (document_id + ".headers.json")
    # No cookies/auth headers retained. Public transport metadata only.
    kept = {
        k: v
        for k, v in metadata.items()
        if k.lower()
        in {
            "content-type",
            "content-length",
            "last-modified",
            "etag",
            "date",
            "content-disposition",
            "content-encoding",
        }
    }
    headers_path.write_text(json.dumps(kept, indent=2, ensure_ascii=False) + "\n")
    doc = {
        "document_id": document_id,
        "original_url": url,
        "final_url": final_url,
        "source_organization": organization,
        "retrieved_at": now,
        "original_filename": unquote(urlsplit(final_url).path.rsplit("/", 1)[-1]) or "index.html",
        "content_type": content_type,
        "byte_length": len(raw),
        "sha256": sha256(raw).hexdigest(),
        "raw_path": str(raw_path.relative_to(ROOT)),
        "text_path": str(text_path.relative_to(ROOT)),
        "text_sha256": sha256(text.encode("utf-8")).hexdigest(),
        "publication_date": None,
        "document_version": None,
        "source_authority_notes": (
            "Public HTTPS page hosted by the named institution; "
            "authorship asserted by host/content, not cryptographically authenticated. "
            "Not source-readiness approval."
        ),
        "retrieval_status": "acquired",
        "restrictions": (
            "Research pilot local frozen copy only; no redistribution license inferred. "
            "No scripts executed, no forms submitted, "
            "no applicant records intentionally collected. "
            "Public navigation/staff attribution may remain in original bytes."
        ),
        "document_category": category,
        "category_evidence": "",
        "derivation_method": method,
    }
    time.sleep(1)
    return doc
