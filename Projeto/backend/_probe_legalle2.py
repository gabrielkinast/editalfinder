import re
import ssl
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
ctx = ssl.create_default_context()
url = "https://portal.editais.legalleconcursos.com.br/edital/ver/2410"
req = Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
with urlopen(req, timeout=45, context=ctx) as r:
    html = r.read().decode("utf-8", "replace")
Path("_legalle_detalhe.html").write_text(html[:120000], encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")
flags = [
    "TopoInformacoes", "blocoPublicacoes", "blocoListaVagas", "blocoEventos",
    "p.insc", "situacaoConcurso", "periodoInscricoes", "pgInformacoes",
]
for f in flags:
    print(f, bool(soup.select_one(f"#{f}") or soup.select(f".{f}") or f in html))
print("h1", soup.find("h1").get_text(" ", strip=True)[:120] if soup.find("h1") else None)
print("h2 sample", [h.get_text(" ", strip=True)[:80] for h in soup.find_all("h2")[:5]])
for sel in ("p.insc", "p.periodoInscricoes", "p.situacaoConcurso", "#blocoPublicacoes li.pdf a"):
    nodes = soup.select(sel)
    print(sel, len(nodes), nodes[0].get_text(" ", strip=True)[:100] if nodes else "")
pdfs = [(a.get_text(" ", strip=True), a.get("href")) for a in soup.select("a[href*='.pdf']")[:8]]
print("pdfs", pdfs)
