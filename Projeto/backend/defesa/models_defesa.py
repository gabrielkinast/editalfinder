from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

@dataclass
class EditalDefesa:
    titulo: str
    link: str
    descricao: Optional[str] = None
    fonte: str = "Ministério da Defesa"
    data_publicacao: Optional[str] = None
    fim_inscricao: Optional[str] = None
    situacao: str = "Aberto"
    extras: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class NoticiaDefesa:
    titulo: str
    link: str
    descricao: Optional[str] = None
    data_publicacao: Optional[str] = None
    categoria: str = "Defesa"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
