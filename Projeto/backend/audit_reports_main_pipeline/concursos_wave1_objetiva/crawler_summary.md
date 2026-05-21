# Crawler piloto — Objetiva Concursos

- **Fonte:** `objetiva` | **Banca:** Objetiva Concursos
- **Portal:** `https://concursos.objetivas.com.br` (CMS selecao.net)
- **Listagens:** `/index/abertos/`, `/index/1/`
- **Coleta (UTC):** `2026-05-16T19:54:31.860648+00:00`
- **URLs candidatas (bruto):** 12
- **Descartados:** 9
- **Standardized:** 3
- **Erros:** 0
- **Ficheiro:** `audit_reports_main_pipeline/concursos_wave1_objetiva/standardized/objetiva_standardized.json`

## Descartes (motivos)

| Motivo | Qtd |
|--------|-----|
| `data_fim_inscricao_passada_sem_prova_futura` | 9 |

## Preenchimento de campos (3 itens)

| Campo | Preenchidos |
|-------|------------:|
| titulo, tipo, orgao, instituicao, banca, cargo, vagas, taxa, datas inscrição, link, link_edital, valido | 3/3 |
| nivel_escolaridade | 1/3 |
| estado, municipio, salario, data_prova | 0/3 |

## Loader dry-run

- `errors_count`: **0**
- `would_upsert_total`: **3**
- `validacao_status`: todos `valido`

## Próximo passo

```powershell
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_objetiva/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_objetiva/loader_dryrun --sources objetiva
```

Documentação: `docs/CONCURSOS_WAVE1_OBJETIVA_CRAWLER.md`

**Apply staging:** recomendado após amostragem (volume baixo, 3 oportunidades ativas). Apply **não** executado.
