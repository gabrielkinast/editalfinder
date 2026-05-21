# Dark mode — tela de Login

## Objetivo

Alinhar a página `/login` ao tema global (`theme-light` / `theme-dark` em `<html>`), usando os tokens `--color-*` já definidos em `global.css`, sem alterar autenticação, `authService`, Supabase ou fluxo de credenciais demo.

## Arquivos alterados

| Arquivo | Alteração |
|---------|-----------|
| `frontend/EditalFinder-React/src/main.jsx` | Chama `applyTheme(getSavedThemePreference())` **antes** do `createRoot(...).render(...)`, evitando um frame inicial com classe de tema errada (login monta antes do `useEffect` do `SettingsProvider`). |
| `frontend/EditalFinder-React/src/styles/global.css` | Bloco **TELA DE LOGIN**: fundo em gradiente com tokens; padrão de grade/ruído em CSS (sem SVG fixo claro); card com `--color-surface`, borda e `--shadow-card`; título com `--color-primary`; subtítulo e demo com `--color-muted` / `--color-text`; botão Entrar com `--color-secondary` e texto escuro fixo para contraste no amarelo; foco de inputs alinhado a `--color-focus-ring`; ajuste global leve em `.form-group input:focus` e `select:focus` para `--color-primary` (beneficia formulários que reutilizam essas classes). |
| `frontend/EditalFinder-React/src/pages/Login.jsx` | Remoção de estilos inline do cabeçalho; classes `login-logo-img`, `logo--with-image` e estrutura inalterada para o form. |

## Como o login usa o tema

1. **Bootstrap:** `main.jsx` lê `localStorage` (`editalfinder.theme`: `light` \| `dark` \| `system`), resolve `system` com `prefers-color-scheme` e aplica `theme-light` ou `theme-dark` no `<html>` imediatamente.
2. **Depois:** `SettingsContext` continua chamando `applyTheme(getSavedThemePreference())` no mount para manter o listener de mudança do tema do sistema quando a preferência é `system` (via `theme.js`).
3. **Visual:** a página de login não lê o contexto de tema; ela herda apenas as variáveis CSS ativas no documento. O card deixa de usar `--bg-white` (sempre branco) e passa a usar `--color-surface`, alinhado a `--color-input-bg` dos campos.

## O que mudou no claro / escuro

### Tema claro

- Fundo: gradiente suave a partir de `--color-bg-page` e `--color-surface-soft` com toque de `--color-primary` via `color-mix` (próximo do visual anterior, sem cinza “morto” fixo).
- Card: superfície branca (`--color-surface`), sombra `--shadow-card`, borda `--color-border`.
- Labels e textos: `--color-text` / `--color-muted`; inputs claros (`--color-input-bg` = branco no `:root`).
- Botão **Entrar**: amarelo de marca (`--color-secondary`) com texto `#1e293b` para leitura estável sobre o amarelo.

### Tema escuro

- Fundo: o mesmo sistema de gradiente lê os valores escuros de `.theme-dark` (`--color-bg-page`, `--color-surface-soft`, etc.), com grade radial discreta em tons do primário/secundário.
- Card: `#111827` / superfície escura coerente com o restante do app, borda `--color-border`.
- Título **Edital Finder** / `logoText`: `--color-primary` (respeita personalização azul em `:root` / tema escuro).
- Subtítulo e bloco **Demo**: `--color-muted`, com `strong` em `--color-text` para destaque discreto.
- Inputs: continuam com `--color-input-bg` e `--color-text` (já corretos no escuro); placeholders com `--color-muted`.

## Limitações

- O botão **Entrar** usa texto na cor fixa `#1e293b` para garantir contraste sobre `--color-secondary` (amarelo); se no futuro o amarelo de marca for alterado para um tom muito claro, pode ser necessário repensar essa cor ou introduzir `--color-on-secondary`.
- O fundo usa `color-mix` e vários gradientes; navegadores muito antigos podem simplificar o degradê (o fundo sólido por token ainda funciona).
- `alert()` em erro de login permanece nativo do navegador (fora do escopo de tema).

## Como testar

1. Limpar cache opcional; abrir `/login`.
2. **Claro:** em Configurações (após login) ou via `localStorage.setItem('editalfinder.theme','light')` + recarregar — card claro, inputs claros, labels escuras, fundo em degradê claro.
3. **Escuro:** `editalfinder.theme` = `dark` — fundo escuro, card escuro, labels claras, inputs escuros coerentes com o card, botão amarelo legível.
4. **Sistema:** `editalfinder.theme` = `system` — alternar o tema do SO e verificar login e, após entrar, que o app continua acompanhando (listener no `SettingsProvider`).
5. Primeiro paint: abrir login com throttling “Slow 3G” no DevTools (opcional) e observar se não há flash longo de tema errado (o bootstrap em `main.jsx` deve minimizar isso).
6. Fluxo: login com credenciais demo inalteradas; redirecionamento ao dashboard intacto.

## Build

Na pasta `frontend/EditalFinder-React`:

```powershell
npm run build
```

**Última execução desta entrega:** `vite build` concluiu com sucesso (~3,6 s). Avisos: chunk JS &gt; 500 kB e timings de plugins CSS (já comuns no projeto), sem falha de compilação.
