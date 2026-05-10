# Dry-run do loader: `plataforma_industria`

**Data de referência (summary):** 2026-05-02T00:47:41Z  
**Modo:** `dry-run` (sem `apply`)

## Comando

```text
python scripts/load_ready_sources.py --dry-run --sources plataforma_industria --exclude-blocked
```

## Resultado

| Métrica | Valor |
|--------|------:|
| Fontes selecionadas | 1 |
| Fontes excluídas (filtro + readiness) | 93 |
| Itens standardized | 23 |
| `would_upsert` | 23 |
| `would_ignore` | 0 |
| Erros de mapeamento | 0 |
| Itens com campos críticos vazios | 0 |
| Documentos perdidos no payload | 0 |
| Perda de documentos não-PDF | 0 |

Ficheiro standardized: `audit_reports_retransform/standardized/plataforma_industria_standardized.json`.

## Conclusão

O dry-run está **limpo** para esta fonte: todos os itens seriam upsertados, sem erros de mapeamento e sem perda de documentos no payload.

**Nota:** O `apply` não foi pedido nesta execução. Para decisão de staging, cruzar com o relatório de duplicidade face ao SENAI (`plataforma_industria_vs_senai_duplicates.*`): o loader usa **upsert por `link`**, pelo que URLs iguais não criam duas linhas na tabela `edital`, mas a **ordem de carga** pode determinar qual valor de `fonte_recurso` permanece no registro.

## Artefacto JSON

Métricas espelhadas em `plataforma_industria_ready_with_notes_loader_dryrun.json`.
