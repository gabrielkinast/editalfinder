# Plano de auditoria (pré-execução) — EditalFinder

## 1. Crawlers com outputs reais para testar

Foram encontrados **95+** ficheiros `**/outputs/*editais*.json` (e variantes como `plataforma_editais.json`, `defesa_noticias_militares.json`). Lista completa é gerada em `audit_by_source.json` após a primeira corrida do script.

## 2. Ficheiros JSON existentes

- **Brutos/intermediários:** `<fonte>/outputs/*editais*.json` (padrão principal).
- **Pós-transformer (opcional):** `CORE/transformer/<fonte>_standardized.json` (não obrigatório para a auditoria; o script re-transforma um subconjunto para dry-run).

## 3. Fontes que parecem maduras (hipótese inicial, a validar empiricamente)

Histórico do projeto: **finep**, **cnpq**, **fapergs**, **embrapii**, **bndes** tendem a estrutura rica. A classificação final **não** fica fixa: sai da matriz no relatório.

## 4. Fontes que parecem problemáticas (hipótese inicial)

**apex** (Menu), **japan_aist** (Contact / home), **china_university_procurement** (intranet/login/overview), fontes Asia com muitas páginas institucionais. Confirmação por contagens de ruído e rejeição.

## 5. Como o transformer será testado

- Importação de `transformer._transform_item_with_result` com `sys.path` em `CORE/`.
- Para cada fonte: carregar JSON → amostra até **N** itens (default configurável) → métricas: rejeitado, motivo, `validacao_status`, `qualidade_dado`, campos preenchidos, ruído no bruto.
- **Sem** gravar `*_standardized.json` global; só memória + relatórios em `audit_reports/`.

## 6. Como o loader será simulado

- `schema.normalizar(item)` + `loader.map_to_db_schema(item_normalizado)`.
- Aplicar `loader._strip_payload` apenas se existir (espelho do upsert) — cópia local da lógica de chaves permitidas se necessário para evitar import circular frágil.
- **Sem** `supabase.upsert`, sem migrações, sem deletes.

## 7. Testes a correr

- Contagens bruto → transformado / rejeitado / incompleto / suspeito.
- Campos preenchidos (% na amostra transformada).
- Lista de títulos de ruído (PT/EN/ES/JA/ZH) no bruto e nos aceites.
- Duplicados por `link` no bruto e na amostra transformada.
- Perda bruto vs transformado (chaves em bruto ausentes no payload).
- Payload loader: campos nulos, `pdf_url` vs `link`.
- Palavras-chave legado: score / relevância / relevance (grep no repo em fase separada ou embutido).
- Unicode: amostra de caracteres não-ASCII preservados.

## 8. Onde os relatórios serão gravados

Pasta **`audit_reports/`** na raiz do repositório (criada pelo script):

- `audit_summary.json`, `audit_summary.md`
- `audit_by_source.json`
- `audit_noise_examples.json`
- `audit_empty_fields.json`
- `audit_data_loss_examples.json`
- `audit_duplicates.json`
- `audit_classification_issues.json`
- `audit_profile_issues.json`
- `audit_loader_payload.json`
- `audit_performance.json`
- `audit_score_legacy.json`
- `audit_matrix_crawlers.json` (matriz por ficheiro: `fonte|nome.json`)
- `audit_relatorio_tecnico.md` (22 secções sintetizadas)

## 9. Scripts criados

- **`scripts/audit_pipeline.py`** — orquestra descoberta de ficheiros, amostragem, transformer dry-run, simulação loader, agregação e escrita dos JSON/MD.
- **`scripts/audit_loader_payload.py`** — invoca `audit_pipeline.py` (mesmos argumentos; dry-run completo).

## 10. Riscos

- **Tempo:** PDF/rede no transformer; mitigação com `--max-items` baixo (ex.: 40–100).
- **Falso “quebrado”:** JSON vazio ou lista vazia por crawler falhado pontualmente.
- **Memória:** ficheiros muito grandes (ex. china_tendering_bidding); amostragem no início da lista.
- **Path/imports:** executar sempre com `ROOT` no `sys.path` como no script.

---

*Documento gerado automaticamente na fase de plano. Métricas reais seguem nos ficheiros `audit_*` após execução.*
