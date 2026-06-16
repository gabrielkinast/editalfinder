# Backend 10 — Calibração de ruído, validade e acionabilidade

Refinamento do Backend 9 com base no dry-run real (~1232 registros).

## Resultado Backend 9 (referência)

| Métrica | Valor |
|---------|------:|
| Total | 1232 |
| Acionáveis | 142 |
| `nao_aplicavel` | 953 |
| `sem_prazo` real | 100 |
| Ruído `is_noise` | 93 |
| Confusão | `noise_by_type` listava `sem_oportunidade` para quase todos os registros, mesmo quando `is_noise=false` |

## O que mudou no Backend 10

### 1. `actionability_type` (taxonomia principal)

| Valor | Uso |
|-------|-----|
| `oportunidade_principal` | Chamada/edital com prazo estruturado |
| `oportunidade_sem_prazo` | Oportunidade real sem data confiável |
| `resultado` / `retificacao` / `documento_auxiliar` | Documentos derivados |
| `portal_util` | Hub de funding (útil, não edital único) |
| `portal_generico` | Sobre, notícias, eventos (menu institucional) |
| `noticia` / `evento` | Conteúdo não acionável |
| `sem_oportunidade` | Sem chamada identificável |

### 2. Métricas de relatório (não confundir)

| Campo | Significado |
|-------|-------------|
| `classification_by_actionability_type` | Buckets: `oportunidade_acionavel`, `nao_aplicavel`, `documento_auxiliar`, `portal_util`, `ruido_provavel`, `desconhecido` |
| `ruido_provavel_count` | Apenas `is_noise=true` |
| `noise_by_type` | Tipos de ruído **somente** onde `is_noise=true` |
| `non_actionable_by_type` | Contagem por `actionability_type` excluindo oportunidades principais |

### 3. Resultado (regras fortes)

Classifica `resultado` só com: resultado final/preliminar, homologação, lista de selecionados, título iniciando em “Resultado”, etc.

**Não** classifica por: chamada, programa, seleção ou edital isolados.

### 4. Evento (regras fortes)

Webinar, workshop, seminário, etc. Título “Eventos” → `portal_generico`, não evento.

“atividades financiadas” (BNB) → `portal_util`, não evento.

### 5. Portal útil vs genérico

- **portal_util:** Funding Opportunities, EIC Accelerator, CAPES Editais, atividades financiadas…
- **portal_generico:** Sobre, Notícias, Privacidade, Data Resources…

### 6. Perfis por fonte

`source_quality_profiles.py`: blocklist BDMG, portal_util BNB/EIC/DoD SBIR, `DE-FOA-*` → oportunidade principal.

### 7. Validade

`validity_resolver` usa `actionability_type`:

- Oportunidades → prazo normal (`aberto`, `sem_prazo`, …)
- `portal_util` → `nao_aplicavel` (sem confundir com edital sem prazo)
- Resultado/retificação → `nao_aplicavel` + nota documento auxiliar

### 8. Enrichment

Versão **`backend_10.0`** — campos `actionability_type`, `classification_bucket`.

## Scripts

```bash
python scripts/audit_noise_backend.py --from-db --limit 5000
python scripts/audit_validity_backend.py --from-db --limit 5000
python scripts/dry_run_quality_enrichment.py --from-db --limit 5000
```

Novos JSONs em `audit_noise_backend/`:

- `classification_by_actionability_type.json`
- `actionability_type_distribution.json`
- `non_actionable_by_type.json`
- `portal_util_examples.json`
- `likely_false_positive_noise.json`
- `source_actionability_breakdown.json`

## Antes / depois esperado

| Indicador | Backend 9 | Backend 10 (meta) |
|-----------|-----------|-------------------|
| Falsos positivos resultado em chamadas | Frequentes | Reduzidos |
| `noise_by_type` sem_oportunidade ≈ total | Sim | Não — só com `is_noise` |
| Portal funding útil | `portal` / ruído | `portal_util` separado |
| Acionáveis | ~142 | Recalibrar após novo dry-run |

Rodar novamente os três scripts e comparar `summary.md`.

## Próximos passos

1. Revisar `likely_false_positive_noise.json` e `likely_false_negative_noise.json`.
2. Ajustar perfis de fonte com maior volume.
3. Shadow/backfill só após aprovação (Backend 7 + 10).

## O que não faz

- UPDATE em massa, migrations, delete, IA, OCR, alteração de frontend.
