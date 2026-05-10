# Limpeza semântica local — Lote Crédito/Desenvolvimento Onda A Brasil

**Data:** 2026-05-05  
**Alterações:** apenas `CORE/taxonomy_filtros.py` (`_calibrate_br_credito_agencia_core` + `calibrate_*` das cinco fontes).  
**Não alterado:** `opportunity_gate.py`, Supabase, `apply`, `config/source_readiness.json`.

## Objetivo

Reduzir `setor_estrategico_excessivo`, tags amplas e áreas inferidas sem evidência, mantendo crédito reembolsável bem rotulado e subvenção só com texto explícito.

## Auditoria semântica — antes × depois

| Métrica | Antes (`lote_credito_brasil_onda_a_semantic`) | Depois (`lote_credito_brasil_onda_a_semantic_fix_audit`) |
|--------|-----------------------------------------------|----------------------------------------------------------|
| Itens | 83 | 83 |
| `setor_estrategico_excessivo` | 6 | **0** |
| `classificacao_muito_ampla` | 3 | **0** |
| `area_cientifica_sem_evidencia` | 1 | **0** |
| **Total de flags** | 10 ocorrências em `flags_totais` | **0** |

Transformação (inalterada): **85** brutos → **83** transformados → **2** rejeitados pelo gate (mesmo comportamento).

## Regras implementadas no núcleo

1. **`setor_estrategico`**: no máximo **3** valores; só entram **agro**, **energia**, **sustentabilidade**, **inovacao**, **industria** ou **desenvolvimento_regional** com padrões explícitos no título/descrição/URL — **sem** preencher “desenvolvimento regional” só por ser agência de fomento.
2. **Inovação**: `_credito_br_innovacao_evidence` — `programa_inovacao` só com P&D, inovação, laboratório, etc.; não basta “banco”.
3. **Crédito reembolsável**: `natureza_recurso` = reembolsavel, `extras.tipo_recurso` = `credito`, `item.tipo_recurso` = financiamento reembolsável.
4. **Subvenção**: lista explícita de termos (subvenção, recursos não reembolsáveis, etc.) **e** ausência do conjunto “strong loan”.
5. **`area_cientifica` / `area_tecnologica`**: limpas se não houver evidência no corpus.
6. **`calibrate_bdmg_extras`**: aceita links em `bdmgorienta.bdmg.mg.gov.br`.
7. **`calibrate_agerio_extras`**: URLs de educação financeira ficam **sem** `setor_estrategico`.
8. **`calibrate_banco_da_amazonia_extras`**: páginas de **relatórios** (ex.: Relatórios do FNO) têm `area` zerada e `perfil_ideal` podado para não disparar “classificação muito ampla” por taxonomia genérica.

## Artefatos gerados

| Artefato | Caminho |
|----------|---------|
| Retransform dry-run | `audit_reports_credito/lote_credito_brasil_onda_a_semantic_fix/` |
| Auditoria semântica | `audit_reports_credito/lote_credito_brasil_onda_a_semantic_fix_audit/` |
| Auditoria de documentos | `audit_reports_credito/lote_credito_brasil_onda_a_semantic_fix_docs/` |
| Resumo JSON | `audit_reports_credito/lote_credito_brasil_onda_a_semantic_fix.json` |

## Readiness recomendado (pós-limpeza)

| Fonte | Recomendação | Notas |
|-------|----------------|-------|
| `bnb` | **ready_with_notes** | Flags semânticos zerados no audit local. |
| `banco_da_amazonia` | **ready_with_notes** | Idem; relatórios FNO tratados como caso especial. |
| `bdmg` | **ready_with_notes** | Idem. |
| `desenvolve_sp` | **needs_manual_review** | Seeds + WAF 403 — sem mudança de política. |
| `agerio` | **needs_manual_review** | Dois itens úteis no standardized; volume baixo. |

Atualização de `source_readiness.json` **não** foi aplicada automaticamente.
