# DESKTOP QA 1.0 — Automated + Semi-Automated EXE Smoke Test Harness

## Objetivo

Criar uma frente de QA em camadas (Web + Desktop/EXE Tauri) para encontrar bugs
reais de navegação, carregamento, botões, links externos, detalhe de edital e
reporte — registrando evidências e relatórios. Sem alterar Supabase/RLS, sem apply
backend, sem `service_role` no frontend, sem deletar registros.

## Estratégia escolhida

Pirâmide pragmática:

- **Camada A (base, obrigatória):** unit/integration via `node --test`. Cobre a
  lógica pura de seleção de URL, badges, dashboard count e reporte. Roda em `npm test`.
- **Camada B (Web E2E, opt-in):** Playwright dirige o build web (preview do Vite),
  exercitando rotas/botões reais com `data-testid` estáveis. É onde os bugs de
  navegação/detalhe/links aparecem de forma reproduzível.
- **Camada C (Desktop E2E):** tauri-driver/WebDriver — **documentado, não configurado**
  (justificativa abaixo).
- **Camada D (Windows fallback, opt-in):** pywinauto abre o EXE, valida janela e
  captura screenshots; sem OCR, sem coordenadas fixas.

A maior parte da cobertura útil mora em A + B: o EXE Tauri usa exatamente o mesmo
bundle web, então um bug de navegação/detalhe/link reproduzível no Web E2E também
existe no EXE. As camadas C/D servem para validar o "container" desktop (janela,
abertura, integração de opener), não a lógica de UI.

## Ferramentas

| Ferramenta | Uso | Decisão |
| ---------- | --- | ------- |
| `node --test` | Camada A | **Usada** (já é o runner do projeto) |
| `@playwright/test` | Camada B | **Configurada (opt-in)**; instalação dev sob demanda para não pesar o `npm test` |
| `tauri-driver` + `msedgedriver` | Camada C | **Não usada agora** — exige Rust/Cargo e `msedgedriver` casado à versão do WebView2; alto custo de setup para ganho marginal sobre a Camada B |
| `pywinauto` (+ `Pillow`, `psutil`) | Camada D | **Configurada (opt-in)**; limitação conhecida com WebView2 |
| OCR | — | **Não usado** (frágil; proibido como base) |

## Como rodar

```bash
# Camada A (obrigatória)
npm test

# Camada B (Web E2E) — opt-in
npm run e2e:install            # npm i -D @playwright/test && npx playwright install chromium
npm run build
npm run e2e                    # config sobe o preview automaticamente
npm run e2e:report            # relatório HTML

# Camada D (Windows fallback) — opt-in
python -m venv .venv-qa
.\.venv-qa\Scripts\Activate.ps1
pip install -r qa/requirements.txt
python qa/windows_desktop_smoke.py --exe "src-tauri/target/release/editalfinder.exe"
```

Instrumentação dev (gated, sem segredos):
`localStorage` `EDITALFINDER_DEBUG_EXTERNAL_LINKS`/`EDITALFINDER_DEBUG_ROUTES`/`EDITALFINDER_DEBUG_DATA_COUNTS`
ou env Vite `VITE_DEBUG_EXTERNAL_LINKS` / `VITE_DEBUG_ROUTES` / `VITE_DEBUG_DATA_COUNTS`.

## Fluxos testados (matriz)

Fonte única: `src/utils/qa/smokeFlows.js`.

| id | rota | prioridade | verificação |
| --- | ---- | ---------- | ----------- |
| dashboard-load | `/` | P0 | mostra "Dashboard", atualiza, sem erro fatal, sem "Editais monitorados" (FRONTEND 1.1H) |
| editais-list-load | `/editais` | P0 | "Mostrando X de Y recebidos", sem erro fatal |
| open-first-edital-detail | `/editais` → detalhe | P1 | abre primeiros N cards, falha se "Não foi possível carregar os dados do edital" |
| report-problem-opens | `/` | P1 | modal abre com ambiente + orientação print/detalhes |
| grants-links | `/editais` | P1 | nenhuma URL externa aponta para page-not-found |

## Bug A — detalhe interno não carrega

**Diagnóstico (causa-raiz provável):**

A lista (`/editais`) é carregada de `dataService.getEditais()` → **view** `vw_editais_front`
(~1051 linhas, `SECURITY DEFINER`). Já o detalhe (`EditalDetalhes.jsx`) chama:

```12:13:src/services/dataService.js
async getEditalById(idEdital) {
  ... .from('edital').select('*').eq('id_edital', idEdital).single();
```

Ou seja, lê a **tabela base** `edital` com `.single()`, e em paralelo
`getAnexosByEdital` (tabela `edital_anexo`). `.single()` lança se vier **0 linhas**
(ou mais de 1); `Promise.all` rejeita se **qualquer** das duas consultas falhar.
Logo, basta:

