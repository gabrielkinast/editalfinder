# Wave 1 — Crawler piloto IBFC

## Diagnóstico (estrutura pública)

| Aspeto | Observação |
|--------|------------|
| **Site** | `https://concursos.ibfc.org.br` — HTML (charset frequentemente ISO-8859-1 / Latin-1). |
| **Plataforma** | Mesma família de CMS usada por outras bancas na rede seleção (rotas e seletores alinhados ao crawler Quadrix). |
| **Listagens (piloto)** | `/index/abertos/` (inscrições abertas), `/index/1/` (em andamento). |
| **Detalhe** | `/informacoes/{id}/` — `p.insc`, `p.situacaoConcurso`, `#blocoPublicacoes` (PDFs), cronograma `#blocoEventos`, vagas `#blocoListaVagas`. |
| **API / SPA** | Conteúdo **HTML** servido; sem API JSON pública de catálogo no piloto. |
| **Inscrição** | Links para área do candidato podem existir no portal; `link` canónico = página de informações IBFC. |
| **`robots.txt`** | Em geral `Allow: /`; `Disallow: /admin/*`, `/painel/*`, `/uploads/*`. O crawler não segue `/painel/`. |

## Última corrida de referência (2026-05-14, ambiente local)

Os números variam com o catálogo IBFC. Nesta execução (`--max-items 40 --sleep 1.5`):

| Métrica | Valor |
|---------|--------:|
| URLs candidatas (bruto, cap) | **10** |
| Descartados (`recency_should_discard`) | **9** (inscrições encerradas sem prova futura no critério atual) |
| Standardized | **1** (Jovem Aprendiz 2º semestre 2026, `informacoes/494`) |
| Loader dry-run | `errors_count` **0**, `would_upsert_total` **1** |
| `validacao_status` | **1** × `valido` (há `link_edital` + `data_fim_inscricao`) |

Quando a listagem «em andamento» repetir muitos certames com `data_fim_inscricao` já passada, o piloto pode devolver **poucos** registos — comportamento esperado das regras de recência.

## Script e comandos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_ibfc_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave1_ibfc/standardized/ibfc_standardized.json` |
| Resumo | `audit_reports_main_pipeline/concursos_wave1_ibfc/crawler_summary.json` / `.md` |
| Testes | `tests/test_ibfc_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_ibfc_concursos.py --max-items 40 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_ibfc/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_ibfc/loader_dryrun --sources ibfc
python -m pytest tests/test_ibfc_crawler.py -q
```

## Regras implementadas

- **Fonte:** `fonte=ibfc`, `fonte_tipo=banca`, `banca=IBFC`, `categoria=banca_ibfc_concurso`.
- **`validacao_status`:** `valido` apenas com **ambos** `link_edital` (PDF oficial no HTML) e `data_fim_inscricao`; caso contrário `incompleto`.
- **Sem invenção:** vagas, salários e datas só com evidência na página; valores ambíguos com taxa não entram em `salario_*`.
- **Descarte:** situação encerrada/cancelada/suspensa; heurísticas de não-oportunidade (resultado/gabarito/convocação); `recency_should_discard` para certames antigos.
- **Conservador:** `--max-items`, `--sleep`, `RobotFileParser` em `robots.txt`.

## Limitações

1. Cobertura limitada às listagens configuradas e ao cap `--max-items`.
2. `estado` / `municipio` muitas vezes ausentes na página de informações.
3. `numero_vagas` / `cargo` / `taxa` da **primeira linha** da tabela de vagas quando há vários cargos.
4. `data_prova` a partir do evento «Prova objetiva» no cronograma.

## Recomendação de apply em staging

1. Dry-run obrigatório; confirmar `errors_count = 0`.
2. Revisar amostralmente `link_edital` e datas antes do primeiro `--apply-staging`.
3. Respeitar variáveis de ambiente e política interna (`EDITALFINDER_ALLOW_STAGING_APPLY`, etc.).

## Relação com o módulo

- **Tabela alvo:** `public.concurso_selecao` (carga fora do âmbito deste doc até apply explícito).
- **PCI:** fonte banca direta; deduplicação global conforme regras do agregador.
