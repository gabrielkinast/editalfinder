# Dry-run com canonização — `senai` + `plataforma_industria`

**Comando**

```text
python scripts/load_ready_sources.py --dry-run --sources senai,plataforma_industria --exclude-blocked
```

**Referência:** `id_execucao` `5c388ae9-2669-43ed-8e3b-04dd6474085c`, `data_auditoria` `2026-05-02T00:58:39Z` (ver `audit_reports_loader_ready/load_ready_summary.json`).

## Configuração

- Ficheiro: `config/source_canonicalization.json`
- Grupo `plataforma_inovacao`: canónico `senai`, alias `plataforma_industria`, política `skip_alias_if_canonical_exists`, regra `url_contains` nos hubs `/categoria/`.

## Ordem de processamento

O loader ordena as fontes para **processar o canónico antes do alias**, de modo a reivindicar os `link` do SENAI antes de avaliar a plataforma_industria.

## Resultados agregados

| Métrica | Valor |
|--------|------:|
| Fontes selecionadas | 2 |
| Itens standardized (soma bruta) | 45 |
| **Upsert simulado** (`would_upsert_total`) | **23** |
| **Ignorados por canonização** | **22** |
| Ignorados por erro de mapeamento | 0 |
| Links reivindicados no grupo (SENAI) | 22 |

## Por fonte

| Fonte | Standardized | would_upsert | canonical_skipped |
|-------|-------------:|-------------:|------------------:|
| senai | 22 | 22 | 0 |
| plataforma_industria | 23 | 1 | 22 |

## Interpretação

As **22** URLs comuns ao SENAI deixam de ser simuladas na `plataforma_industria`, evitando sobrescrever `fonte_recurso` sem necessidade. O **único** upsert restante da alias corresponde ao URL **não** presente no standardized do SENAI (categoria exclusiva).

## Recomendação final

- **Com canonização (recomendado para staging quando aplicarem):** manter **ambas** as fontes no pipeline de carga com `source_canonicalization.json` — efeito líquido igual a **SENAI + exclusivos da plataforma**.
- **Sem canonização:** carregar **apenas SENAI** para os hubs, e usar `plataforma_industria` só para URLs que o crawl SENAI não cobre.

JSON espelhado: `plataforma_inovacao_canonical_dryrun.json`.
