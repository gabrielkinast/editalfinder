# Recovery A — Resumo executivo

## Estado do dry-run (`audit_reports_main_pipeline/recovery_a/`)

- **Fontes:** `esa_star`, `dod_sbir_sttr`, `banco_da_amazonia`
- **Itens brutos / transformados:** ver `recovery_a/retransform_summary.json` (última corrida: 32 transformados, 0 rejeitados pelo transform)
- **Loader-only:** `mapping_errors` **0** nas três fontes; ver `recovery_a/loader_dryrun/audit_loader_only_summary.json`
- **Semântica:** ver `recovery_a/semantic/audit_semantic_summary.json` (ex.: `publico_alvo_sem_evidencia` residual)

## O que foi recuperado

| Fonte | Resultado |
|--------|-----------|
| **BASA** | 26 linhas de crédito/financiamento após filtros de ruído (Conta PJ, PF, renegociação, etc.) |
| **DoD SBIR/STTR** | 6 URLs reais `sbir.gov/topics/<id>` no fallback HTML (API com 429); excluídos success-stories, events-listing e hubs de apoio |
| **ESA STAR** | Nenhum item — coleta vazia de propósito (sem SSO/login isolado) |

## O que permanece bloqueado / limitado

- **ESA STAR:** continua **blocked** no readiness oficial até existir listagem pública com tenders verificáveis fora de SSO.

## O que foi tratado como ruído (não coletado ou filtrado)

- **DoD:** `/success-stories`, `/events-listing`, `/api`, `/data-resources`, `/participating-agencies`, `/impact`, FAQ, community, etc.; apenas detalhe `/topics/<id>` (ou solicitações) no HTML fallback.

## Critérios Recovery A (verificação)

- `mapping_errors_total`: **0**
- Tópicos DoD: **não** são páginas API/docs nem success stories
- Setores DoD calibrados: **≤ 3** entradas em `setor_estrategico`
- Títulos genéricos HTML "Topic" substituídos na calibração por rótulo explícito com ID numérico do tópico (`calibrate_dod_sbir_sttr_extras`)

## Próximos comandos sugeridos

1. Quando a API `api.www.sbir.gov` responder sem 429: `python dod_sbir_sttr/main_dod_sbir_sttr.py` e novo dry-run.
2. Dry-run loader oficial sobre pasta canónica **apenas** quando for promover (sem `--apply`).
3. Investigação manual: procurement ESA / convites públicos para destravar `esa_star`.

Ficheiro JSON espelho: `recovery_a_summary.json`.
