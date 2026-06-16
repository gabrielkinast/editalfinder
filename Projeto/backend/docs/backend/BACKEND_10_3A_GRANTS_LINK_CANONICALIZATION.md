# BACKEND 10.3A — Grants.gov Link Canonicalization & Link Health Audit

## Bug observado no frontend

Ao clicar em um card Grants.gov (ex.: *"CONSORTIUM FOR NUCLEAR FORENSICS"*, prazo 06/10/2026),
o navegador abre **"PAGE NOT FOUND"** no Grants.gov.

Causa provável: o campo `link` de muitos registros Grants.gov aponta para rotas que
não resolvem mais para a página de detalhe da oportunidade:

- `https://simpler.grants.gov/opportunity/<id>` (rota legada/instável que cai em Page Not Found);
- `https://www.grants.gov/web/grants/view-opportunity.html?oppId=<id>` (rota antiga);
- `.../page-not-found`;
- link vazio / `null` / domínio externo.

## Padrão correto

Página pública de detalhe atual:

```
https://www.grants.gov/search-results-detail/<opportunity_id>
```

onde `<opportunity_id>` é o ID numérico interno da oportunidade.

Quando **não há ID numérico**, mas há **Funding Opportunity Number**, usa-se busca:

```
https://www.grants.gov/search-grants?keywords=<FON encoded>
```

Última opção segura (sem ID e sem número):

```
https://www.grants.gov/search-grants
```

## Módulos criados

### `CORE/grants_link_resolver.py`
- `normalize_grants_gov_link(record)` → `{canonical_link, link_status, reason, opportunity_id, opportunity_number, source_field, old_link, old_link_invalid}`.
  - `link_status`: `canonical_detail | search_fallback | missing | invalid`.
- ID numérico procurado em campos dedicados (`opportunity_id`, `opportunityId`,
  `opportunityIdNumber`, `legacy_opp_id`, `grants_gov_opp_id`, etc., em raiz e em `extras`)
  e, por fim, extraído do próprio link **somente** se o domínio for `grants.gov`.
- `id` só é aceito como ID se for numérico (UUID/strings não numéricas são ignorados).
- Funding Opportunity Number procurado em `opportunity_number`, `opportunityNumber`,
  `funding_opportunity_number`, `fundingOpportunityNumber`, `codigo_oportunidade`,
  `numero_chamada` (raiz e `extras`).
- Garantias de segurança: nunca retorna `page-not-found`, `javascript:`, `data:`,
  URL não-HTTPS, nem domínio fora de `grants.gov`. `is_safe_grants_link()` valida isso.
- `apply_link_resolution_to_item(item, rewrite_link=...)` carimba `extras.grants_link_*`
  e reescreve `item["link"]` conforme política (`if_broken` por padrão).
- `audit_grants_links(records)` e `build_link_fix_candidates(records)`: auditoria e
  dry-run puros (sem rede, sem banco).

### `CORE/grants_link_apply.py`
- `apply_grants_link_candidates(candidates, ...)`: apply controlado por `id_edital`.
- Flags obrigatórias: `EDITALFINDER_ALLOW_CONTROLLED_APPLY=1` e `EDITALFINDER_ALLOW_LINK_FIX=1`.

## Integração (pontos seguros)

- **Recrawl** (`grants_gov/simpler_grants_common.py::build_pipeline_item`): aplica o
  resolver ao final, gerando link canônico para novas coletas.
- **Transformer** (`CORE/transformer.py`): após `_enrich_grants_gov_catalog_extras`,
  chama o resolver (`rewrite_link="if_broken"`) — reescreve apenas links quebrados/legados
  ou converte `simpler.../opportunity/<id>` para o canônico `www.../search-results-detail/<id>`.
- **Loader** (`CORE/loader.py::upsert_routed_item`): guarda `_guard_grants_link_pre_upsert`
  — nunca faz upsert de link `page-not-found`/inseguro; reescreve o link **apenas** quando
  ele está claramente quebrado e há canônico seguro, carimbando `extras.grants_link_status`.

## Riscos com `link` UNIQUE

A tabela `edital` faz upsert com `on_conflict="link"`. Trocar o `link` via upsert criaria
**registro duplicado**. Por isso o apply controlado **atualiza por `id_edital`**
(`UPDATE edital SET link=... WHERE id_edital=...`) e **ignora** candidatos sem `id_edital`.

