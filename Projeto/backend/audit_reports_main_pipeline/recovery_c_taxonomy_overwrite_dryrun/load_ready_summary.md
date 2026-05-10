# Loader controlado (dry-run)

- Modo: **dry-run**
- Apply status: `not_requested`
- `config/source_readiness.json` escrito: **False** (`none`)
- Slice derivado (relatório): `D:\Computational_Physics\My Projects\edital\audit_reports_main_pipeline\recovery_c_taxonomy_overwrite_dryrun\readiness_derived_slice.json`
- Fontes selecionadas: **2**
- Fontes excluídas: **0**
- Itens standardized: **41**
- Destinos: `{'edital': 41}`
- Upsert simulado: **41**
- Ignorados simulados: **0**
- Ignorados por canonização (alias duplicado): **0**
- Erros de mapeamento: **0**

## Preservação

- Itens com documentos na entrada: **41**
- Itens com documentos preservados: **41**
- Itens com documentos perdidos no payload: **0**
- Itens com docs não-PDF no standardized: **20**
- Itens com docs não-PDF no payload: **20**
- Perda de docs não-PDF: **0**
- Itens com pdf_url na entrada: **40**
- Itens com pdf_url preservado: **40**
- Itens com validacao_status preservado: **41**
- Itens com qualidade_dado preservada: **41**
- Itens com campos críticos vazios: **0**

## Taxonomia — sobrescrita (`--overwrite-fields`)

- taxonomy_overwrite_enabled: **True**
- overwrite_fields: `['setor_estrategico']`
- overwrite_sources: `['embrapii', 'nuclep']`
- overwritten_fields_count (diff merge default vs merge com replace): **38**
- taxonomy_overwrite_preview_errors_total: **0**

### Pré-visualização (dry-run com leitura DB para diff)

- **embrapii** — Chamada Pública 01/2016 – RESULTADO FINAL — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'industria']` → overwrite=`['ciencia_tecnologia', 'defesa_industrial', 'aeroespacial']`
- **embrapii** — Chamada Pública 01/2017 – RESULTADO FINAL — default=`['defesa_industrial', 'aeroespacial', 'energia', 'industria', 'ciencia_tecnologia']` → overwrite=`['ciencia_tecnologia', 'energia', 'defesa_industrial']`
- **embrapii** — Chamada Pública 02/2017 – RESULTADO FINAL — default=`['defesa_industrial', 'aeroespacial', 'industria', 'ciencia_tecnologia', 'energia']` → overwrite=`['ciencia_tecnologia', 'energia', 'defesa_industrial']`
- **embrapii** — CHAMADA PÚBLICA – 01/2020 – Resultado final — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'industria']` → overwrite=`['ciencia_tecnologia', 'industria', 'defesa_industrial']`
- **embrapii** — CHAMADA PÚBLICA – 02/2020 – Resultado final — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'industria']` → overwrite=`['ciencia_tecnologia', 'industria', 'defesa_industrial']`
- **embrapii** — Chamada Pública 03/2020 – Resultado Final — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'energia']` → overwrite=`['ciencia_tecnologia', 'energia', 'defesa_industrial']`
- **embrapii** — CHAMADA PÚBLICA 04/2020 PROGRAMA ROTA 2030 – Resultado Final — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'defesa']` → overwrite=`['ciencia_tecnologia', 'defesa_industrial', 'aeroespacial']`
- **embrapii** — CHAMADA PÚBLICA CENTRO DE COMPETÊNCIA 01/2022 — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'industria']` → overwrite=`['ciencia_tecnologia', 'industria', 'defesa_industrial']`
- **embrapii** — CHAMADA PÚBLICA CENTRO DE COMPETÊNCIA 02/2022 — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'industria']` → overwrite=`['ciencia_tecnologia', 'industria', 'defesa_industrial']`
- **embrapii** — Chamada Pública 03/2022 – RESULTADO FINAL — default=`['defesa_industrial', 'aeroespacial', 'industria', 'energia']` → overwrite=`['industria', 'energia', 'defesa_industrial']`
- **embrapii** — CHAMADA PÚBLICA CENTRO DE COMPETÊNCIA 04/2022 — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'industria']` → overwrite=`['ciencia_tecnologia', 'defesa_industrial', 'aeroespacial']`
- **embrapii** — CHAMADA PÚBLICA 04/2022 – Resultado Final — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'defesa']` → overwrite=`['ciencia_tecnologia', 'defesa', 'defesa_industrial']`
- **embrapii** — CHAMADA PÚBLICA 05/2022 PARA CREDENCIAMENTO NO SISTEMA EMBRAPII – Resultado Prel — default=`['defesa_industrial', 'aeroespacial', 'industria', 'materiais_avancados', 'ciencia_tecnologia', 'energia']` → overwrite=`['ciencia_tecnologia', 'energia', 'defesa_industrial']`
- **embrapii** — Chamada Pública Unidades Embrapii nº 03/2025 — default=`['defesa_industrial', 'aeroespacial', 'industria', 'ciencia_tecnologia', 'energia']` → overwrite=`['ciencia_tecnologia', 'energia', 'defesa_industrial']`
- **embrapii** — Chamada Pública Centro de Competência Embrapii nº 03/2025 — default=`['defesa_industrial', 'aeroespacial', 'ciencia_tecnologia', 'industria']` → overwrite=`['ciencia_tecnologia', 'defesa_industrial', 'aeroespacial']`

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
