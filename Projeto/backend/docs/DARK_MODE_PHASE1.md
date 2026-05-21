# Dark Mode — Fase 1 (incremental) — EditalFinder

Esta fase introduz uma infraestrutura **segura e incremental** de tema **claro/escuro/sistema** no frontend React/Vite, sem tentar converter 100% do CSS de uma vez.

## Objetivo

- Permitir que o utilizador selecione:
  - **Tema claro** (`light`)
  - **Tema escuro** (`dark`)
  - **Usar tema do sistema** (`system`)
- Persistir a preferência no browser.
- Aplicar o tema globalmente via **classe no `<html>`** e **variáveis CSS**.
- Cobrir primeiro os **elementos globais principais** (body, header, modal, inputs).

## Onde a preferência é salva

- **localStorage key**: `editalfinder.theme`
- Valores possíveis: `light` | `dark` | `system`

## Como o tema é aplicado

### Classes no documentElement

O tema resolvido é aplicado no `<html>` como uma destas classes:

- `theme-light`
- `theme-dark`

### Preferência `system`

Quando `system` está selecionado:

- o tema é resolvido usando `window.matchMedia('(prefers-color-scheme: dark)')`
- o app escuta mudanças do sistema (quando disponível) e alterna automaticamente

### Arquivo central

- `frontend/EditalFinder-React/src/config/theme.js`

Funções principais:

- `getSavedThemePreference()`
- `saveThemePreference(pref)`
- `resolveThemePreference(pref)`
- `applyTheme(pref)` (aplica classe e configura listener quando `system`)

Integração atual:

- `SettingsContext` aplica o tema salvo no mount.
- `SettingsForm` expõe a seção **Aparência** e aplica imediatamente ao selecionar.

## Variáveis CSS criadas (Fase 1)

Arquivo:

- `frontend/EditalFinder-React/src/styles/global.css`

Tokens adicionados em `:root`:

- `--color-bg`
- `--color-surface`
- `--color-surface-soft`
- `--color-text`
- `--color-muted`
- `--color-border`
- `--color-primary`
- `--color-secondary`
- `--shadow-card`
- `--color-input-bg`
- `--color-backdrop`

Override em `.theme-dark`:

- redefine `--color-*` para o tema escuro
- **preserva customização** de `primaryBlue`/`primaryYellow` usando:
  - `--color-primary: var(--primary-blue)`
  - `--color-secondary: var(--primary-yellow)`

## Áreas cobertas nesta fase

- **Base global**: `html, body` agora usam `--color-bg` / `--color-text`
- **Header/menu**: ajustes iniciais para usar `--color-surface`, `--color-border`, `--color-text`, `--color-primary`
- **Modal**: backdrop e surface/border usando tokens
- **Inputs principais**: `form-group` inputs/selects/textarea e busca no header
- **Empty/Error states**: cores principais migradas para `--color-text`/`--color-muted`

## Limitações conhecidas (intencionais)

- O `global.css` ainda contém muitos usos de variáveis legadas (`--text-dark`, `--bg-white`, `--border-light`) e cores hardcoded.
- Não foi feita conversão total de todos os componentes/cards/tabelas nesta fase.
- O tema escuro pode ter pequenos “pontos claros” até as próximas fases.

## Como testar (manual)

1. Abrir o app e fazer login.
2. Abrir **Configurações** (botão ⚙️).
3. Alternar:
   - Tema escuro → verificar `header`, `modal`, fundos e inputs
   - Recarregar a página → a preferência deve persistir
   - Tema claro → deve ficar parecido com o tema atual
   - Usar tema do sistema → alternar o tema do SO (se suportado) e confirmar mudança automática
4. Navegar por:
   - Editais
   - Cadastros
   - Radar
   - Portais Estratégicos
   - Notícias / Pesquisas
5. Abrir modais:
   - Configurações
   - Pré-cadastro (verificar se o modal mantém legibilidade; sem alterar PDF)

## Próximos passos (Fase 2 sugerida)

- Ver documentação dedicada: [`DARK_MODE_PHASE2.md`](./DARK_MODE_PHASE2.md) (dashboard, filtros, cards Editais, tokens adicionais).
- Migrar gradualmente mais blocos do `global.css` de `--bg-white/--text-dark/--border-light` para `--color-*`.
- Padronizar botões, tabelas e sidebars com tokens.
- Reduzir cores hardcoded em cards e estados vazios.
- Criar pequenos “snapshots” de regressão visual (checklist + screenshots) para temas light/dark.

