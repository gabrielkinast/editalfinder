# Backend 10.2D-HOTFIX — BNDES Submission Deadline Priority

## Objetivo

Corrigir o parser BNDES para que `prazo_envio` represente **somente** prazo de envio/submissão/recebimento de propostas — nunca dúvidas, resultado, diligência, convocação ou aprovação.

## Módulo

- `CORE/bndes_submission_deadline.py` — `extract_bndes_submission_deadline(text)`
  - Retorno: `deadline_kind = submission_deadline`, `confidence`, `ignored_dates`
  - Prioridade alta: bloco **Como participar**, intervalos `a partir de X até as 18h do dia Y`, recebimento de propostas
  - Rejeição: dúvidas, resultado final, due diligence, convocação, aprovação diretoria, lançamento/publicação

## Integração

| Área | Comportamento |
|------|----------------|
| `deadline_backfill._backfill_bndes` | Usa submission extractor antes do fallback genérico |
| `bndes_detail_recrawl` | Preenche `fim_inscricao`/`prazo_envio` só se `deadline_kind == submission_deadline` |
| `bndes_controlled_apply` | Candidato só vai para apply se `deadline_kind == submission_deadline`; datas administrativas em `bndes_ignored_dates` |

## Testes

```bash
python -m pytest tests/test_bndes_controlled_apply.py tests/test_deadline_backfill.py tests/test_validity_resolver.py -q
python scripts/dry_run_bndes_deadline_apply.py --input outputs/recrawl/bndes/bndes_recrawl.json --compare-db
```

## Critérios de aceite (dry-run live)

- FIP IA 2026 → candidato `2026-05-28`
- ETFs → candidato `2025-12-05` (não `2025-11-28` de dúvidas)
- Chamada de Clima → não usa `2027-01-26` como prazo_envio
- Datas de dúvidas/resultado/diligência em `rejected`/`ignored_dates`
- **Nenhum apply automático**
