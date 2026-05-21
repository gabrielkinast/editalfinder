# Wave 1 — Crawler piloto Objetiva Concursos

## Diagnóstico (estrutura pública)

| Aspeto | Observação |
|--------|------------|
| **Portal** | `https://concursos.objetivas.com.br` — CMS **selecao.net** (mesma família Quadrix/IBFC). |
| **Listagens** | `/index/abertos/` (inscrições abertas), `/index/1/` (em andamento). Menu também: futuros, encerrados (`/index/3/`), todos (`/index/todos/`). |
| **Detalhe** | `/informacoes/{id}/` — `#TopoInformacoes`, `p.insc` (período de inscrição), `p.situacaoConcurso`, `#blocoPublicacoes` (PDFs em `cdn.selecao.net.br`), `#blocoEventos` (cronograma), `#blocoListaVagas` (cargos, escolaridade, taxa). |
| **Inscrição** | Período no HTML; inscrição online via portal (não extraída neste piloto). |
| **Tipo** | **HTML** servido (UTF-8 / ISO-8859-1); sem API JSON pública identificada. |
| **robots.txt** | `User-agent: *` — Disallow `/admin/*`, `/painel/*`, `/uploads/*`. O fetch padrão do `RobotFileParser.read()` recebe **403** sem User-Agent; o crawler usa `_load_robots_parser` com cabeçalho identificado. |

## Script e comandos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_objetiva_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave1_objetiva/standardized/objetiva_standardized.json` |
| Resumo | `crawler_summary.json` / `.md` |
| Testes | `tests/test_objetiva_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_objetiva_concursos.py --max-items 15 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_objetiva/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_objetiva/loader_dryrun --sources objetiva
python -m pytest tests/test_objetiva_crawler.py -q
```

## Regras implementadas

- **Fonte:** `fonte=objetiva`, `fonte_tipo=banca`, `banca=Objetiva Concursos`, `categoria=banca_objetiva_concurso`.
- **`validacao_status`:** `valido` com `link_edital` (PDF em `#blocoPublicacoes`) + `data_fim_inscricao`; caso contrário `incompleto`.
- **Descarte:** situação encerrada/cancelada/suspensa, heurísticas resultado/gabarito/homologação, `recency_should_discard`.
- **Sem invenção:** vagas = linhas em `#blocoListaVagas`; taxa da tabela de vagas ou texto; salário só quando não ambíguo com taxa.

## Limitações

1. Volume ativo pequeno nas listagens `abertos` + `andamento` (muitos itens em andamento com inscrição já encerrada).
2. **`estado` / `municipio`:** título traz `CIDADE/UF` mas o inferidor geográfico nem sempre separa; costumam ficar nulos.
3. **`data_prova`:** só quando consta em `#blocoEventos` ou texto; frequentemente ausente.
4. **`salario_min` / `salario_max`:** valores monetários no HTML podem ser taxas; notas em `extras.value_extraction_notes`.
5. **`numero_vagas`:** contagem de linhas de cargo, não total oficial do edital.

## Última corrida de referência (2026-05-16)

| Métrica | Valor |
|---------|------:|
| URLs candidatas (bruto, cap) | **12** |
| Descartados | **9** (maioria `data_fim_inscricao_passada_sem_prova_futura`) |
| **Standardized** | **3** |
| Erros de crawl | **0** |
| Loader dry-run | `errors_count` **0**, `would_upsert_total` **3**, todos `valido` |

Campos bem preenchidos no subset: título, tipo, órgão/instituição, banca, cargo, nível (quando na tabela), vagas, taxa, datas de inscrição, `link`, `link_edital`, validação, qualidade.

Costumam ausentes: `estado`, `municipio`, `salario_*`, `data_prova`, `area`, `curso`.

## Recomendação de apply em staging

Dry-run limpo com **3** registos `valido`: recomenda-se **apply em staging** após amostragem de PDFs e conferência de `numero_vagas` / taxas. Volume baixo — útil como fonte regional complementar, não como feed principal. **Apply não executado neste piloto.**

## Relação com o módulo

- **Tabela alvo:** `public.concurso_selecao`.
- **PCI:** fonte banca regional; deduplicação global por `link` / metadados.
