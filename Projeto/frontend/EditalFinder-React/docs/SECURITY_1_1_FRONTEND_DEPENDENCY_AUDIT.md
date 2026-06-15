# SECURITY 1.1 — Frontend Dependency Audit and Safe Fixes

**Data:** 2026-06-10  
**Escopo:** `frontend/EditalFinder-React`

---

## 1. Resumo

| Métrica | Antes | Depois |
|---------|------:|-------:|
| Total (`npm audit`) | 9 (4 moderate, 5 high) | **1 high** |
| Produção (`npm audit --omit=dev`) | 5 (2 moderate, 3 high) | **1 high** |
| Correção | — | `npm audit fix` (sem `--force`) |
| Remanescente | — | `xlsx` (sem fix no npm) |

Artefatos: `qa/artifacts/npm_audit_before.json`, `qa/artifacts/npm_audit_after.json`.

---

## 2. Tabela de vulnerabilidades (antes)

| Severidade | Pacote | Origem | Runtime/Dev | Fix disponível | Ação |
|------------|--------|--------|-------------|----------------|------|
| moderate | brace-expansion | `eslint` → `minimatch` | Dev (transitiva) | Sim (patch) | `npm audit fix` → 1.1.15 |
| moderate | dompurify | `jspdf` | Runtime (transitiva) | Sim (patch) | `npm audit fix` → 3.4.10 |
| high | picomatch | `vite`, `tinyglobby`/`fdir` | Dev (transitiva) | Sim (patch) | `npm audit fix` → 4.0.4 |
| moderate | postcss | `vite` | Dev (transitiva) | Sim (patch) | `npm audit fix` → 8.5.15 |
| high | react-router | `react-router-dom` (direto) | Runtime | Sim (minor) | `npm audit fix` → 7.17.0 |
| high | react-router-dom | dependência direta | Runtime | Sim (minor) | `npm audit fix` → 7.17.0 |
| high | vite | dependência direta | Dev | Sim (patch) | `npm audit fix` → 8.0.16 |
| moderate | ws | `@supabase/realtime-js` | Runtime (transitiva) | Sim (patch) | `npm audit fix` → 8.21.0 |
| high | xlsx | dependência direta | Runtime | **Não** | Documentar + SECURITY 1.2 |

---

## 3. Correções aplicadas

```powershell
npm audit fix   # sem --force
```

- **14 pacotes** atualizados no `package-lock.json` (1 removido).
- `package.json`: floors de `react-router-dom` (^7.17.0) e `vite` (^8.0.16).
- **`npm audit fix --force` não foi usado.**

### Versões resolvidas (pós-fix)

| Pacote | Antes (aprox.) | Depois |
|--------|----------------|--------|
| brace-expansion | &lt;1.1.13 | 1.1.15 |
| dompurify | ≤3.3.3 | 3.4.10 |
| picomatch | 4.0.0–4.0.3 | 4.0.4 |
| postcss | &lt;8.5.10 | 8.5.15 |
| react-router / react-router-dom | 7.13.x | 7.17.0 |
| vite | 8.0.0–8.0.4 | 8.0.16 |
| ws | 8.0.0–8.20.0 | 8.21.0 |

---

## 4. Caso `xlsx` — risco remanescente

### Advisories

- [GHSA-4r6h-8v6p-xvw6](https://github.com/advisories/GHSA-4r6h-8v6p-xvw6) — Prototype Pollution
- [GHSA-5pgg-2g8v-p4x9](https://github.com/advisories/GHSA-5pgg-2g8v-p4x9) — ReDoS

**npm:** `No fix available` (pacote `xlsx@0.18.5` no registry público).

### Onde o projeto usa `xlsx`

| Arquivo | Uso |
|---------|-----|
| `src/pages/EditaisPage.jsx` | Exportação XLSX do catálogo de editais (`json_to_sheet` + `writeFile`) |
| `src/pages/FeedListaPage.jsx` | Exportação XLSX de feeds/listas (`json_to_sheet` + `writeFile`) |

**Não há** importação/parsing de arquivos XLSX enviados por usuários — apenas **geração** no browser.

### Fonte dos dados exportados

- Catálogo carregado via Supabase/API (dados controlados pelo app).
- Campos mapeados explicitamente (título, status, links, etc.) a partir de objetos já normalizados no frontend.
- Não é input arbitrário de planilha externa.

### Mitigação temporária (SECURITY 1.1)

1. **Não importar** XLSX de usuários (não implementado hoje).
2. **Somente export** com `XLSX.utils.json_to_sheet` + `writeFile`.
3. Dados originados do catálogo autenticado / feeds internos.
4. Risco de Prototype Pollution/ReDoS é **baixo no fluxo atual** (write-only, browser, sem parse de arquivo hostil).
5. Vulnerabilidades de **dev server** (vite) mitigadas pelo fix; `xlsx` não afeta CI build além do bundle estático.

### Recomendação — patch futuro

**SECURITY 1.2 — Replace xlsx export dependency**

Caminhos possíveis:

| Opção | Prós | Contras |
|-------|------|---------|
| `exceljs` ou lib mantida | Geração XLSX ativa, CVEs rastreáveis | Migração de API, tamanho do bundle |
| CSV seguro temporário | Simples, baixo risco | Perde formato `.xlsx` |
| Manter `xlsx` + mitigação | Zero churn agora | Advisory permanece no `npm audit` |

**Neste patch:** export XLSX **mantido**; sem remoção.

---

## 5. QA pós-fix

| Comando | Resultado |
|---------|-----------|
| `npm test` | 290 passed |
| `npm run build` | OK |
| `npm run qa:local` (sem credenciais) | OK — E2E 5 passed / 13 skipped |
| `npm run qa:local` (com credenciais) | OK — E2E **18 passed / 1 skipped** |

Único skip com credenciais: escrita opt-in Cadastros (`E2E_ALLOW_WRITE_TESTS`).

---

## 6. `npm audit` após correção (SECURITY 1.1)

```txt
1 high severity vulnerability — xlsx (no fix available)
```

`npm audit --omit=dev`: idem — apenas `xlsx`.

**Atualização SECURITY 1.2:** `xlsx` removido; `npm audit` → **0 vulnerabilities**.

---

## 7. Próximo patch recomendado

**SECURITY 1.2** — concluído. Ver `docs/SECURITY_1_2_REPLACE_XLSX_EXPORT_DEPENDENCY.md`.

## Referências

- `docs/QA_AUTOMATION_GUIDE.md`
- `docs/QA_1_3B_GITHUB_ACTIONS_CI.md`
- `docs/SECURITY_1_2_REPLACE_XLSX_EXPORT_DEPENDENCY.md`
- Advisories npm / GitHub Security Advisories (links acima)
