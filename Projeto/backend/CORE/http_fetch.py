"""
Download robusto para PDFs/HTML (evita 403 de WAFs que bloqueiam clientes sem headers).
Usado pelo transformer ao enriquecer dados a partir de anexos PDF.
"""
from __future__ import annotations

import logging
import subprocess
import sys
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

PDF_HEADERS_BASE = {
    "User-Agent": USER_AGENT,
    "Accept": "application/pdf,*/*;q=0.9",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Upgrade-Insecure-Requests": "1",
}


def _origin_referer(url: str) -> str:
    try:
        p = urlparse(url)
        if p.scheme and p.netloc:
            return f"{p.scheme}://{p.netloc}/"
    except Exception:
        pass
    return "https://www.google.com/"


def _fetch_via_curl(url: str, referer: str) -> Optional[bytes]:
    curl_bin = "curl.exe" if sys.platform == "win32" else "curl"
    cmd = [
        curl_bin,
        "-L",
        "-sS",
        "--compressed",
        "--max-time",
        "25",
        "-A",
        USER_AGENT,
        "-H",
        f"Accept: {PDF_HEADERS_BASE['Accept']}",
        "-H",
        f"Referer: {referer}",
        "-H",
        "Accept-Language: pt-BR,pt;q=0.9,en-US;q=0.8",
        url,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=35,
        )
        if proc.returncode == 0 and proc.stdout and len(proc.stdout) > 100:
            if proc.stdout[:4] == b"%PDF":
                return proc.stdout
    except Exception as exc:
        logger.debug("curl fallback falhou para %s: %s", url, exc)
    return None


def fetch_pdf_bytes(url: str, page_referer: Optional[str] = None) -> Optional[bytes]:
    """
    Baixa bytes de um PDF com headers de navegador + Referer na origem do host.
    Se ``page_referer`` for a URL da página do edital (HTML), muitos WAFs aceitam melhor.
    Ordem: requests (verify) -> requests (verify=False) -> curl.
    """
    if not url or not url.lower().startswith(("http://", "https://")):
        return None

    referer = page_referer.strip() if page_referer and page_referer.strip() else _origin_referer(url)
    if not referer.startswith("http"):
        referer = _origin_referer(url)
    headers = {**PDF_HEADERS_BASE, "Referer": referer}
    try:
        pdf_host = urlparse(url).netloc.lower().lstrip("www.")
        ref_host = urlparse(referer).netloc.lower().lstrip("www.")
        headers["Sec-Fetch-Site"] = "same-origin" if pdf_host == ref_host else "cross-site"
    except Exception:
        pass

    try:
        import requests
    except Exception:
        requests = None  # type: ignore

    if requests is not None:
        try:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception:
            pass
        for verify in (True, False):
            try:
                r = requests.get(
                    url,
                    headers=headers,
                    timeout=25,
                    verify=verify,
                    allow_redirects=True,
                )
                if r.status_code == 200 and r.content[:4] == b"%PDF":
                    return r.content
                if r.status_code == 403:
                    logger.debug(
                        "PDF HTTP %s para %s (verify=%s); tentando próxima estratégia",
                        r.status_code,
                        url,
                        verify,
                    )
            except Exception as exc:
                logger.debug("requests PDF falhou %s verify=%s: %s", url, verify, exc)

    data = _fetch_via_curl(url, referer)
    if data:
        return data

    return None
