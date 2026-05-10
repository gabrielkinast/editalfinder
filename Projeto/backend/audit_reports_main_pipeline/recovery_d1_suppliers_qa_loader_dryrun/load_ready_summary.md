# Loader controlado (dry-run)

- Modo: **dry-run**
- Apply status: `not_requested`
- `config/source_readiness.json` escrito: **False** (`none`)
- Slice derivado (relatório): `D:\Computational_Physics\My Projects\edital\audit_reports_main_pipeline\recovery_d1_suppliers_qa_loader_dryrun\readiness_derived_slice.json`
- Fontes selecionadas: **3**
- Fontes excluídas: **0**
- Itens standardized: **26**
- Destinos: `{'edital': 18, 'pesquisa': 2, 'noticia': 6}`
- Upsert simulado: **26**
- Ignorados simulados: **0**
- Ignorados por canonização (alias duplicado): **0**
- Erros de mapeamento: **0**

## Preservação

- Itens com documentos na entrada: **15**
- Itens com documentos preservados: **15**
- Itens com documentos perdidos no payload: **0**
- Itens com docs não-PDF no standardized: **0**
- Itens com docs não-PDF no payload: **0**
- Perda de docs não-PDF: **0**
- Itens com pdf_url na entrada: **15**
- Itens com pdf_url preservado: **15**
- Itens com validacao_status preservado: **18**
- Itens com qualidade_dado preservada: **18**
- Itens com campos críticos vazios: **0**

## Taxonomia — sobrescrita (`--overwrite-fields`)

- taxonomy_overwrite_enabled: **False**
- overwrite_fields: `[]`
- overwrite_sources: `['bae_systems_suppliers', 'general_dynamics_suppliers', 'lockheed_martin_suppliers']`
- overwritten_fields_count (diff merge default vs merge com replace): **0**
- taxonomy_overwrite_preview_errors_total: **0**

## Official link only (auditoria)

- official_link_only_total (`extras.extraction_mode` no payload pós-mapeamento): **1**
- Itens standardized com `extras.extraction_mode == official_link_only` (pré-simulação): **1**
- access_limited_total (`access_status == access_limited` ou `validacao_status` acesso_limitado): **2**

### official_link_only_by_source

- `bae_systems_suppliers`: **1**

### access_reason_counts

- `(sem access_reason)`: **1**
- `cloudflare_or_403`: **1**

### official_link_only_examples

- **bae_systems_suppliers** — Responsible supply chain | BAE Systems UK suppliers — `access_reason=cloudflare_or_403` — link=`https://www.baesystems.com/en-uk/suppliers/responsible-supply-chain`

## Fontes excluídas
