#!/usr/bin/env python3
"""Diagnóstico rápido URLs military expansion."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

H = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


def probe_url(name: str, url: str) -> None:
    try:
        r = requests.get(url, headers=H, timeout=60)
        print(f"{name}: status={r.status_code} bytes={len(r.text or '')} final={r.url[:90]}")
    except Exception as e:
        print(f"{name}: ERR {e}")


def probe_arl() -> None:
    for path in ("/media-center/", "/resources/"):
        url = f"https://arl.devcom.army.mil{path}"
        r = requests.get(url, headers=H, timeout=60)
        soup = BeautifulSoup(r.text or "", "html.parser")
        print(f"\nARL {path}: {r.status_code} len={len(r.text or '')}")
        for sel in ("article", ".views-row", "h2 a", "h3 a", "time", ".field-content"):
            n = len(soup.select(sel))
            if 0 < n < 100:
                print(f"  {sel}: {n}")
        for a in soup.select("a[href]")[:200]:
            href = a.get("href") or ""
            if path.strip("/") in href and href.count("/") >= 3:
                if href not in getattr(probe_arl, "_seen", set()):
                    probe_arl._seen = getattr(probe_arl, "_seen", set()) | {href}
                    if len(probe_arl._seen) <= 6:
                        print(f"  link: {href[:100]}")


def probe_afrl_tech() -> None:
    url = "https://afresearchlab.com/technology/"
    r = requests.get(url, headers=H, timeout=60)
    soup = BeautifulSoup(r.text or "", "html.parser")
    print(f"\nafresearchlab technology: {r.status_code} len={len(r.text or '')}")
    seen = set()
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if "/technology/" in href and href not in seen and href.rstrip("/") != url.rstrip("/"):
            seen.add(href)
            tit = re.sub(r"\s+", " ", (a.get_text() or "")).strip()[:60]
            if len(tit) > 4 and len(seen) <= 15:
                print(f"  {tit} -> {href[:80]}")


def probe_wayback_listing(domain: str, path: str) -> None:
    if "spaceforce" in domain:
        wb = f"https://web.archive.org/web/2025/https://www.spaceforce.mil/{path}/"
    else:
        wb = f"https://web.archive.org/web/2025/https://www.{domain}.af.mil/{path}/"
    r = requests.get(wb, headers=H, timeout=90)
    print(f"\nwayback {domain}/{path}: {r.status_code} len={len(r.text or '')}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text or "", "html.parser")
        print("  article-listing-item:", len(soup.select("article.article-listing-item")))
        print("  Article-Display links:", len(soup.select('a[href*="Article-Display"]')))


def probe_rss_site(base: str, site: int) -> int:
    url = f"{base}/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site={site}&max=8"
    r = requests.get(url, headers=H, timeout=45)
    if r.status_code != 200 or "<item>" not in (r.text or "").lower():
        return 0
    root = ET.fromstring(r.content)
    hosts = set()
    for it in root.findall(".//item"):
        lk = (it.findtext("link") or "").strip()
        if lk:
            hosts.add(lk.split("/")[2] if "://" in lk else "")
    return len(hosts)


if __name__ == "__main__":
    probe_arl._seen = set()
    for n, u in [
        ("afmc", "https://www.afmc.af.mil/News/"),
        ("afnwc", "https://www.afnwc.af.mil/News/"),
        ("ussf", "https://www.spaceforce.mil/News/"),
    ]:
        probe_url(n, u)
    probe_arl()
    probe_afrl_tech()
    probe_wayback_listing("afmc", "News")
    probe_wayback_listing("afnwc", "News")
    probe_wayback_listing("spaceforce.mil", "News")
    for base, label in [
        ("https://www.afmc.af.mil", "afmc"),
        ("https://www.afnwc.af.mil", "afnwc"),
        ("https://www.spaceforce.mil", "ussf"),
    ]:
        for site in (1, 50, 100, 200, 945):
            n = probe_rss_site(base, site)
            if n:
                print(f"RSS {label} site={site} hosts={n}")