1. um `id_edital` presente na view mas que retorne 0 linhas no SELECT base
   (divergência view × base, ou linha inacessível por RLS na base), **ou**
2. erro de policy/RLS em `edital_anexo`,

para cair no `catch` → "Não foi possível carregar os dados do edital." Isso explica
por que **alguns** detalhes falham e outros não.

**Correção recomendada (patch separado, frontend-only, baixo risco):**

- Trocar `.single()` por `.maybeSingle()` em `getEditalById` (0 linhas → `null` →
  "Edital não encontrado" em vez da mensagem fatal);
- Desacoplar `getEditalById` de `getAnexosByEdital` (usar `Promise.allSettled`),
  para que uma falha de anexos não zere a página inteira.

Não aplicado aqui por ser correção de comportamento (escopo do harness é detectar +
documentar). Sugerido: **FRONTEND 1.1F-DETALHE**.

## Bug B — Grants.gov page-not-found

**Diagnóstico:** o resolvedor de link (`actionUrlResolver.js`) usa o primeiro campo
de link disponível sem canonicalizar Grants.gov. Quando o `link` armazenado é um
`simpler.grants.gov/opportunity/<id>`, `view-opportunity/<id>` ou um
`page-not-found`, o botão abre uma URL quebrada.

**Entregue:** `src/utils/edital/officialEditalUrl.js` — `getOfficialEditalUrl(item)`:

- usa `link` canônico `search-results-detail/<id>` quando válido;
- **nunca** escolhe `page-not-found`/`/404`;
- normaliza `simpler.grants.gov/opportunity/<id>`, `view-opportunity/<id>` e
  `?oppId=<id>` → `https://www.grants.gov/search-results-detail/<id>`;
- constrói canônico a partir de `extras.grants_opportunity_id`;
- fallback para busca do Grants.gov (nunca page-not-found).

Coberto por `officialEditalUrl.test.js`. **Integração nos botões** (`EditalCard`,
`EditalDetalhes`) recomendada em patch separado para evitar mudança ampla de
comportamento sem revisão — sugerido **FRONTEND 1.1G-GRANTS-LINKS**.

Instrumentação: `src/utils/qa/externalLinkDebug.js` loga
`[EditalFinder][ExternalLinkDebug] { title, fonte, chosenUrl, fieldUsed, flags }`
quando `VITE_DEBUG_EXTERNAL_LINKS=1` ou localStorage. O spec
`tests/e2e/grants-links.spec.js` captura as URLs sem abrir o navegador.

## Bug C — cadastro / policy (RLS)

**Não reproduzido neste patch** (exige login admin + escrita real, e não usamos
`service_role` no frontend). Recomendação: teste de diagnóstico com **mock** do
insert retornando erro RLS, validando que a tela: não quebra, não limpa o
formulário, mostra mensagem amigável, salva rascunho local, habilita reporte com
metadata (`errorKind`, `operation`, `table`, `route`) **sem tokens**. Sugerido
**FRONTEND 1.1F**.

## Bug D — reporte: print/detalhes

**Corrigido.** Orientação por runtime:

- Desktop/EXE: "De preferência, anexe uma foto/print da tela no e-mail…";
- Web: "De preferência, descreva o problema com o máximo de detalhes…";
- Corpo do e-mail inclui a linha combinada (print + descrição).

Arquivo: `src/utils/feedback/appFeedbackGuidance.js`; integrado em
`AppFeedbackModal.jsx` e `EditalFeedbackModal.jsx`; linha adicionada em
`buildSupportEmailBody`.

## Evidências coletadas

- Camada A: 186/186 testes (`npm test`).
- Camada B: artefatos em `qa/artifacts/playwright/` (json/html/traces/screenshots)
  + anexos `broken-details.json` e `external-urls.json` por teste.
- Camada D: `qa/artifacts/windows/desktop_smoke_report.{json,md}` + screenshots.

## Limitações

- WebView2 não expõe DOM à UI Automation → Camada D é screenshot/janela, não texto.
- Camada B exige instalação do Playwright (download de browser) — opt-in.
- Camada C não configurada (custo de toolchain Rust + msedgedriver).
- Bug C não reproduzido sem credenciais/escrita.

## Próximos patches recomendados (ordem)

1. **FRONTEND 1.1F-DETALHE** — `.maybeSingle()` + `Promise.allSettled` no detalhe (Bug A).
2. **FRONTEND 1.1G-GRANTS-LINKS** — integrar `getOfficialEditalUrl` nos botões (Bug B).
3. **FRONTEND 1.1F** — tratamento de erro de cadastro/RLS + rascunho local + reporte (Bug C).
4. **QA 1.1** — rodar Playwright no CI (headless) com matriz P0/P1.
5. **QA 1.2** — avaliar tauri-driver para validar o opener externo no EXE.
