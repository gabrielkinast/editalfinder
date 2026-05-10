"""
Download robusto para PDFs/HTML (evita 403 de WAFs que bloqueiam clientes sem headers).
Usado pelo transformer ao enriquecer dados a partir de anexos PDF.
"""
from __future__ import annotations

import random
import logging
import subprocess
import sys
import os
from typing import Optional, List, Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Lista de User-Agents modernos para rotação
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (AppleWebKit/537.36; KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

def get_random_ua() -> str:
    return random.choice(USER_AGENTS)

def get_proxies() -> Optional[Dict[str, str]]:
    """Busca proxies das variáveis de ambiente (opcional)."""
    http_proxy = os.getenv("HTTP_PROXY")
    https_proxy = os.getenv("HTTPS_PROXY")
    if http_proxy or https_proxy:
        return {
            "http": http_proxy,
            "https": https_proxy or http_proxy,
        }
    return None

def get_pdf_headers(referer: Optional[str] = None, ua: Optional[str] = None) -> Dict[str, str]:
    headers = {
        "User-Agent": ua or get_random_ua(),
        "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    if referer:
        headers["Referer"] = referer
    return headers

def _origin_referer(url: str) -> str:
    try:
        p = urlparse(url)
        if p.scheme and p.netloc:
            return f"{p.scheme}://{p.netloc}/"
    except Exception:
        pass
    return "https://www.google.com/"


def _fetch_via_curl(url: str, referer: str, ua: str) -> Optional[bytes]:
    curl_bin = "curl.exe" if sys.platform == "win32" else "curl"
    proxies = get_proxies()
    
    cmd = [
        curl_bin,
        "-L",
        "-sS",
        "--compressed",
        "--max-time",
        "30",
        "-A",
        ua,
        "-H", "Accept: application/pdf,*/*;q=0.9",
        "-H", f"Referer: {referer}",
        "-H", "Accept-Language: pt-BR,pt;q=0.9,en-US;q=0.8",
        url,
    ]
    
    if proxies and proxies.get("http"):
        cmd.extend(["-x", proxies["http"]])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=40,
        )
        if proc.returncode == 0 and proc.stdout and len(proc.stdout) > 100:
            # Verifica se o início do arquivo é um PDF
            if proc.stdout[:4] == b"%PDF" or b"<PDF" in proc.stdout[:100]:
                return proc.stdout
    except Exception as exc:
        logger.debug("curl fallback falhou para %s: %s", url, exc)
    return None


def fetch_pdf_bytes(url: str, page_referer: Optional[str] = None) -> Optional[bytes]:
    """
    Baixa bytes de um PDF com rotação de User-Agent e suporte a Proxy.
    Ordem: requests (modern UA) -> requests (no verify) -> curl fallback.
    """
    if not url or not url.lower().startswith(("http://", "https://")):
        return None

    referer = page_referer.strip() if page_referer and page_referer.strip() else _origin_referer(url)
    if not referer.startswith("http"):
        referer = _origin_referer(url)
        
    ua = get_random_ua()
    headers = get_pdf_headers(referer, ua)
    proxies = get_proxies()

    try:
        import requests
    except Exception:
        requests = None

    if requests is not None:
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except Exception:
            pass

        # Estratégia 1 & 2: Requests com e sem verificação de SSL
        for verify in (True, False):
            try:
                r = requests.get(
                    url,
                    headers=headers,
                    timeout=30,
                    verify=verify,
                    allow_redirects=True,
                    proxies=proxies
                )
                
                if r.status_code == 200:
                    content_type = r.headers.get("Content-Type", "").lower()
                    if "application/pdf" in content_type or r.content[:4] == b"%PDF":
                        return r.content
                
                if r.status_code in (403, 401):
                    logger.debug("HTTP %s para %s; tentando próxima estratégia", r.status_code, url)
                    # Tenta mudar o User-Agent e o Referer para uma busca do Google (bypass comum de WAF)
                    headers["User-Agent"] = get_random_ua()
                    headers["Referer"] = "https://www.google.com/"
                    
            except Exception as exc:
                logger.debug("requests falhou %s (verify=%s): %s", url, verify, exc)

    # Estratégia 3: Curl (frequentemente ignora bloqueios que o requests pega)
    data = _fetch_via_curl(url, referer, ua)
    if data:
        return data

    return None
