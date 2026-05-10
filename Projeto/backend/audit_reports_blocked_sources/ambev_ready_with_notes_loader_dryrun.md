# Ambev — `ready_with_notes` e dry-run do loader

**Data:** 2026-05-03  

## Decisão aplicada

- **`ambev`** passa a **`ready_with_notes`** (não ready pleno).
- No disco atual, **`ambev` estava em `blocked`** em `config/source_readiness.json`, não em `needs_manual_review`; a alteração foi **remover de `blocked`** e **inserir em `ready_with_notes`** (ordem alfabética após `amazul`).

## Diff de readiness

| Ficheiro | Alteração |
|----------|-----------|
| `config/source_readiness.json` | `ambev` removido de **`blocked`**; adicionado a **`ready_with_notes`**. |
| `audit_reports_retransform/readiness_for_loader.json` | `ambev` removido de **`fontes_bloqueadas_temporariamente`**; adicionado ao fim de **`fontes_prontas_para_loader`** (entra no slice **`pronto_com_observacoes`**). `status_distribution`: **`pronto_com_observacoes` 64→65**, **`bloquear_temporariamente` 14→13**. |
| `audit_reports_retransform/standardized/ambev_standardized.json` | Substituído por cópia de `audit_reports_blocked_sources/lote4_fix_ambev/standardized/ambev_standardized.json`. |

O script `load_ready_sources.py` deriva `ready` vs `ready_with_notes` pela ordem em `fontes_prontas_para_loader` e pelos contadores `pronto_para_loader` (8) e `pronto_com_observacoes` (65); com **`ambev` na posição 72**, continua dentro do bloco **com observações**.

## Comando dry-run

```text
python scripts/load_ready_sources.py --dry-run --sources ambev --exclude-blocked --input-dir audit_reports_retransform/standardized --readiness audit_reports_retransform/readiness_for_loader.json
```

Saída global do script: `audit_reports_loader_ready/` (`load_ready_summary.json`, `load_ready_by_source.json`, etc.).

## Resultado do dry-run (totais)

| Métrica | Valor |
|---------|------:|
| Fontes selecionadas | 1 |
| Itens standardized | **7** |
| `would_upsert` | **7** |
| `would_ignore` | 0 |
| `mapping_errors` | **0** |
| `critical_empty_items` | **0** |
| Documentos na entrada | 0 |
| `documentos_perdidos_no_payload` | **0** |

## Verificação pedida (standardized `ambev`)

- **7 itens** — ok.  
- **`tipo_oportunidade`:** `chamada_publica` em todos (padrão acordado para desafios 100+ no pipeline).  
- **`tipo_recurso`:** `apoio_inovacao` — ok.  
- **`tipo_conteudo_ambev`:** `open_innovation_aceleracao` — ok.  
- **`regiao` (nível superior):** `Internacional` — ok.  
- **`idioma_original`:** `en` em `extras` — ok.  
- **Documentos:** nenhum no bruto; **sem perdas** no payload.  
- **Conteúdo:** desafios oficiais 100+ Accelerator; **sem** notícia/produto/marketing genérico no conjunto carregado.

## Staging — recomendação

- **Pode aplicar em staging** quando a equipa quiser **gravar** os 7 registos: o dry-run está **limpo** (`would_upsert = 7`, erros e críticos vazios a zero).  
- Manter **notas de produto**: programa **corporativo/privado**, texto **EN**, **sem prazo/valor** no standardized, **gate relaxado** documentado nos `extras` (`opportunity_gate_relax_scope=ambev_local`).  
- **Não** foi executado `--apply`; o snapshot de `environment_guard` no `load_ready_summary.json` indica **`has_allow_staging_apply: false`** — o apply real em staging deve seguir a **documentação de ambiente** do projeto (variável/guard explícitos), não este relatório sozinho.

## JSON irmão

Detalhe estruturado: `audit_reports_blocked_sources/ambev_ready_with_notes_loader_dryrun.json`.
