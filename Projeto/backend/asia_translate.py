"""asia_translate.py

Stub estavel de tradutor para fontes asiaticas.

Objetivos:
  - Manter o crawler INDEPENDENTE de qualquer servico externo.
  - Oferecer uma interface unica que pode ser substituida por DeepL, Google
    Translate, MarianMT local, etc., sem mudar o restante do codigo.
  - Garantir que, quando o tradutor estiver desativado, os itens passem
    com `necessita_traducao=True` e os campos traduzidos vazios.

Uso pretendido:
  - Pode ser chamado dentro do transformer (rota Asia) APOS build_asia_extras
    para popular `titulo_traduzido` e `descricao_traduzida`.
  - Por padrao, `enrich_asia_translation()` e um no-op: nao faz nenhuma
    chamada externa. Para ativar tradutor real:
      a) implementar uma classe que herde de `BaseTranslator`;
      b) registrar via `set_default_translator(MyTranslator())`;
      c) chamar `enrich_asia_translation(extras)` no fluxo desejado.

Configuracao por variaveis de ambiente (opcional):
  - EDITALFINDER_ASIA_TRANSLATOR     # nome do backend ('noop' | 'deepl')
  - EDITALFINDER_ASIA_TRANSLATOR_KEY # chave do servico (se aplicavel)
  - EDITALFINDER_ASIA_TARGET_LANG    # idioma alvo, default 'pt'
  - EDITALFINDER_ASIA_TRANSLATE_MAX  # limite de caracteres por chamada
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional, Protocol


@dataclass
class TranslationResult:
    """Resultado de uma traducao."""
    text: str
    source_lang: str
    target_lang: str
    backend: str
    ok: bool


class BaseTranslator(Protocol):
    """Contrato minimo de qualquer backend de traducao."""

    name: str

    def translate(
        self,
        text: str,
        *,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        ...


# ---------------------------------------------------------------------------
# Backend noop (default)
# ---------------------------------------------------------------------------

class NoopTranslator:
    """Tradutor padrao: nao faz traducao real, retorna string vazia.

    Em conjunto com `enrich_asia_translation`, isso preserva o original
    e marca `necessita_traducao=True`.
    """

    name = "noop"

    def translate(
        self,
        text: str,
        *,
        source_lang: str = "auto",
        target_lang: str = "pt",
    ) -> TranslationResult:
        return TranslationResult(
            text="",
            source_lang=source_lang,
            target_lang=target_lang,
            backend=self.name,
            ok=False,
        )


# ---------------------------------------------------------------------------
# Backend DeepL (placeholder; ativacao por chave de API)
# ---------------------------------------------------------------------------

class DeepLTranslator:
    """Stub para DeepL. NAO faz chamada externa por padrao.

    Para ativar de verdade, instale `requests` (ja dependencia do projeto)
    e DESCOMENTE o bloco indicado em `translate`. A chave deve vir de
    EDITALFINDER_ASIA_TRANSLATOR_KEY.
    """

    name = "deepl"
    ENDPOINT = "https://api-free.deepl.com/v2/translate"

    def __init__(self, api_key: Optional[str] = None, max_chars: int = 4500):
        self.api_key = api_key or os.environ.get("EDITALFINDER_ASIA_TRANSLATOR_KEY", "")
        self.max_chars = max_chars

    def translate(
        self,
        text: str,
        *,
        source_lang: str = "auto",
        target_lang: str = "pt",
    ) -> TranslationResult:
        if not self.api_key or not text:
            return TranslationResult("", source_lang, target_lang, self.name, False)

        # Bloco real (mantido comentado ate o usuario decidir ativar):
        # try:
        #     import requests
        #     payload = {
        #         "auth_key": self.api_key,
        #         "text": text[: self.max_chars],
        #         "target_lang": target_lang.upper(),
        #     }
        #     if source_lang and source_lang != "auto":
        #         payload["source_lang"] = source_lang.upper()
        #     resp = requests.post(self.ENDPOINT, data=payload, timeout=20)
        #     resp.raise_for_status()
        #     data = resp.json()
        #     translated = (data.get("translations") or [{}])[0].get("text", "")
        #     return TranslationResult(translated, source_lang, target_lang, self.name, bool(translated))
        # except Exception:
        #     return TranslationResult("", source_lang, target_lang, self.name, False)

        return TranslationResult("", source_lang, target_lang, self.name, False)


# ---------------------------------------------------------------------------
# Singleton de tradutor padrao
# ---------------------------------------------------------------------------

_DEFAULT: Optional[BaseTranslator] = None


def _resolve_default() -> BaseTranslator:
    backend = (os.environ.get("EDITALFINDER_ASIA_TRANSLATOR") or "noop").strip().lower()
    if backend == "deepl":
        return DeepLTranslator()
    return NoopTranslator()


def get_default_translator() -> BaseTranslator:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = _resolve_default()
    return _DEFAULT


def set_default_translator(translator: BaseTranslator) -> None:
    """Permite substituir o tradutor em runtime (testes ou plug-in)."""
    global _DEFAULT
    _DEFAULT = translator


# ---------------------------------------------------------------------------
# Funcao de alto nivel
# ---------------------------------------------------------------------------

def translate_text(
    text: str,
    *,
    source_lang: str = "auto",
    target_lang: Optional[str] = None,
) -> TranslationResult:
    """Funcao de conveniencia: usa o tradutor padrao."""
    target_lang = target_lang or os.environ.get("EDITALFINDER_ASIA_TARGET_LANG", "pt")
    return get_default_translator().translate(
        text or "",
        source_lang=source_lang,
        target_lang=target_lang,
    )


def enrich_asia_translation(extras: Dict[str, object]) -> Dict[str, object]:
    """Popula `titulo_traduzido` e `descricao_traduzida` em-place.

    - Se ja existirem nao-vazios, nao mexe.
    - Se backend padrao for noop, deixa vazios e mantem necessita_traducao=True.
    - Se backend retornar texto, popula e seta necessita_traducao=False.
    """
    if not isinstance(extras, dict):
        return extras

    src_lang = str(extras.get("idioma_original") or "auto")
    target_lang = os.environ.get("EDITALFINDER_ASIA_TARGET_LANG", "pt")

    titulo_orig = str(extras.get("titulo_original") or "")
    desc_orig = str(extras.get("descricao_original") or "")
    titulo_trad = str(extras.get("titulo_traduzido") or "")
    desc_trad = str(extras.get("descricao_traduzida") or "")

    translator = get_default_translator()

    if titulo_orig and not titulo_trad:
        r = translator.translate(titulo_orig, source_lang=src_lang, target_lang=target_lang)
        if r.ok and r.text:
            extras["titulo_traduzido"] = r.text
            titulo_trad = r.text

    if desc_orig and not desc_trad:
        r = translator.translate(desc_orig, source_lang=src_lang, target_lang=target_lang)
        if r.ok and r.text:
            extras["descricao_traduzida"] = r.text
            desc_trad = r.text

    extras["necessita_traducao"] = not (titulo_trad and desc_trad) and src_lang in ("ja", "zh")
    return extras


__all__ = [
    "TranslationResult", "BaseTranslator",
    "NoopTranslator", "DeepLTranslator",
    "get_default_translator", "set_default_translator",
    "translate_text", "enrich_asia_translation",
]
