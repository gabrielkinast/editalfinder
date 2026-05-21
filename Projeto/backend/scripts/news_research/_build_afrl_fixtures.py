#!/usr/bin/env python3
"""Gera fixtures HTML para diretorias AFRL (RA/RJ/RR) a partir de snapshot de diagnóstico."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENT = (
    Path(__file__).resolve().parents[2].parent
    / ".cursor"
    / "projects"
    / "d-Computational-Physics-My-Projects-edital"
    / "agent-tools"
    / "0a5fea26-ae70-4288-8ded-5f60802b695d.txt"
)
# fallback path used in prior session
AGENT_ALT = Path(
    r"C:\Users\ResTIC55\.cursor\projects\d-Computational-Physics-My-Projects-edital"
    r"\agent-tools\0a5fea26-ae70-4288-8ded-5f60802b695d.txt"
)
OUT = ROOT / "fixtures" / "news_research"


def _cards_from_text(text: str, limit: int = 50) -> list[tuple[str, str]]:
    return re.findall(
        r"- \[(.+?)\]\((https://www\.afrl\.af\.mil/News/Article-Display/Article/\d+/[^)]+)\)",
        text,
    )[:limit]


def _write_fixture(code: str, heading: str, cards: list[tuple[str, str]]) -> None:
    parts = [
        "<html><body><section class='directorate-highlights'>",
        f"<h2>{heading}</h2>",
    ]
    for summary, href in cards:
        tit = summary.split(" Read More")[0].strip()[:220]
        if len(tit) < 12:
            tit = summary[:120]
        parts.append(
            f"<article class='highlight-card'><h1>{tit}</h1>"
            f"<p>{summary[:500]} <a href='{href}'>Read More</a></p></article>"
        )
    parts.append("</section></body></html>")
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"afrl_{code}_directorate.html"
    path.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {path.name} ({len(cards)} cards)")


def main() -> int:
    agent = AGENT_ALT if AGENT_ALT.is_file() else AGENT
    text = agent.read_text(encoding="utf-8", errors="replace") if agent.is_file() else ""
    links = _cards_from_text(text, 50) if text else []
    if not links:
        print("[WARN] sem snapshot RA; fixtures RJ/RR vazios")
    _write_fixture("RA", "Air Warfare Directorate Highlights", links[:45] if links else [])
    _write_fixture("RJ", "Space Warfare Directorate Highlights", links[:12] if links else [])
    _write_fixture("RR", "Technology Transition Office Highlights", links[12:24] if links else [])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
