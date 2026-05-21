# Consolidado — Fundatec wave1 (v4 artigo principal, pré-apply)

**JSON:** `consolidado_final.json`  
**Loader dry-run v4:** `loader_dryrun_v4/load_concursos_selecao_summary.json`  
**Último crawl (UTC):** ver `crawler_summary.json` → `collected_at_utc`

## Totais (última corrida de referência)

| Métrica | Valor |
|--------|--------|
| URLs brutas | 10 |
| Standardized | 7 |
| Descartados | 3 (`noticia_nao_oportunidade_ativa`) |
| Loader `errors_count` | **0** |
| `would_upsert_total` | **7** |

## O que o v4 acrescenta

### Escopo HTML (`extract_fundatec_article_text`)

- Texto e extração monetária / vagas / datas só a partir do **corpo principal** (`.entry-content` / `.post-content` dentro de `article`, com fallbacks).
- Remoção de **sidebar**, **widgets**, **posts relacionados**, **comentários**, **nav/footer**, **scripts/styles**.
- **`link_edital`**: apenas links `portal/concursos` ou `index_concursos.php` encontrados **dentro** desse fragmento; caso contrário `null`, `official_link_missing = true`.

### Descarte de notícia passada / não oportunidade

- Padrões no título+corpo (ex.: prova realizada, candidatos participam, resultado, gabarito, homologação, convocação, retificação sem link, combinação domingo + prova realizada).
- Entradas em `discarded` com `motivo: noticia_nao_oportunidade_ativa`.
- Mantém o item se existir **`data_fim_inscricao` futura** (inscrições ainda relevantes).

### Baixa confiança sem portal nem fim de inscrições

- Sem `link_edital` **e** sem `data_fim_inscricao`: **não** preenche `numero_vagas`, `salario_min`, `salario_max`, `taxa_inscricao` (nota `valores_suprimidos_sem_link_oficial_nem_data_fim`).
- **`qualidade_dado = baixa`** quando faltam link e data fim; com link mas sem data fim continua **`media`**.

### Regras v3 mantidas (common + parsing)

- Remuneração / taxa na faixa ambígua, vagas por parágrafo de certame com cruzamento ao título, ajuste de confiança por notas — aplicados **só** sobre o texto principal.

## Recomendação

Apply **só** após revisão humana; subset `validacao_status=valido` após abrir `link_edital`. **Apply não executado** nesta entrega.

## Reprodução

```bash
python -m pytest tests/test_concursos_common.py tests/test_fundatec_crawler.py -q
python concursos/main_fundatec_concursos.py --max-items 10 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_fundatec/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fundatec/loader_dryrun_v4 --sources fundatec
```

## Comando apply staging (referência — não executar)

Ver `consolidado_final.json` → `comando_apply_staging`.
