# EditalFinder — App desktop Windows (Tauri)

Versão desktop do frontend React em uma janela própria. **Não é offline**: login, editais e demais dados continuam via internet (Supabase), como na versão web.

## Requisitos

| Ferramenta | Uso |
|------------|-----|
| Node.js 18+ | `npm install`, Vite, CLI Tauri |
| Rust (rustup) | Compilar o shell desktop |
| WebView2 | Já presente no Windows 10/11 recentes |

Instalar Rust: https://rustup.rs/

## Estrutura

```
frontend/EditalFinder-React/
  src-tauri/           # Projeto Rust + tauri.conf.json
  src-tauri/tauri.conf.json
  src-tauri/src/main.rs
  src-tauri/Cargo.toml
  vite.config.js       # base `/` quando TAURI_ENV_PLATFORM está definido
  src/config/routerBase.js
```

A versão **web** (`npm run build` / GitHub Pages) mantém `base: /editalfinder/`. O Tauri define `TAURI_ENV_PLATFORM` e o Vite usa `base: /` e Router sem basename.

## Variáveis de ambiente

Copie `.env.example` → `.env.local` (nunca commite `.env.local`).

| Variável | Desktop |
|----------|---------|
| `VITE_SUPABASE_URL` | Obrigatória (mesma da web) |
| `VITE_SUPABASE_ANON_KEY` | Obrigatória — **somente chave anon** |
| `VITE_PUBLIC_SITE_URL` | Em `desktop:dev`: `http://localhost:5173` |
| `VITE_AUTH_CALLBACK_URL` | Em `desktop:dev`: `http://localhost:5173/auth/callback` |

**Não usar** `service_role` no frontend nem embutir secrets no instalador.

No Supabase → **Authentication → URL Configuration**, inclua as URLs de redirect usadas no desktop (dev e, após instalar, a origem da janela Tauri + `/auth/callback`).

## Desenvolvimento (janela + hot reload)

```bash
cd frontend/EditalFinder-React
npm install
npm run desktop:dev
```

Isso executa `npm run dev` (Vite) e abre a janela apontando para `http://localhost:5173/`.

Scripts npm:

| Script | Função |
|--------|--------|
| `npm run dev` | Só frontend web (`/editalfinder/`) |
| `npm run build` | Build web para deploy |
| `npm run desktop:dev` | `tauri dev` |
| `npm run desktop:build` | `tauri build` (gera instalador) |
| `npm run desktop:release` | `desktop:build` + copia para `/releases` (ver `DESKTOP_RELEASE_PROCESS.md`) |

## Release para cliente (Desktop 2)

Após o build, copiar artefatos padronizados para a pasta `releases/` na raiz do repositório:

```bash
npm run desktop:release
# ou: npm run desktop:build && python ../../scripts/create_desktop_release.py
```

Detalhes: `docs/DESKTOP_RELEASE_PROCESS.md`, checklist em `docs/DESKTOP_RELEASE_CHECKLIST.md`.

## Gerar .exe / instalador Windows

```bash
cd frontend/EditalFinder-React
npm run desktop:build
```

Primeira execução pode demorar (download de crates Rust).

### Onde ficam os artefatos

| Artefato | Caminho típico |
|----------|----------------|
| Executável debug | `src-tauri/target/debug/editalfinder.exe` |
| Executável release | `src-tauri/target/release/editalfinder.exe` |
| Instalador NSIS | `src-tauri/target/release/bundle/nsis/EditalFinder_0.1.0_x64-setup.exe` |

Distribua o **setup.exe** NSIS para usuários que preferem instalador, ou o `.exe` em `target/release/` para uso direto (sem installer).

## O que não commitar

- `src-tauri/target/` (build Rust)
- `dist/` (build Vite)
- `*.msi`, instaladores `.exe` gerados
- `.env`, `.env.local`

**Versionar** `src-tauri/tauri.conf.json`, `Cargo.toml`, `src/`, `capabilities/`, ícones em `src-tauri/icons/`.

## Ícone do app

Ícones padrão em `src-tauri/icons/`. Para substituir pelo logo oficial:

```bash
npx tauri icon caminho/para/logo-1024.png
```

## Validação sugerida

1. `npm run build` — build web inalterado (`/editalfinder/`).
2. `npm run desktop:dev` — janela abre, login, Dashboard, menu ☰, Ajuda, Reportar problema, Workspace do Consultor.
3. `/workspace-cientifico` → redirect `/dashboard`.
4. `npm run desktop:build` — gera instalador sem erro.

## Limitações

- App **depende de internet** (API Supabase e links externos).
- Versão web em produção **permanece**; desktop é canal extra.
- Backend/schema **não** são alterados por este empacotamento.

## Referência

Documentação Tauri: https://tauri.app/
