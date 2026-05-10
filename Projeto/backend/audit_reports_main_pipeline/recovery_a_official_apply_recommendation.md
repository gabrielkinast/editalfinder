# Recovery A — recomendação oficial de apply

## Opção recomendada: **1 — Staging para BASA e DoD SBIR/STTR**

### Porquê

- **Loader (dry-run oficial):** 2 fontes selecionadas, **32** upserts simulados, **0** erros de mapeamento, **0** itens com vazios críticos, **0** documentos perdidos no payload; destino **`edital`: 32**.
- **Semântica (scan + flags):** critérios pedidos (setor > 3, título ruidoso, login/SSO, API/docs, páginas institucionais genéricas) **cumpridos** no conjunto oficial; apenas **`publico_alvo_sem_evidencia`: 1** — impacto baixo, documentado em `recovery_a_official_semantic_summary.json`.
- **Ruído excluído:** sem Conta PJ, sem Success Stories / News / Events / hubs DoD, sem ESA no lote.

### Ressalvas operacionais

- **DoD:** com **API 429**, os tópicos vêm sobretudo de **HTML** — muitos itens em **`incompleto`**; convém **revisão humana** antes de `apply` a staging.
- **BASA:** linhas reais; também predominam incompletos por falta voluntária de inventar prazo/valor.

## O que **não** fazer nesta fase

- Não executar **`apply`** nem promover **readiness oficial** sem decisão explícita da equipa.

## Alternativas

- **Opção 2:** só **BASA** em staging se quiserem **adiar DoD** até a API estar estável.
- **Opção 3:** não aplicar se um **re-crawl** futuro introduzir ruído — neste dry-run **não** se verifica ruído crítico.

Espelho JSON: `recovery_a_official_apply_recommendation.json`.
