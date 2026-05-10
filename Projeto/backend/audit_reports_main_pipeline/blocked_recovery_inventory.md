# Inventário: fontes bloqueadas / revisão e sinais de recuperação

**Auditoria:** 2026-05-10 (artefactos locais apenas; sem Supabase, sem apply, sem mudanças de readiness ou código)

## Fontes bloqueadas (`config/source_readiness.json` → `blocked`)

`bid_lab`, `caf`, `china_cnnc`, `dcta_ita_iae`, `esa_star`, `japan_e_rad`, `japan_jaxa`, `marinha`, `sam_gov`, `science_scraper`.

## Fontes em revisão manual (`needs_manual_review`)

`china_avic`, `china_norinco`, `eurostars`, `fonplata`, `innovate_uk`, `japan_jaea`, `japan_jst`, `japan_kawasaki_heavy`.

## Cruzamento com `readiness_for_loader.json`

O JSON derivado lista **`fontes_bloqueadas_temporariamente`** incluindo as acima **e** outras (`badesul`, `petrobras`, `pncp`, `plataforma_industria`, `senai`, `softex`, …). O ficheiro `audit_reports_loader_ready/load_ready_summary.json` documenta **overlay curado** (`readiness_curated_overlay`) que promoveu várias fontes — **esta auditoria não propõe alterar** esse estado; apenas regista que a “verdade operacional” do último load pode diferir do `source_readiness.json` em disco.

## `suspeito_ativo_true` por fonte (staging)

Fonte: `audit_reports_main_pipeline/post_daily_warning_examples.json` (agregado `edital.suspeito_ativo_true`).

| Fonte (rótulo) | Contagem |
|----------------|------------|
| BASA | 22 |
| AMAZUL | 14 |
| BADESUL | 7 |
| Ambev | 7 |
| General Dynamics Suppliers | 6 |
| Apex Brasil | 4 |
| Petrobras | 4 |
| Lockheed Martin Suppliers | 3 |
| BAE Systems Suppliers | 2 |
| EIT | 2 |
| Rheinmetall Suppliers | 2 |
| SENAI | 2 |
| Softex | 2 |
| ESA OSIP | 1 |
| Thales Suppliers | 1 |
| UKRI Funding | 1 |

## Rejeições recentes no transform (amostra documentada)

| Lote / ficheiro | Fonte | Brutos | Transformados | Rejeitados | Motivo dominante |
|-----------------|-------|--------|---------------|------------|-------------------|
| `lote_inovacao_internacional_onda_c_fix/retransform_by_source.json` | esa_star | 1 | 0 | 1 | Login/autenticação |
| Idem | esa_osip | 18 | 17 | 1 | Login/autenticação |
| `lote_credito_multilateral_onda_b_fix/retransform_by_source.json` | eureka_network | 23 | 21 | 2 | Login/autenticação |
| Idem | fonplata | 7 | 5 | 2 | Relevância limite |

## Crawler encontrou algo mas standardized = 0 (caso emblemático)

- **`esa_star`:** `raw_count=1`, `standardized_count=0`; bruto aponta para `https://esastar-publication-ext.sso.esa.int` (SSO). Diagnóstico em `audit_reports_credito/lote_inovacao_internacional_onda_c_diagnostico.json` confirma recomendação `blocked` por rejeição no transformer.

## Warnings globais de referência (staging)

Mesmo ficheiro `post_daily_warning_examples.json`: `prazo_vencido_ativo_true` 41, `titulo_ruidoso` 6, `credito_tipo_recurso_incoerente` 4, `setor_estrategico_muito_amplo` 72, `suspeito_ativo_true` 80.

## Erros de carga em `audit_reports_loader_ready/staging_load_errors.json`

Na leitura atual o array está **vazio** (nenhuma linha de erro persistida nesse snapshot).

## `latest_error.json` em crawlers

Existem cópias em `senai/`, `japan_mitsubishi_heavy/`, `horizon_europe/`, `japan_kawasaki_heavy/`, `china_norinco/`, `china_cnnc/`, `japan_jaea/` — úteis para classificar **coleta vazia** / URLs falhadas sem assumir bloqueio permanente.

## Mapa das cinco vias (objetivo do programa)

1. **Manter bloqueado:** login isolado, WAF sem alternativa, FAQ/careers/about como “edital”.
2. **Crawler/parser:** filtros de URL, deteção de hub vs topic, PDF/HTML enrichment.
3. **Curadoria manual:** linhas de crédito reais vs páginas bancárias genéricas; fornecedores internacionais.
4. **Soft-continue local:** confirmar lista vazia vs filtro agressivo (`coleta_vazia_sem_confirmacao`).
5. **Fonte alternativa:** RSS/API/sitemap oficial (UKRI, SBIR topics, ESA Open ITT público).

Ficheiro estruturado: **`blocked_recovery_inventory.json`**.
