# Dry-run news/research → noticia / pesquisa

- Gerado em: `2026-05-05T00:22:12Z`
- Entrada: `D:\Computational_Physics\My Projects\edital\audit_reports_news_research\standardized`
- **Sem Supabase**, sem apply. Deduplicação por link antes das métricas.

## Totais

- Itens antes dedupe: **158**
- Itens depois dedupe: **158**
- **deduplicated_total**: **0**
- Simulado `public.noticia`: **127**
- Simulado `public.pesquisa`: **30**
- **review_for_edital_total**: **0** (só sinal forte em título/URL)
- **rejected_noise_total**: **1**
- **missing_date_total**: **17**
- **review_missing_date_total** (notícia sem data): **13**
- **missing_summary_total**: **42**
- Fora dos últimos 12 meses: **0**

## Qualidade

- Itens com campos faltantes: **64**
- Arrays mal tipados: **0**

## Readiness apply futuro (por fonte)

```json
{
  "darpa_news": {
    "apply_futuro_ok": true,
    "motivo": "criterios_minimos_ok"
  },
  "darpa_opportunities_research": {
    "apply_futuro_ok": false,
    "motivo": "volume_baixo"
  },
  "eurekalert_science_filtered": {
    "apply_futuro_ok": false,
    "motivo": "volume_baixo"
  },
  "iaea_news_publications": {
    "apply_futuro_ok": false,
    "motivo": "maioria_sem_resumo"
  },
  "nasa_news": {
    "apply_futuro_ok": true,
    "motivo": "criterios_minimos_ok"
  }
}
```

## NASA Onda 1

- **nasa_news**: `{'apply_futuro_ok': True, 'motivo': 'criterios_minimos_ok'}`

## Por fonte

```json
[
  {
    "source_id": "iaea_news_publications",
    "total": 50,
    "noticia": 40,
    "pesquisa": 10,
    "review_for_edital": 0,
    "rejected_noise": 0,
    "sem_data": 15,
    "fora_12_meses": 0,
    "missing_summary": 42,
    "review_missing_date": 13,
    "pesquisa_sem_data": 2,
    "missing_fields_total": 44,
    "array_issues_total": 0,
    "dedupe_removidos_destino_fonte": 0,
    "linhas_pre_dedupe": 50,
    "linhas_removidas_no_dedupe": 0
  },
  {
    "source_id": "nasa_news",
    "total": 95,
    "noticia": 78,
    "pesquisa": 17,
    "review_for_edital": 0,
    "rejected_noise": 0,
    "sem_data": 0,
    "fora_12_meses": 0,
    "missing_summary": 0,
    "review_missing_date": 0,
    "pesquisa_sem_data": 0,
    "missing_fields_total": 17,
    "array_issues_total": 0,
    "dedupe_removidos_destino_fonte": 0,
    "linhas_pre_dedupe": 95,
    "linhas_removidas_no_dedupe": 0
  },
  {
    "source_id": "darpa_news",
    "total": 10,
    "noticia": 9,
    "pesquisa": 1,
    "review_for_edital": 0,
    "rejected_noise": 0,
    "sem_data": 0,
    "fora_12_meses": 0,
    "missing_summary": 0,
    "review_missing_date": 0,
    "pesquisa_sem_data": 0,
    "missing_fields_total": 1,
    "array_issues_total": 0,
    "dedupe_removidos_destino_fonte": 0,
    "linhas_pre_dedupe": 10,
    "linhas_removidas_no_dedupe": 0
  },
  {
    "source_id": "darpa_opportunities_research",
    "total": 1,
    "noticia": 0,
    "pesquisa": 0,
    "review_for_edital": 0,
    "rejected_noise": 1,
    "sem_data": 0,
    "fora_12_meses": 0,
    "missing_summary": 0,
    "review_missing_date": 0,
    "pesquisa_sem_data": 0,
    "missing_fields_total": 0,
    "array_issues_total": 0,
    "dedupe_removidos_destino_fonte": 0,
    "linhas_pre_dedupe": 1,
    "linhas_removidas_no_dedupe": 0
  },
  {
    "source_id": "eurekalert_science_filtered",
    "total": 2,
    "noticia": 0,
    "pesquisa": 2,
    "review_for_edital": 0,
    "rejected_noise": 0,
    "sem_data": 2,
    "fora_12_meses": 0,
    "missing_summary": 0,
    "review_missing_date": 0,
    "pesquisa_sem_data": 2,
    "missing_fields_total": 2,
    "array_issues_total": 0,
    "dedupe_removidos_destino_fonte": 0,
    "linhas_pre_dedupe": 2,
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
    "pendentes": [
      "iaea_news_publications",
      "eurekalert_science_filtered"
    ]
  },
  "notas_por_fonte": {
    "nasa_news": "candidata_onda_1_criterios_apply_futuro_ok",
    "darpa_news": "onda_2_apos_reduzir_ruido_e_sem_data",
    "darpa_opportunities_research": "onda_3_apos_politica_pesquisa_vs_edital",
    "iaea_news_publications": "pendente_crawler",
    "eurekalert_science_filtered": "pendente_crawler"
  },
  "totais_globais": {
    "total_antes_dedupe": 158,
    "total_depois_dedupe": 158,
    "deduplicated_total": 0,
    "public.noticia": 127,
    "public.pesquisa": 30,
    "review_for_edital": 0,
    "rejected_noise": 1,
    "missing_date_total": 17,
    "review_missing_date_total": 13,
    "missing_summary_total": 42
  }
}
```

## Recomendação por fonte

- **darpa_news**: onda_2_apos_limpeza
- **darpa_opportunities_research**: onda_3_politica_edital
- **eurekalert_science_filtered**: pendente_crawler
- **iaea_news_publications**: pendente_crawler
- **nasa_news**: OK_onda_1_apply_futuro_se_staging_validado

## Ajustes antes de qualquer apply

- Reexecutar crawler após melhorias de RSS/HTML para datas e resumos.
- Itens noticia com review_missing_date: corrigir data na fonte antes do apply.
- Itens com missing_summary: enriquecer só a partir de HTML/RSS real (sem invenção).
- Manter dedupe por link no job de carga dedicado.
- Auditoria manual apenas para review_for_edital; nunca public.edital automático neste módulo.

## Dedupe

- Ver `dedup_report.json` / `dedup_report.md` (0 removidos).
