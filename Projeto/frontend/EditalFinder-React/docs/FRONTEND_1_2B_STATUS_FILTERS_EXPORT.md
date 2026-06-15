# FRONTEND 1.2B — Status Filters + Export Status Column

**Data:** 2026-06-10  
**Pré-requisito:** FRONTEND 1.2A (badges), FRONTEND 10.3C (duplicatas ocultas).

---

## 1. Objetivo

Permitir filtrar editais por status/validade semântico na aba Editais e incluir o status nas exportações PDF e XLSX, reutilizando a lógica central de `editalStatusBadges.js` sem duplicar regras.

## 2. Status disponíveis (filtro sidebar)

| Chave | Label |
|-------|-------|
| `aberto` | Aberto |
| `vencendo_7` | Vencendo em 7 dias |
| `vencendo_30` | Vencendo em 30 dias |
| `encerrado` | Encerrado |
| `sem_prazo` | Sem prazo |
| `prazo_em_pdf_ou_detalhe` | Prazo em PDF/detalhe |
| `prazo_a_definir` | Prazo a definir |
| `linha_permanente` | Linha permanente |
| `resultado_publicado` | Resultado publicado |
| `chamada_pos_resultado` | Chamada pós-resultado |
| `portal_util` | Portal útil |
| `ruido_provavel` | Ruído provável |
| `indefinido` | Indefinido |

`duplicata_oculta` é classificada por `getEditalStatusFilterKeys` para uso futuro/admin, mas **não** aparece na sidebar pública.

## 3. Regras herdadas do 1.2A

- `prazo_envio` tem prioridade sobre `fim_inscricao`.
- `sem_prazo` e `encerrado` não são ruído.
- BNDES pós-resultado nunca classifica como `aberto`.
- Badges visuais (`EditalStatusBadges`) inalterados — mesma função `getEditalStatusBadges`.

## 4. Como filtros combinam

| Camada | Comportamento |
|--------|---------------|
| `semanticStatusSelections` | OR entre status marcados; vazio = sem filtro |
| Demais filtros (`filtersEngine`) | AND com busca, fonte, prazo preset, toggles etc. |
| `curadoriaHidden` | Sempre primeiro — duplicatas ocultas nunca ressuscitam |
| `prazoVencido` | Encerrados ocultos por padrão; filtro "Encerrado" só funciona com "Incluir encerrados" |

## 5. Export PDF / XLSX

| Formato | Colunas |
|---------|---------|
| PDF | Nova coluna **Status** (label curto via `getEditalStatusLabel`) |
| XLSX | **Status** + **Status Detalhado** (`getEditalStatusDetailLabels`) |

Export usa `resolveExportDataset()` — escopo `filtered` = lista filtrada atual; catálogo já exclui duplicatas ocultas via `getEditais()`.

## 6. Arquivos principais

- `src/utils/edital/editalStatusBadges.js` — `getEditalStatusFilterKeys`, `getEditalStatusSemantic`, `getEditalStatusLabel`, `editalMatchesSemanticStatusSelection`
- `src/utils/edital/filtersEngine.js` — passo `semanticStatus`
- `src/components/dashboard/EditaisFiltersSidebar.jsx` — seção "Filtrar por status"
- `src/utils/pdf/editaisPdfFormatters.js` — coluna Status no PDF
- `src/pages/EditaisPage.jsx` — colunas Status no XLSX + chips

## 7. Como testar

```bash
npm test
npm run build
npm run e2e
```

Testes unitários: `editalStatusBadges.test.js`, `editaisPdfFormatters.test.js`  
E2E: `tests/e2e/editais-status-filter.spec.js` (autenticado; skip sem credenciais)

## 8. Limitações

- Filtro "Encerrado" exige toggle "Incluir encerrados" (pipeline AND).
- Deep link / detalhe por ID não alterado.
- Sem toggle admin "mostrar duplicatas ocultas" (FRONTEND 10.3D).
- Export escopo `all` exporta catálogo carregado (já sem ocultos), não necessariamente com filtros da sidebar.

## 9. Próximo patch recomendado

- **FRONTEND 10.3D** — toggle admin duplicatas ocultas.
- **FRONTEND 1.2C** — facetas/contagens por status na StatsBar ou sidebar.

## Referências

- `docs/FRONTEND_1_2A_VALIDITY_STATUS_BADGES.md`
- `docs/FRONTEND_10_3C_DEFENSIVE_HIDDEN_DUPLICATE_FILTER.md`
