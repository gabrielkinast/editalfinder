# Backend 9 — Ruído, validade e qualidade

> **Calibração:** ver [BACKEND_10_NOISE_CALIBRATION.md](./BACKEND_10_NOISE_CALIBRATION.md) para `actionability_type`, métricas de relatório e regras refinadas (`backend_10.0`).

Camada central **somente leitura** (classificação + relatórios) antes de qualquer UPDATE em massa ou backfill na sombra.

## Problema

Muitos registros em `public.edital` aparecem “sem validade” no frontend porque:

1. São **notícias, portais, resultados ou retificações** — prazo de inscrição não se aplica (`nao_aplicavel`).
2. São **oportunidades reais** sem prazo estruturado no crawler (`sem_prazo`).
3. Têm **prazo inválido** ou extraído com baixa confiança.

Backend 9 separa esses casos para o front não “adivinhar”.

## `sem_prazo` vs `nao_aplicavel`

| Status | Significado |
|--------|-------------|
| `sem_prazo` | Oportunidade acionável, mas sem data de encerramento confiável |
| `nao_aplicavel` | Notícia, portal, evento, resultado, retificação, etc. — prazo de edital não faz sentido |
| `encerrado` / `aberto` / `vencendo_7` / `vencendo_30` | Prazo estruturado interpretado |
| `prazo_invalido` | Texto/data inválida |
| `desconhecido` | Dados insuficientes |

## Ruído (`noise_classifier`)

Não exclui registros. Retorno principal: `classify_noise(record)`.

Tipos: `noticia`, `portal`, `evento`, `resultado`, `homologacao`, `retificacao`, `documento_auxiliar`, `pagina_institucional`, `sem_oportunidade`, `duplicata_provavel`, `link_invalido`, `prazo_inexistente`, `outro`.

Exemplos:

- “Resultado preliminar do edital X” → `resultado`, não acionável principal.
- “Retificação da chamada pública Y” → `retificacao` / `documento_auxiliar`.
- “Chamada pública para projetos” → acionável, `is_noise=false`.

Perfis por fonte: `CORE/source_quality_profiles.py` (flags, sem alterar crawlers).

## Validade (`validity_resolver`)

`resolve_validity(record)` usa `normalize_deadline` + `classify_noise`.

## Qualidade (`quality_score`)

`compute_quality_score(record, enrichment)` → score 0–100, nível `alto|medio|baixo|revisao`.

Não filtra listagens automaticamente — marca `revisao_humana` via flags.

## Enriquecimento `backend_9.0`

`CORE/opportunity_enricher.py` — versão `backend_9.0`, campos novos em `extras.backend_enrichment`:

`noise_score`, `is_noise`, `noise_type`, `is_actionable_opportunity`, `actionability_score`, `validade_status`, `validade_data`, `validade_raw`, `validade_confidence`, `validade_source`, `quality_score`, `quality_level`, `quality_flags`, `review_reasons`.

Feature flag inalterada: `EDITALFINDER_ENABLE_BACKEND_ENRICHMENT=false` por padrão.

## Scripts

```bash
cd backend

# Ruído
python scripts/audit_noise_backend.py --from-db --limit 5000

# Validade (explica os +400 “sem validade”)
python scripts/audit_validity_backend.py --from-db --limit 5000

# Dry-run completo Backend 9
python scripts/dry_run_quality_enrichment.py --from-db --limit 5000
```

Saídas:

| Script | Pasta |
|--------|--------|
| `audit_noise_backend.py` | `outputs/audit_noise_backend/` |
| `audit_validity_backend.py` | `outputs/audit_validity_backend/` |
| `dry_run_quality_enrichment.py` | `outputs/backend_9_quality_dry_run/` |

## Testes

```bash
python -m pytest backend/tests/test_noise_classifier.py backend/tests/test_validity_resolver.py backend/tests/test_quality_score.py -q
```

## SQL (proposta)

`docs/sql/PROPOSAL_BACKEND_ENRICHMENT_COLUMNS.sql` e `PROPOSAL_VW_EDITAIS_FRONT_WITH_SHADOW.sql` — **não aplicar** sem aprovação.

## Próximos passos

1. Rodar auditorias em staging/produção (read-only).
2. Revisar `nao_aplicavel` vs `sem_prazo` por fonte.
3. Ajustar crawlers prioritários (fontes com mais ruído no ranking).
4. Gerar payload sombra Backend 7+9 e backfill controlado (sem DELETE).

## O que não faz

- UPDATE em massa em `public.edital`
- Alteração de frontend
- IA externa / OCR
- Auto-exclusão de registros
