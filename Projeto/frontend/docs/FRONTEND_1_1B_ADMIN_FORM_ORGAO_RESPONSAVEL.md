# FRONTEND 1.1B — Admin form: órgão / organização responsável

## Problema

O formulário admin (`EditalForm.jsx`) exigia **Organização Responsável** via `<select required>` ligado a `id_organizacao`, carregado de `organizacao`. No staging Supabase:

- A tabela `organizacao` **não está exposta** no PostgREST (erro `PGRST205`).
- O campo **`organizacao_responsavel` não existe** na tabela `edital`.
- O campo textual canónico é **`orgao_responsavel`**.
- **`id_organizacao`** existe mas deve ser **opcional**.

Resultado: cadastro/edição bloqueado ou payload inválido.

## Correção

| Antes | Depois |
|-------|--------|
| Select obrigatório `id_organizacao` | Campo textual opcional `orgao_responsavel` |
| Falha silenciosa se `getOrganizations()` quebra | `loadOrganizationsSafe()` — formulário continua |
| Select de org só quando lista disponível | Select opcional `id_organizacao` |
| Payload com `organizacao`, `status`, campos fantasma | `buildEditalWritePayload()` — só colunas reais de `edital` |

## Arquivos

- `src/utils/supabase/postgrestErrors.js` — `isMissingPostgrestTableError`
- `src/utils/admin/loadOrganizationsSafe.js` — carregamento resiliente
- `src/utils/admin/buildEditalWritePayload.js` — sanitização insert/update
- `src/components/admin/EditalForm.jsx` — UI e submit
- `src/services/dataService.js` — `getOrganizations` + `createEdital` / `updateEdital`

## Mapeamento de campos

| Label na UI | Coluna Supabase |
|-------------|-----------------|
| Órgão / organização responsável | `orgao_responsavel` (text, opcional) |
| Vincular organização (opcional) | `id_organizacao` (bigint, opcional) |
| Status (Ativo/Inativo) | `ativo` (boolean) — **não** coluna `status` |

## Testes

```bash
npm test
```

Inclui `buildEditalWritePayload.test.js`.

## Fora do escopo (1.1B)

- Migration / criação da tabela `organizacao`
- Links externos (FRONTEND 1.1A)
- Colunas Backend 10.1 (`actionability_*`, etc.)
