# Wave 1 — Crawler piloto FGV Conhecimento

## Diagnóstico da estrutura pública (2026)

| Aspeto | Observação |
|--------|------------|
| **Listagem** | `https://conhecimento.fgv.br/concursos` — **HTML** (Drupal) com links `https://conhecimento.fgv.br/concursos/{slug}`. |
| **Detalhe** | Página por slug; conteúdo principal em `article` / `div.region-content` / `main`. Marcador **«Em Andamento»** no HTML para certames ativos; **«Realizado»** / ausência do marcador para encerrados. |
| **Edital** | Frequentemente **PDF** em `conhecimento.fgv.br/sites/default/files/concursos/*.pdf`. O crawler usa como `link_edital` o PDF oficial quando encontrado (prioridade a âncora cujo texto começa por «Edital»). |
| **Inscrição** | Links para `portal.conhecimento.fgv.br` podem existir; **não** substituem o PDF de edital quando este está presente. |
| **robots.txt** | `https://conhecimento.fgv.br/robots.txt` (Drupal) — rotas públicas de `/concursos/` não costumam estar em `Disallow`; o script consulta `RobotFileParser` antes de GET. |
| **Taxa de pedidos** | `--sleep` entre pedidos; `--max-items` limita quantos certames entram no JSON; listagem truncada de forma conservadora. |
| **PDF de edital** | Download opcional com `--max-pdf-mb`, `--max-pdfs`, `--pdf-timeout`; extração de texto via `CORE.pdf_enrichment` (pypdf/pdfplumber) ou `pypdf` direto — **sem OCR**. Datas procuradas em frases como «período de inscrições», «encerramento das inscrições», «prova objetiva», etc. (`concursos/fgv_edital_dates.py`). |

## Script e artefactos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_fgv_concursos.py` |
| Datas (HTML + PDF texto) | `concursos/fgv_edital_dates.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave1_fgv/standardized/fgv_standardized.json` |
| Resumo crawl | `audit_reports_main_pipeline/concursos_wave1_fgv/crawler_summary.json` / `.md` |
| Loader dry-run | `audit_reports_main_pipeline/concursos_wave1_fgv/loader_dryrun_v2/` (recomendado após enriquecimento PDF) |

### Comandos

```bash
python concursos/main_fgv_concursos.py --max-items 12 --sleep 1.5 --max-pdf-mb 4 --max-pdfs 6 --pdf-timeout 25

python -m pytest tests/test_fgv_crawler.py tests/test_fgv_edital_dates.py -q

python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_fgv/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fgv/loader_dryrun_v2 --sources fgv
```

## Mapeamento para `concurso_selecao` (standardized)

| Campo | Origem |
|--------|--------|
| `titulo` | `og:title` / `h1` / `<title>` da página oficial. |
| `tipo_selecao` | `infer_tipo_selecao_meta` (título + corpo). |
| `categoria` | `banca_fgv_conhecimento`. |
| `orgao` / `instituicao` | Sufixo oficial «… para o/a *entidade*» no título + `infer_orgao_local_from_title` no sufixo (ex.: Prefeitura → município). |
| `banca` | **FGV**. |
| `municipio` / `estado` | Heurísticas PCI quando o sufixo do título casa (ex. Prefeitura de X). |
| `nivel_escolaridade` | `infer_nivel_escolaridade` (texto oficial). |
| `data_inicio_inscricao` / `data_fim_inscricao` / `data_prova` | `fgv_schedule_from_text` no HTML; re-merge após texto do PDF (quando baixado). Padrões PT-BR explícitos; depois helpers PCI onde aplicável — **sem** inventar. |
| `extras.pdf_checked` | `true` se foi feita tentativa de GET do `link_edital` PDF (dentro do limite `--max-pdfs`). |
| `extras.pdf_date_extraction_notes` | Lista curta: resultado do fetch, motor de texto, pistas de regex (`schedule_pdf:*` / `schedule_html:*`). |
| `data_publicacao` | Primeira data ISO inferida do corpo, quando existir. |
| `numero_vagas`, `salario_*`, `taxa_inscricao` | Parsing do texto; **suprimidos** se não houver `data_fim_inscricao` nem PDF de edital (baixa confiança). |
| `link` | URL canónica da página do certame. |
| `link_edital` | URL do PDF de edital quando encontrado. |
| `fonte` | `fgv` |
| `fonte_tipo` | `banca` |
| `validacao_status` | `valido` se **ambos** `link_edital` e `data_fim_inscricao`; caso contrário `incompleto` (p.ex. PDF só imagem ou sem frase parseável — revisão manual). |
| `qualidade_dado` | Após `valido`, `pci_infer_qualidade_dado` é recalculado; nunca fica `baixa` se `valido` (mínimo `media`). |
| `status` / `ativo` | `infer_status_concurso` + regras de descarte (ver código). |

