"""Bounded local input. Only whitelisted non-label provenance is consumed."""

import hashlib
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

MAX_RAW = 5 * 1024 * 1024
MAX_TEXT = 1024 * 1024
MAX_NODES = 30000


class InputFailure(ValueError):
    """Stable operational code; never a semantic negative."""


class Provenance(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    document_id: str
    source_url: str
    content_type: str
    raw_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    derivation_method: str


@dataclass(frozen=True)
class Block:
    start: int
    end: int
    heading: bool = False
    excluded: bool = False
    page: int | None = None
    containers: tuple[int, ...] = ()


@dataclass(frozen=True)
class InputDocument:
    provenance: Provenance
    text: str
    blocks: tuple[Block, ...]
    limitations: tuple[str, ...]


class PassiveHTML(HTMLParser):
    """Reproduce frozen node text and retain conservative structural boundaries."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts: list[str] = []
        self.blocks: list[Block] = []
        self.stack: list[tuple[str, bool, int]] = []
        self.node_counter = 0
        self.cursor = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.node_counter += 1
        if tag in {"script", "style", "noscript", "template"}:
            self.hidden += 1
        marker = " ".join(v or "" for k, v in attrs if k in {"id", "class", "role"})
        excluded = tag in {"nav", "header", "footer", "aside", "head"} or bool(
            re.search(r"(?:^|[ _-])(menu|breadcrumb|related|share|social)(?:$|[ _-])", marker, re.I)
        )
        if tag not in {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }:
            self.stack.append((tag, excluded, self.node_counter))
        if len(self.stack) > 256:
            raise InputFailure("html_depth_limit")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "template"} and self.hidden:
            self.hidden -= 1
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self.hidden or not data.strip():
            return
        if len(self.parts) >= MAX_NODES:
            raise InputFailure("html_node_limit")
        value = " ".join(data.split())
        self.parts.append(value)
        self.blocks.append(
            Block(
                self.cursor,
                self.cursor + len(value),
                any(t in {"h1", "h2", "h3", "h4"} for t, _, _ in self.stack),
                any(ex for _, ex, _ in self.stack),
                containers=tuple(
                    node
                    for tag, _, node in self.stack
                    if tag in {"html", "body", "main", "article", "section", "div", "li", "td"}
                ),
            )
        )
        self.cursor += len(value) + 1


def bounded(root: Path, name: str, prefix: str, limit: int) -> bytes:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or relative.parts[:1] != (prefix,):
        raise InputFailure("unsafe_input_path")
    try:
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise InputFailure("unsafe_input_path")
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
    except OSError as exc:
        raise InputFailure("missing_or_unreadable_file") from exc
    if len(data) > limit:
        raise InputFailure("input_size_limit")
    return data


def read_document(root: Path, meta: dict[str, Any]) -> InputDocument:
    """Never reads annotation files, category evidence, publication labels or URLs."""
    if meta["content_type"] not in {"text/html", "application/pdf"}:
        raise InputFailure("unsupported_content_type")
    raw = bounded(root, meta["raw_path"], "raw", MAX_RAW)
    frozen = bounded(root, meta["text_path"], "text", MAX_TEXT)
    if hashlib.sha256(raw).hexdigest() != meta["sha256"] or len(raw) != meta["byte_length"]:
        raise InputFailure("raw_hash_or_length_mismatch")
    if hashlib.sha256(frozen).hexdigest() != meta["text_sha256"]:
        raise InputFailure("text_hash_mismatch")
    try:
        text = frozen.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise InputFailure("invalid_utf8_text") from exc
    if not text.strip():
        raise InputFailure("empty_document")
    if any(ord(c) < 32 and c not in "\n\r\t\f" for c in text):
        raise InputFailure("invalid_text_control")
    provenance = Provenance(
        document_id=meta["document_id"],
        source_url=meta["original_url"],
        content_type=meta["content_type"],
        raw_sha256=meta["sha256"],
        text_sha256=meta["text_sha256"],
        derivation_method=meta["derivation_method"],
    )
    if meta["content_type"] == "text/html":
        if not re.search(rb"<(?:!doctype\s+html|html)\b", raw[:10000], re.I):
            raise InputFailure("invalid_html_signature")
        if not meta["derivation_method"].startswith("stdlib-HTMLParser-data-whitespace-v1"):
            raise InputFailure("unsupported_derivation")
        # The frozen HTML contract uses UTF-8 for this release. Other encodings
        # need an explicit charset adapter, not guessed replacement characters.
        parser = PassiveHTML()
        try:
            parser.feed(raw.decode("utf-8", errors="strict"))
        except UnicodeError as exc:
            raise InputFailure("unsupported_html_encoding") from exc
        if "\n".join(parser.parts) + "\n" != text:
            raise InputFailure("html_derivation_mismatch")
        blocks = tuple(parser.blocks)
        limitations: tuple[str, ...] = (
            "passive_not_rendered_DOM",
            "unfrozen_attachments_unavailable",
        )
    else:
        if not raw.startswith(b"%PDF-"):
            raise InputFailure("invalid_pdf_signature")
        if not meta["derivation_method"].startswith("poppler-pdftotext-utf8-pages-v1"):
            raise InputFailure("unsupported_derivation")
        items: list[Block] = []
        start = 0
        for page, value in enumerate(text.split("\f"), 1):
            for match in re.finditer(r"\S(?:[^\n]|\n(?!\s*\n))*", value):
                items.append(Block(start + match.start(), start + match.end(), page=page))
            start += len(value) + 1
        blocks = tuple(items)
        limitations = (
            "frozen_pdf_text_no_OCR_or_layout_recovery",
            "physical_pages_include_empty_pages",
            "unfrozen_attachments_unavailable",
        )
    return InputDocument(provenance, text, blocks, limitations)
