# Wave 2 — Fuvest (USP)

## Diagnóstico da estrutura pública

| Aspeto | Observação |
|--------|------------|
| **Site** | [www.fuvest.br](https://www.fuvest.br/) — WordPress |
| **Hubs** | Vestibular, Concursos, Residência, Pós-graduação (URLs fixas no crawler) |
| **Concursos USP** | Páginas por edital (`auxiliar-laboratorio-2026`, `tecnico-laboratorio-2026`, …) com PDF de abertura |
| **Vestibular 2027** | Calendário no HTML: inscrições `17/08/2026`–`09/10/2026`, 1ª fase `15/11/2026` |
| **SSL** | Certificado pode falhar em Windows sem cadeia ICP-Brasil; crawler usa fallback SSL só para `fuvest.br` |
| **robots.txt** | Não bloqueante nas rotas usadas (2026) |

## Hubs e `tipo_selecao`

| URL | `tipo_selecao` | Coleta filha |
|-----|----------------|--------------|
| `/vestibular-da-usp` | `vestibular` | Só a página hub (evita menu lateral de concursos) |
| `/concursos/` | `concurso_publico` / `processo_seletivo` | Editais `auxiliar-*`, `tecnico-*`, `especialista-*`, … |
| `/residencia/` | `residencia` | `residencia-medica`, `residencia-ipusp`, etc. (exclui notícias) |
| `/pos-graduacao/` | `programa_ingresso` | Processos `*-2026-*` com inscrição/seleção (exclui notícias) |

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_fuvest_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_fuvest/standardized/fuvest_standardized.json` |
| Resumo | `crawler_summary.json` / `.md` |
| Testes | `tests/test_fuvest_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_fuvest_concursos.py --max-items 12 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_fuvest/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_fuvest/loader_dryrun --sources fuvest
python -m pytest tests/test_fuvest_crawler.py -q
```

Opções: `--no-pdf` desativa enriquecimento por PDF.

## Mapeamento de campos

| Campo | Valor / origem |
|--------|----------------|
| `fonte` | `fuvest` |
| `fonte_tipo` | `universidade` |
| `orgao` | `Fuvest — Fundação Universitária para o Vestibular` |
| `instituicao` | `Universidade de São Paulo (USP)` |
| `banca` | `Fuvest` |
| `estado` / `municipio` | `SP` / `São Paulo` |
| Datas | HTML (`Inscrição: das 12h de … até …`) + `fgv_schedule_from_text` em PDF |
| `link_edital` | PDF com «edital» / «abertura» no rótulo ou URL |
| `validacao_status` | `valido` se `link_edital` **e** `data_fim_inscricao` |

## Regras

- Não inventar datas, vagas ou taxas.
- `incompleto` sem `data_fim_inscricao`.
- Descarte por recência (`recency_should_discard`) e páginas de resultado/lista (sem edital/datas).
- Excluir paginação (`/residencia/2`) e slugs de notícia (resultado, lista, convocação).
- PDF: até 6 MB, sem OCR.

## Última corrida de referência (2026-05-16)

| Métrica | Valor |
|---------|------:|
| URLs candidatas | **22** |
| Descartados | **20** |
| **Standardized** | **2** |
| `valido` | **0** |
| `incompleto` | **2** |
| Loader dry-run | `errors_count` **0**, `would_upsert_total` **2** |
| pytest | **6** passed |

**Mantidos:**

1. **Vestibular USP 2027** — `data_inicio`/`data_fim` e `data_prova` no HTML; taxa R$ 228; sem PDF de edital prioritizado na página → `incompleto`.
2. **Hub Pós-graduação** — landing sem cronograma estruturado → `incompleto`.

**Descartes típicos:** concursos 2025/2026 com inscrição já encerrada (ex. Auxiliar Laboratório mar/2026); notícias de residência; hub `/concursos/` (datas antigas no carrossel).

## Recomendação de apply em staging

**Não recomendado** neste momento: **0** `valido`. Manter **implementado/latente** até:

1. Publicação de PDF de edital do Vestibular 2027 na página oficial.
2. Novos concursos com inscrições abertas (ou relaxar recency só para páginas com `data_fim` futura já extraída).

**Apply não executado** neste piloto.

## Relação com o módulo

- Deduplicação por `(fonte, link)` com `fonte=fuvest`.
- Ver também: [CONCURSOS_WAVE2_FONTES_PRIORIZADAS.md](./CONCURSOS_WAVE2_FONTES_PRIORIZADAS.md).
