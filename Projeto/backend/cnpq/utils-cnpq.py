from __future__ import annotations

import re
import unicodedata
from datetime import datetime, date
from typing import Optional, Iterable
from urllib.parse import urlparse


RUIDOS = (
    "Seu navegador não pode executar javascript",
    "Alguns recursos podem não funcionar corretamente",
    "Compartilhe:",
    "Copiar para área de transferência",
    "facebook",
    "twitter",
    "linkedin",
    "whatsapp",
    "telegram",
    "email",
    "imprimir",
)


PDF_NEGATIVOS = (
    "facebook",
    "twitter",
    "linkedin",
    "whatsapp",
    "telegram",
    "share",
    "compart",
    "imprimir",
    "print",
    "mailto:",
    "javascript:",
    "copiar",
    "transferencia",
)


PDF_POSITIVOS = (
    ".pdf",
    "@@download/file",
    "/download/",
    "download?",
    "download=1",
    "pdf",
)


def normalizar_espacos(texto: str | None) -> str:
    if not texto:
        return ""
    texto = texto.replace("\xa0", " ")
    return re.sub(r"\s+", " ", texto).strip()


def remover_acentos(texto: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(ch)
    )


def slug_texto(texto: str) -> str:
    return remover_acentos(normalizar_espacos(texto)).lower()


def texto_util(texto: str | None) -> bool:
    texto = normalizar_espacos(texto)
    if not texto:
        return False
    if len(texto) < 3:
        return False
    for ruido in RUIDOS:
        if ruido.lower() in texto.lower():
            return False
    return True


def parse_data_br(texto: str | None) -> Optional[date]:
    texto = normalizar_espacos(texto)
    if not texto:
        return None

    match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    if not match:
        return None

    try:
        return datetime.strptime(match.group(1), "%d/%m/%Y").date()
    except ValueError:
        return None


def extrair_datas_publicacao(texto: str) -> tuple[Optional[date], Optional[date]]:
    texto = normalizar_espacos(texto)
    publicado = None
    atualizado = None

    m_pub = re.search(r"Publicado em\s*(\d{2}/\d{2}/\d{4})", texto, flags=re.I)
    if m_pub:
        publicado = parse_data_br(m_pub.group(1))

    m_at = re.search(r"Atualizado em\s*(\d{2}/\d{2}/\d{4})", texto, flags=re.I)
    if m_at:
        atualizado = parse_data_br(m_at.group(1))

    return publicado, atualizado


def extrair_periodo_inscricoes(texto: str) -> tuple[Optional[date], Optional[date]]:
    texto = normalizar_espacos(texto)
    m = re.search(r"(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})", texto, flags=re.I)
    if not m:
        return None, None
    return parse_data_br(m.group(1)), parse_data_br(m.group(2))


def escolher_descricao(blocos: Iterable[str]) -> Optional[str]:
    melhores: list[str] = []
    for bloco in blocos:
        bloco = normalizar_espacos(bloco)
        if not texto_util(bloco):
            continue
        low = bloco.lower()
        if low.startswith("publicado em"):
            continue
        if low.startswith("inscrições") or low.startswith("inscricoes"):
            continue
        if low == "chamada":
            continue
        if len(bloco) < 40:
            continue
        melhores.append(bloco)
    if not melhores:
        return None
    return "\n\n".join(melhores[:3])


def eh_link_de_chamada(nome: str, url: str) -> bool:
    s = slug_texto(nome)
    u = slug_texto(url)
    return ("chamada" in s or "edital" in s) and ("pdf" in u or "download" in u or "@@download" in u)


def eh_pdf_url(url: str) -> bool:
    u = slug_texto(url)
    if not u:
        return False
    if any(neg in u for neg in PDF_NEGATIVOS):
        return False
    return any(pos in u for pos in PDF_POSITIVOS)


def eh_anexo_pdf_relevante(nome: str, url: str) -> bool:
    nome_s = slug_texto(nome)
    url_s = slug_texto(url)

    if not url_s:
        return False
    if any(neg in nome_s or neg in url_s for neg in PDF_NEGATIVOS):
        return False
    if not eh_pdf_url(url):
        return False

    parsed = urlparse(url)
    path = (parsed.path or "").lower()
    return path.endswith(".pdf") or "pdf" in path or "@@download" in path or "/download/" in path
