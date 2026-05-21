# Wave 2 — Avança SP

Crawler piloto da banca **Avança SP** (`avancasp.org.br`) para `public.concurso_selecao`.

## Diagnóstico

| Aspeto | Observação |
|--------|------------|
| **CMS** | ProSeleta / **selecao.net** (mesma família Quadrix, Objetiva, IBFC) |
| **Listagem** | [index/abertos/](https://www.avancasp.org.br/index/abertos/) — cards com links `/informacoes/{id}/` |
| **Detalhe** | `#TopoInformacoes`, `p.insc`, `#blocoPublicacoes`, `#blocoEventos`, `#blocoListaVagas` |
| **PDF** | CDN `anexos.cdn.selecao.net.br` (URL absoluta no HTML) |
| **robots.txt** | `Disallow: /admin/*`, `/painel/*`, `/uploads/*` — **listagem e detalhe permitidos** |
| **API** | Não há JSON público; HTML server-rendered + assets `static-cdn.selecao.net.br` |

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_avancasp_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_avancasp/standardized/avancasp_standardized.json` |
| Testes | `tests/test_avancasp_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_avancasp_concursos.py --max-items 10 --sleep 2.0
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_avancasp/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_avancasp/loader_dryrun --sources avancasp
python -m pytest tests/test_avancasp_crawler.py -q
```

## Mapeamento

| Campo | Valor |
|--------|--------|
| `fonte` | `avancasp` |
| `fonte_tipo` | `banca` |
| `banca` | `Avança SP` |
| `categoria` | `banca_avancasp_concurso` |
| `validacao_status` | `valido` iff `link_edital` + `data_fim_inscricao` |

## Regras

- Respeitar `robots.txt` (sem override; rotas `/painel/` excluídas no código).
- `--max-items` e `--sleep` conservadores (default 10 e 2,0 s).
- Descartar certames antigos, resultado/gabarito/convocação sem oportunidade ativa.
- Apply **não** executado nesta wave.

## Última corrida de referência (2026-05-17)

| Métrica | Valor |
|---------|------:|
| URLs listagem (únicas) | **5** |
| Standardized | **5** |
| `valido` | **5** |
| Loader dry-run | `errors_count` **0**, `would_upsert` **5** |
| pytest | **4** passed |
