# Diagnóstico IARPA (lote 2)

Data: 2026-05-01

## Resumo executivo

O pipeline retransform marcava o IARPA como excluído pelo `opportunity_gate` porque o JSON bruto tinha **um único registo** apontando para o **hub** `https://www.iarpa.gov/research-programs`, típico de **fallback** após falha do caminho Grants.gov (parse de campos errados) e ausência de itens úteis no scrape.

## Respostas (checklist)

1. **O crawler roda?** Sim (`python iarpa/main_iarpa.py` conclui sem erro).
2. **Existe output bruto?** Sim: `iarpa/outputs/iarpa_editais.json` (e CSV quando há linhas).
3. **Quantos itens brutos?** Após correção: **8** (todos Grants.gov filtrados; hub e página institucional «Proposers' Days» excluídos).
4. **Hubs ou oportunidades reais?** Oportunidades reais no catálogo Grants.gov (`oppId`, número, datas, agency); não há gravação do hub como item final.
5. **`/research-programs` como fallback?** **Sim no código antigo** (`_fallback_items`). **Removido** na versão corrigida; a URL serve só como **listagem** para descobrir links em `iarpa.gov`.
6. **Links de detalhe dentro de `/research-programs`?** O HTML expõe várias âncoras; o scrape filtra caminhos de detalhe. O volume estável veio da **API Grants.gov** com `oppStatuses` incluindo `archived`.
7. **Opportunities / solicitations / BAA / funding?** Sim via Grants.gov (synopsis, FOAs ligados a IARPA/IC); páginas iarpa.gov complementam contexto (BAA, proposers day) sem substituir o registo de oportunidade.
8. **Sitemap / RSS?** Não integrados; abordagem conservadora (API + listagem oficial).
9. **Documentos / anexos?** `docType` e texto descritivo no item; ligações PDF podem surgir na página Grants ou referências SAM quando existirem no HTML detalhado.
10. **Por que o gate rejeitou?** Item único era **página índice** sem código de chamada nem corpo de oportunidade → **oportunidade não evidenciada** / score insuficiente.

## Causa raiz

| Problema | Efeito |
|----------|--------|
| Campos JSON da API (`title`, `id`, …) não lidos | `_fetch_iarpa_via_grants_api` devolvia lista vazia |
| Fallback para `/research-programs` | Um «edital» falso; gate correto a rejeitar |

## Alterações feitas (âmbito local)

- `iarpa/main_iarpa.py`: coleta **Grants.gov search2** com parse correcto, filtros, merge opcional com scrape da listagem; **sem** fallback hub; exclusão de páginas institucionais genéricas (`proposers-days` landing).
- `CORE/taxonomy_filtros.py`: `calibrate_iarpa_extras` (inclui itens Grants sem a palavra «IARPA» no texto quando `programa == IARPA`; setor `inteligencia` / `pesquisa_avancada`; ciber só com marcadores fortes).
- `CORE/transformer.py`: chamada à calibração para `source == iarpa`.
- `CORE/official_link_only.py`: rejeição explícita do hub `iarpa.gov/.../research-programs`.
- `scripts/audit_semantic_classification.py`: isenção `fonte_defesa_sem_defesa` para IARPA com marcadores IC/grants/BAA.
- `scripts/audit_official_link_only.py`: argumento opcional `--extra-dirs` para incluir pastas de standardized de testes (ex. `retransform_official_link_only_test_iarpa/standardized`).

## Resultados do pipeline (corridos localmente)

| Etapa | Pasta / ficheiro | Destaque |
|--------|------------------|----------|
| retransform | `lote2_fix_iarpa/retransform_summary.json` | 8 brutos, 8 transformados, 0 rejeitados |
| semântica | `lote2_fix_iarpa_semantic/audit_semantic_summary.json` | 8 itens, 0 flags |
| docs | `lote2_fix_iarpa_docs/audit_docs_summary.json` | 8 itens; sem `documentos`/`pdf_url` no bruto (Grants synopsis) |
| official_link_only | `audit_reports_access/official_link_only_summary.json` (com `--extra-dirs` no teste IARPA) | 0 `official_link_only` (sem barreira técnica nem modo OLO nos JSON analisados) |

## Readiness (recomendação manual — **não** atualizada automaticamente)

**`ready_with_notes`**

- Há transformados > 0 e ligações concretas (Grants `oppId`).
- Texto da agência pode ser «Dept of the Army — Materiel Command» em programas históricos IARPA: nota para **revisão humana** de alinhamento orgânico.
- Itens maioritariamente **archived** no Grants: útil para arquivo/rastreabilidade, não para «aberto agora» sem nova consulta.
- `official_link_only`: usar só com barreira técnica; com dados Grants completos tende a **não** aplicar.

Ficheiros de evidência: `lote2_iarpa_diagnostico.json`, `lote2_iarpa_examples.json`, pastas `audit_reports_blocked_sources/lote2_fix_iarpa*` após correr o pipeline.
