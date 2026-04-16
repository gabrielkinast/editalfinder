class EditalScience:
    def __init__(self, titulo, link, fonte, descricao="", data_publicacao=None, fim_inscricao=None, situacao="Aberto", extras=None):
        self.titulo = titulo
        self.link = link
        self.fonte = fonte
        self.descricao = descricao
        self.data_publicacao = data_publicacao
        self.fim_inscricao = fim_inscricao
        self.situacao = situacao
        self.extras = extras or {}

    def to_dict(self):
        return {
            "titulo": self.titulo,
            "descricao": self.descricao,
            "link": self.link,
            "fonte": self.fonte,
            "data_publicacao": self.data_publicacao,
            "fim_inscricao": self.fim_inscricao,
            "situacao": self.situacao,
            "extras": self.extras
        }
