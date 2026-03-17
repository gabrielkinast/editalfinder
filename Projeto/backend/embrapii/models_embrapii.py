from dataclasses import dataclass, asdict

@dataclass
class Chamada:
    titulo: str
    link: str
    ano: str
    data_publicacao: str = "Não informada"
    deadline: str = "Não informada"

    def to_dict(self):
        return asdict(self)
