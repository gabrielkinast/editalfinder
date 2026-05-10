# Duplicidade: `plataforma_industria` vs `senai`

## Contexto

Ambas as fontes recolhem **páginas agregadas** da Plataforma Inovação no Portal da Indústria (URLs com `/categoria/`). O diagnóstico já assinalava risco de URLs semelhantes ao SENAI.

## Metodologia

- **Brutos:** `senai/outputs/senai_editais.json` e `plataforma_industria/outputs/plataforma_editais.json`
- **Standardized:** `audit_reports_retransform/standardized/senai_standardized.json` e `plataforma_industria_standardized.json`
- **Link:** normalização `strip`, `rstrip('/')`, `lower`
- **Título:** igualdade de string para o **mesmo** link normalizado
- **`extras.content_hash`:** igualdade para o **mesmo** link (quando ambos existem)
- **`hash_deduplicacao`:** não encontrado em `extras` nestes ficheiros standardized — **N/A** para esta comparação
- **Categoria (proxy):** último segmento do path (slug da URL `/categoria/...`)

## Resultados

| Critério | Resultado |
|----------|-----------|
| Itens brutos SENAI | 22 |
| Itens brutos plataforma_industria | 23 |
| **Links iguais** (interseção) | **22** |
| Links só em plataforma_industria | **1** |
| Links só em SENAI | 0 |
| Títulos iguais (mesmo link) | 22 |
| `content_hash` iguais (mesmo link) | 22 |
| Slug de categoria igual (mesmo link) | 22 |

URL **apenas** em `plataforma_industria`:

- `https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/categoria/inova-mes`

## Interpretação

A sobreposição é **muito alta** (22/23): na prática são **as mesmas URLs de hub** captadas por dois pipelines. Isto é **explicável** pelo desenho do produto (categorias agregadas partilhadas), não um bug aleatório de dedupe.

## Efeito no loader (Supabase)

O carregamento usa **upsert por `link`**. Assim:

- **Não** se esperam duas linhas na tabela `edital` para o mesmo `link`.
- Se ambas as fontes forem aplicadas, **a última execução que gravar aquele link** pode definir campos como `fonte_recurso` e metadados associados.

## Recomendação

1. **Apply em staging** pode ser **tecnicamente aceitável** do ponto de vista de integridade do dry-run de `plataforma_industria` (payload limpo), **desde** que a equipa aceite a política de **qual fonte “ganha”** nos registos com link comum ao SENAI.
2. Para reduzir redundância e ambiguidade: **manter uma fonte como canónica para estes hubs**, **ou** filtrar na origem URLs já cobertas, **ou** documentar ordem de `apply` (ex.: SENAI primeiro, plataforma depois — ou o inverso — conforme o rótulo institucional desejado).

Detalhe JSON: `plataforma_industria_vs_senai_duplicates.json`.
