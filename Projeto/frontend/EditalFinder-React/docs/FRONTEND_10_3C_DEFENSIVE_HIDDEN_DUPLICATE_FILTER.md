# FRONTEND 10.3C — Defensive Hidden Duplicate Filter

**Data:** 2026-06-15  
**Contexto:** BACKEND 10.3B/10.3C ocultaram 97 duplicatas Grants.gov em `extras.curadoria_front`.

---

## 1. Problema

Duplicatas podem chegar ao frontend com metadados parciais:

- só `hidden_duplicate: true` (apply 10.3B inicial);
- só `visibility: "hidden_duplicate"` (backfill 10.3C);
- ambos (formato final);
- `extras` vs `extras_raw` conforme mapper/view.

Sem filtro defensivo, duplicatas podem aparecer em Editais, Dashboard, Radar e exportações.

## 2. Formato final (staging)

```json
{
  "curadoria_front": {
    "hidden_duplicate": true,
    "visibility": "hidden_duplicate",
    "duplicate_of_id_edital": 123,
    "duplicate_reason": "same_grants_opportunity_id",
    "resolved_by": "backend_10.3b",
    "canonical_link": "https://www.grants.gov/search-results-detail/..."
  }
}
```

## 3. Formatos reconhecidos pelo frontend

| Sinal | Reconhecido |
|-------|-------------|
| `visibility === "hidden_duplicate"` | Sim |
| `hidden_duplicate === true` | Sim |
| `hidden_duplicate === "true"` | Sim (defensivo) |
| Demais `visibility` em `hidden_*` (curadoria legada) | Sim (comportamento anterior) |
| `extras` objeto | Sim |
| `extras_raw` | Sim |
| `extras` string JSON | Sim |

## 4. Onde o filtro é aplicado

| Camada | Função |
|--------|--------|
| `editalVisibility.js` | `isCuradoriaHidden()`, `filterPublicVisibleEditais()` |
| `dataService.getEditais()` | Filtra catálogo após `mapRawEditalRow` (Dashboard, Radar, Consultor, Editais) |
| `filtersEngine.filterCatalog()` | Passo `curadoriaHidden` (defesa em profundidade na aba Editais + export PDF/XLSX da lista filtrada) |

**Fora de escopo:** `getAllEditaisAdmin()` (Cadastros manuais) — não usa catálogo público.

## 5. Fora de escopo neste patch

- Toggle admin “mostrar duplicatas ocultas”.
- Alterações backend/Supabase/RLS/schema.
- Página de detalhe por ID direto (deep link) — registro oculto pode ainda ser consultado se URL conhecida.

## 6. Como testar

```bash
npm test
npm run build
npm run e2e
```

Testes unitários: `src/utils/edital/editalVisibility.test.js`

Com credenciais QA:

```powershell
$env:E2E_USER_EMAIL="..."
$env:E2E_USER_PASSWORD="..."
npm run e2e
```

## 7. Próximo patch opcional

**FRONTEND 10.3D:** toggle admin “Mostrar duplicatas ocultas” + badge de duplicata em modo debug; filtro condicional que bypassa `isCuradoriaHidden` quando flag ativa.

## Referências

- `backend/docs/backend/BACKEND_10_3B_GRANTS_DUPLICATE_RESOLUTION.md`
- `backend/docs/backend/BACKEND_10_3C_GRANTS_DUPLICATE_VISIBILITY_BACKFILL.md`
- `docs/QA_1_1C_GRANTS_E2E_TARGETING.md`
