# Investimentos Wave 1 — consolidado (`portal_estrategico`)

**Ambiente:** staging  
**Tabela:** `public.portal_estrategico`  
**Data de referência dos relatórios:** 2026-05-10  

Este documento consolida a **Wave 1 de investimentos** (Apex, BNDES, EIC) após correções do loader e do validador. **Não foi executado novo apply** ao gerar este consolidado.

---

## 1. Fontes e volumes

| Fonte | Itens na Wave (payload dedicado) |
|--------|----------------------------------|
| apex | 5 |
| bndes | 5 |
| eic | 5 |
| **Total** | **15** |

Pasta de entrada: `audit_reports_main_pipeline/investimentos_wave1_portais/standardized/`

---

## 2. Por que Apex, BNDES e EIC

- Cobertura **complementar**: exportação / internacionalização (Apex), **mercado de capitais e fundos** no Brasil (BNDES), **instrumentos europeus** de inovação e financiamento (EIC).
- O **diagnóstico** (`investimentos_wave1_diagnostico.json`) documenta o standardized existente (Apex com poucos registos; BNDES com muitas **chamadas** individuais; EIC com **programas**, listagem, calls e PDF). A Wave 1 **não** copia chamadas individuais nem calls fechadas para `portal_estrategico`; escolhe **hubs** estáveis por fonte.

---

## 3. Por que `portal_estrategico` e não `public.edital`

- São **portais ou páginas de programa agregadas**, não substitutos de editais com o mesmo contrato de negócio que `public.edital`.
- **BNDES/EIC**: FIPs, ETF, calls 2026, etc. continuam no pipeline **edital**; aqui só entram URLs de **secção** ou **programa** (listagem de fundos, mercado de capitais, Pathfinder, …).
- **Flags**: `categoria=investimentos`, `frontend_section=investimentos`, `mostrar_em_investimentos=true`, `mostrar_em_fornecedores=false`, `mostrar_no_radar=false` — alinhado ao desenho «Fornecedores & Investimentos» (ver também `portais_estrategicos_recovery_d1_consolidado.json` para o braço **fornecedores** na mesma tabela).

---

## 4. CHECK `portal_tipo` e solução `portal_tipo_db` + `extras.portal_tipo_wave1`

- A base impõe **`portal_estrategico_portal_tipo_check`** apenas com valores **legados** (ex.: `hub`, `registration`, `procurement`, …), incompatíveis com a taxonomia rica da Wave (`market_access`, `internationalization`, …).
- **Solução no loader:** a coluna **`portal_tipo`** enviada no upsert é **normalizada** para um valor permitido pela CHECK; a taxonomia original fica em **`extras.portal_tipo_wave1`** (e metadados auxiliares como `portal_tipo_db` na versão corrente do loader).
- **Resumo de apply** (`investimentos_wave1_portais_apply/load_portais_estrategicos_summary.json`): contagens na **coluna** após normalização — `hub` 11, `procurement` 3, `registration` 1.  
  O ficheiro `investimentos_wave1_portais.json` ainda descreve contagens **semânticas** do payload (pré-CHECK); usar o resumo de **apply** como fonte de verdade para o que está na BD.

---

## 5. Correção do validador (investimentos)

- O script `validate_portais_estrategicos_after_load.py` suporta **`--frontend-section auto|fornecedores|investimentos`** (em `auto`, infere a partir dos JSONs).
- Para **investimentos**: regras próprias (radar falso, investimentos verdadeiro, fornecedores falso, `portal_tipo_wave1` presente) e consulta **`vw_investimentos_front`** em vez de `vw_fornecedores_front`.

---

## 6. `mostrar_no_radar=false` e o Radar

- Mantém estes registos **fora** do agregador Radar de Fomento: o Radar deve filtrar `mostrar_no_radar` (ou equivalente) para não misturar portais estratégicos com oportunidades de fomento.

---

## 7. `vw_investimentos_front` e o frontend

- A view deve refletir linhas com **`frontend_section=investimentos`** (e política de flags acordada), alimentando a **área Investimentos** em paralelo a `vw_fornecedores_front` para fornecedores.
- Na validação pós-carga (`investimentos_wave1_portais_validation/validate_portais_estrategicos_after_load.json`): **15/15** links na tabela e **15/15** na view, **0** violações de regras.

---

## 8. Apply — inseridos / atualizados

Fonte: `investimentos_wave1_portais_apply/load_portais_estrategicos_summary.json`

| Métrica | Valor |
|---------|--------|
| `apply_status` | `applied` |
| Total processado | 15 |
| Inseridos | **0** |
| Atualizados | **15** |
| `upserted_total` | **15** |
| Erros | 0 |

Interpretação: todos os links já existiam ou foram tratados como **update** no upsert por `link` (cenário típico após tentativa anterior ou re-aplicação da mesma Wave).

---

## 9. Resultado da validação

| Verificação | Resultado |
|-------------|-----------|
| `status` | **ok** |
| Em `portal_estrategico` | **15/15** |
| Em `vw_investimentos_front` | **15/15** |
| Violações por linha | **0** |
| `investimentos_view_skipped` | **false** |

---

## 10. Próximos passos (frontend)

1. Consumir **`vw_investimentos_front`** na rota **Investimentos**; não misturar com listagens do Radar sem filtro de `mostrar_no_radar`.
2. Usar **`extras.portal_tipo_wave1`** para UI rica (badges, filtros); a coluna `portal_tipo` mantém compatibilidade com a CHECK.
3. Manter **Fornecedores** em `vw_fornecedores_front` / `frontend_section=fornecedores`.
4. Acompanhar **deduplicação** se a mesma URL surgir em `edital` e em `portal_estrategico`.

---

## 11. Restrições desta consolidação

- Sem **novo** apply, sem alteração de **schema**, sem alteração global de **opportunity_gate**.

---

## 12. JSON irmão

`audit_reports_main_pipeline/investimentos_wave1_consolidado.json`
