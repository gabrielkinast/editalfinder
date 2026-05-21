# Wave 1 — Crawler piloto Instituto AOCP

## Diagnóstico (estrutura pública)

| Aspeto | Observação |
|--------|-------------|
| **Site institucional** | `https://www.aocp.com.br` — SPA **Next.js**; secção de concursos na página inicial (`/#concursos`). |
| **Página por certame** | `https://www.aocp.com.br/concursos/{id}/` — HTML 200 (id da lista pública). |
| **API JSON oficial** | `https://link.aocp.com.br/api/concursos` — array com todos os certames (campos `id`, `nome`, `chamada`, `status`, `dataInscricao`, …). |
| **Detalhe API** | `https://link.aocp.com.br/api/concursos/{id}` — array com um objeto: datas `dataInicioInscricao` / `dataFinalInscricao`, `publicacoes[]` com `nome` + `url` (PDF em `arquivos-site.aocp.com.br`). |
| **Listagem “abertos”** | Não há endpoint separado identificado no piloto; a lista completa traz sobretudo `FINISHED` e raros `IN_PROGRESS`. O crawler filtra por `--include-only-status` (default `IN_PROGRESS`). |
| **robots.txt** | Ficheiros observados: comentários Cloudflare («content signals») **sem** blocos `User-agent:`. O `RobotFileParser` puro interpretaria isso como bloqueio total; o crawler trata como **ausência de regras legíveis** e mantém `--sleep` + poucos GET. |

## Script e comandos

| Item | Caminho |
|------|---------|
| Crawler | `concursos/main_aocp_concursos.py` |
| Standardized | `audit_reports_main_pipeline/concursos_wave1_aocp/standardized/aocp_standardized.json` |
| Resumo | `crawler_summary.json` / `.md` |
| Testes | `tests/test_aocp_crawler.py` |

```powershell
cd "d:\Computational_Physics\My Projects\edital"
python concursos/main_aocp_concursos.py --max-items 10 --sleep 1.5
python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_aocp/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_aocp/loader_dryrun --sources aocp
python -m pytest tests/test_aocp_crawler.py -q
```

Opções: `--include-only-status IN_PROGRESS` (default), `--output-root`, `--max-items`, `--sleep`.

## Regras implementadas

- Só dados de **link.aocp.com.br** (API) + link canónico **www.aocp.com.br/concursos/{id}**.
- **Descarte** por texto de não-oportunidade (resultado final, homologação de resultado, etc.) em `nome`/`chamada`.
- **Recência:** `recency_should_discard` com datas da API (não prolongar certames encerrados).
- **`validacao_status`:** `valido` apenas com `link_edital` + `data_fim_inscricao`; `link_edital` escolhido entre `publicacoes` (prioridade a “Edital de Abertura” / “Edital nº …”).
- **`banca`:** `Instituto AOCP`; `fonte=aocp`, `fonte_tipo=banca`, `categoria=banca_aocp_concurso`.

## Limitações

1. A lista pública pode ter **zero** certames `IN_PROGRESS` com oportunidade real; o único `IN_PROGRESS` observado em 2026 era legado (chamada de resultado final) → **descartado**.
2. **PDF de edital:** depende do texto em `publicacoes[].nome`; sem correspondência → `link_edital` nulo e `validacao_status` incompleto.
3. **Vagas / salário / taxa:** só quando existirem em campos ou texto parseável; não inventar.
4. **SPA:** não se extrai conteúdo renderizado no cliente além do que a API expõe.

## Última corrida de referência (ambiente local, 2026-05-14)

| Métrica | Valor |
|---------|--------:|
| Registos na lista API (`/api/concursos`) | **230** |
| Itens `IN_PROGRESS` após filtro de status | **1** (SUSIPE, id 342) |
| Descartados (pré-detalhe) | **1** (`aocp_nao_oportunidade_ativa` — chamada com «Divulgado o Edital de Resultado Final») |
| GET ao detalhe `/api/concursos/{id}` | **0** (evita chamadas desnecessárias após descarte) |
| **Standardized** | **0** (`aocp_standardized.json` = `[]`) |
| Loader dry-run | `errors_count` **0**, `would_upsert_total` **0** |

Quando o AOCP publicar novos `IN_PROGRESS` com inscrições futuras e chamada de abertura, o mesmo crawler deve passar a emitir linhas `valido` sem alteração de schema.

## Recomendação de apply em staging

- Com **0** linhas: apply não acrescenta dados; manter o crawler no repositório para corridas futuras.
- Com **N > 0**: dry-run sem erros → revisão manual de PDF e datas → apply staging conforme política interna.

## Relação com o módulo

- **Tabela alvo:** `public.concurso_selecao` (fora do âmbito até `--apply-staging`).
- **PCI:** fonte `aocp` / banca para deduplicação global.
