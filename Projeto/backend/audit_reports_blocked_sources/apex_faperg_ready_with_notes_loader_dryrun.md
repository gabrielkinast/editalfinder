# Apex e FAPERGS (`faperg`) — `ready_with_notes` e dry-run do loader

**Data:** 2026-05-02  

**Apply:** não executado. **Gate global:** inalterado.

## 1. Diff de readiness

### `config/source_readiness.json`

| Fonte | Antes | Depois |
|--------|--------|--------|
| **apex** | `blocked` | `ready_with_notes` |
| **faperg** | `needs_manual_review` | `ready_with_notes` |

Lista `ready_with_notes` mantida em ordem alfabética (`apex` e `faperg` integrados).

### `audit_reports_retransform/readiness_for_loader.json`

| Alteração | Valor |
|-----------|--------|
| **apex** | Removido de `fontes_bloqueadas_temporariamente`; acrescentado ao fim de `fontes_prontas_para_loader` (fatia `pronto_com_observacoes`). |
| **faperg** | Removido de `fontes_para_revisao`; acrescentado ao fim de `fontes_prontas_para_loader`. |
| `status_distribution.pronto_com_observacoes` | 61 → **63** |
| `status_distribution.bloquear_temporariamente` | 16 → **15** |
| `status_distribution.precisa_revisao_manual` | 9 → **8** |

O loader continua a derivar `ready` / `ready_with_notes` pela ordem da lista: primeiros **8** = `pronto_para_loader`, seguintes **63** = `pronto_com_observacoes` (ver `scripts/load_ready_sources.py::_build_source_readiness`).

## 2. Standardized copiados

Origem → destino:

- `audit_reports_blocked_sources/lote4_fix_apex_faperg/standardized/apex_standardized.json` → `audit_reports_retransform/standardized/apex_standardized.json`
- idem `faperg_standardized.json`

## 3. Dry-run do loader

Comando:

```text
python scripts/load_ready_sources.py --dry-run --sources apex,faperg --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

**Saída resumida** (`audit_reports_loader_ready/load_ready_summary.json`):

| Métrica | Valor |
|---------|--------|
| Modo | dry-run |
| Fontes selecionadas | 2 |
| Itens standardized | **5** |
| **would_upsert** | **5** |
| would_ignore | 0 |
| **mapping_errors** | **0** |
| **critical_empty_items** | **0** |
| documentos perdidos no payload | 0 |
| pdf preservado (agregado) | 1 |
| validacao_status preservado | 5 |
| qualidade_dado preservado | 5 |

**Por fonte** (`load_ready_by_source.json`):

| Fonte | standardized | would_upsert | mapping_errors | critical_empty | docs preservados | pdf preservado |
|--------|--------------|--------------|----------------|----------------|------------------|----------------|
| apex | 3 | 3 | 0 | 0 | 0 | 0 |
| faperg | 2 | 2 | 0 | 0 | 1 | 1 |

## 4. Verificações pedidas

- **Standardized:** 5 itens nos JSONs em `audit_reports_retransform/standardized/`.
- **would_upsert:** 5 (todos os itens mapeados com sucesso).
- **mapping_errors:** 0.
- **critical_empty:** 0.
- **Documentos / pdf_url:** preservados no fluxo para o caso **faperg** com PDF (Centelha); apex sem PDF no bruto (0/0 preservação documental esperada).
- **tipo_oportunidade / tipo_recurso / perfil_ideal:** contagem não vazia em payload para os 5 itens (ver campos agregados no summary).
- **validacao_status / qualidade_dado:** preservados em todos os itens simulados.
- **origem_portal:** `ApexBrasil` nos itens apex; `FAPERGS` no faperg (standardized).
- **UF (faperg):** `extras.uf` / `extras.estado` = **RS** na amostra verificada.
- **Sem Menu / evento genérico / notícia institucional:** títulos apex são linhas **Exporta Mais**; faperg são editais/programas (Centelha, SICT), não índice nem PSS.

**Nota:** no standardized atual de **apex**, o campo `tipo_recurso` pode aparecer como “licitação” por heurísticas de classificação apesar do conteúdo ser programa de exportação — útil marcar como *observação de produto* antes de staging se o schema exigir coerência estrita.

## 5. Staging — recomendação

**Sim: adequado para próximo passo de staging**, desde que:

1. Se use `apply`, seguir **sempre** a política do script (`--staging` e variáveis de ambiente de confirmação, conforme `load_ready_sources.py`).
2. Revisão humana breve dos **rótulos** apex (programa vs licitação) se isso impactar dashboards ou filtros.
3. Confirmar que o registo de execução em `carga_execucao` (se o script o gravar no dry-run) está alinhado com a política interna de auditoria em Supabase.

**Não** foi executado `apply`; nenhuma escrita de editais em base foi feita por este passo.

## 6. JSON consolidado

`audit_reports_blocked_sources/apex_faperg_ready_with_notes_loader_dryrun.json`
