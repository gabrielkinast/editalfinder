# Rascunho consolidado de auditoria

Legenda: **fato** = demonstrado por artefato/código; **inferência** = projeção determinística sem banco remoto; **hipótese** = depende do ambiente/dados.

| Conceito | Crawler | Transformer | Loader | Banco | View | Mapper | Filtro | Situação |
|---|---|---|---|---|---|---|---|---|
| título | aliases variados | limpa/enriquece/PDF | `titulo` | `titulo` | `titulo` | `getDisplayTitle` | busca/ruído | divergência suspeita |
| descrição | texto/resumo/objetivo | limpa e limita 50k | merge mais longo | `descricao` | `descricao` | direto | busca | consistente |
| link | link/url/url_pagina etc. | gate e normalização por fonte | `link`, conflito | NOT NULL UNIQUE | `link` | `linkOriginal/link_raw` | busca indireta/escopo/ação | consistente |
| fonte | fonte/source/orgao etc. | fallback source name | `fonte_recurso` | `fonte_recurso` | original + alias `fonte` | vira também `orgao` | fonte/escopo/busca | divergência confirmada |
| órgão/organização | texto em extras | calibradores; sem FK | fallback textual + primeiro ID global | texto + `id_organizacao` | org textual depende da versão | ignorado; fonte vira orgao | fonte | divergência confirmada |
| país | livre/extras | sem normalizador global | espelho estendido | `pais` | presente na view atual | `pais_raw` | includes normalizado/escopo | divergência suspeita |
| estado | livre/extras | sem normalizador global | espelho | `estado` e `uf` coexistem | view atual usa `uf` | `uf_raw`; sem `estado_raw` | igualdade exata UF | divergência confirmada |
| região | regiao/region/abrangencia | regex/default Nacional | `regiao` | `regiao` | presente no snapshot atual; ausente em versões | `regiao_raw` | includes normalizado | divergência suspeita |
| abrangência | alias possível | colapsa em região | sem campo | sem coluna dedicada | sem campo | sem campo | sem regra | divergência confirmada |
| escopo | extras | extras/enrichment opcional | geralmente extras | sem coluna canônica no snapshot | extras | `extras_raw` | recalculado sem usar escopo | divergência confirmada |
| área | livre/extras | taxonomia/calibradores | `text[]` estendido | `area` + áreas específicas | view atual omite `area` geral | `area` cai para temas/classificação | arrays normalizados | divergência confirmada |
| setor estratégico | extras | calibradores | `setor_estrategico` | text[] | presente | list/flat | checkbox | consistente |
| tipo oportunidade | extras | classificador/calibradores | espelho | text | presente | raw | igualdade/includes | divergência suspeita |
| tipo recurso | aliases | extrator + classificador | espelho; também pode ocupar objetivo | text | presente | raw + classificação local | compara ambos | divergência confirmada |
| prazo | muitos aliases/texto | data parser/deadline parser | `prazo_envio`; expira ativo | date | original + `fim_inscricao` | dataLimite/raws | recalcula status | regras duplicadas; divergência confirmada |
| data abertura | campos/extras | não canônica | espelho estendido se extras | `data_abertura` | omitida | não mapeada | não usada | não rastreado |
| valor | aliases/texto | regex/string | float/numeric e espelhos | múltiplas colunas | min/max na view atual | escolhe principal Number | faixas | divergência suspeita |
| moeda | extras | calibradores | espelho | `moeda` | omitida na view atual | `moeda_raw` espera campo | não filtra | divergência confirmada |
| status | situacao | extração/default aberto + validade | situacao/ativo/validacao | três conceitos | presentes parcialmente | `inferAtivo` | várias derivações | divergência confirmada |
| favorito | ausente | ausente | fluxo separado | `edital_favorito` | view separada não definida localmente | hook associa por ID/link | pós-filterCatalog | derivado apenas em uma camada |
| hash | ausente ou fonte | `extras.content_hash` | aceita `hash_deduplicacao` diferente | `hash_deduplicacao` | omitido na view atual | não mapeado | não usado | divergência confirmada |

## Principais conclusões

- O caminho nominal é crawler JSON -> transformer standardized -> loader/upsert -> `edital` -> `vw_editais_front` -> `mapRawEditalRow` -> filtros/card.
- O contrato efetivo depende de qual das múltiplas views foi instalada e de `EDITALFINDER_EXTENDED_SCHEMA`.
- Geografia, status, tipo e área são recalculados/renomeados em mais de uma camada.
- Nenhuma conclusão sobre dados remotos, RLS ou volume deve ser tomada apenas deste rascunho.
