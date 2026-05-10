# Horizon Europe — `ready_with_notes` e dry-run do loader

Data: 2026-05-02.

## Resumo do diff de readiness

| Ficheiro | Alteração |
|----------|-----------|
| `config/source_readiness.json` | `horizon_europe` retirado de **`blocked`**; passou para **`ready_with_notes`**. |
| `audit_reports_retransform/readiness_for_loader.json` | `horizon_europe` retirado de **`fontes_bloqueadas_temporariamente`**; acrescentado ao fim de **`fontes_prontas_para_loader`**; contagens: `fontes_total` 94→95, `pronto_com_observacoes` 14→15, `bloquear_temporariamente` 17→16. |

**Nota:** ao correr `load_ready_sources.py`, o script **regenera** `config/source_readiness.json` a partir de `readiness_for_loader.json` (`_build_source_readiness`). A lista `ready_with_notes` fica **ordenada alfabeticamente** (`badesul`, `horizon_europe`, `mapa`, …).

## Standardized copiado

- **Origem:** `CORE/transformer/horizon_europe_standardized.json`  
- **Destino:** `audit_reports_retransform/standardized/horizon_europe_standardized.json`

## Comando executado (dry-run)

```text
python scripts/load_ready_sources.py --sources horizon_europe --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

Saída do script: diretório `audit_reports_loader_ready/` (resumo JSON, by_source, exemplos de payload).

## Resultado do dry-run

| Métrica | Valor |
|---------|------:|
| Fontes selecionadas | 1 |
| Itens standardized | 25 |
| **would_upsert** | **25** |
| would_ignore | 0 |
| **mapping_errors** | **0** |
| **critical_empty_items** | **0** |
| documentos perdidos no payload | 0 |
| pdf preservado / input | 0 / 0 (sem PDF na origem) |
| validacao_status preservado | 25 |
| qualidade_dado preservado | 25 |
| apply | não solicitado (`not_requested`) |

## Verificações pedidas (amostra + standardized)

- **URLs:** `topic-details/horizon-*` em todos os itens.  
- **tipo_oportunidade:** `funding_opportunity`.  
- **tipo_recurso:** `fomento`.  
- **natureza_recurso (extras):** `nao_reembolsavel`.  
- **topic_id / call_code:** presentes no `extras`.  
- **links_oficiais:** `topico_oficial` + `portal_funding_tenders`.  
- **origem_portal:** Funding & Tenders Portal.  
- **validacao_status:** `incompleto`.  
- **qualidade_dado:** 60.  
- **pdf_url:** `null` nos exemplos de payload — **sem valor inventado**.  
- **Documentos:** 0 entrada, 0 perdas.

## Restrições cumpridas

- **Apply** automático: não executado.  
- **Supabase:** sem alterações de dados (dry-run; o script pode registar metadados de execução conforme implementação atual).  
- **Gate global:** não alterado.

## Recomendação para staging

O dry-run está **coerente para um primeiro load**: 25 linhas prontas para upsert, sem erros de mapeamento nem campos críticos vazios inesperados.

**Sugestão:** quando quiserem materializar no staging, usar **`--apply --staging`** (e variáveis de ambiente / flags de segurança que o projeto exige — o resumo indicou `has_allow_staging_apply: false` no ambiente corrente até se confirmar staging). Fazer **uma revisão curta** de uma amostra de linhas no Supabase após o primeiro apply.

---

Relatório JSON paralelo: `horizon_europe_ready_with_notes_loader_dryrun.json`.
