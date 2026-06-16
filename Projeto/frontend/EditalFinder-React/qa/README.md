# QA — EditalFinder (DESKTOP QA 1.0)

Bateria de testes em camadas para Web e Desktop/EXE (Tauri).

## Camadas

| Camada | Ferramenta | O que cobre | Obrigatório |
| ------ | ---------- | ----------- | ----------- |
| A | `node --test` | Unit/integration (helpers de URL, badges, dashboard, reporte, QA utils) | Sim (`npm test`) |
| B | Playwright | Web E2E (rotas, botões, detalhe, Grants.gov, reporte) | Opt-in |
| C | tauri-driver/WebDriver | Desktop E2E | Documentado, não configurado |
| D | pywinauto (Windows) | Smoke do EXE (janela, screenshots) | Opt-in |

## Camada A — unit tests

```bash
npm test
```

## Camada B — Playwright (Web E2E)

```bash
# 1) instalar (uma vez)
npm run e2e:install        # = npm i -D @playwright/test && npx playwright install chromium

# 2) gerar build + rodar (o config sobe o preview automaticamente)
npm run build
npm run e2e

# relatório HTML
npm run e2e:report
```

Variáveis úteis:

- `QA_BASE_URL` — base URL (default `http://localhost:4173`).
- `QA_NO_WEBSERVER=1` — não sobe o preview (use um server já rodando).
- `QA_DETAIL_SAMPLE=10` — quantos cards o teste de detalhe abre.

Artefatos: `qa/artifacts/playwright/` (json, html, traces, screenshots).

## Camada C — Desktop E2E (tauri-driver) — NÃO configurado

Requer Rust/Cargo e `tauri-driver` + Microsoft Edge WebDriver (`msedgedriver`).

```bash
cargo install tauri-driver --locked
# baixar msedgedriver compatível com a versão do Edge/WebView2 instalado
```

Não foi configurado neste patch por exigir toolchain Rust e versão de
`msedgedriver` casada ao WebView2 do ambiente. Ver doc do patch para o porquê.

## Camada D — pywinauto (Windows, opcional)

```powershell
python -m venv .venv-qa
.\.venv-qa\Scripts\Activate.ps1
pip install -r qa/requirements.txt
python qa/windows_desktop_smoke.py --exe "src-tauri/target/release/editalfinder.exe"
```

Limitação conhecida: o conteúdo roda em WebView2 e normalmente não é exposto à
UI Automation nativa — a verificação textual pode ser inconclusiva. O script
captura screenshots e gera `qa/artifacts/windows/desktop_smoke_report.{json,md}`.

## Instrumentação dev de QA (gated, sem segredos)

Habilite no console/localStorage (ou via env Vite):

```js
localStorage.setItem('EDITALFINDER_DEBUG_EXTERNAL_LINKS', '1'); // logs de URL externa
localStorage.setItem('EDITALFINDER_DEBUG_ROUTES', '1');         // logs de rota
localStorage.setItem('EDITALFINDER_DEBUG_DATA_COUNTS', '1');    // contagens
```

Env (build): `VITE_DEBUG_EXTERNAL_LINKS=1`, `VITE_DEBUG_ROUTES=1`, `VITE_DEBUG_DATA_COUNTS=1`.
