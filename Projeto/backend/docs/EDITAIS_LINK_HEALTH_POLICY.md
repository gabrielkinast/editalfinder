# Política de saúde de links (aba Editais)

## Por que links quebrados não são apagados automaticamente

- O edital pode continuar válido como **oportunidade catalogada** mesmo quando o portal oficial mudou URL, removeu a página ou exige sessão.
- Apagar linhas destruiria histórico, favoritos e rastreio de coleta.
- A correção correta é **atualizar URL** (re-crawl, oppId Grants.gov, `url_detalhe`) ou marcar metadados em `extras.link_health`, não remover o registro.

## Status HTTP vs erro semântico do site

| Camada | O que mede | Exemplo Grants.gov |
|--------|------------|-------------------|
| **HTTP** | Código da resposta (`200`, `404`, …) | `GET view-opportunity?oppId=362132` → **200** |
| **Semântico (SPA)** | Conteúdo/URL final após redirects e HTML | Redirect para `/page-not-found` ou texto **PAGE NOT FOUND** |

Muitos portais modernos (SPAs) devolvem **HTTP 200** com shell HTML e depois renderizam “Page Not Found” no cliente. A auditoria usa `CORE/link_health.py` com **GET + leitura do corpo** e checagem de `final_url` para classificar `broken_spa_not_found` mesmo quando o status HTTP é 200.

## Classificação (`link_status`)

| Status | Significado |
|--------|-------------|
| `ok` | HTTP 200 e página não indica erro semântico |
| `redirect_ok` | Redirecionamento 3xx com destino utilizável |
| `broken_404` | HTTP 404 / 410 ou corpo HTML genérico de não encontrado |
| `broken_spa_not_found` | HTTP 200 (ou redirect) mas landing **Page Not Found** (SPA) |
| `forbidden_403` | 403 (geo/WAF; revisão manual) |
| `timeout` | Timeout ou falha de conexão |
| `ssl_error` | Erro de certificado TLS |
| `invalid_url` | Esquema/host inválido |
| `suspicious` | Home/busca genérica ou Grants.gov sem `oppId` |
| `missing` | Campo vazio |

## Grants.gov legado vs Simpler.Grants.gov (canônico)

**Nota:** O portal legado `https://www.grants.gov/web/grants/view-opportunity.html?oppId=…` foi substituído por **Simpler.Grants.gov** como rota canônica pública. Links `view-opportunity` são tratados como legados e sujeitos a `broken_spa_not_found` mesmo com HTTP 200.

| Rota | Papel |
|------|--------|
| `https://simpler.grants.gov/opportunity/{legacy_id\|uuid}` | **Link principal** (crawler `grants_gov/main_simpler_grants_gov.py`) |
| `view-opportunity.html?oppId=` | Legado — SPA vazia / Page Not Found |
| `https://www.grants.gov/search-results-detail/{oppId}` | Legado intermédio (não usar como canônico) |

### Legado `view-opportunity.html`

- HTTP 200 frequentemente **não** significa página válida.
- Auditoria: `broken_spa_not_found`; se existir `legacy_opp_id`, `recommendation: corrigir_url` → `https://simpler.grants.gov/opportunity/{oppId}`.
- `extras.source_variant`: `simpler_grants_gov`; `extras.legacy_url` guarda a URL antiga.

Heurísticas (`detect_grants_gov_legacy_view_opportunity`):

1. Payload Nuxt da rota legada vazio; `search-results-detail/{oppId}` ou API `fetchOpportunity` ainda podem responder.
2. Redirect/HTML para `/page-not-found`.

### Simpler.Grants.gov

- `detect_simpler_grants_opportunity_page`: HTTP 200 + marcadores de detalhe (posted/closing date, opportunity number) → `ok`.
- Listagem `/search?page=1` é SPA (sem resultados SSR); coleta via API (`POST api.simpler.grants.gov/v1/opportunities/search`, chave `SIMPLER_GRANTS_API_KEY`) ou fallback `api.grants.gov/search2` com links Simpler.

**Migração em massa (sem apply automático):**

```bash
python scripts/audit_grants_legacy_to_simpler.py --from-json CORE/transformer/grants_gov_standardized.json
python scripts/grants_simpler_dryrun.py
```

## Recomendações (auditoria)

- `manter` — link OK
- `corrigir_url` — reprocessar fonte ou ajustar campo
- `marcar_link_quebrado` — gravar em `extras.link_health` (SQL manual)
- `review_manual` — 403, missing, ambíguo
- `ocultar_botao_pdf` — só PDF ruim; manter card
- `ocultar_card_do_front` — **somente** se todos os links essenciais falharem (consenso manual)

## Como auditar uma fonte

```bash
# Supabase (produção / staging)
python scripts/audit_edital_links.py --source grants --from-db --limit 100 --sleep 0.5 \
  --output-dir audit_reports_main_pipeline/link_health_grants_db_v2

# Artefato local
python scripts/audit_edital_links.py --source grants --limit 100 --sleep 0.5
```

Saídas:

- `summary.json` / `summary.md`
- `checked_links.json`
- `broken_links.json` — inclui `broken_spa_not_found`
- `review_candidates.json`

SQL comentado: `docs/sql/FIX_GRANTS_BROKEN_LINKS.sql` (somente itens broken; inclui `atualizado_em = now()` quando aplicável).

## Frontend (aba Editais)

- `src/utils/edital/linkHealth.js`
- Trata como indisponível: `broken_404`, `broken_spa_not_found`, `timeout`, `invalid_url`
- Badge **Link indisponível**; botões Site/Inscrição/PDF desabilitados por campo
- Card visível se outro link essencial estiver OK
- Sem `extras.link_health`: comportamento legado

## Fonte Grants.gov (pipeline)

| Etapa | Campo de link |
|-------|----------------|
| Crawler | `link` = `view-opportunity.html?oppId={opportunityId}` |
| Extras | `url_detalhe`, `origem`, `opportunity_id` |
| Transformer | `_enrich_grants_gov_catalog_extras` + `stamp_structural_link_health` |

Após auditoria com broken: re-crawl → SQL manual em `extras.link_health` → frontend passa a exibir aviso.

**Não** usar apply automático no banco a partir do script de auditoria.
