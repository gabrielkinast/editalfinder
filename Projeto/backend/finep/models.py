from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional


@dataclass(slots=True)
class EditalFinep:
    titulo: str
    url: str
    situacao: Optional[str] = None
    data_publicacao: Optional[date] = None
    prazo_envio: Optional[date] = None
    fonte_recurso: Optional[str] = None
    publico_alvo: Optional[str] = None
    temas: Optional[str] = None
    objetivo: Optional[str] = None
    descricao: Optional[str] = None
    pdf_url: Optional[str] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        for key in ("data_publicacao", "prazo_envio"):
            if data[key] is not None:
                data[key] = data[key].isoformat()
        return data
