# Referência arquivada — Workspace Científico

Este código foi **removido do produto EditalFinder** em maio/2026.

- **Motivo:** módulo pessoal/acadêmico, sem relação direta com o fluxo consultor/cliente.
- **Destino previsto:** aplicativo pessoal separado.
- **Plano de remoção:** `docs/frontend/SCIENTIFIC_WORKSPACE_REMOVAL_PLAN.md`

## Estrutura

```
archive/scientific_workspace_reference/
  pages/ScientificWorkspace.jsx
  context/ScientificWorkspaceContext.jsx
  components/scientific/
  utils/scientific/
```

## Reintegrar noutro app

1. Copiar pastas para o novo projeto React.
2. Ajustar imports (`../../context` → paths locais).
3. Restaurar estilos `.scientific-*` de `src/styles/global.css` ou extrair para CSS dedicado.
4. Reativar rota e feature flag no router do novo app.

## localStorage

Chaves documentadas em `utils/scientific/clearScientificWorkspaceLocalCache.js`.

O EditalFinder **não limpa** essas chaves automaticamente.
