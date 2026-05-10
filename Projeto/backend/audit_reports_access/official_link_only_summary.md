# Official link only / acesso limitado

- `official_link_only_total`: **0**
- `access_limited_total` (validacao_status): **0**

## Por fonte (official_link_only)


## access_reason


## Exemplos


## Readiness

Se `official_link_only_total / itens_transformados >= 0.35` numa fonte (ver `retransform_by_source.json`), `build_loader_readiness.py` despromove de `pronto_para_loader` para `pronto_com_observacoes`.
Fontes dependentes de link-only não devem ir a **ready** pleno sem revisão humana.