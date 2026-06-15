# Releases — EditalFinder Desktop (Windows)

Pasta para **distribuição manual** dos instaladores gerados localmente.

## Uso

1. Gere o build com `npm run desktop:build` ou `npm run desktop:release` em `frontend/EditalFinder-React`.
2. O script `scripts/create_desktop_release.py` copia os artefatos para aqui com nome padronizado.
3. Envie ao cliente o arquivo `EditalFinder_v{versão}_Windows_x64_Setup.exe` (recomendado).

## Instalador recomendado

Use o **setup NSIS** (`*_Setup.exe`), não apenas o `.exe` solto, para usuários finais — inclui atalho e desinstalação pelo Painel de Controle.

## O que não commitar

Estes arquivos ficam no `.gitignore` e **não** devem ir para o Git:

- `*.exe`
- `*.msi`
- `*.zip` / `*.7z`
- `*.blockmap`
- `README_RELEASE_*.txt` e `SHA256SUMS_*.txt` gerados por release (opcional local; também ignorados se copiados aqui)

Mantemos versionados apenas este `README.md` e `.gitkeep`.

## Atualização

Sem auto-update: cada versão nova exige novo instalador e reinstalação (ou instalação por cima do setup NSIS). Ver `docs/DESKTOP_RELEASE_PROCESS.md`.
