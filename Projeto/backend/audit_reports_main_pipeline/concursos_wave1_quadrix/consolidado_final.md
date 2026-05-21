# Consolidado — Quadrix wave 1 (pré-apply staging)

**JSON:** `consolidado_final.json`  
**Crawler:** `crawler_summary.json` (`collected_at_utc` ≈ 2026-05-14T20:37Z)  
**Loader dry-run:** `loader_dryrun/load_concursos_selecao_summary.json`  
**Erros loader:** `loader_dryrun/load_concursos_selecao_errors.json` → **lista vazia** (`[]`)  
**Payloads exemplo:** `loader_dryrun/load_concursos_selecao_payload_examples.json` (10 linhas, alinhadas ao standardized)

## Totais

| Origem | Métrica | Valor |
|--------|---------|------:|
| Crawler | URLs brutas (candidatas, dedupe) | **10** |
| Crawler | Descartados | **0** |
| Crawler | Standardized gravados | **10** |
| Crawler | `errors` | **0** |
| Loader (dry-run) | `total_items` | **10** |
| Loader (dry-run) | `would_upsert_total` | **10** |
| Loader (dry-run) | `errors_count` | **0** |
| Loader (dry-run) | `expired_items_count` | **0** |

## Distribuições

| Campo | Distribuição |
|--------|----------------|
| `validacao_status` | `valido`: **10**, `incompleto`: **0** |
| `qualidade_dado` | `media`: **10** |
| `tipo_selecao` | `concurso_publico`: **6**, `processo_seletivo`: **4** |
| `status` | `inscricoes_abertas`: **10** |

## Campos

**Bem preenchidos (10/10 no snapshot):** título, tipo, categoria, órgão, instituição, banca, cargo, nível escolaridade, número de vagas, taxa, datas (publicação, início e fim de inscrição, prova), status, `link`, `link_edital`, fonte, validação, qualidade, tags, extras, ativo.

**Geralmente ausentes:** `estado`, `municipio`, `area`, `curso`, `salario_min`, `salario_max`, `regiao`, `modalidade`.

## Revisão de datas

- Origem: texto oficial (`p.insc` + cronograma «Prova objetiva»).
- Valores distintos de `data_fim_inscricao`: 2026-05-18, 2026-05-20, 2026-06-08, 2026-06-22, 2026-07-13.
- **Atenção:** vários certames com fim **2026-05-18** ou **2026-05-20** — poucos dias após o crawl; úteis em staging/histórico, podem estar ultrapassados no front sem novo crawl.
- **SEDES:** `data_publicacao` 2026-05-13 vs `data_inicio_inscricao` 2026-06-09 — conferir página viva e messaging.

## Revisão de `link_edital`

- Todos os PDFs em `anexos.cdn.selecao.net.br/.../concursos/{id}/anexos/*.pdf`.
- Nenhum `official_link_missing`.
- Sugestão: abrir amostralmente 1–2 PDFs antes do primeiro apply.

## Revisão de taxas e vagas

- Taxa e vagas da **primeira linha** de `#blocoListaVagas`.
- Faixa de taxa no lote: **60** a **2500** (exames de suficiência no topo).
- Risco: totais de vagas por certame com vários cargos podem subestimar o agregado real.

## Riscos restantes

1. Geolocalização vazia na maioria dos registos.  
2. Primeira linha da tabela de vagas pode não representar o certame completo.  
3. Cobertura limitada às listagens piloto e ao dedupe do momento.  
4. Calendário pode mudar no site sem novo crawl.

## Classificação por registro (uma etiqueta principal)

| `link` | Classificação | Motivo (resumo) |
|--------|---------------|-----------------|
| …/3032 | `pronto_para_apply` | Janelas amplas; taxa típica |
| …/3063 | `pronto_para_apply` | Idem |
| …/3043 | `revisar_data` | Fim inscrição 2026-05-20 |
| …/3046 | `revisar_data` | Idem |
| …/3051 | `revisar_data` | Idem |
| …/1018 | `revisar_data` | Idem |
| …/3059 | `revisar_valor` | Taxa 1500 + fim 2026-05-18 |
| …/3058 | `revisar_valor` | Taxa 1500 |
| …/1012 | `revisar_valor` | Taxa 2500 |
| …/3056 | `revisar_data` | Início inscrição vs publicação |

**Contagens:** `pronto_para_apply` 2 · `revisar_data` 5 · `revisar_valor` 3 · `revisar_link` 0 · `descartar` 0.

## Recomendação de apply (staging)

- **Recomendado:** **apply de todos os 10** em staging **depois** de amostragem rápida nos grupos `revisar_data` e `revisar_valor` (não exige alteração ao crawler: dry-run limpo).
- **Alternativa conservadora:** aplicar só os 2 `pronto_para_apply` e expandir após revisão.

## Comando apply staging (referência — não executar)

Ver `consolidado_final.json` → `comando_apply_staging` (PowerShell e bash).

## Reprodução (sem apply)

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python -m pytest tests/test_quadrix_crawler.py -q
python concursos/main_quadrix_concursos.py --max-items 40 --sleep 1.2
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_quadrix/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_quadrix/loader_dryrun --sources quadrix
```
