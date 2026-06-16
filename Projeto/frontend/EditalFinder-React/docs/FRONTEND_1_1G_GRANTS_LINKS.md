# FRONTEND 1.1G-GRANTS-LINKS — Official URL Resolution Integration

## Bug observado

Alguns editais Grants.gov continuavam abrindo:

```
https://www.grants.gov/page-not-found
```

Mesmo após o BACKEND 10.3A canonicalizar links no banco, o frontend ainda usava o
**primeiro campo disponível** (`link`, `url_detalhe`, etc.) sem canonicalização Grants.gov.

## Causa técnica

- `resolveActionLinks` (linkHealth) lia `linkOriginal`/`link_raw` diretamente.
- `actionUrlResolver` usava `pickFirstNormalized` sem regras Grants.gov.
- `ExternalActionButton` abria a URL passada sem recanonizar.
- Componentes como `CardEditalRadar` e `EditalDetailsModal` usavam links crus.

O helper `officialEditalUrl.js` (DESKTOP QA 1.0) já resolvia URLs corretamente, mas
**não estava integrado** nos botões reais.

## Relação com BACKEND 10.3A

O backend canonicalizou muitos registros, mas:

- registros antigos/cache local ainda podem ter `page-not-found`;
- `simpler.grants.gov/opportunity/<id>` pode persistir em campos legados;
- `extras.grants_opportunity_id` pode existir enquanto `link` está quebrado.

O frontend agora **sempre** canonicaliza na abertura, independentemente do campo bruto.

## Helper central

### `officialEditalUrl.js`

- `getOfficialEditalUrl(edital)` — atalho para URL oficial.
- `resolveOfficialEditalUrlInfo(edital)` — metadata (`fieldUsed`, `canonicalized`, `rejectedUrls`).

### `getEditalActionUrls.js` (novo)

- `getEditalOfficialUrl` — botão Site/Abrir edital.
- `getEditalPdfUrl` — só `pdf_url` (nunca substituído por Grants detail).
- `getEditalInscricaoUrl` — `link_inscricao` se seguro; fallback para official se page-not-found.
- `resolveEditalActionUrls` — pacote site/pdf/inscrição + rejectedUrls.
- `resolveExternalActionUrl` — usado por `ExternalActionButton` e `actionUrlResolver`.

## Pontos integrados

| Camada | Arquivo |
| ------ | ------- |
| Resolver central | `getEditalActionUrls.js`, `actionUrlResolver.js` |
| Listagem cards | `linkHealth.js` → `EditalCard.jsx` |
| Modal dashboard | `EditalDetailsModal.jsx` |
| Radar | `CardEditalRadar.jsx` |
| Detalhe | `EditalDetalhes.jsx` (via `resolveActionLinks` + `ExternalActionButton`) |
| Botão externo | `ExternalActionButton.jsx` — recanoniza + debug + alerta de falha |
| Debug QA | `externalLinkDebug.js` — log gated |

## Comportamento antes/depois

**Antes:** `link = page-not-found` → botão abre page-not-found.

**Depois:**

1. `extras.grants_opportunity_id` ou ID extraído de URL legada →
   `https://www.grants.gov/search-results-detail/<id>`.
2. `simpler.grants.gov/opportunity/<id>` → canonicalizado antes de abrir.
3. `view-opportunity` / `view-opportunity.html` → canonicalizado.
4. Sem URL segura → alerta *"Não encontramos um link oficial seguro para este edital."*
   (não abre page-not-found).

PDF e inscrição:

- PDF continua usando `pdf_url`.
- Inscrição usa `link_inscricao` quando seguro; se page-not-found, cai para official URL.

## Debug (dev/QA)

```js
localStorage.setItem('EDITALFINDER_DEBUG_EXTERNAL_LINKS', '1');
```

Log:

```
[EditalFinder][ExternalLinkDebug] {
  title, id_edital, fonte, chosenUrl, fieldUsed,
  wasCanonicalized, rejectedUrls, runtime, flags
}
```

## Como testar

```bash
npm test
npm run build

# E2E (opt-in)
npm run e2e:install
npm run build
npm run e2e
# ou: npx playwright test tests/e2e/grants-links.spec.js
```

Testes unitários: `officialEditalUrl.test.js`, `getEditalActionUrls.test.js`.

## Limitações

- Fallback final sem ID Grants.gov → URL de busca genérica (`/search-grants`), não page-not-found.
- Alerta de falha usa `window.alert` (simples; toast do app não acoplado para evitar dependência de context).
- E2E requer Playwright instalado e app com dados Grants.gov reais.

## Próximo patch recomendado

**FRONTEND 1.1F** — tratamento de erro de cadastro/RLS + rascunho local + reporte com metadata.
