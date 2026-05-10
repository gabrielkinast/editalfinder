# Recovery C — recomendação de apply

**Apply não executado neste passo** (pedido explícito).

## Situação

- Dry-run em `recovery_c_setores_loader_dryrun` com **0** erros de mapeamento, **0** itens críticos vazios, **0** documentos perdidos.
- Standardized local: **0** itens com mais de 3 setores estratégicos após `recovery_c_cap_setor_estrategico_br`.

## Recomendação

1. Rever **NUCLEP**: URLs institucionais passam a `tipo_oportunidade = noticia_institucional` com aviso `recovery_c_nuclep_pagina_institucional` — confirmar se o produto deseja manter destino `edital` ou roteamento futuro para notícia (fora do âmbito desta recovery).
2. Quando a equipa validar, aplicar **só** `embrapii` e `nuclep` com readiness operacional acordado.

Comando de exemplo está em `recovery_c_setores_apply_recommendation.json`.
