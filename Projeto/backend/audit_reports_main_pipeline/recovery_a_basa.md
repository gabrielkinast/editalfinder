# Recovery A — Banco da Amazônia (BASA)

## Alterações

- **Crawler:** excluídos links `solucoes-pf`, `pessoa-fisica`, renegociação, conta-pj, concurso, internet-banking, fale-conosco, ouvidoria (salvo quando ainda em rotas de crédito empresas/agro).
- **Ruído URL:** regex `renegociacao` em `credito_brasil_onda_a_noise.py`; `crawler_link_exclude_extra` ampliado.
- **Taxonomia:** `strong_loan` inclui FNO/PRONAF/FUNGETUR/Finame; `calibrate_banco_da_amazonia_extras` força `programa_credito` em URLs de linhas oficiais.
- **Qualidade:** `item_quality` usa `fonte`/`fonte_recurso`; linhas BASA com `opportunity_gate_relaxed` + scope `credito_brasil_onda_a` passam a **`incompleto`** em vez de **`suspeito`** quando o URL indica linha oficial (incl. `fundo-constitucional`).

## Resultado (dry-run `recovery_a/`)

- **26** itens transformados; **0** rejeitados pelo transform; **`suspeito_ativo_true` local = 0**; **`incompleto` = 26** (ausência de prazo/valor — esperado; não inventamos campos).
- **`setor_estrategico` > 3:** 0 nos itens verificados.
- **mapping_errors (loader-only):** 0.

## Ficheiros

- JSON: `recovery_a_basa.json`
- Raw: `recovery_a/raw/banco_da_amazonia_editais.json`
- Standardized: `recovery_a/standardized/banco_da_amazonia_standardized.json`
