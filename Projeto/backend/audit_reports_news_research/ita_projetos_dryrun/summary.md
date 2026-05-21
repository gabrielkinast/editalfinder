# ITA Projetos — dry-run (Pesquisas Estratégicas)

- **Execução:** 2026-05-17T04:33:26Z
- **Modo:** dry-run (sem apply)
- **Fonte:** `ita_projetos`
- **Diagnóstico:** listagem/catálogo Drupal de projetos de pesquisa

## Diagnóstico

| Aspeto | Detalhe |
|--------|---------|
| url | http://www.ita.br/projetos |
| tipo_pagina | listagem/catálogo Drupal de projetos de pesquisa |
| cms | Drupal (site ITA) |
| rss | Não identificado no hub |
| recorrencia | Catálogo institucional (não feed de notícias) |
| datas | Ausentes nas fichas auditadas; validacao_status tipicamente incompleto |
| destino | public.pesquisa — tipo_pesquisa=projeto_pesquisa |
| https | HTTPS www.ita.br com timeout frequente; usar HTTP no crawl |

## Resultados

- **Standardized:** 4
- **Na janela 24m:** 0
- **Sem data:** 4
- **Enrich:** 4

### tipo_pesquisa

- `projeto_pesquisa`: **4**

### Validação

- `incompleto`: **4**

## Itens

### 1. Abordagens analíticas em inteligência de mercado

- **Link:** http://www.ita.br/projetos/abordagensanalticasemintelignciademercado
- **Data:** —
- **tipo_pesquisa:** `projeto_pesquisa`
- **Categoria:** projeto
- **Eixos:** engenharia, ciencia_tecnologia
- **Validação:** `incompleto`

### 2. Centro de Pesquisa em Engenharia para a Mobilidade Aérea do Futuro (CPE-MAF)

- **Link:** http://www.ita.br/projetos/cpemaf
- **Data:** —
- **tipo_pesquisa:** `projeto_pesquisa`
- **Categoria:** projeto
- **Eixos:** engenharia, ciencia_tecnologia, energia
- **Validação:** `incompleto`

### 3. Curso de Especialização em Engenharia Aeronáutica

- **Link:** http://www.ita.br/projetos/cursodeespecializaoemengenhariaaeronutica
- **Data:** —
- **tipo_pesquisa:** `projeto_pesquisa`
- **Categoria:** projeto
- **Eixos:** engenharia, ciencia_tecnologia, aeroespacial
- **Validação:** `incompleto`

### 4. Estudo Experimental da Emissão de Poluentes em Queimadores de Gás Natural

- **Link:** http://www.ita.br/projetos/estudoexperimentaldaemissodepoluentesemqueimadoresdegsnatural
- **Data:** —
- **tipo_pesquisa:** `projeto_pesquisa`
- **Categoria:** projeto
- **Eixos:** engenharia, ciencia_tecnologia, energia
- **Validação:** `incompleto`

## Warnings

- {'tipo': 'sem_data_publicacao', 'count': 4, 'detalhe': 'Esperado para catálogo/portal ITA; janela 24m não filtra standardized.'}
