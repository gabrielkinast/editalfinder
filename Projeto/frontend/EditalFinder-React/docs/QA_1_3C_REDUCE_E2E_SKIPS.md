# QA 1.3C — Reduce Avoidable E2E Skips

**Data:** 2026-06-10

---

## 1. Objetivo

Reduzir skips evitáveis na suíte E2E autenticada, mantendo apenas o skip legítimo de escrita em Cadastros sem `E2E_ALLOW_WRITE_TESTS=1`.

**Meta com credenciais QA:** `18 passed / 1 skipped / 0 failed`.

---

## 2. Diagnóstico dos skips (antes do patch)

| Teste | Motivo real | Evidência |
|-------|-------------|-----------|
| Cadastros — modal sem salvar | Admin QA abre Cadastros na aba **Usuários** por padrão (`canManageUsers`); botão `cadastro-novo-edital` só existe na aba **Editais** | `debug-e2e/skip-cadastro_novo_edital_not_visible.*` |
| Editais filters — busca + status | Seção **Filtrar por status** usa `<details defaultOpen={false}>`; checkboxes existem no DOM mas não estão visíveis até expandir o collapse | `debug-e2e/skip-status_filters_not_visible.*` |
| Editais status filter — Aberto | Mesmo problema do collapse; além disso skip genérico sem evidência | idem |
| Escrita opt-in | Esperado: `E2E_ALLOW_WRITE_TESTS !== "1"` | — |

---

## 3. Correções aplicadas

### Cadastros (`cadastros-smoke.spec.js`)

- Navega para aba Editais via `data-testid="cadastros-tab-editais"` antes de procurar `cadastro-novo-edital`.
- Fecha modal com `edital-form-cancel` ou `edital-form-close` (sem `.first()` genérico em “Fechar”).
- Skip com `cadastro_without_permission` apenas se houver mensagem de permissão na página.

### Filtros Editais (`editais-filters.spec.js`, `editais-status-filter.spec.js`)

- `openStatusFilterSection()` expande o collapse **Filtrar por status** (`semantic-status-section-toggle`).
- `toggleFirstAvailableStatusFilter()` tenta `aberto` → `sem_prazo` → `encerrado` → `indefinido` → primeiro checkbox visível.
- Não depende de quantidade de cards após filtrar; valida toggle checked/unchecked e ausência de erro fatal.

### Escrita opt-in

- Mensagem de skip padronizada: `SKIP_WRITE_OPT_IN_DISABLED: set E2E_ALLOW_WRITE_TESTS=1 to create a manual edital`.

---

## 4. Helpers novos/alterados (`tests/e2e/_helpers.js`)

| Helper | Função |
|--------|--------|
| `waitForAuthenticatedAppReady` | Dashboard estável pós-login |
| `waitForEditaisCatalogReady` | Página Editais + stats sem loading |
| `getFirstVisibleEditalCard` | Primeiro card visível |
| `getSearchableCardTitle` | Título pesquisável (ignora badges) |
| `openEditaisSidebarIfNeeded` | Sidebar mobile |
| `openStatusFilterSection` | Expande collapse de status |
| `toggleFirstAvailableStatusFilter` | Marca primeiro status disponível |
| `navigateCadastrosEditaisTab` | Aba Editais em Cadastros |
| `closeAdminEditalModal` | Cancelar/fechar sem salvar |
| `ensureEditaisFiltersVisible` | Agora delega para `openStatusFilterSection` |

---

## 5. testids adicionados

| testid | Onde |
|--------|------|
| `cadastros-tab-editais` | Sidebar Cadastros — aba Editais |
| `edital-form-cancel` | Botão Cancelar do `EditalForm` |
| `edital-form-close` | Botão Fechar do `Modal` (somente edital) |
| `semantic-status-section` | `<details>` do collapse de status |
| `semantic-status-section-toggle` | `<summary>` Filtrar por status |

---

## 6. Resultado esperado

```powershell
$env:E2E_USER_EMAIL="..."
$env:E2E_USER_PASSWORD="..."
npm run qa:local
```

| Camada | Resultado |
|--------|-----------|
| Unit | 290 passed |
| Build | passed |
| E2E | **18 passed / 1 skipped / 0 failed** |

Único skip: `cadastros-smoke` — cria edital manual (escrita opt-in).

Sem credenciais: specs autenticados skipped (esperado).

---

## 7. Limitações

- Usuário sem `canCreate` ainda skipa com `cadastro_without_permission`.
- Catálogo vazio ainda skipa com evidência (`no_visible_cards`, `catalog_received_zero`).
- Escrita opt-in cria registro no DB (não executada neste patch).

---

## 8. Próximo patch recomendado

**QA 1.3B** — GitHub Actions/CI com secrets e publicação de artefatos.

## Referências

- `docs/QA_1_2_EXPANDED_E2E_REGRESSION_SUITE.md`
- `docs/QA_1_3A_STANDARDIZED_QA_SCRIPTS.md`
