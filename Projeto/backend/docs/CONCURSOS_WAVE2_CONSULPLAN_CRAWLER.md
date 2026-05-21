# Wave 2 — Instituto Consulplan

Crawler piloto da banca **Consulplan** (`institutoconsulplan.org.br`) para `public.concurso_selecao`.

## Diagnóstico

| Aspeto | Observação |
|--------|------------|
| **Stack** | ASP.NET WebForms (`concursosNovo.aspx`, `getConc.aspx?key=`) |
| **Listagem** | Uma página com três painéis: **Abertas/Aguardando**, **Em andamento**, **Encerrados** |
| **Seletividade** | Crawler usa só os dois primeiros painéis; **Encerrados** ignorado |
| **Detalhe** | `getConc.aspx` — título, botão inscrição, tabela de publicações (PDF na CDN) |
| **Datas** | Pouco texto no HTML; enriquecimento opcional via PDF (`fgv_edital_dates`, até 6 MB) |
| **robots.txt** | Inexistente (404); bloqueio manual de `/admin/`, `/painel/` |

### Painéis na listagem

| ID do painel | Uso no crawler |
|--------------|----------------|
| `ContentPlaceHolder1_PanelRepeaterAbertas_e_Aguardando` | **Sim** (`secao_listagem=abertas`) |
| `ContentPlaceHolder1_PanelRepeaterAndamento` | **Sim** (`andamento`) |
| `ContentPlaceHolder1_PanelRepeaterConcluidos` | **Não** |

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_consulplan_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_consulplan/standardized/consulplan_standardized.json` |
| Testes | `tests/test_consulplan_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_consulplan_concursos.py --max-items 10 --sleep 2.0
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_consulplan/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_consulplan/loader_dryrun --sources consulplan
python -m pytest tests/test_consulplan_crawler.py -q
```

`--no-pdf` desativa download de PDF para datas.

## Regras

- `valido` = `link_edital` + `data_fim_inscricao`
- Descarte por `recency_should_discard` (inscrição/prova passadas)
- Descarte de publicações tipo gabarito/resultado/homologação
- Apply **não** executado nesta wave

## Última corrida de referência (2026-05-17)

| Métrica | Valor |
|---------|------:|
| Candidatos listagem (abertas+andamento) | **32** |
| Encerrados ignorados | painel `PanelRepeaterConcluidos` |
| Standardized (`--max-items 10`) | **10** |
| `valido` | **0** (PDFs frequentemente sem texto extraível — `text_len` baixo) |
| `incompleto` | **10** |
| Loader dry-run | `errors_count` **0**, `would_upsert` **10** |
| pytest | **4** passed |

**Nota:** certames em **abertas** com edital/botão de inscrição são mantidos mesmo sem `data_fim` no HTML/PDF; andamento passa por `recency_should_discard`.
