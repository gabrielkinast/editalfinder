# Recovery B — por fonte (AMAZUL, Ambev, BADESUL)

| fonte | staging suspeito (pós Recovery A) | itens local | suspeito ativo local | incompleto | válido |
|---|---:|---:|---:|---:|---:|
| amazul | 14 | 20 | 0 | 6 | 14 |
| ambev | 7 | 7 | 0 | 7 | 0 |
| badesul | 7 | 5 | 0 | 5 | 0 |

## Provável causa (resumo)

Gate relaxado (opportunity_gate_relaxed) sem estado final adequado em item_quality — corrigido com scopes amazul_local, ambev_local, badesul_local → incompleto; BADESUL: calibrate_badesul_extras + remoção de fallback institucional.