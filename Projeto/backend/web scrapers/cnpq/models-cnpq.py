from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import date
from typing import Optional, List


@dataclass
class AnexoCNPq:
    nome: str
    url: str
    tipo: str = "anexo"


@dataclass
class EditalCNPq:
    titulo: str
    url_pagina: str
    url_chamada: Optional[str] = None
    publicado_em: Optional[date] = None
    atualizado_em: Optional[date] = None
    inscricoes_inicio: Optional[date] = None
    inscricoes_fim: Optional[date] = None
    situacao: str = "Aberta para Submissão"
    descricao: Optional[str] = None
    anexos: List[AnexoCNPq] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        for key in ("publicado_em", "atualizado_em", "inscricoes_inicio", "inscricoes_fim"):
            if data[key] is not None:
                data[key] = data[key].isoformat()
        return data
