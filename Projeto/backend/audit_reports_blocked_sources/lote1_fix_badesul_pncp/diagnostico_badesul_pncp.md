# Diagnóstico específico — Badesul e PNCP

## Escopo

- Correções pequenas e locais aplicadas apenas em `badesul` e `pncp`.
- Sem alterações no `opportunity_gate` global.
- Sem apply em loader, sem Supabase, sem migration.

## Badesul

- **Antes:** 10 brutos, 0 transformados, 10 rejeitados.
- **Depois:** 7 brutos, 7 transformados, 0 rejeitados.
- **Ajustes efetivos:**
  - filtro local de ruído/anexos no crawler (remove anexos-modelo genéricos);
  - melhoria de classificação local (`tipo_oportunidade`, `perfil_ideal`);
  - soft-continue local no transformer para sinais fortes de crédito/subvenção oficial.
- **Qualidade atual:** `qualidade_dado_media=66.14`, `itens_suspeitos=7`.
- **Documentos:** preservação sem perdas (`7/7` com `documentos`, perdas `0`).
- **Semântica:** sem flags críticas no recorte atual.

## PNCP

- **Antes:** 1 bruto genérico, 0 transformados, 1 rejeitado.
- **Depois:** 0 brutos válidos nesta execução, 0 transformados, 0 rejeitados.
- **Ajustes efetivos:**
  - coleta mais robusta de API (tentativa com sessão/retry/parâmetros);
  - desativação de fallback genérico para não inserir página índice sem objeto oficial;
  - soft-continue local cauteloso preparado no transformer para casos com metadados oficiais.
- **Resultado prático:** sem dados válidos retornados pela API nesta execução, mas sem ruído novo.

## Recomendação de readiness

- `badesul`: **ready_with_notes** (ganho real; ainda exige refinamento para reduzir itens suspeitos).
- `pncp`: **manter blocked** (necessita coleta com itens oficiais concretos antes de liberar).
