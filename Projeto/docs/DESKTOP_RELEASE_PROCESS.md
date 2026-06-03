# Processo de release — EditalFinder Desktop (Windows)

Fluxo **manual** para gerar e distribuir o instalador Tauri. Auto-update não está implementado (ver `DESKTOP_AUTO_UPDATE_PLAN.md`).

## Versão canônica

A versão do release vem de **`frontend/EditalFinder-React/src-tauri/tauri.conf.json`** (`version`).

Antes de cada release:

1. Atualize `version` em `tauri.conf.json` (ex.: `0.1.0` → `0.1.1`).
2. Alinhe `package.json` do frontend (campo `version`) ao mesmo valor.
3. A UI exibe a versão via `VITE_APP_VERSION` (injetada no build a partir do `tauri.conf.json`).

## Variáveis de ambiente (build de produção)

Use `.env.production` ou `.env.local` **apenas na máquina de build** (nunca commitar):

| Variável | Regra |
|----------|--------|
| `VITE_SUPABASE_URL` | URL do projeto correto |
| `VITE_SUPABASE_ANON_KEY` | **Somente** chave anon/public |
| `VITE_ENABLE_CONSULTOR_WORKSPACE` | `true` para clientes com Workspace |
| `VITE_PUBLIC_SITE_URL` / `VITE_AUTH_CALLBACK_URL` | Conforme ambiente desktop (ver `DESKTOP_APP_WINDOWS.md`) |

**Nunca** `service_role` no frontend.

## Comandos

```bash
cd frontend/EditalFinder-React

# Validar build web (GitHub Pages)
npm run build

# Release completo: compila + copia para /releases
npm run desktop:release
```

Ou em duas etapas:

```bash
npm run desktop:build
python ../../scripts/create_desktop_release.py
```

## Artefatos em `/releases`

| Arquivo | Descrição |
|---------|-----------|
| `EditalFinder_v{X}_Windows_x64_Setup.exe` | **Recomendado** para o cliente (NSIS) |
| `EditalFinder_v{X}_Windows_x64_Portable.exe` | Opcional, se existir após build |
| `README_RELEASE_v{X}.txt` | Instruções para o cliente |
| `SHA256SUMS_v{X}.txt` | Hashes para verificação |

Binários **não** vão para o Git (ver `.gitignore` na raiz).

## Testar antes de enviar

Siga `DESKTOP_RELEASE_CHECKLIST.md` — instalar em máquina limpa ou perfil de teste, login, Dashboard, Ajuda, Workspace do Consultor, etc.

## Distribuição ao cliente

1. Envie o **Setup.exe** (e opcionalmente `README_RELEASE` + `SHA256SUMS`).
2. Informe que é necessário **internet**.
3. Avise que **não há atualização automática**: nova versão = novo instalador e reinstalação (ou instalar por cima com o NSIS).

## Aviso de segurança Windows

Instaladores sem assinatura digital podem exibir SmartScreen. Isso é esperado até contratar certificado de código (futuro).

## Referências

- `docs/DESKTOP_APP_WINDOWS.md` — dev e build Tauri
- `releases/README.md` — pasta de distribuição
- `docs/DESKTOP_RELEASE_CHECKLIST.md` — checklist QA
