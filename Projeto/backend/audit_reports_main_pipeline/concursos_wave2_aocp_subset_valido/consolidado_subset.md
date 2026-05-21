# Wave 2 AOCP — Subset válido

**Consolidado em:** 2026-05-16 (UTC)  
**Critério:** `validacao_status = valido`  
**Origem:** `concursos_wave2_aocp/standardized/aocp_standardized.json`  
**Apply:** não executado

---

## Resumo

| Métrica | Valor |
|---------|------:|
| Standardized (origem) | **2** |
| Subset válido | **1** |
| Excluídos (`incompleto`) | **1** |
| Loader dry-run `would_upsert` | **1** |
| Loader `errors_count` | **0** |

---

## Filtro

Incluídos apenas registos com **`link_edital`** e **`data_fim_inscricao`** (regra `valido` do crawler AOCP).

### Excluído do subset

| Título | Status | Motivo |
|--------|--------|--------|
| CBM/RJ — Corpo de Bombeiros do Estado do Rio de Janeiro | `incompleto` | Sem `link_edital` (edital «em breve»; API `NEW`) |

---

## Item no subset

| Campo | Valor |
|-------|--------|
| **Título** | CESAMA — Companhia de Saneamento Municipal — MG |
| **tipo_selecao** | `concurso_publico` |
| **Inscrições** | 2026-06-10 → 2026-07-10 |
| **Link** | https://www.institutoaocp.org.br/concursos/690/ |
| **Edital** | PDF em `arquivos-site.institutoaocp.org.br` |
| **API** | `NEW` (id 690) |

---

## Loader dry-run

```powershell
python scripts/load_concursos_selecao.py --dry-run `
  --input-dir audit_reports_main_pipeline/concursos_wave2_aocp_subset_valido/standardized `
  --output-dir audit_reports_main_pipeline/concursos_wave2_aocp_subset_valido/loader_dryrun `
  --sources aocp
```

**Resultado:** 1 item mapeado, `would_upsert_total=1`, sem erros.

---

## Recomendação

Subset pronto para **apply em staging** quando desejado (1 concurso válido). Re-crawl com `--max-items` maior para ampliar o subset à medida que novos editais `NEW` ganhem PDF de abertura.
