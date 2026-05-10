# Lote 4 — relatório consolidado (Brasil / legado)

**Data de fecho:** 2026-05-03  
**Estado inicial de referência:** `audit_reports_blocked_sources/lote4_brasil_legado_diagnostico.json` (2026-05-01).

## Resumo executivo

O lote 4 tratou **sete** fontes brasileiras ou de legado. **Quatro** atingiram critério de carga em staging com **observações** (`ready_with_notes`): **apex**, **faperg**, **amazul** e **ambev**, totalizando **31** registos standardized combinados. O **dry-run** conjunto do loader (`apex,faperg,amazul,ambev`) ficou **limpo**: **31** `would_upsert`, **0** erros de mapeamento, **0** itens com campos críticos vazios; **documentos** e **`pdf_url`** preservados em todos os itens que os trazem no standardized (**20** itens com documentos ao nível agregado do resumo do loader).

**Três** fontes **não** entram no fecho positivo do módulo edital: **marinha** (listagem inacessível por **403/Cloudflare**), **dcta_ita_iae** (**404** em URLs antigas) e **science_scraper** (conteúdo de **agenda/notícias**, mantido **blocked** / fora de `public.edital`; possível módulo futuro, **sem** correção neste lote).

Neste relatório: **não** se executou `--apply`, **não** se alterou Supabase, **não** se aplicaram migrations e **não** se tocou no **opportunity_gate** global.

---

## Tabela por fonte

| Fonte | Antes (lote / legado) | Depois | Brutos (ref.) | Transform. | Rej. | Docs / PDF | Readiness | Staging |
|--------|----------------------|--------|---------------|------------|------|------------|-----------|---------|
| **apex** | 1 bruto, 0 T, 1 rej.; ruído eventos | 3 Exporta Mais; `apoio_internacionalizacao` | 3 | 3 | 0 | — | ready_with_notes | Sim |
| **faperg** | 0 brutos no snapshot legado | 2 chamadas; 1 PDF | 2 | 2 | 0 | 1 PDF preservado | ready_with_notes | Sim |
| **amazul** | 0 brutos no snapshot legado | 19 licitações/dispensas | 19 | 19 | 0 | 19 com docs/PDF simulados | ready_with_notes | Sim |
| **ambev** | 7 brutos, 0 T, 7 rej. (gate) | 7 desafios 100+ | 7 | 7 | 0 | — | ready_with_notes | Sim |
| **marinha** | 0 brutos; URL sem itens | Inalterado | 0 | 0 | — | — | blocked | Não |
| **dcta_ita_iae** | 0 brutos; 404 | Inalterado | 0 | 0 | — | — | blocked | Não |
| **science_scraper** | 14 brutos, 0 T, 14 rej. | Inalterado (fora edital) | 14 | 0 | 14 | — | blocked | Não |

*(“T” = transformados no pipeline; “Rej.” = rejeitados pelo gate/transformação no relatório legado ou situação atual.)*

---

## Problemas encontrados (síntese)

| Fonte | Problema principal |
|--------|---------------------|
| apex | Confusão listagem **eventos** vs **programas** reais; título de ruído |
| faperg | **Crawler/URLs** editais RS; legado sem itens |
| amazul | **Índice/heurística** sem itens no snapshot legado |
| ambev | **Gate** + **EN** + taxonomia sem calibração local |
| marinha | **403 / Cloudflare** |
| dcta_ita_iae | **404** gov.br |
| science_scraper | **Agenda** + gate; não edital BR |

---

## Correções feitas (síntese)

- **apex:** extração/calibração; **`tipo_recurso` → `apoio_internacionalizacao`**.
- **faperg:** fontes/URLs e fluxo para editais; preservação de **PDF**.
- **amazul:** dados reais de **licitação/dispensa**; **`tipo_recurso` → licitação** em massa.
- **ambev:** **`calibrate_ambev_extras`** + **`_ambev_soft_continue`** (sem alterar gate global).
- **marinha / dcta / science:** nenhuma correção no âmbito deste fecho (conforme pedido).

---

## Dry-run combinado (fontes prontas)

- **Comando:** `python scripts/load_ready_sources.py --dry-run --sources apex,faperg,amazul,ambev --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json`
- **Relatório dedicado:** `audit_reports_blocked_sources/lote4_ready_sources_loader_dryrun.md` e `.json`
- **Artefactos do script:** `audit_reports_loader_ready/load_ready_summary.json`, `load_ready_by_source.json`

---

## Listas operacionais

**Liberadas para staging (com observações):** `apex`, `faperg`, `amazul`, `ambev`.

**Pendentes / bloqueadas / fora do módulo edital:** `marinha`, `dcta_ita_iae`, `science_scraper`.

---

## Apply staging — comando recomendado (não executado)

PowerShell:

```powershell
$env:EDITALFINDER_ALLOW_STAGING_APPLY="true"
$env:EDITALFINDER_ENV="staging"
python scripts/load_ready_sources.py --apply --staging --sources apex,faperg,amazul,ambev --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json --test-db-before-apply
```

*(Variáveis conforme `docs/STAGING_LOADER.md`.)*

## Validação pós-apply — comandos recomendados (não executados)

```powershell
python scripts/validate_database_after_load.py --staging --source apex
python scripts/validate_database_after_load.py --staging --source faperg
python scripts/validate_database_after_load.py --staging --source amazul
python scripts/validate_database_after_load.py --staging --source ambev
```

---

## Próximo passo recomendado

1. **Revisão humana curta** das quatro fontes (notas EN Ambev, confiança Apex, PDF FAPERGS, volume Amazul).  
2. **Apply em staging** com o bloco PowerShell acima.  
3. **`validate_database_after_load.py`** por fonte.  
4. Abrir **novo lote** apenas para **marinha** / **dcta_ita_iae** após mapeamento de URLs ou política de acesso; para **science_scraper**, decisão de produto (**módulo notícias** vs desligar).

---

## JSON consolidado

Dados estruturados: `audit_reports_blocked_sources/lote4_consolidado.json`.
