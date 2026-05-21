# Wave 1 — Crawler piloto Quadrix

## Diagnóstico (estrutura pública)

| Aspeto | Observação |
|--------|------------|
| **Site** | `https://www.quadrix.org.br` — HTML (charset frequentemente ISO-8859-1 / Latin-1). |
| **Listagens (piloto)** | `/index/abertos/` (inscrições abertas), `/index/1/` (em andamento). O menu também referencia `/index/3/` (encerrados), `/index/4/` (suspenso), `/index/6/` (em breve); o piloto **não** inclui encerrados por defeito. |
| **Detalhe** | `/informacoes/{id}/` — `p.insc` (intervalo de inscrição com hora), `p.situacaoConcurso`, `#blocoPublicacoes` (PDFs no CDN `anexos.cdn.selecao.net.br` → `link_edital`), `#blocoEventos` (cronograma; prova objetiva), `#blocoListaVagas` (primeira linha: cargo, vagas, escolaridade, taxa). |
| **API / SPA** | Não há API JSON pública dedicada ao catálogo no piloto; conteúdo é **HTML** renderizado no servidor. |
| **`robots.txt`** | Em geral `Allow: /`; `Disallow: /admin/*`, `/painel/*`, `/uploads/*`. O crawler **não** segue links para `/painel/` e prefixos excluídos. |

### Host oficial vs. domínios incorretos

- **Base correta do crawler:** `https://www.quadrix.org.br` (e rotas `/index/…`, `/informacoes/{id}/`).
- **`quadrix.com.br`** (sem `www`, ou domínio `.com.br` em sondas externas): em testes de conectividade devolveu **HTTP 522** (origem indisponível); **não** usar como base do crawler nem confundir com o site oficial do piloto.

## Última corrida de referência (ambiente local)

Os números variam com o catálogo ao vivo da Quadrix. Após `python concursos/main_quadrix_concursos.py --max-items 40 --sleep 1.2`:

| Métrica | Valor típico (snapshot) |
|---------|-------------------------|
| **URLs brutas (dedupe)** | Depende das listagens; com as duas listagens por defeito costuma coincidir com o número de certames listados (ex.: **10**). |
| **Standardized** | Igual ao número de páginas de detalhe processadas com sucesso. |
| **Descartados** | Certames fora de janela de recência, situação encerrada, ou heurísticas de não-oportunidade (resultado/gabarito/convocação sem contexto de inscrição ativa). |
| **Loader dry-run** | `errors_count = 0` quando o JSON está alinhado com o schema esperado pelo loader. |

Consulte sempre `audit_reports_main_pipeline/concursos_wave1_quadrix/crawler_summary.json` e `loader_dryrun/load_concursos_selecao_summary.json` após cada execução.

## Regras implementadas (`concursos/main_quadrix_concursos.py`)

- **Fonte:** `fonte=quadrix`, `fonte_tipo=banca`, `banca=Quadrix`, `categoria=banca_quadrix_concurso`.
- **`validacao_status`:** `valido` apenas com **ambos** `link_edital` e `data_fim_inscricao`; caso contrário `incompleto`.
- **Sem invenção:** não preencher `numero_vagas`, salários ou datas sem evidência na página oficial; salários ambíguos (valores típicos de taxa) ficam fora de `salario_*` (notas em `extras`).
- **`nivel_escolaridade`:** prioriza a coluna «Escolaridade» da primeira linha de `#blocoListaVagas`; em falta, usa `infer_nivel_escolaridade` sobre título/corpo.
- **Descarte:** situação/recência e títulos alinhados a resultado/gabarito/convocação sem oportunidade ativa; não incluir listagem de encerrados no piloto por defeito.
- **Conservador:** `--max-items` e `--sleep` configuráveis; respeito a `robots.txt` via `RobotFileParser`.

## Script e comandos

| Item | Caminho / comando |
|------|-------------------|
| Crawler | `concursos/main_quadrix_concursos.py` |
| Testes | `tests/test_quadrix_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_quadrix_concursos.py --max-items 40 --sleep 1.2
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_quadrix/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_quadrix/loader_dryrun --sources quadrix
python -m pytest tests/test_quadrix_crawler.py -q
```

Opções úteis: `--listings URL1 URL2` (substituir listagens), `--output-root` (raiz do relatório).

## Limitações conhecidas

1. **Cobertura:** apenas URLs encontradas nas listagens configuradas; o catálogo completo pode exceder o cap `--max-items`.
2. **`estado` / `municipio`:** em muitos certames a Quadrix não expõe UF/cidade de forma estruturada na página de informações; podem ficar `null` (refletido em `extras.missing_core_fields`).
3. **`salario_min` / `salario_max`:** ausentes quando a tabela de vagas não traz remuneração clara ou o valor é ambíguo com taxa.
4. **`data_prova`:** derivada do cronograma «Prova objetiva» quando existir; outros eventos não são mapeados como prova única.
5. **Charset:** páginas em ISO-8859-1 são normalizadas para UTF-8 na leitura; HTML inválido pode falhar parse pontual (entrada em `errors` do summary).

## Relatórios

- `audit_reports_main_pipeline/concursos_wave1_quadrix/standardized/quadrix_standardized.json`
- `audit_reports_main_pipeline/concursos_wave1_quadrix/crawler_summary.json` e `crawler_summary.md`
- Dry-run: `audit_reports_main_pipeline/concursos_wave1_quadrix/loader_dryrun/`
- Consolidado pré-apply: `audit_reports_main_pipeline/concursos_wave1_quadrix/consolidado_final.json` e `consolidado_final.md` (totais, classificações, comando de apply de referência)

## Recomendação de apply em staging

Quando o produto quiser carregar na base de **staging**:

1. Regenerar o JSON com listagens e `--sleep` conservadores.
2. Confirmar `crawler_summary.json` → `errors` vazio e taxa de `validacao_status` aceitável.
3. Executar `load_concursos_selecao.py` com **dry-run** e `errors_count = 0`.
4. Só então aplicar com os flags de ambiente já usados no projeto para **staging** (nunca misturar com produção sem revisão). Este documento **não** substitui a política interna de `ALLOW_STAGING_APPLY` / variáveis Supabase.

## Relação com o módulo

- **Tabela alvo da carga:** `public.concurso_selecao` (fora do âmbito deste crawler até apply explícito).
- **PCI:** Quadrix é fonte **banca** direta; o agregador PCI pode continuar a deduplicar por `link` / metadados conforme regras globais do módulo.