## Auditoria

```
python scripts/audit_grants_links.py --from-db --limit 1000
```

Saídas em `outputs/grants_link_audit/`: `summary.md`, `audit_stats.json`,
`invalid_links.json`, `canonical_candidates.json`, `search_fallback_candidates.json`,
`already_valid.json`, `missing_identifiers.json`.

Validação estrutural por padrão (sem HTTP). Opcional `--check-http --http-limit 10`
para checar uma amostra pequena (evita rate limit). Não usar em lote por padrão.

## Dry-run de correção

```
python scripts/dry_run_grants_link_fix.py --from-db --limit 1000
```

Saídas em `outputs/grants_link_fix/`: `summary.md`, `candidates_to_update.json`,
`no_change.json`, `invalid_unfixable.json`. Não escreve no banco.

## Apply controlado (PowerShell)

```powershell
$env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
$env:EDITALFINDER_ALLOW_LINK_FIX="1"

python scripts/apply_grants_link_fix.py --input outputs/grants_link_fix/candidates_to_update.json

Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
Remove-Item Env:EDITALFINDER_ALLOW_LINK_FIX
```

Proteções:
- aborta sem as duas flags;
- só fonte Grants.gov (aborta o lote se houver candidato de outra fonte);
- só `new_link` https em `grants.gov`, nunca `page-not-found`;
- update por `id_edital` (sem `id_edital` → ignora, para não duplicar por link);
- lote > 100 exige `--confirm-large`;
- gera `apply_log.json` com `old_link`/`new_link`;
- nunca deleta registros.

## Limitações

- Para registros sem ID numérico, o melhor possível é o fallback de busca por FON
  (`search-grants?keywords=...`) — não é a página de detalhe direta.
- Links com UUID Simpler (sem ID numérico) caem para fallback de busca / `search-grants`.
- A checagem HTTP é opcional e amostral (não valida 100% dos links por padrão).

## Apply automático

Nenhum apply automático ocorre: correções no banco só rodam com as flags explícitas
(`EDITALFINDER_ALLOW_CONTROLLED_APPLY=1` + `EDITALFINDER_ALLOW_LINK_FIX=1`) e revisão
do dry-run.

## Execução no banco real (2026-06-09)

Rodado contra o Supabase de staging (chave `service_role` no backend):

- Auditoria: 278 Grants.gov, 0 já canônicos, 127 rotas legadas (`view-opportunity`),
  151 `simpler/opportunity/<id>`; 278 candidatos, todos `canonical_detail`.
- Apply controlado (`--confirm-large`): **181 OK** + **97 colisões de UNIQUE
  (`edital_link_key`, código 23505)** = duplicatas da mesma oportunidade.
- Re-dry-run pós-apply: **181 já canônicos, 0 candidatos restantes, 97 alvos
  duplicados, 0 não-corrigíveis**.

### Achado: oportunidades duplicadas

As 97 colisões são linhas distintas que apontam para a **mesma** `opportunity_id`
(ex.: uma com link `simpler` e outra com `view-opportunity`). Ao canonicalizar,
ambas resolvem para o mesmo `search-results-detail/<id>`, e o `link` UNIQUE rejeita
a segunda. A versão canônica correta já existe num registro irmão (entre os 181),
referenciado em `duplicate_of_id_edital` no relatório `duplicate_targets.json`.

Tratamento (sem deletar nada):
- O dry-run agora separa esses casos em `duplicate_targets` e nunca os envia ao apply.
- O apply trata colisão de UNIQUE como `skipped`/`duplicate`, não como erro.
- Dedup real (ocultar/mesclar duplicatas) fica para um patch próprio, pois exige
  decisão de produto e **não** pode deletar registros.

Impacto no usuário: os 97 cards duplicados ainda abrem a rota antiga, mas a mesma
oportunidade já é acessível pelo card irmão com link canônico.

## Testes

`tests/test_grants_link_resolver.py` cobre: canonicalização por ID, normalização www,
fallback por FON, rejeição de `javascript:`/domínio externo/UUID não numérico,
auditoria/dry-run e proteções do apply controlado.
