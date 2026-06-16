# Comparação shadow vs principal — Backend 7

**Registros na tabela principal:** 1232
**Linhas na tabela sombra (DB):** 0
**Match por id_edital:** 0
**Sem linha shadow:** 1232

_Nota: tabela sombra vazia ou indisponível — métricas calculadas a partir do enricher (fallback)._

## Cobertura
- Prazo estruturado (`prazo_data`): **207**
- Baixa confiança (qualquer campo): **860**
- tipo_registro ≠ edital (notícia/pesquisa/concurso): **70**
- area sem_classificacao: **371**

## Distribuição — prazo_status (top)

- `sem_prazo`: 1025
- `encerrado`: 152
- `prazo_confortavel`: 39
- `vencendo_30`: 10
- `vencendo_7`: 6

## Distribuição — tipo_registro

- `edital`: 821
- `desconhecido`: 317
- `pesquisa`: 32
- `portal`: 24
- `concurso`: 23
- `noticia`: 15

## Distribuição — area_tematica_normalizada (top)

- `sem_classificacao`: 371
- `multissetorial`: 170
- `defesa_seguranca`: 130
- `educacao_pesquisa`: 106
- `industria`: 104
- `saude`: 96
- `energia`: 71
- `startups`: 41
- `agronegocio`: 39
- `nuclear`: 30

Artefatos: `field_coverage.json`, `deadline_distribution.json`, `kind_distribution.json`,
`modality_distribution.json`, `area_distribution.json`, `risky_review.json`.