# SECURITY 1.2 — Replace XLSX Export Dependency

**Data:** 2026-06-10  
**Escopo:** `frontend/EditalFinder-React`

---

## 1. Motivação

O pacote `xlsx` (SheetJS 0.18.5) permanecia como **única vulnerabilidade** após SECURITY 1.1:

- Prototype Pollution ([GHSA-4r6h-8v6p-xvw6](https://github.com/advisories/GHSA-4r6h-8v6p-xvw6))
- ReDoS ([GHSA-5pgg-2g8v-p4x9](https://github.com/advisories/GHSA-5pgg-2g8v-p4x9))
- **Sem fix** no registry npm público

Uso no projeto: **somente geração** de `.xlsx` no browser (sem import/upload de planilhas).

---

## 2. Substituição

| Antes | Depois |
|-------|--------|
| `xlsx@0.18.5` | **`exceljs@^4.4.0`** |
| `XLSX.utils.json_to_sheet` + `writeFile` | `exportRowsToXlsx()` com dynamic import |

**Override npm** (`package.json`):

```json
"overrides": {
  "uuid": "^11.1.0"
}
```

Mitiga advisory moderada em `uuid` (transitiva do exceljs) sem `npm audit fix --force`.

---

## 3. Arquitetura

### Módulo central

`src/utils/export/spreadsheetExport.js`

| Export | Função |
|--------|--------|
| `sanitizeSpreadsheetCell(value)` | Mitiga formula injection; null → `''` |
| `sanitizeExportRows(rows, columns?)` | Sanitiza linhas preservando ordem de colunas |
| `exportRowsToXlsx(rows, options)` | Gera `.xlsx` e dispara download no browser |

### Telas atualizadas

| Arquivo | Comportamento |
|---------|---------------|
| `src/pages/EditaisPage.jsx` | Export mantém colunas (Título, Status, Status Detalhado, Fonte, prazo, link, etc.) |
| `src/pages/FeedListaPage.jsx` | Export de feeds com mesmas colunas anteriores |

Botão `editais-export-xlsx` e nomes de arquivo equivalentes preservados.

---

## 4. Mitigação formula injection

Strings que começam com `=`, `+`, `-` ou `@` recebem prefixo `'` (apóstrofo Excel).

- Números reais (ex.: `-10`) permanecem numéricos.
- Strings textuais `-10` viram `'`-10`.
- Caracteres de controle removidos.
- Células truncadas em 32.000 caracteres.

Testes: `src/utils/export/spreadsheetExport.test.js` (11 casos).

---

## 5. Resultado `npm audit`

| Comando | Resultado |
|---------|-----------|
| `npm ls xlsx` | *(empty)* — não instalado |
| `npm audit` | **0 vulnerabilities** |
| `npm audit --omit=dev` | **0 vulnerabilities** |

---

## 6. QA pós-patch

| Comando | Resultado |
|---------|-----------|
| `npm test` | **301 passed** |
| `npm run build` | OK |
| `npm run qa:local` (sem credenciais) | OK — E2E 5 passed / 13 skipped |
| `npm run qa:local` (com credenciais) | OK — E2E **18 passed / 1 skipped** |

Export PDF, filtros e E2E de download XLSX (`editais-export.spec.js`) inalterados em comportamento.

---

## 7. Limitações

- `exceljs` aumenta o bundle (carregado via **dynamic import** apenas no export).
- Dependências legadas do exceljs (archiver, etc.) — mitigadas com override de `uuid`.
- Geração XLSX não validada byte-a-byte em unit test; cobertura via sanitização + E2E download.

---

## 8. Próximo patch recomendado

Monitorar releases do `exceljs` e remover override de `uuid` quando upstream atualizar. Opcional: chunk dedicado no Vite para lazy-load do export.

## Referências

- `docs/SECURITY_1_1_FRONTEND_DEPENDENCY_AUDIT.md`
- `docs/QA_AUTOMATION_GUIDE.md`
