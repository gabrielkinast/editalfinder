# Loader controlado (dry-run)

- Modo: **dry-run**
- Apply status: `not_requested`
- `config/source_readiness.json` escrito: **False** (`none`)
- Slice derivado (relatório): `D:\Computational_Physics\My Projects\edital\audit_reports_main_pipeline\recovery_a_official_loader_dryrun_bundle\readiness_derived_slice.json`
- Fontes selecionadas: **2**
- Fontes excluídas: **0**
- Itens standardized: **32**
- Destinos: `{'edital': 32}`
- Upsert simulado: **32**
- Ignorados simulados: **0**
- Ignorados por canonização (alias duplicado): **0**
- Erros de mapeamento: **0**

## Preservação

- Itens com documentos na entrada: **10**
- Itens com documentos preservados: **10**
- Itens com documentos perdidos no payload: **0**
- Itens com docs não-PDF no standardized: **7**
- Itens com docs não-PDF no payload: **7**
- Perda de docs não-PDF: **0**
- Itens com pdf_url na entrada: **4**
- Itens com pdf_url preservado: **4**
- Itens com validacao_status preservado: **32**
- Itens com qualidade_dado preservada: **32**
- Itens com campos críticos vazios: **0**

## Official link only (auditoria)

- official_link_only_total (`extras.extraction_mode` no payload pós-mapeamento): **0**
- Itens standardized com `extras.extraction_mode == official_link_only` (pré-simulação): **0**
- access_limited_total (`access_status == access_limited` ou `validacao_status` acesso_limitado): **0**

### official_link_only_by_source

- *(nenhum item com extraction_mode official_link_only no payload)*

### access_reason_counts

- *(vazio)*

### official_link_only_examples

- *(nenhum)*

## Fontes excluídas

*(vazio — apenas banco_da_amazonia e dod_sbir_sttr solicitados; esa_star fora do input e fora do readiness pronto.)*

---

## Recovery A — verificação pedida

| Critério | Resultado |
|----------|-----------|
| `sources_selected` | **2** |
| `would_upsert_total` | **32** (> 0) |
| `mapping_errors_total` | **0** |
| `critical_empty_items_total` | **0** |
| `documentos_perdidos_no_payload_total` | **0** |
| `destination_counts_total` | **`{"edital": 32}`** |
| **esa_star** | Fora do `--sources` e fora da pasta `recovery_a_official_dryrun_standardized` |
| Login isolado / SSO ESA | **0** (scan dos links no standardized oficial) |
| FAQ / API / Data Resources / Success Stories / News / Events | **0** URLs desses padrões |
| Conta PJ | **0** links `conta-pj` nos 26 itens BASA |

Relatório JSON espelho: `recovery_a_official_loader_dryrun.json` (cópia de `load_ready_summary` do bundle). Pasta completa: `recovery_a_official_loader_dryrun_bundle/`.
