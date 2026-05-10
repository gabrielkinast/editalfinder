# Dry-run loader — Crédito multilateral Onda B (EIC + Eureka)

## Escopo

Promoção operacional apenas de **`eic`** e **`eureka_network`** para `ready_with_notes` / `pronto_com_observacoes` no readiness, com standardized canónico copiado para `audit_reports_retransform/standardized/`. **Não** promovidos: `fonplata` (revisão manual), `bid_lab` e `caf` (bloqueados). **Apply não executado.**

## Comando

```text
python scripts/load_ready_sources.py --dry-run --sources eureka_network,eic --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

## Ficheiros standardized copiados

- `audit_reports_retransform/standardized/eureka_network_standardized.json`
- `audit_reports_retransform/standardized/eic_standardized.json`

Origem: `audit_reports_credito/lote_credito_multilateral_onda_b_fix/standardized/`.

## Resumo do dry-run (loader)

| Métrica | Valor |
|--------|------:|
| `sources_selected` | 2 |
| Itens standardized (total) | 35 |
| `would_upsert_total` | 35 |
| `would_ignore_total` | 0 |
| `mapping_errors_total` | 0 |
| `critical_empty_items_total` | 0 |
| `documentos_perdidos_no_payload_total` | 0 |

## Por fonte

| Fonte | Itens | Would upsert | Mapping errors | Docs perdidos |
|-------|------:|-------------:|---------------:|--------------:|
| eic | 14 | 14 | 0 | 0 |
| eureka_network | 21 | 21 | 0 | 0 |

## Verificação (tarefa 6)

- `sources_selected = 2`: sim.
- `would_upsert_total > 0`: sim (35).
- `mapping_errors_total = 0`: sim.
- `critical_empty_items_total = 0`: sim.
- `documentos_perdidos_no_payload_total = 0`: sim.
- **Institucional genérico:** amostragem por `tipo_oportunidade` nos standardized — Eureka com `call_for_proposals`, EIC com `funding_opportunity` (ações concretas de chamada / funding), sem páginas institucionais óbvias na amostra.
- **`programa_agregado`:** não há campo `programa_agregado` nos JSON analisados; nenhum hub agregador foi marcado explicitamente.

## Configuração atualizada

- `config/source_readiness.json`: `eic`, `eureka_network` em `ready_with_notes`; `fonplata` em `needs_manual_review`; `bid_lab`, `caf` em `blocked`.
- `audit_reports_retransform/readiness_for_loader.json`: mesmas fontes nas listas derivadas; `eic` e `eureka_network` incluídos em `fontes_prontas_para_loader` (bloco `pronto_com_observacoes` via contagem + posição na lista).

## Artefatos do loader

- `audit_reports_loader_ready/load_ready_summary.json`
- `audit_reports_loader_ready/load_ready_by_source.json`

Versão estruturada deste relatório: `credito_multilateral_onda_b_ready_with_notes_loader_dryrun.json`.