## Regras implementadas

- Apenas conteúdo do domínio **oficial** FGV Conhecimento na coleta.
- Filtra páginas **sem** «Em Andamento» (e descarta «Realizado» / não oportunidade).
- Descarta notícia / resultado / gabarito / homologação final quando heurística indicar o fim da oportunidade ativa.
- `recency_should_discard` (HTML) → opcional **PDF** (só se faltar início/fim/prova após HTML) → **segunda** verificação de recência com datas já fundidas.
- PDF: `--max-pdf-mb`, `--max-pdfs`, `--pdf-timeout`; HEAD opcional para `Content-Length`; **sem OCR**.
- **Não** executar `apply` neste piloto; **não** escrever no Supabase a partir deste doc.

## Última corrida de referência (ambiente de desenvolvimento)

Valores típicos após enriquecimento por PDF + datas **por extenso** (execução local; o catálogo FGV muda ao longo do tempo):

| Métrica | Valor (exemplo) |
|---------|-----------------|
| **URLs candidatas (bruto)** | 32 |
| **Descartados** | 29 |
| **Standardized** | 3 |
| **PDFs analisados** | `pdf_enrichment.attempts` = 3 (só após passar `drop_no` e 1.ª recência HTML; limite típico 0 em `skipped_limit_reached`) |
| **Loader dry-run v2** | `errors_count` = **0**; `would_upsert_total` = 3; `valido` = 1, `incompleto` = 2 |

**Exemplo:** Prefeitura de Macaé — `data_inicio_inscricao` / `data_fim_inscricao` extraídas do PDF com «30 de março de 2026 a 30 de abril de 2026» (`match:periodo_inscricoes_por_extenso`); `validacao_status` = **valido** com `link_edital` + `data_fim_inscricao`. Outros certames podem permanecer **incompleto** se o PDF não trouxer texto útil (imagem) ou só datas em formato não coberto.

## Limitações

1. **HTML variável** — datas e vagas dependem de como o órgão publicou o texto; sem dados explícitos, campos permanecem `null`.
2. **PDF digital vs imagem** — editais digitalizados como imagem não têm camada de texto: **não há OCR**; `validacao_status` pode permanecer `incompleto` até revisão manual ou outra fonte.
3. **Tamanho e volume de PDF** — PDFs acima de `--max-pdf-mb` ou além de `--max-pdfs` por execução não são analisados (nota em `pdf_date_extraction_notes`).
4. **`strip_orgao_title_noise` (PCI)** corta títulos no primeiro « para »; por isso o crawler usa **primeiro** o padrão FGV «Concurso/Processo … para o/a …» no título completo, depois o inferidor PCI no sufixo.
5. **Listagem** — o crawl limita URLs examinadas em função de `--max-items`; não percorre necessariamente todos os slugs históricos numa única execução curta.
6. **Prova no passado** — itens «Em Andamento» com prova já realizada e sem `data_fim_inscricao` futura são descartados como não oportunidade útil para o front.

## Recomendação de apply staging

- Manter **dry-run** obrigatório após cada crawl; confirmar `errors_count = 0`.
- Só considerar **`--apply-staging`** com revisão manual de `link`, `link_edital`, datas e `validacao_status` (muitos registos ficarão `incompleto` até o HTML trouxer fim de inscrição parseável ou enriquecimento futuro controlado).
- **Decisão atual do produto:** ver a secção **Decisão de apply** no fim deste documento.

## Decisão de apply

Registo da avaliação em **2026** (subset wave1 FGV após enriquecimento PDF / loader v2):

| Ponto | Estado |
|--------|--------|
| **Crawler FGV v2** | Funcional (`concursos/main_fgv_concursos.py`, fluxo listagem → detalhe → PDF opcional). |
| **PDF enrichment** | Funcionando (extração de texto + merge de datas com `fgv_edital_dates`; sem OCR). |
| **Subset standardized** | **1** item com `validacao_status` = **valido** (`link_edital` + `data_fim_inscricao`); restantes tipicamente `incompleto` (PDF sem texto útil ou datas não parseáveis). |
| **Item válido (datas)** | `data_fim_inscricao` = **2026-04-30**; `data_prova` = **2026-05-14**. |

**Conclusão:** por estar no **limite da recência** em relação ao uso na página pública do módulo (inscrições já encerradas e prova iminente ou passada conforme calendário de produção), **não se recomenda apply em staging neste momento** só para «preencher» o front com este único certame — risco de ruído ou informação desatualizada para o utilizador.

**Manutenção:** manter a FGV como **fonte implementada** no repositório (crawler + PDF enrichment + testes + dry-run) para **novas execuções futuras**, quando o catálogo trouxer mais certames «Em Andamento» com janela de inscrição e prova úteis.
