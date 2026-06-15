# FRONTEND 1.1F-DETALHE — Robust Edital Detail Loading

## Sintoma

Ao clicar em alguns editais (Web e EXE/Tauri), a tela de detalhe exibia:

```
Não foi possível carregar os dados do edital.
```

O DESKTOP QA 1.0 classificou como bug **P1**.

## Diagnóstico do QA

| Camada | Comportamento anterior |
| ------ | ---------------------- |
| Lista | `dataService.getEditais()` → view `vw_editais_front` (~1051 registros) |
| Detalhe | `getEditalById(id)` → tabela base `edital` com `.single()` |
| Anexos | `getAnexosByEdital(id)` em `Promise.all` com o edital |

Problemas:

1. `.single()` **lança** quando retorna 0 linhas (PostgREST PGRST116) — comum quando o registro
   existe na view mas não na base (ou RLS difere entre view e tabela).
2. `Promise.all` rejeita se **anexos** falharem, derrubando a página inteira mesmo com edital válido.
3. Parâmetro de rota (`id`, `id_edital`, prefixo `manual-`) não era normalizado.

## Causa técnica

Divergência **view × tabela base** + uso de `.single()` + acoplamento edital/anexos via
`Promise.all`.

## Mudanças implementadas

### `getEditalById` (via `lookupEditalForDetail`)

1. Normaliza o id de rota (`manual-123`, `"123"`, `123`).
2. Busca na tabela `edital` com **`.maybeSingle()`** (0 linhas → `null`, sem throw).
3. Se não encontrar, fallback na view `vw_editais_front` (mesma da listagem).
4. Tenta colunas `id_edital` e `id` por candidato.
5. Retorna objeto estruturado:

```js
{
  edital,           // row normalizada ou null
  errorKind,        // 'not_found' | 'supabase' | 'network' | null
  lookupMode,       // 'base' | 'view' | null
  routeParam,
  normalizedId,
  lookupBaseFound,
  lookupViewFound,
}
```

### Anexos

- Novo `getAnexosByEditalSafe()` → `{ ok, data, error }` (nunca lança).
- `EditalDetalhes` usa **`Promise.allSettled`** para edital + anexos em paralelo.
- Falha de anexos → detalhe renderiza + aviso discreto:
  *"Não foi possível carregar os anexos deste edital."*

### Tela de detalhe — erros classificados

| errorKind | Mensagem |
| --------- | -------- |
| `not_found` | Não encontramos este edital no catálogo atual. |
| `supabase` / `network` | Não foi possível carregar os dados do edital agora. |

Tela de erro inclui **Voltar** e **Reportar problema** (`AppReportProblemButton`) com metadata:

```json
{
  "origem": "edital_detail_load",
  "routeParam": "...",
  "errorKind": "...",
  "lookupMode": "base_then_view"
}
```

### Log dev/QA

`src/utils/qa/detailDebug.js` — gated por `VITE_DEBUG_ROUTE_DETAIL=1` ou
`localStorage.EDITALFINDER_DEBUG_ROUTE_DETAIL=1`:

```
[EditalFinder][DetailDebug] { routeParam, normalizedId, lookupBaseFound, ... }
```

## Comportamento antes/depois

**Antes:** base 0 linhas → `.single()` throw → catch genérico → página inteira quebrada.

**Depois:** base 0 linhas → fallback view → detalhe carrega; se anexos falham, detalhe
continua com aviso; se ambos ausentes, mensagem `not_found` + reporte.

## Arquivos

**Criados:**

- `src/utils/edital/editalDetailLookup.js` (+ `.test.js`)
- `src/utils/qa/detailDebug.js` (+ `.test.js`)
- `docs/FRONTEND_1_1F_DETALHE_ROBUST_LOAD.md`

**Alterados:**

- `src/services/dataService.js` — lookup robusto + `getAnexosByEditalSafe`
- `src/pages/EditalDetalhes.jsx` — `allSettled`, erros classificados, aviso anexos, reporte
- `src/services/editaisService.js` — `fetchEditalById` retorna `.edital`
- `package.json` — novos testes

## O que NÃO foi alterado

- Supabase, RLS, schema, backend.
- Links Grants.gov (patch seguinte: **FRONTEND 1.1G-GRANTS-LINKS**).

## Testes

`editalDetailLookup.test.js` (10) + `detailDebug.test.js` (4):

- maybeSingle / fallback view / not_found / erro Supabase;
- anexos falham sem derrubar edital;
- id string/numérico/manual-;
- mensagens de erro classificadas;
- log dev gated.

E2E `tests/e2e/editais-detail.spec.js` continua falhando se aparecer a mensagem fatal
antiga quando dados existem na listagem.

## Limitações

- Fallback view retorna a linha da view (shape pode diferir levemente da base); `normalizeEditalDetailRow` mapeia aliases comuns.
- Se o registro não existir nem na base nem na view, ainda mostra `not_found` (correto).
- E2E Playwright opt-in — não executado neste patch se não instalado.

## Próximo patch recomendado

**FRONTEND 1.1G-GRANTS-LINKS** — integrar `getOfficialEditalUrl` nos botões externos.
