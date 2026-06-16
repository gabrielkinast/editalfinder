# Backend 10.3 — Consolidação pós-apply cross-source

## Objetivo

Consolidar o estado **pós-apply** dos patches 10.2B (Grants.gov), 10.2C (DOE_ARPAE) e 10.2D (BNDES) para medir qualidade, evitar regressões e orientar próximos passos.

**Somente leitura** — nenhuma escrita no banco, nenhum apply automático.

## Fontes consolidadas

| Chave | Label | Apply log |
|-------|-------|-----------|
| `grants_gov` | Grants.gov | `outputs/grants_deadline_apply/apply_log.json` |
| `doe_arpae` | DOE_ARPAE | `outputs/doe_arpae_deadline_apply/apply_log.json` |
| `bndes` | BNDES | `outputs/bndes_deadline_apply/apply_log.json` |

## Comando

```bash
python scripts/consolidate_post_apply_quality.py --sources grants_gov doe_arpae bndes --from-db --with-backfill --limit 1000
```

Opções:

- `--from-db` / `--no-from-db` — carrega registros do Supabase (default: true se `.env` configurado)
- `--with-backfill` / `--no-with-backfill` — enriquecimento em memória com deadline backfill
- `--output outputs/post_apply_consolidation`
- `--sources grants_gov doe_arpae bndes`
- `--limit 1000`

## Saídas

`backend/outputs/post_apply_consolidation/`:

1. `summary.md` — resumo geral + tabela de applies + métricas por fonte
2. `consolidated_metrics.json`
3. `source_breakdown.json`
4. `deadline_status_by_source.json`
5. `actionability_by_source.json`
6. `no_deadline_review.json`
7. `rejected_or_blocked_review.json`
8. `pdf_detail_candidates_review.json`
9. `applied_updates_summary.json`
10. `next_actions.md`

## Métricas

- Oportunidades acionáveis, `oportunidade_principal`, `oportunidade_sem_prazo`
- Validade: `aberto`, `vencendo_7`, `vencendo_30`, `encerrado`, `sem_prazo`, `nao_aplicavel`
- Ruído provável (`is_noise`) — **separado** de `sem_prazo` e `encerrado`
- Distribuição `quality_level`
- Apply logs: updates, erros, status

## Interpretação correta

| Status | É ruído? | Notas |
|--------|----------|-------|
| `sem_prazo` | Não | Oportunidade real pode existir sem deadline estruturado |
| `encerrado` | Não | Prazo conhecido já vencido |
| `resultado` (actionability) | Não necessariamente | Documento pós-edital |
| `portal_util` | Não é erro | Hub/navegação útil |
| BNDES Resultado Final | Não aberto | Não promover como oportunidade aberta |

## Applies executados (referência)

| Fonte | Updates | Erros |
|-------|---------|-------|
| Grants.gov | 151 | 0 |
| DOE_ARPAE | 4 | 0 |
| BNDES | 1 | 0 |

## Limitações

- Sem Supabase configurado, métricas de registros usam **recrawl fallback** (`outputs/recrawl/...`) — subset, não espelho completo do banco.
- Apply logs ausentes aparecem como `unknown` sem abortar o script.

## Próximos passos recomendados

Ver `next_actions.md` gerado — categorias APPLY_DONE_OK, NEEDS_MANUAL_REVIEW, NEEDS_DETAIL_FETCH, NEEDS_SOURCE_SEMANTICS, READY_FOR_FRONTEND_BADGES, SECURITY_NEXT.

## Testes

```bash
python -m pytest tests/test_post_apply_consolidation.py -q
```
