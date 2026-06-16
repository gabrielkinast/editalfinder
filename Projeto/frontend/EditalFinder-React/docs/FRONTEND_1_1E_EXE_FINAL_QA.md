# FRONTEND 1.1E — QA final e checklist de release (EXE)

Rodada de estabilização após os patches 1.1A–1.1D. **Sem features novas** — apenas validação automatizada, auditoria de código e checklist para teste manual no instalador.

---

## Patches validados

| Patch | Escopo | Evidência automatizada |
|-------|--------|------------------------|
| **1.1A** | Links externos / Tauri opener | `externalActions.test.js` (normalize, resolve URLs); `openExternalUrl.js` usa `@tauri-apps/plugin-opener` no runtime desktop |
| **1.1B** | Formulário admin alinhado ao schema | `buildEditalWritePayload.test.js` — sem `organizacao_responsavel`, `id_organizacao` opcional |
| **1.1C** | Reportar problema resiliente | `appFeedback.test.js`, `appFeedbackSubmitFlow.test.js`, `appFeedbackModuleImports.test.js` |
| **1.1C.4** | Gmail Web Compose | `appFeedbackMailto.test.js` — `buildGmailComposeUrl`, fluxo Gmail → mailto → localStorage |
| **1.1C.5** | Severidade no reporte | `appFeedbackSeverity.test.js`, assunto `[EditalFinder][ALTA]…` nos testes mailto |
| **1.1D** | PDF export layout fix | `editaisPdfFormatters.test.js`; `exportEditaisToPdf` com 9 colunas paisagem |

Documentação de referência: `FRONTEND_1_1C_APP_FEEDBACK_RESILIENCE.md`, `FRONTEND_1_1C4_GMAIL_SUPPORT_FEEDBACK.md`, `FRONTEND_1_1C5_REPORT_PROBLEM_SEVERITY.md`, `FRONTEND_1_1D_PDF_EXPORT_LAYOUT_FIX.md`.

---

## Comandos rodados

Diretório: `frontend/EditalFinder-React`

```powershell
cd frontend/EditalFinder-React
npm test
npm run build
npm run build:tauri
npm run desktop:release:quick
npm run lint   # falha pré-existente — ver seção Avisos
```

| Comando | Resultado | Observação |
|---------|-----------|------------|
| `npm test` | **106/106 pass** | ~2,1 s |
| `npm run build` | **✓ built** | 1ª tentativa falhou com `EBUSY` (PDF em `public/docs/` bloqueado); 2ª tentativa OK |
| `npm run build:tauri` | **✓ built** | `dist/index.html` com `./assets/` (paths relativos — OK para EXE) |
| `npm run desktop:release:quick` | **✓ sucesso** | Rust release ~4 min + NSIS; artefatos em `releases/` |
| `npm run lint` | **falha** | Sem `eslint.config.js` (config legada não migrada) |

---

## Resultado dos testes

```
# tests 106
# suites 46
# pass 106
# fail 0
```

Cobertura relevante para release:

- Links externos: `externalActions.test.js`
- Payload admin edital: `buildEditalWritePayload.test.js`
- Feedback + Gmail + severidade: `appFeedback*.test.js`, `appFeedbackMailto.test.js`
- PDF editais: `editaisPdfFormatters.test.js`
- Boot seguro (null context): `appFeedbackModuleImports.test.js`, `mapContextToDefaultTipo(null)`

---

## Resultado do build

### Web (`npm run build`)

- Bundle gerado em `dist/`
- Base path: `/editalfinder/` (deploy GitHub Pages)

### Desktop (`npm run build:tauri` + `tauri build`)

- `HashRouter` + `base: './'` em modo `tauri`
- `beforeBuildCommand`: `npm run build:tauri`
- Binários:
  - `src-tauri/target/release/editalfinder.exe`
  - `src-tauri/target/release/bundle/nsis/EditalFinder_0.1.0_x64-setup.exe`

### Instalador gerado (release)

| Arquivo | Caminho |
|---------|---------|
| **Setup (recomendado)** | `releases/EditalFinder_v0.1.0_Windows_x64_Setup.exe` |
| Portable | `releases/EditalFinder_v0.1.0_Windows_x64_Portable.exe` |
| README | `releases/README_RELEASE_v0.1.0.txt` |
| SHA256 | `releases/SHA256SUMS_v0.1.0.txt` |

**SHA-256 (setup):** `6d1337f41345b8a9db0c3f5309ff50c7f961f1a85fc1abe193a5b834ec4aac07`

---

## Checklist manual (tester)

Marcar ✅ / ❌ / N/A após instalar o Setup em Windows limpo ou VM.

### 1. Startup do EXE

- [ ] App abre sem tela branca/azul vazia
- [ ] Login ou dashboard renderiza
- [ ] DevTools (F12 no EXE): sem `TypeError` / `ReferenceError` fatal no boot
- [ ] Sem `Cannot read properties of null`
- [ ] Sem erro de import/export no console

### 2. Links externos (navegador padrão via Tauri)

Pontos de código: `EditalCard`, `EditalDetailsModal`, `EditalDetalhes`, `CardEditalRadar`, `ConcursoCard`, `PortalEstrategicoCard`, `AdminTable`.

- [ ] **Editais** — abrir site/link do edital
- [ ] **Editais** — abrir PDF
- [ ] **Editais** — abrir inscrição
- [ ] **Detalhe do edital** — PDF / anexos / site
- [ ] **Radar de Fomento** — inscrição, PDF, site
- [ ] **Concursos** — edital/link
- [ ] **Portais** — abrir portal

