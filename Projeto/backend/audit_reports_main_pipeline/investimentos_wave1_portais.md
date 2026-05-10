# Investimentos Wave 1 — portais estratégicos (payloads)

## Objectivo

Primeira onda pequena (**5 itens por fonte**, máximo) de registos para `public.portal_estrategico`, secção **«Fornecedores & Investimentos» / investimentos**, sem:

- duplicar chamadas BNDES/EIC já modeladas como edital em `public.edital`;
- misturar com o Radar de Fomento (`mostrar_no_radar=false`);
- alterar schema, `opportunity_gate` global ou executar apply nesta entrega.

## Onde estão os standardized

`audit_reports_main_pipeline/investimentos_wave1_portais/standardized/`

- `apex_standardized.json` — 5 hubs (internacionalização, exporta mais, IAra, Qualifica, URL curta).
- `bndes_standardized.json` — 5 hubs (mercado de capitais, fundos, listagem de chamadas de fundos, CRIATEC, fundos empresas/projetos).
- `eic_standardized.json` — 5 hubs (listagem funding opportunities, Pathfinder, Transition, Accelerator, STEP Scale).

Todos com `extras.frontend_section=investimentos`, `mostrar_em_investimentos=true`, `mostrar_em_fornecedores=false`, `wave=investimentos_wave1`, `categoria_portal=investimentos`, `portal_tipo` explícito, `validacao_status=incompleto`, `setor_estrategico` com ≤ 3 valores.

## Dry-run do loader

Comando (já executado nesta tarefa):

```text
python scripts/load_portais_estrategicos.py --dry-run --sources apex,bndes,eic --input-dir audit_reports_main_pipeline/investimentos_wave1_portais/standardized --output-dir audit_reports_main_pipeline/investimentos_wave1_portais_dryrun
```

**Resultado:** `total_items=15`, `errors_count=0`, `mostrar_no_radar_true_count=0`, `mostrar_em_investimentos_true_count=15`, `mostrar_em_fornecedores_true_count=0`, sem `suspeito` nos `validacao_status_counts`.

Relatórios: `investimentos_wave1_portais_dryrun/load_portais_estrategicos_*.json|md`.

## Diagnóstico das fontes “reais”

Ver `investimentos_wave1_diagnostico.md` / `.json` (leitura de `audit_reports_retransform/standardized`).

## Alteração de código

`scripts/load_portais_estrategicos.py` — suporte a **investimentos** (categorias, `portal_tipo` Wave 1, validação condicionada a `frontend_section`, contagens `mostrar_em_investimentos_true_count`, `origem_pipeline` / `wave` a partir de extras).
