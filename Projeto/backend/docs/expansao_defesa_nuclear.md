# Expansao EditalFinder Defesa/Nuclear

## Relatorio tecnico curto

### Estrutura atual entendida
- Orquestracao central em `main.py` com execucao sequencial por fonte.
- Cada fonte publica JSON bruto em `/<fonte>/outputs/*_editais.json`.
- Padronizacao em `CORE/transformer.py` e carga em `CORE/loader.py`.
- Modelo base em `CORE/schema.py` ja comporta campos essenciais; especializacao deve ficar em `extras`.

### Pontos reaproveitaveis
- `scraper_generic.py` para fontes HTML com baixo acoplamento.
- `process_source` no transformer para integrar novas fontes sem alterar o banco.
- Upsert por `link` no loader evita duplicidade no armazenamento final.

### Riscos observados
- Portais institucionais com mudanca frequente de layout.
- Fontes com muito conteudo navegacional podem gerar ruído (ex.: paginas institucionais sem edital).
- APIs com timeout/rate limit (PNCP) podem retornar vazio em execucoes pontuais.

### Fontes prioritarias e status
- Ja existiam: `finep`, `defesa`, `cnen`, `cnpq`, `embrapii`, `mcti`, `bndes`, `fapergs`, `fapesp`, `fapesc`.
- Novas implementadas agora: `pncp`, `marinha`, `dcta_ita_iae`, `inb`, `nuclep`, `amazul`, `fapemig`.
- Roadmap sugerido: `compras.gov` (API dedicada), `iaea`, `edf`, `nato_diana`, `darpa_sbir`.

### Ordem recomendada
1. Consolidar `pncp` com paginação/filtros por endpoint estavel.
2. Refinar qualidade dos crawlers HTML de defesa/nuclear (menos ruído).
3. Incluir `compras.gov` com estrategia de API de dados abertos.
4. Expandir internacionais por fases, com validacao de ToS/robots.

## Matriz de fontes novas (resumo)

- `PNCP`
  - URL: `https://pncp.gov.br/app/`
  - Tipo: API + portal
  - Dificuldade: media
  - Risco: timeout/rate limit e variacao de endpoint
  - Decisao: crawler implementado
- `Marinha`
  - URL: `https://www.marinha.mil.br/`
  - Tipo: HTML
  - Dificuldade: media
  - Risco: estrutura CMS
  - Decisao: crawler implementado
- `DCTA/ITA/IAE`
  - URL: `https://www.gov.br/dcta/pt-br`, `https://www.gov.br/ita/pt-br`, `https://www.gov.br/iae/pt-br`
  - Tipo: HTML
  - Dificuldade: media
  - Risco: fragmentacao entre portais
  - Decisao: crawler implementado
- `INB`
  - URL: `https://www.inb.gov.br/`
  - Tipo: HTML
  - Dificuldade: media
  - Risco: baixa frequencia de editais
  - Decisao: crawler implementado
- `NUCLEP`
  - URL: `https://www.nuclep.gov.br/`
  - Tipo: HTML
  - Dificuldade: media
  - Risco: variação de navegacao/menus
  - Decisao: crawler implementado
- `Amazul`
  - URL: `https://www.amazul.mar.mil.br/`
  - Tipo: HTML
  - Dificuldade: media
  - Risco: seletor de pagina
  - Decisao: crawler implementado
- `FAPEMIG`
  - URL: `https://fapemig.br/pt/`
  - Tipo: HTML
  - Dificuldade: baixa-media
  - Risco: ruído de pagina institucional
  - Decisao: crawler implementado

## Classificacao tematica e filtro de palavras-chave
- Taxonomia central adicionada em `keyword_taxonomy.py`.
- Tags automaticas em `extras.thematic_tags` com score simples em `extras.thematic_confidence`.
- Escopo de seguranca mantido: apenas informacoes publicas de fomento, compras e oportunidades.
- Conteudo sensivel/operacional e excluido via contexto negativo.

## Como adicionar novas fontes no futuro
1. Criar pasta `<fonte>/` e script `main_<fonte>.py`.
2. Gerar `outputs/<fonte>_editais.json` no formato padrao.
3. Incluir fonte em `SCRAPERS` (`main.py`).
4. Incluir fonte em `sources` (`CORE/transformer.py`).
5. Garantir campos minimos: `titulo`, `descricao`, `link`, `fonte`.
6. Incluir `extras` com metadados e, quando aplicavel, `thematic_tags`.
7. Rodar smoke test do crawler e `python -m py_compile` dos arquivos alterados.

## Exemplos de JSON

### Exemplo bruto (FAPEMIG)
Arquivo: `fapemig/outputs/fapemig_editais.json`
```json
{
  "titulo": "Chamada 004/2026 - Participacao Coletiva em Eventos Tecnicos no Pais",
  "descricao": "Oportunidades e resultados de chamadas em Ciencia, Tecnologia e Inovacao...",
  "link": "https://fapemig.br/",
  "fonte": "FAPEMIG",
  "data_publicacao": "2026-04-15",
  "fim_inscricao": null,
  "situacao": "Em andamento",
  "valor": "R$ 5,9 mil",
  "programa": "Fomento a Ciencia e Tecnologia",
  "tipo_recurso": "Subvencao (Nao Reembolsavel)",
  "extras": {
    "url_pagina": "https://fapemig.br/pt/",
    "coletado_em": "2026-04-28"
  }
}
```

### Exemplo padronizado (transformer)
Arquivo: `CORE/transformer/fapemig_standardized.json`
```json
{
  "titulo": "Auxilios e Bolsas",
  "descricao": "Auxilios e Bolsas ...",
  "link": "https://fapemig.br/auxilios-e-bolsas",
  "fonte": "FAPEMIG",
  "data_publicacao": "2026-04-28",
  "fim_inscricao": null,
  "situacao": "Em andamento",
  "valor": null,
  "programa": "Fomento a Ciencia e Tecnologia",
  "acao": "...",
  "tipo_recurso": "Subvencao (Nao Reembolsavel)",
  "regiao": "Internacional",
  "extras": {
    "thematic_tags": ["ciencia_tecnologia", "nuclear"],
    "thematic_confidence": 0.55,
    "public_investment_scope": true
  }
}
```