### 3. Cadastro de edital (admin)

- [ ] Cadastros → Editais → Novo edital
- [ ] Salvar **sem** organização (`id_organizacao` vazio)
- [ ] `orgao_responsavel` opcional
- [ ] `link` obrigatório — validação impede salvar sem link
- [ ] Sem erro PGRST205 (coluna inexistente)
- [ ] Editar edital existente

### 4. Reportar problema

- [ ] Modal abre e fecha várias vezes sem quebrar app
- [ ] Tipos de problema listados (incl. **Desktop/EXE**)
- [ ] Severidade visível; default **Média**
- [ ] Enviar abre **Gmail** no navegador padrão
- [ ] Destinatário: `Suporte.EditalFinder@gmail.com`
- [ ] Assunto: `[EditalFinder][…]` + severidade + tipo + rota
- [ ] Corpo: descrição, rota, ambiente `Desktop/EXE (Tauri)`, contexto
- [ ] Se Gmail falhar: fallback mailto ou salvamento `localStorage` + painel manual

### 5. Exportação PDF

- [ ] Editais sem filtro → PDF paisagem, tabela alinhada (9 colunas)
- [ ] Editais com filtro → cabeçalho mostra resumo de filtros
- [ ] Poucos registros (1–10) e muitos (50+)
- [ ] Título longo truncado, layout estável
- [ ] Rodapé: `Gerado pelo EditalFinder` + `Página X de Y`
- [ ] **XLSX** de editais continua OK
- [ ] **PDF de notícias** (`FeedListaPage`) continua OK

### 6. Notícias / Pesquisas / Concursos

- [ ] Listagens carregam
- [ ] Filtros básicos respondem
- [ ] Exportações existentes funcionam
- [ ] Nenhuma tela branca

### 7. Console — erros a evitar

- [ ] Sem `TypeError` / `ReferenceError` bloqueando UI
- [ ] Sem `Failed to fetch module` / import quebrado
- [ ] Sem `Cannot read properties of null/undefined` em loop
- [ ] Erros Supabase isolados (toast/alert) não derrubam o app

---

## Bugs encontrados

| ID | Severidade | Descrição | Status |
|----|------------|-----------|--------|
| QA-01 | Baixa | `npm run lint` falha — falta `eslint.config.js` (ESLint 9) | **Documentado** — pré-existente, fora do escopo |
| QA-02 | Baixa | `npm run build` pode falhar com `EBUSY` se `public/docs/formulario-apresentacao-projeto-referencia.pdf` estiver aberto em outro processo | **Workaround:** fechar PDF e repetir build |
| QA-03 | Info | Vite: chunk principal > 500 kB e `INEFFECTIVE_DYNAMIC_IMPORT` em `api.js` | **Documentado** — warning, não bloqueia release |
| QA-04 | — | Regressões em fluxos EXE (links, PDF, cadastro, feedback) | **Pendente validação manual** pelo tester |

Nenhuma regressão confirmada por testes automatizados nesta rodada.

---

## Bugs corrigidos nesta rodada (1.1E)

Nenhum — QA não encontrou defeito de código que exigisse patch adicional. Correções já estavam nos patches 1.1A–1.1D.

---

## Bugs restantes / limitações

1. **Validação EXE interativa** depende do checklist manual acima.
2. **ESLint** não configurado para v9 flat config.
3. **Instalador sem assinatura digital** — Windows SmartScreen pode alertar (ver `README_RELEASE`).
4. **PDF de editais** não inclui URLs longas na tabela (by design 1.1D); usar XLSX para links completos.
5. **Internet obrigatória** para Supabase e abertura de links.

---

## Como gerar o instalador

```powershell
cd frontend/EditalFinder-React

# Completo (testes + build + release):
npm run desktop:release

# Rápido (sem testes — usado nesta QA):
npm run desktop:release:quick
```

Pré-requisitos: Node.js, Rust toolchain, Tauri CLI, NSIS (instalado pelo Tauri no Windows).

Saída copiada automaticamente para `releases/` pelo script `scripts/create_desktop_release.py`.

---

## Instruções para o tester validar

1. Baixar/copiar `releases/EditalFinder_v0.1.0_Windows_x64_Setup.exe`.
2. (Opcional) Verificar hash com `SHA256SUMS_v0.1.0.txt`.
3. Instalar com internet ativa.
4. Abrir o app, fazer login.
5. Percorrer o **checklist manual** seção por seção.
6. Anotar falhas com: tela, passo, mensagem de console, screenshot.
7. Reportar via **Reportar problema** no próprio app (severidade conforme impacto).

**Contato suporte:** `Suporte.EditalFinder@gmail.com`

---

## Critérios de aceite (automáticos — atendidos)

- [x] `npm test` passa (106/106)
- [x] `npm run build` passa
- [x] `npm run build:tauri` passa
- [x] `npm run desktop:release:quick` gera instalador
- [x] `dist/index.html` usa paths relativos (`./assets/`)
- [x] Documentação criada

## Critérios de aceite (manuais — pendentes tester)

- [ ] EXE abre sem tela vazia
- [ ] Links externos no navegador padrão
- [ ] Cadastro sem organização
- [ ] Gmail no reporte
- [ ] PDF editais legível + XLSX + PDF notícias
- [ ] Sem erro fatal no console

---

*Gerado em: 2026-05-18 — FRONTEND 1.1E QA final*
