# Wave 2 — Vestibulares / Ingresso (UFSC — Coperve)

## Escolha da fonte

| Fonte | Viabilidade | Motivo |
|-------|-------------|--------|
| **Vunesp Vestibulares** | Não | `vunesp.com.br` → HTTP 403; `vestibular.vunesp.com.br` → falha DNS no ambiente de teste. WAF documentado no stub `main_vunesp_concursos.py`. |
| **Comvest/Unicamp** | Não | `robots.txt` com `Disallow: /` para todos os user-agents. |
| **Fuvest** | Parcial | HTML rico (~168 KB), mas `CERTIFICATE_VERIFY_FAILED` com `urllib` padrão em Windows; exige ajuste SSL/certifi. Candidata Wave 2b. |
| **UFSC Coperve** | **Sim** | HTML público, robots permissivo (exc. calendários), subdomínios oficiais `*.ufsc.br`, portal de inscrição com período explícito (`De DD/MM/YYYY a DD/MM/YYYY`). |

**Fonte implementada:** `coperve` (organizador: Coperve / UFSC).

## Diagnóstico (estrutura pública)

| Aspeto | Observação |
|--------|------------|
| **Hubs** | `coperve.ufsc.br`, `coperve.ufsc.br/proximos-vestibulares/`, `coperve.paginas.ufsc.br/proximos-vestibulares/` |
| **Processos** | Subdomínios (`vestibularunificado2026.ufsc.br`, `refugiados2026.ufsc.br`), páginas `coperve.paginas.ufsc.br/processo-seletivo-*` |
| **Inscrição** | `vestibular.coperve.ufsc.br/inscricao/evento/{id}/dados` — HTML com «De … a …» (não API JSON pública) |
| **Editais** | PDFs em `*.ufsc.br/files/...` (edital, programa vestibular) |
| **Tipo** | HTML WordPress / portais institucionais; **não** SPA pesada nos hubs analisados |
| **robots.txt** | `coperve.ufsc.br`: disallow parcial (`/calendar/...`); fetch com User-Agent identificado |

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_vestibulares_coperve.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave2_vestibulares_coperve/standardized/coperve_standardized.json` |
| Resumo | `crawler_summary.json` / `.md` |
| Testes | `tests/test_vestibulares_coperve_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_vestibulares_coperve.py --max-items 12 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_coperve/standardized --output-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_coperve/loader_dryrun --sources coperve
python -m pytest tests/test_vestibulares_coperve_crawler.py -q
```

## Mapeamento de campos

| Campo | Origem |
|--------|--------|
| `tipo_selecao` | `vestibular` ou `programa_ingresso` (suplementares, refugiados, histórico escolar) |
| `fonte` / `fonte_tipo` | `coperve` / `universidade` |
| `orgao` / `instituicao` / `banca` | Coperve / UFSC |
| `estado` / `municipio` | SC / Florianópolis (sede UFSC) |
| `nivel_escolaridade` | `ensino_medio` |
| `data_*` | Texto da página + portal `evento/.../dados` quando linkado |
| `link_edital` | PDF com «edital» ou «programa» no rótulo/caminho (sem repositório de obras literárias) |
| `link` | URL oficial do processo (subdomínio ou página Coperve) |

## Regras

- `validacao_status = valido` somente com `link_edital` + `data_fim_inscricao`.
- Descarte: `recency_should_discard`, inscrições encerradas sem período futuro, títulos de processos antigos.
- **Não** seguir `concursos.ufsc.br` (concursos públicos DDP, fora do escopo vestibular).
- **Não** inventar vagas, datas ou taxas.

## Última corrida de referência (2026-05-16)

| Métrica | Valor |
|---------|------:|
| URLs candidatas | **12** |
| Descartados | **3** (vestibular unificado encerrado; refugiados com fim 14/05/2026) |
| **Standardized** | **9** |
| `valido` | **0** (nenhum com fim de inscrição + PDF no subset mantido) |
| `incompleto` | **9** |
| Loader dry-run | `errors_count` **0**, `would_upsert_total` **9** |
| `tipo_selecao` | 2 vestibular, 7 programa_ingresso |

### Limitações

1. Muitos processos suplementares publicam cronograma genérico («conforme prazos legais») sem `data_fim_inscricao` no HTML.
2. **Refugiados 2026** tinha período no portal de inscrição, mas foi **descartado** por recência na data da corrida (fim 14/05/2026).
3. **Vestibular Unificado 2026** — inscrições encerradas; páginas `/edital` mantidas como `incompleto` para descoberta, sem datas de inscrição extraídas.
4. `numero_vagas`, `taxa_inscricao`, `data_prova` — raramente estruturados no HTML hub.
5. `fonte=coperve` identifica o **organizador**; não confundir com Fundatec (`fonte=fundatec` na Wave 1).

## Próximos passos

1. **Fuvest** como segunda fonte vestibular (resolver SSL com `certifi` ou bundle corporativo).
2. Enriquecer datas a partir de PDF de edital (sem OCR), só quando URL já for `link_edital`.
3. Re-crawl antes de apply em staging; priorizar processos com portal `evento/.../dados` ativo.
4. **Apply não executado** neste piloto.

## Relação com o frontend

A aba **Vestibulares** em `/concursos` filtra `tipo_selecao` em `vestibular` e `programa_ingresso`. Após apply futuro, entradas `fonte=coperve` aparecerão nessa aba se passarem na recência de `vw_concursos_front`.
