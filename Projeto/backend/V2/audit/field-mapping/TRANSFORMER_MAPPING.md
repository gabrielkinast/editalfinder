# Mapeamento do transformer

## Fluxo

`transform_generic` distribui itens para `_transform_item_with_result`, deduplica o resultado por `link|titulo|fonte|data_publicacao|fim_inscricao` e grava `*_standardized.json` (`backend/CORE/transformer.py:879-962,3232-3308`). A função individual normaliza aliases/HTML, aplica gate, enriquecimento de detalhe/PDF, taxonomias, qualidade e sanitiza (`:2266-3197`). Campos não canônicos são preservados em `extras` (`:2810-2865`; `data_cleaning.py:211-243`).

## Campos

| Campo | Aliases/entradas | Função e transformação | Saída/fallback | Risco conhecido |
|---|---|---|---|---|
| título | `titulo,title,name,nome,chamada,edital,oportunidade,objeto` | `normalize_aliases`; `clean_text_fields`; título genérico pode ser substituído por frase do PDF (`data_cleaning.py:15-31,137-203`; `transformer.py:2281-2282,2728-2734`) | `titulo`; fallback de campos de descrição/gate depende da fonte | PDF pode alterar identidade; aliases amplos. |
| descrição | `descricao,description,resumo,summary,snippet,texto,conteudo,content,objetivo,detalhes,details` | limpeza HTML; `enrich_description`; limite 50.000 (`data_cleaning.py:32-46`; `transformer.py:2790-2808`) | `descricao`; texto de listing/PDF | `objetivo` vira descrição por alias; texto muito amplo. |
| link | `link,url,href,url_detalhe,detail_url,link_detalhe,pagina,page_url,url_chamada,url_pagina` | alias; resolução/validação pelo gate e perfis de fonte (`data_cleaning.py:47-64`; `transformer.py:2266-2730`) | `link`; `extras.url_detalhe` | URL de listagem/documento pode ocupar link canônico. |
| fonte | `fonte,source,origem,portal,orgao,instituicao,institution` | alias (`data_cleaning.py:65-76`) | `fonte`; fallback `source_name.upper()` (`transformer.py:2844`) | órgão/instituição colapsam em fonte. |
| organização | sobretudo `extras.orgao_responsavel`, `instituicao`, `orgao_contratante`, `agency` | calibradores de fonte e defesa/Ásia; transformer não resolve FK | permanece em `extras`; fallback posterior no loader | Sem identidade/FK canônica. |
| país | `pais` geralmente em `extras`; metadados por fonte | **Não existe normalizador global de país.** Calibradores escrevem valores livres (`taxonomy_filtros.py:1935-3167`) e enriquecimento opcional gera `pais_origem` (`opportunity_enricher.py:247-313`) | `extras.pais`; ausente/vazio | `Brasil`, `japao`, nomes em idiomas diferentes. |
| estado | `estado`,`uf` como campos livres/órfãos | sem normalização global no transformer | `extras.estado/uf` se presentes | UF/nome completo e ausência coexistem. |
| região | `regiao,region,abrangencia` | alias + `extract_regiao` por regex (`data_cleaning.py:113-120`; `transformer.py:320-356`) | `regiao`; fallback final `Nacional` | Regex de siglas e default causam falsos positivos; amostras reais contraditórias. |
| abrangência | `abrangencia` | **normalização equivalente:** colapsa em `regiao` via aliases (`data_cleaning.py:113-120`) | não existe campo próprio | Perda semântica confirmada. |
| escopo | `escopo`; enriquecedor produz `escopo_geografico` | não integra o núcleo; `opportunity_enricher` calcula scope sob feature flag (`opportunity_enricher.py:40-42,247-313`) | `extras.escopo`/`backend_enrichment.escopo_geografico` | Dois nomes; persistência opcional/não confirmada. |
| área | `extras.area`, texto temático, `temas` | **normalização equivalente:** `enrich_opportunity_classification`, `_prune_area`, taxonomia por keywords (`taxonomy_filtros.py:191-269`) | `extras.area`; fallback vazio | Valores livres + taxonomia; classificadores de fonte podem sobrescrever/calibrar. |
| tipo oportunidade | principalmente `extras.tipo_oportunidade` | calibradores e `enrich_opportunity_classification` (`taxonomy_filtros.py:251-345` e calibradores) | `extras.tipo_oportunidade` | Artefatos mostram editais classificados `noticia_institucional`. |
| tipo recurso | `tipo_recurso,resource_type,modalidade,tipo,categoria,type`; extras | alias; `extract_resource_type`; `_infer_tipo_recurso` (`data_cleaning.py:99-106`; `transformer.py:555-599,2781-2784`; `taxonomy_filtros.py:224-269`) | `tipo_recurso`; fallback `Não Especificado` | Múltiplas regras e vocabulários. |
| datas | publicação: `data_publicacao,published_at,publication_date,data,data_inicio,publicado_em`; prazo: `fim_inscricao,deadline,closing_date,prazo,prazo_envio,data_fim,submission_deadline,application_deadline,inscricoes_fim` | **extração equivalente:** `normalize_date_str`, `extract_deadline_from_text`; locale PT/EN (`data_cleaning.py:77-98`; `date_parser.py:191-338`; `transformer.py:2755-2779`) | ISO em `data_publicacao`,`fim_inscricao`; raws em extras | Primeira data do texto pode virar publicação/prazo errado. |
| valores | `valor,amount,funding,budget,valor_total,valor_maximo,recurso,financiamento` | **extração equivalente:** `finance_parser.extract_value/extract_value_min` (`data_cleaning.py:107-112`; `finance_parser.py:8-93`; `transformer.py:2779-2784`) | `valor`; `extras.valor_total_texto` | Regex pode capturar número/ano como moeda; string só vira número no loader. |
| status | `situacao`; texto completo | `extract_situacao` (`transformer.py:296-318`) | `situacao`; fallback `Aberto` (`:2847`) | Default aberto sem prazo; validade é outra classificação. |
| hash | título, descrição, PDF; PNCP inclui link/códigos | `generate_content_hash`: lowercase, remove espaços/pontuação, SHA-256 (`transformer.py:1008-1019,2747-2753`) | `extras.content_hash` | Não é o mesmo campo que `hash_deduplicacao`; mudanças de texto mudam hash. |
| classificações | texto, fonte, extras | tema, conteúdo, oportunidade, gate, qualidade, calibradores (`transformer.py:2736-3190`) | `extras.thematic_*`, `area`, setores, confiança, qualidade, content type | Ordem e regras por fonte tornam o resultado difícil de reproduzir isoladamente. |
| extras | `extras,metadata,meta,detalhes_extras` + órfãos | `merge_item_extras`, patches não vazios e sanitização (`data_cleaning.py:122`; `transformer.py:72-99,2810-2865`) | `extras` | Mistura raw, derivados, auditoria e campos de filtro; duplicidade com colunas. |

## Funções equivalentes solicitadas

- País: não há função global; calibradores por fonte e `opportunity_enricher` são equivalentes parciais.
- Abrangência: `normalize_aliases` (`abrangencia -> regiao`).
- Área: `enrich_opportunity_classification` + `_prune_area`.
- Tipo: `extract_resource_type` + `_infer_tipo_recurso` + calibradores.
- Data: `normalize_date_str`, `extract_deadline_from_text`, e a segunda família `deadline_normalizer.normalize_deadline` (`deadline_normalizer.py:287-597`).
- Valor: `finance_parser.extract_value`, `extract_value_min`.

**Fato:** existem duas famílias de prazo (transformer e enrichment/deadline normalizer), portanto a regra é duplicada.
