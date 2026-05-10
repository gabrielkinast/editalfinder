# AMAZUL — loader dry-run (`ready_with_notes`)

**Data:** 2026-05-03  
**Comando:** `python scripts/load_ready_sources.py --dry-run --sources amazul --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json`

## Diff / resumo de readiness

| Ficheiro | Alteração |
|----------|-----------|
| `config/source_readiness.json` | **amazul** removido de `blocked` → inserido em `ready_with_notes` (ordem alfabética). **marinha**, **dcta_ita_iae** inalterados em `blocked`. |
| `audit_reports_retransform/readiness_for_loader.json` | **amazul** retirado de `fontes_bloqueadas_temporariamente` (14 entradas); acrescentado ao fim de `fontes_prontas_para_loader`; `pronto_com_observacoes` 63→**64**; `bloquear_temporariamente` 15→**14**. |
| `audit_reports_retransform/readiness_rows.json` | Linha **amazul** alinhada a métricas atuais e `recomendacao_loader`: **pronto_com_observacoes**. |
| `audit_reports_retransform/standardized/amazul_standardized.json` | Cópia a partir de `audit_reports_blocked_sources/lote4_fix_defesa_brasil/standardized/amazul_standardized.json`. |

## Resultado do dry-run (loader)

| Métrica | Valor |
|---------|------:|
| Fontes selecionadas | 1 |
| Itens standardized | **19** |
| **would_upsert** | **19** |
| would_ignore | 0 |
| **mapping_errors** | **0** |
| **critical_empty_items** | **0** |
| documentos preservados (itens) | 19 / 19 |
| **pdf_url** preservado (itens) | 19 / 19 |
| documentos perdidos no payload | 0 |

Campos rastreados (entrada = payload, contagens iguais): `tipo_oportunidade` 19, `tipo_recurso` 19, `perfil_ideal` 19, `validacao_status` 19, `qualidade_dado` 19, `setor_estrategico` 17, `area` 15, `publico_alvo` 7.

## Verificações pedidas (item 6)

- **tipo_oportunidade:** em todos os 19 registos, `licitacao` — coerente com compra pública / dispensa, não índice institucional.
- **tipo_recurso:** 13 com **«licitação»**; **6** com rótulos de **Prémio/Concurso**, **Subvenção** ou **Reembolsável** — provável ruído do texto/PDF DOU agregado; **não** estão como «fomento» explícito na maioria, mas convém **revisão manual** ou ajuste futuro de regra local se o produto exigir só «Contrato público / aquisição».
- **validacao_status:** 14 `valido`, 3 `incompleto`, 2 `suspeito`.
- **Notícia institucional:** nenhum título analisado com padrão óbvio de notícia/menu.
- **setor_estrategico:** preenchido em 17 itens (2 vazios, alinhado às flags semânticas conhecidas).

Detalhe tabulado: ver `amazul_ready_with_notes_loader_dryrun.json` → `verificacao_pedido_6`.

## JSON irmão

`audit_reports_blocked_sources/amazul_ready_with_notes_loader_dryrun.json` — espelho estruturado + recomendação de staging.

## Recomendação: aplicar em staging?

**Sim, com ressalvas (`ready_with_notes`):** o dry-run está **limpo** para upsert (0 erros de mapeamento, 0 críticos vazios, documentos e `pdf_url` preservados). Antes de um **apply** real: validar os **6** `tipo_recurso` atípicos face ao objeto da dispensa; opcionalmente corrigir taxonomia/transformer numa iteração seguinte. **Apply não foi executado** nesta tarefa.
