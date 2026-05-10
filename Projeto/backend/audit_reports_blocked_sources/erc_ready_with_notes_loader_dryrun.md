# ERC — `ready_with_notes` e dry-run do loader

## Diff de readiness

### `config/source_readiness.json`

- **Removido de `blocked`:** `erc`.
- **Adicionado a `ready_with_notes`:** `erc`.
- **Nota:** ao correr `load_ready_sources.py`, o script **reconstrói** este ficheiro a partir de `audit_reports_retransform/readiness_for_loader.json` (primeiros 54 = `ready`, seguintes 16 = `ready_with_notes`). A lista fica **ordenada alfabeticamente** dentro de cada bucket.

### `audit_reports_retransform/readiness_for_loader.json`

- **`erc` retirado** de `fontes_bloqueadas_temporariamente`.
- **`erc` inserido** em `fontes_prontas_para_loader` no segmento **pronto_com_observacoes** (entre `badesul` e `horizon_europe`).
- **`status_distribution`:** `pronto_com_observacoes` 15→**16**; `bloquear_temporariamente` 16→**15**.

### Standardized para o loader

- Cópia: `CORE/transformer/erc_standardized.json` → `audit_reports_retransform/standardized/erc_standardized.json`.

## Comando do dry-run

```text
python scripts/load_ready_sources.py --dry-run --sources erc --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

**Execução bem-sucedida** (`id_execucao`: `2fda3404-9ba0-44ae-9932-b56f82203a3c`, ver `audit_reports_loader_ready/load_ready_summary.json`).

## Resultado agregado

| Métrica | Valor |
|--------|------:|
| Fontes selecionadas | 1 |
| Itens standardized | 8 |
| **would_upsert** | **8** |
| would_ignore | 0 |
| Erros de mapeamento | 0 |
| **critical_empty_items** | **0** |
| Documentos (input → preservados no payload) | 8 → 8 |
| pdf_url (input → preservados) | 8 → 8 |
| validacao_status / qualidade_dado preservados | 8 / 8 |
| canonical_skipped | 0 |

## Verificações pedidas

- **tipo_oportunidade:** presente nos 8 payloads; mistura **grant** e **chamada_publica** (páginas de elegibilidade / oportunidades adicionais).
- **tipo_recurso:** **fomento** em todos os exemplos inspecionados no payload.
- **perfil_ideal:** preenchido nos 8 itens (ex.: `icts` ou lista mais rica em “Additional opportunities”).
- **publico_alvo:** 7/8 com campo não vazio no contador do loader (um item sem entrada contabilizada).
- **validacao_status:** exemplos com **`incompleto`** (prazo estruturado em falta).
- **qualidade_dado:** 82–90 nos exemplos do relatório de payload.
- **codigo_oportunidade / valor / prazo:** continuam com **ruído conhecido** no standardized (ex.: `R$ …`, fragmento `entifier`, `fim_inscricao` null); **não** geraram `critical_empty` neste dry-run.

## Environment guard

- `editalfinder_env`: staging; **`has_allow_staging_apply`: false** (`block_reason`: `missing_staging_flag`).
- Isto **não impede** o dry-run; impede apply “cego” sem o fluxo de flags de staging documentado no projeto.

## Recomendação: apply em staging?

**Sim, de forma condicional:** o dry-run indica **8 upserts** limpos, documentos e `pdf_url` preservados, sem erros de mapeamento. Antes de `--apply --staging`, confirmar variáveis e permissões (`EDITALFINDER_ALLOW_STAGING_APPLY` ou equivalente), rever política de dados (valor em R$, códigos truncados, `incompleto`) e **não** usar apply em produção nesta fase.

**Apply não foi executado** nesta tarefa; **gate global** e **migrations** não foram alterados.
