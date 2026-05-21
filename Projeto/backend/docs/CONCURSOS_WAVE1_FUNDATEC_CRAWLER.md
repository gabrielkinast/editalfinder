# Wave 1 — Crawler piloto Fundatec

## Diagnóstico (estrutura pública)

| Aspeto | Observação |
|--------|------------|
| **Site** | `https://www2.fundatec.org.br` (WordPress). |
| **Listagem** | `https://www2.fundatec.org.br/category/concursos/` — URLs `/{ano}/{mês}/{dia}/{slug}/`. |
| **Detalhe** | Artigo com texto editorial; `link_edital` quando existe `a[href]` para `portal/concursos` ou `index_concursos.php` **no corpo principal do post** (não na sidebar). |
| **`robots.txt`** | Pode vir vazio; `RobotFileParser` + User-Agent de browser + `--sleep`. |

## Última corrida de referência (v4 — artigo principal)

| Métrica | Valor |
|---------|--------|
| **URLs brutas** | **10** |
| **Standardized** | **7** |
| **Descartados** | **3** (`noticia_nao_oportunidade_ativa`: participação em massa, domingo/prova realizada, etc.) |
| **Loader dry-run v4** | `errors_count = 0`, `would_upsert_total = 7` |
| **Ficheiros** | `standardized/fundatec_standardized.json`, `crawler_summary.json`, `loader_dryrun_v4/` |

## Regras implementadas (`concursos/common.py` + `main_fundatec_concursos.py`)

### v4 — escopo HTML e qualidade

- **`extract_fundatec_article_text(soup)`**: resolve `article` → `.entry-content` / `.post-content` (ou `div.entry-content`, `main`); clona e remove `aside`, `nav`, `footer`, `.sidebar`, `#secondary`, `.widget*`, comentários, blocos relacionados (classes típicas WP), `script`/`style`.
- **Parsing**: `parse_vagas_certame`, `parse_remuneracao_taxa_br`, `parse_all_dates_br`, `extract_data_fim_inscricao_fundatec`, `extract_data_prova_fundatec` usam **somente** o texto do corpo principal (`article_text_main_only`), não `soup.get_text()` da página inteira.
- **`link_edital`**: `_pick_portal_concurso_link_from_node` no fragmento limpo; se ausente → `null`, `official_link_missing: true`.
- **Descarte**: `fundatec_should_discard_non_opportunity` — prova realizada, participação em massa, resultado, gabarito, homologação, convocação, retificação sem link, combinação “domingo, N” + texto de prova realizada; título com resultado/gabarito/homologação/convocação sem link. **Exceção:** `data_fim_inscricao` ≥ hoje. Motivo em `discarded`: `noticia_nao_oportunidade_ativa`.
- **Baixa confiança**: sem `link_edital` e sem `data_fim_inscricao` → **não** preencher `numero_vagas`, `salario_min`, `salario_max`, `taxa_inscricao` (`valores_suprimidos_sem_link_oficial_nem_data_fim`).
- **`validacao_status`**: `valido` apenas com **ambos** `link_edital` e `data_fim_inscricao`; `incompleto` nos demais casos gravados.
- **`qualidade_dado`**: `baixa` se faltam link e data fim; `media` se há link mas falta data fim (sobrepõe parcialmente à inferência PCI).

### v3 (mantido no common / uso Fundatec)

- **Salário:** `R$ X,Y mil` → `salario_max`; evita fragmentos «até R$ 9» antes de «,5 mil».
- **Taxa vs salário:** faixa **R$ 40–250** com léxico de taxa → só `taxa_inscricao`; «full» sem léxico de taxa → ambíguo (fora de salário, notas).
- **Vagas:** `parse_vagas_certame` com `paragraph_scope=True` e `title_for_crosscheck` sobre o texto principal.
- **Confiança:** `pci_adjust_confidence_for_ambiguity` quando há notas de valor/vagas ambíguas.
- **Órgão / local:** `strip_orgao_title_noise` + inferência a partir do título.
- **`tipo_selecao`:** `infer_tipo_selecao_meta` (estágio só pelo título).

## Script e comandos

| Item | Caminho / comando |
|------|-------------------|
| Crawler | `concursos/main_fundatec_concursos.py` |
| Testes | `tests/test_concursos_common.py`, `tests/test_fundatec_crawler.py` |

```bash
python concursos/main_fundatec_concursos.py --max-items 10 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_fundatec/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fundatec/loader_dryrun_v4 --sources fundatec
python -m pytest tests/test_concursos_common.py tests/test_fundatec_crawler.py -q
```

## Limitações conhecidas

1. Listagem: primeira página da categoria (~10 URLs).
2. **`data_fim_inscricao`:** muitos `null` se o post não trouxer frase explícita capturável.
3. **`link_edital`:** ausente quando o artigo principal não inclui link para o portal (sidebar não conta).
4. **HTML atípico:** se o tema colocar conteúdo essencial fora de `.entry-content`, pode faltar texto; notas de extração ajudam a auditar.
5. **`tipo_selecao`:** depende do título para estágio.

## Consolidação

Ver `audit_reports_main_pipeline/concursos_wave1_fundatec/consolidado_final.md` e `consolidado_final.json`.

## Relação com o módulo

- **Tabela alvo da carga:** `public.concurso_selecao` (fora do âmbito deste crawler).
- **Contraste PCI:** Fundatec = notícia + portal; `fonte_tipo = banca`.
