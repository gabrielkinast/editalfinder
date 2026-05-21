# F-35 — comparação dry-run 10 vs 30

## Feed (inventário)

| Métrica | Valor |
|---------|------:|
| Total no feed JSON | 302 |
| Dentro de 12 meses | 80 |
| Elegível (pipeline, sem cap) | 80 |

## Execuções

| Métrica | `f35_news_dryrun` (10) | `f35_news_dryrun_30` (30) | Δ |
|---------|------------------------:|--------------------------:|--:|
| Processado | 10 | 30 | +20 |
| Válido | 10 | 30 | +20 |
| Incompleto | None | 0 | +0 |
| errors_count | 0 | 0 | — |

### Validação (ampliado)

- `valido`: **30**

### Content type — ampliado (30 itens)

- `News`: 30

### Eixos (ampliado)

- `aeroespacial`: 30
- `defesa`: 30
- `aviacao_militar`: 28
- `industria_estrategica`: 14
- `tecnologia_militar`: 14
- `geopolitica_tecnologica`: 7
