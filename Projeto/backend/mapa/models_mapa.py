from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

@dataclass
class EditalMAPA:
    titulo: str
    link: str
    descricao: Optional[str] = None
    fonte: str = "MAPA"
    data_publicacao: Optional[str] = None
    fim_inscricao: Optional[str] = None
    situacao: str = "Aberto"
    extras: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
