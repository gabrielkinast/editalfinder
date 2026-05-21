# Wave 2 — Militar/Aeroespacial — ITA Vestibular (piloto)

Crawler piloto do **Vestibular ITA** para `public.concurso_selecao`.

## Diagnóstico

| Aspeto | Observação |
|--------|------------|
| **Portal** | `https://www.vestibular.ita.br/` — frameset (`topo.htm` + `principal.htm`) |
| **Edital** | `instrucoes/edital_2026_retificado.pdf` (link no topo) |
| **Cronograma** | `principal.htm` — Vestibular **2027**; 1ª fase **27 set 2026**; 2ª fase **20–23 out 2026** |
| **PDF** | Escaneado (`text_len` baixo) — datas de inscrição não extraídas automaticamente |
| **Inscrição** | Período SIPTI «encerrado» no HTML; `data_fim_inscricao` geralmente ausente → `incompleto` |

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_militar_aeroespacial_ita.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ita/standardized/ita_standardized.json` |
| Mapeamento geral | [CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md](./CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_FONTES.md) |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_militar_aeroespacial_ita.py --max-items 5 --sleep 2.0
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ita/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ita/loader_dryrun --sources ita
python -m pytest tests/test_militar_aeroespacial_ita_crawler.py -q
```

## Mapeamento

| Campo | Valor |
|--------|--------|
| `fonte` | `ita` |
| `fonte_tipo` | `instituicao` |
| `tipo_selecao` | `vestibular` |
| `categoria` | `militar_aeroespacial_ita_vestibular` |
| `orgao` / `instituicao` | ITA |
| `banca` | `ITA — Comissão de Vestibular` |
| `estado` / `municipio` | SP / São José dos Campos |
| `link` | `https://www.vestibular.ita.br/principal.htm` |
| `link_edital` | PDF edital (topo) |
| `validacao_status` | `valido` iff `link_edital` + `data_fim_inscricao` |

## Regras

- Não inventar vagas, taxa ou datas de inscrição.
- Manter com `data_prova` futura mesmo sem `data_fim` (recência).
- Apply **não** executado nesta wave.

## Última corrida de referência (2026-05-17)

| Métrica | Valor |
|---------|------:|
| Standardized | **1** (Vestibular 2027) |
| `valido` | **0** (sem `data_fim_inscricao` no HTML/PDF) |
| `incompleto` | **1** |
| `data_prova` | **2026-09-27** (1ª fase) |
| `link_edital` | PDF retificado 2026 |
| Loader dry-run | `errors_count` **0** |
| pytest | **4** passed |
