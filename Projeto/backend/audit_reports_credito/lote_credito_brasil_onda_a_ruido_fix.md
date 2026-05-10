# Limpeza de ruido — Onda A Brasil (resultado)

**Data:** 2026-05-06 (UTC)

## Pipeline executado

```text
python bnb/main_bnb.py
python banco_da_amazonia/main_banco_da_amazonia.py
python bdmg/main_bdmg.py
python agerio/main_agerio.py
python desenvolve_sp/main_desenvolve_sp.py

python scripts/retransform_all.py --sources bnb,banco_da_amazonia,bdmg,agerio,desenvolve_sp --dry-run --output-dir audit_reports_credito/lote_credito_brasil_onda_a_ruido_fix
python scripts/audit_semantic_classification.py --input-dir audit_reports_credito/lote_credito_brasil_onda_a_ruido_fix/standardized --output-dir audit_reports_credito/lote_credito_brasil_onda_a_ruido_fix_semantic
python scripts/audit_docs_pipeline.py --sources bnb,banco_da_amazonia,bdmg,agerio,desenvolve_sp --output-dir audit_reports_credito/lote_credito_brasil_onda_a_ruido_fix_docs
```

**Sem** apply, **sem** Supabase, **sem** alteracao ao `opportunity_gate` global.

## Comparacao agregada (baseline `…/onda_a_fix` vs pos-limpeza)

| Metrica | Antes | Depois | Delta |
|---------|------:|-------:|------:|
| Itens brutos | 85 | 79 | -6 |
| Transformados | 83 | 79 | -4 |
| Rejeitados pelo gate | 2 | 0 | -2 |

Detalhe por fonte e flags semanticas: ver `audit_reports_credito/lote_credito_brasil_onda_a_ruido_fix.json`.

## Confirmacoes solicitadas

| Pergunta | Resultado |
|----------|-----------|
| **Entre em contato** (BDMG) saiu? | Sim — removido no bruto e barrado pelo detector de URL `investimento_hub` / titulos institucionais se reaparecer. |
| Paginas conta/login/atendimento sairam? | **Conta PJ** BASA filtrada; padroes `/login`, internet banking dedicado, FAQ/atendimento cobertos pelo modulo de ruido. |
| Paginas genericas de banco sairam? | Grandes blocos BDMG (sobre, imprensa, licitacoes hub, EN, documentacao, carreiras, correspondentes) filtrados; ver diagnostico JSON. |
| Linhas de credito preservadas? | Sim — pronampe, micro/pequenas/medias empresas, agronegocio, municipios, PDFs de regulamento/cartilha quando URL de produto; AgeRio microcredito/microempreendedor mantidos com soft-continue local estendido. |

## Auditoria semantica

- **Antes** (`…/onda_a_semantic_fix_audit`): sem flags totais registradas.
- **Depois** (`…/onda_a_ruido_fix_semantic`): 1 flag `area_cientifica_sem_evidencia` (volume baixo).

## Readiness recomendado (manual)

| Fonte | Recomendacao | Motivo |
|-------|----------------|--------|
| bnb | **ready_with_notes** | Volume estavel; ainda ha texto repetido/layout Liferay. |
| banco_da_amazonia | **ready_with_notes** | Conta PJ removida; revisar ancoras genericas “suspeitas”. |
| bdmg | **ready_with_notes** | Ruido institucional caiu forte; duplicatas de titulo/segmentos municipios podem precisar dedupe futuro. |
| agerio | **needs_manual_review** | Poucos itens; dependencia de areas-de-atuacao; educacao financeira excluida. |
| desenvolve_sp | **needs_manual_review** | Seeds curados + WAF 403; sem texto rico automatico. |

Nao atualizado: `config/source_readiness.json`.
