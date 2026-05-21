#!/usr/bin/env python3
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "EditalFinderBot/1.0 (+public scientific/news monitoring)"}
BASE = "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias"
r = requests.get(BASE, headers=HEADERS, timeout=60)
print("hub", r.status_code, len(r.text))
soup = BeautifulSoup(r.text, "html.parser")
# rss links
for l in soup.find_all("link", href=True):
    t = (l.get("type") or "").lower()
    if "rss" in t or "atom" in t or "feed" in (l.get("href") or "").lower():
        print("link", l.get("href"), l.get("type"))
for a in soup.find_all("a", href=True):
    h = a.get("href", "")
    if "rss" in h.lower() or "atom" in h.lower():
        print("a feed", h)
# news article links
links = []
for a in soup.select("a[href]"):
    href = urljoin(BASE, a["href"]).split("#")[0]
    if "/noticias/" in href and href.rstrip("/") != BASE.rstrip("/"):
        if re.search(r"/noticias/\d{4}/", href) or re.search(r"/@@search", href):
            pass
        tit = " ".join(a.get_text().split()).strip()
        if len(tit) > 15 and href not in {x[0] for x in links}:
            links.append((href, tit[:80]))
print("article links sample", len(links))
for h, t in links[:15]:
    print(" ", h[:90], "|", t)
# try aggregator search RSS patterns
for path in [
    "/noticias/feed/RSS",
    "/noticias/feed/Atom",
    "/acompanhe-o-mcti/noticias/feed/RSS",
    "/acompanhe-o-mcti/noticias/feed/Atom",
]:
    url = "https://www.gov.br/mcti/pt-br" + path
    rr = requests.get(url, headers=HEADERS, timeout=30)
    print("try", url, rr.status_code, (rr.text or "")[:80])
