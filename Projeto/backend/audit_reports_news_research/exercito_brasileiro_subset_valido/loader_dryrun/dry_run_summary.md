# Dry-run news/research → noticia / pesquisa

- Gerado em: `2026-05-17T04:05:27Z`
- Entrada: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\exercito_brasileiro_subset_valido\standardized`
- **Sem Supabase**, sem apply. Deduplicação por link antes das métricas.

## Totais

- Itens antes dedupe: **6**
- Itens depois dedupe: **6**
- **deduplicated_total**: **0**
- Simulado `public.noticia`: **6**
- Simulado `public.pesquisa`: **0**
- **review_for_edital_total**: **0** (só sinal forte em título/URL)
- **rejected_noise_total**: **0**
- **missing_date_total**: **0**
- **review_missing_date_total** (notícia sem data): **0**
- **missing_summary_total**: **0**
- Fora dos últimos 12 meses: **0**

## Qualidade

- Itens com campos faltantes: **0**
- Arrays mal tipados: **0**

## Readiness apply futuro (por fonte)

```json
{
  "exercito_brasileiro": {
    "apply_futuro_ok": true,
    "motivo": "criterios_minimos_ok"
  }
}
```

## NASA Onda 1

- **nasa_news**: `{}`

## Por fonte

```json
[
  {
    "source_id": "exercito_brasileiro",
    "total": 6,
    "noticia": 6,
    "pesquisa": 0,
    "review_for_edital": 0,
    "rejected_noise": 0,
    "sem_data": 0,
    "fora_12_meses": 0,
    "missing_summary": 0,
    "review_missing_date": 0,
    "pesquisa_sem_data": 0,
    "missing_fields_total": 0,
    "array_issues_total": 0,
    "dedupe_removidos_destino_fonte": 0,
    "linhas_pre_dedupe": 6,
    "linhas_removidas_no_dedupe": 0
  }
]
```

## Plano por ondas

```json
{
  "waves": {
    "onda_1": [
      "nasa_news"
    ],
    "onda_2": [
      "darpa_news"
    ],
    "onda_3": [
      "darpa_opportunities_research"
    ],
    "pendentes": [],
    "preparacao_iaea_wave1": [
      "iaea_news_publications"
    ],
    "preparacao_eurekalert_wave1": [
      "eurekalert_science_filtered"
    ]
  },
  "notas_por_fonte": {
    "nasa_news": "sem_itens",
    "darpa_news": "onda_2_apos_reduzir_ruido_e_sem_data",
    "darpa_opportunities_research": "onda_3_apos_politica_pesquisa_vs_edital",
    "iaea_news_publications": "wave1: crawl + build_iaea_wave1_payloads + load --dry-run --wave iaea_wave1 (sem apply)",
    "eurekalert_science_filtered": "wave1: crawl + build_eurekalert_wave1_payloads + generate_eurekalert_wave1_diagnostico + load --dry-run --wave eurekalert_wave1 (sem apply; WAF pode bloquear bots)"
  },
  "totais_globais": {
    "total_antes_dedupe": 6,
    "total_depois_dedupe": 6,
    "deduplicated_total": 0,
    "public.noticia": 6,
    "public.pesquisa": 0,
    "review_for_edital": 0,
    "rejected_noise": 0,
    "missing_date_total": 0,
    "review_missing_date_total": 0,
    "missing_summary_total": 0
  }
}
```

## Recomendação por fonte

- **exercito_brasileiro**: pendente_crawler

## Ajustes antes de qualquer apply

- Reexecutar crawler após melhorias de RSS/HTML para datas e resumos.
- Itens noticia com review_missing_date: corrigir data na fonte antes do apply.
- Itens com missing_summary: enriquecer só a partir de HTML/RSS real (sem invenção).
- Manter dedupe por link no job de carga dedicado.
- Auditoria manual apenas para review_for_edital; nunca public.edital automático neste módulo.

## Dedupe

- Ver `dedup_report.json` / `dedup_report.md` (0 removidos).
