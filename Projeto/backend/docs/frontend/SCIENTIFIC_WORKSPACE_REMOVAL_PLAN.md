# Plano de remoção — Workspace Científico (EditalFinder)

**Data:** 2026-05  
**Status:** Desconectado do produto; código arquivado em `frontend/EditalFinder-React/archive/scientific_workspace_reference/`.

**Motivo:** O Workspace Científico será reaproveitado em aplicativo pessoal separado. O EditalFinder foca em editais, radar, cadastros e **Workspace do Consultor**.

---

## Rotas

| Rota | Antes | Depois |
|------|-------|--------|
| `/workspace-cientifico` | `ScientificWorkspace` (flag `VITE_ENABLE_SCIENTIFIC_WORKSPACE`) | `Navigate` → `/dashboard` |
| `/workspace-consultor` | `ConsultorWorkspace` (flag + `canViewCadastros`) | **Mantido** |

Arquivo: `src/router/index.jsx`

---

## Menu (hambúrguer)

| Item | Arquivo | Ação |
|------|---------|------|
| Workspace Científico | `appNavigationConfig.js` | Removido |
| Workspace do Consultor | `appNavigationConfig.js` | Mantido (`ENABLE_CONSULTOR_WORKSPACE && canViewCadastros`) |

---

## Dashboard

| Componente | Ação |
|------------|------|
| `DashboardQuickActions.jsx` | Removido atalho Workspace Científico |
| `DashboardRadarSummary.jsx` | Mantido Workspace do Consultor |

---

## Feature flags

| Variável | Ação |
|----------|------|
| `VITE_ENABLE_SCIENTIFIC_WORKSPACE` | Removida de `.env.example` e `config/env.js` |
| `VITE_ENABLE_SCIENTIFIC_AI` | Mantida documentada como futura Edge Function (sem UI no produto) |
| `VITE_ENABLE_CONSULTOR_WORKSPACE` | **Default `true` em `.env.example`** |

---

## Componentes arquivados (`archive/scientific_workspace_reference/`)

- `components/scientific/*` (~40 componentes)
- `pages/ScientificWorkspace.jsx`
- `context/ScientificWorkspaceContext.jsx`

---

## Utils arquivados

- `utils/scientific/*` (~90 módulos): catálogos, progresso, XP, sessões, feed, notebook, export Markdown, auditoria DEV, etc.

---

## Hooks

Nenhum hook dedicado em `src/hooks/` — lógica em `ScientificWorkspaceContext.jsx` (arquivado).

---

## Estilos

- `src/styles/global.css` — bloco `.scientific-*` (~linhas 10071+) **permanece** por ora (não entra no bundle de rotas ativas; limpeza CSS opcional futura).

---

## localStorage (não apagar automaticamente)

Chaves documentadas em `clearScientificWorkspaceLocalCache.js` (arquivado):

- `scientific_workspace_interests`
- `scientific_workspace_notebook`
- `scientific_workspace_study_progress`
- `scientific_workspace_xp`
- `scientific_workspace_mastery_checks`
- `scientific_workspace_book_progress`
- `scientific_workspace_study_sessions`
- `scientific_workspace_project_level_filter`
- (outras listadas no util arquivado)

Dados permanecem no navegador do usuário; o EditalFinder não as lê mais.

---

## Documentação relacionada (repo, não movida)

| Arquivo | Nota |
|---------|------|
| `docs/SCIENTIFIC_WORKSPACE_PLAN.md` | Referência histórica |
| `docs/SCIENTIFIC_WORKSPACE_QA_CHECKLIST.md` | Referência histórica |
| `docs/SCIENTIFIC_WORKSPACE_AI_PLAN.md` | IA futura / outro app |
| `docs/FRONTEND_BACKEND_CONTEXT.md` §7b | Atualizado → remoção + Consultor |

---

## Imports removidos do produto ativo

| Arquivo | Antes |
|---------|-------|
| `router/index.jsx` | `ScientificWorkspace`, `SCIENTIFIC_LOCAL_STORAGE_KEYS` |
| `appNavigationConfig.js` | `ENABLE_SCIENTIFIC_WORKSPACE` |
| `DashboardQuickActions.jsx` | atalho científico |
| `config/env.js` | `ENABLE_SCIENTIFIC_WORKSPACE` |
| `AppReportProblemButton.jsx` | `logScientificWorkspace` |

Mantidos (strings apenas): `appFeedbackConfig.js` (`workspace_cientifico` em lista de origens históricas), `globalErrorReporter.js`.

---

## Workspace do Consultor — checklist de visibilidade

1. `.env.local`: `VITE_ENABLE_CONSULTOR_WORKSPACE=true`
2. Utilizador com `canViewCadastros` (ADMIN, CONSULTOR, FUNCIONARIO)
3. Rota `/workspace-consultor` registada quando flag true
4. DEV: log `[workspace-consultor] availability_check` no `Header.jsx`

---

## Opção aplicada

**Opção B:** código movido para `archive/scientific_workspace_reference/` (fora de `src/`), sem imports no bundle ativo.

**Não aplicado:** delete permanente; **não aplicado:** limpeza automática de localStorage.

---

## Validação

```bash
cd frontend/EditalFinder-React
npm run build
```

Manual: menu sem Científico; `/workspace-cientifico` → dashboard; menu Consultor visível com flag + permissão.
