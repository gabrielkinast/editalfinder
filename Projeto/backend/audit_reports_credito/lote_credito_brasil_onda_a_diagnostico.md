# Lote Crédito / Desenvolvimento — Onda A Brasil

**Data:** 2026-05-05 (UTC)  
**Fontes:** `bnb`, `banco_da_amazonia`, `desenvolve_sp`, `bdmg`, `agerio`

## Escopo e separação de destinos

| Destino | Critério |
|--------|-----------|
| **public.edital** | Linhas acionáveis, chamadas com inscrição/solicitação, financiamento com canal explícito, programas com cadastro. |
| **public.noticia** | Anúncios, resultados de programa, imprensa institucional sem canal de solicitação imediato. |
| **public.pesquisa** | Relatórios, FAQs longas, páginas só explicativas; páginas institucionais sem ação. |

**Regras de classificação (taxonomia):** não classificar fomento/subvenção se for apenas empréstimo reembolsável; não usar “edital” para página só institucional; não rotular como notícia uma página de produto de crédito com solicitação.

### Tipos de oportunidade (uso esperado)

`credito`, `financiamento`, `programa_credito`, `programa_inovacao`, `chamada_publica`, `edital`, `selecao_propostas`, `desenvolvimento_regional`, `apoio_empresarial`.

### Tipos de recurso

`reembolsavel`, `nao_reembolsavel`, `subvensao`, `credito`, `financiamento`, `apoio_tecnico`, `apoio_inovacao`.

### Perfis e setores

Conforme especificação do lote (empresa, ME/EPP, startup, rural, cooperativa, município, ICT etc.; setores inovação, agro, energia, sustentabilidade, desenvolvimento regional, …).

---

## Diagnóstico por fonte

### Banco do Nordeste (`bnb`)

| Item | Status |
|------|--------|
| Crawler | `bnb/main_bnb.py` → `bnb/outputs/bnb_editais.json` |
| Coleta | HTML leve via `scrape_source`, listagens de produtos/solicitação/microcrédito |
| URLs úteis | `…/produtos-e-servicos`, `…/solicitacao-de-credito`, `…/microcredito` |
| Excluir | `/imprensa/`, notícias, Open Finance, páginas só educação financeira |
| Readiness | **ready_with_notes** — boa cobertura; revisar itens “suspeitos” (texto curto) |

### Banco da Amazônia (`banco_da_amazonia`)

| Item | Status |
|------|--------|
| Crawler | `banco_da_amazonia/main_banco_da_amazonia.py` |
| Coleta | Listagens empresas/rural/FNO |
| URLs úteis | Crédito empresas, agro, linhas FNO/PRONAF/FINAME |
| Excluir | Cartão PF genérico, seguros, investimento sem vínculo com crédito |
| Readiness | **ready_with_notes** — muitas linhas; parte dos itens incompletos/suspeitos |

### Desenvolve SP (`desenvolve_sp`)

| Item | Status |
|------|--------|
| Crawler | `desenvolve_sp/main_desenvolve_sp.py` (seeds curados) |
| Coleta | **HTTP 403** para requests automatizados (WAF). Sem bypass: 4 URLs oficiais de crédito/solicitação. |
| URLs úteis | Opções de crédito, como solicitar, máquinas/equipamentos, negócios online |
| Readiness | **needs_manual_review** — seeds válidos; falta enriquecimento de texto sem fetch |

### BDMG (`bdmg`)

| Item | Status |
|------|--------|
| Crawler | `bdmg/main_bdmg.py` |
| Coleta | Home + linhas permanentes + micro/pequenas empresas |
| URLs úteis | `linhaspermanentes`, segmentos por porte |
| Excluir | Relação com investidores, PDF de termos genéricos |
| Readiness | **ready_with_notes** — volume alto; possível ruído em âncoras `#` |

### AgeRio (`agerio`)

| Item | Status |
|------|--------|
| Crawler | `agerio/main_agerio.py` |
| Coleta | Linhas de crédito + áreas de atuação; exclusão de notícias/orienta |
| URLs úteis | `linhas-de-credito/`, áreas empresas |
| Excluir | `/noticias/`, dicas em `/agerio-orienta/`, `/sem-categoria/` |
| Readiness | **needs_manual_review** — poucos itens; 1 rejeição por página genérica (microempreendedor) |

---

## Calibração local

Em `CORE/taxonomy_filtros.py`: `calibrate_bnb_extras`, `calibrate_banco_da_amazonia_extras`, `calibrate_desenvolve_sp_extras`, `calibrate_bdmg_extras`, `calibrate_agerio_extras` (núcleo `_calibrate_br_credito_agencia_core`).  
Em `CORE/transformer.py`: chamadas por `source_name` + relaxamento local **`_credito_brasil_onda_a_soft_continue`** (não altera `opportunity_gate.py`; só continua pipeline para hosts oficiais deste lote quando o gate corta por pontuação).

---

## Pipeline executado (dry-run)

```text
python scripts/retransform_all.py --sources bnb,banco_da_amazonia,desenvolve_sp,bdmg,agerio --dry-run --output-dir audit_reports_credito/lote_credito_brasil_onda_a_fix
python scripts/audit_semantic_classification.py --input-dir audit_reports_credito/lote_credito_brasil_onda_a_fix/standardized --output-dir audit_reports_credito/lote_credito_brasil_onda_a_semantic
python scripts/audit_docs_pipeline.py --sources bnb,banco_da_amazonia,desenvolve_sp,bdmg,agerio --output-dir audit_reports_credito/lote_credito_brasil_onda_a_docs
python scripts/audit_source_access_methods.py --sources bnb,banco_da_amazonia,desenvolve_sp,bdmg,agerio --output-dir audit_reports_credito/lote_credito_brasil_onda_a_access
```

### Resumo numérico (retransform)

Ver `audit_reports_credito/lote_credito_brasil_onda_a_fix/retransform_summary.json` e `retransform_by_source.json`.

### Auditoria semântica

Ver `audit_reports_credito/lote_credito_brasil_onda_a_semantic/audit_semantic_summary.md`.

---

## Restrições respeitadas

- Não executado `apply`; sem alterações Supabase ou schema.  
- `config/source_readiness.json` **não** atualizado automaticamente.  
- `opportunity_gate.py` **não** modificado (ajuste apenas via helper local no transformer).

---

## Artefatos deste lote

| Artefato | Caminho |
|----------|---------|
| Diagnóstico JSON | `audit_reports_credito/lote_credito_brasil_onda_a_diagnostico.json` |
| Por fonte | `audit_reports_credito/lote_credito_brasil_onda_a_by_source.json` |
| Exemplos | `audit_reports_credito/lote_credito_brasil_onda_a_examples.json` |
| Retransform | `audit_reports_credito/lote_credito_brasil_onda_a_fix/` |
| Semântica | `audit_reports_credito/lote_credito_brasil_onda_a_semantic/` |
| Docs | `audit_reports_credito/lote_credito_brasil_onda_a_docs/` |
| Acesso | `audit_reports_credito/lote_credito_brasil_onda_a_access/` |
