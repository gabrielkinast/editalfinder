from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import date
from typing import Optional, List


@dataclass
class FapergsAnexo:
    nome: str
    url: str


@dataclass
class EditalFapergs:
    titulo: str
    url_pagina: str
    pdf_url: Optional[str] = None
    situacao: str = "Aberto"
    data_publicacao: Optional[date] = None
    prazo_envio: Optional[date] = None
    objetivo: Optional[str] = None
    descricao: Optional[str] = None
    numero_edital: Optional[str] = None
    anexos: List[FapergsAnexo] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.data_publicacao:
            d["data_publicacao"] = self.data_publicacao.isoformat()
        if self.prazo_envio:
            d["prazo_envio"] = self.prazo_envio.isoformat()
        return d
