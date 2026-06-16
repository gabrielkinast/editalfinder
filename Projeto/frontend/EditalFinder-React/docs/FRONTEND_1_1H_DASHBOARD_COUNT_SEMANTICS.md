# FRONTEND 1.1H — Dashboard Count Semantics Fix

## Sintoma

No Dashboard, o card principal exibia:

```
Editais monitorados
437
6 com prazo confirmado
```

Já a tela de Editais mostrava `Mostrando 995 de 1051 recebidos editais`.

A diferença entre **437** (Dashboard) e **1051** (catálogo recebido) dava a
impressão de que o EXE/Tauri tinha apenas 437 editais — ou seja, parecia
*perda de dados*, quando na verdade era apenas um **subconjunto**.

## Confirmação no EXE novo (DESKTOP 1.1G)

O DESKTOP 1.1G confirmou, com logs dev-only (`catalogCount`, `filteredCount`,
`supabaseHost`, `runtime`), que:

- o EXE lê o banco correto (mesmo `supabaseHost` do web);
- a paginação funciona;
- não há divergência de RLS;
- o catálogo recebido tem **~1051** registros, igual ao web.

Portanto não existe divergência real de banco. O problema é **semântico/visual**.

## Diferença entre 1051 recebidos e 437 monitorados

| Número | Origem no código | Significado |
| ------ | ---------------- | ----------- |
| ~1051  | `editais.length` (catálogo recebido de `dataService.getEditais()`) | Total carregado do banco/view `vw_editais_front` |
| ~437   | `metrics.totalEditais` = `buildDashboardAggregations` → `list.length` | Subconjunto **após o filtro de escopo do Dashboard** (`dashboard_scope_filter`, ex.: Brasil) e limite de processamento |
| 6      | `metrics.prazoConfirmado` | Oportunidades com prazo estruturado válido |

O `437` é o resultado do **scope filter do Dashboard** (persistido em
`localStorage` como `dashboard_scope_filter`). Com escopo `Todos`, o card passa a
mostrar ~1051; com `Brasil`/`Internacional`/`Multilateral`, mostra o subconjunto.
Em nenhum caso isso representa perda de dados.

## Comportamento antes/depois

**Antes:**

```
Editais monitorados
437
6 com prazo confirmado
```

**Depois:**

```
Editais priorizados
437
De 1.051 recebidos no catálogo · subconjunto priorizado do Dashboard · 6 com prazo confirmado
```

E logo abaixo da grade de métricas, um texto de ajuda:

> O Dashboard mostra um subconjunto priorizado dos editais. Para ver o catálogo
> completo, acesse a tela de Editais, que indica quantos registros foram recebidos
> do banco e quantos permanecem visíveis após os filtros.

Quando o catálogo recebido é igual ao priorizado (escopo `Todos`), o subtexto
omite o `De X` para não soar contraditório:

```
Editais priorizados
1.051
1.051 recebidos no catálogo · subconjunto priorizado do Dashboard · 10 com prazo confirmado
```

## Contadores exibidos

- **Editais priorizados** = `metrics.totalEditais` (subconjunto escopado do Dashboard).
- **Recebido no catálogo** = `metrics.catalogEditais` (`editais.length` bruto), citado no subtexto.
- **com prazo confirmado** = `metrics.prazoConfirmado`.
- A tela de Editais segue mostrando `995 de 1051 recebidos` (não alterada).

## Arquivos

**Criados:**

- `src/utils/dashboard/dashboardCountSemantics.js` — lógica pura dos textos/labels
  de contagem + `DASHBOARD_COUNT_HELP_TEXT`.
- `src/utils/dashboard/dashboardCountSemantics.test.js` — testes da semântica.
- `docs/FRONTEND_1_1H_DASHBOARD_COUNT_SEMANTICS.md` — este documento.

**Alterados:**

- `src/utils/dashboard/dashboardAggregations.js` — expõe `metrics.catalogEditais`
  (total bruto recebido) e `metrics.scopedEditais`.
- `src/pages/Dashboard.jsx` — usa `buildDashboardCountContexts`, renomeia o card
  para "Editais priorizados", adiciona subtexto com o total recebido e a nota de ajuda.
- `src/styles/dashboard.css` — estilo `.home-dash-metrics-note`.
- `package.json` — inclui o novo teste no script `test`.

## O que NÃO foi alterado

- Backend, Supabase, RLS, views.
- Query de dados (`dataService.getEditais`).
- Filtros (scope do Dashboard e filtros da tela de Editais permanecem iguais).
- Demais cards do Dashboard.

## Testes

`dashboardCountSemantics.test.js` cobre:

1. diferencia `catalogEditais` (recebido) de `totalEditais` (priorizado);
2. card não rotula 437 como "total recebido";
3. subtexto cita o total recebido quando `catalogEditais` existe;
4. catálogo == priorizado não gera "De X" contraditório;
5. sem `catalogEditais`, o contexto continua renderizando sem quebrar;
6. objeto vazio não quebra;
7. compatibilidade dos demais contextos (`total`, `open`, `expiring`, `reports`);
8. texto de ajuda menciona catálogo completo vs subconjunto priorizado;
9. `truncated` adiciona nota de amostra.

Resultado: `npm test` → **157 testes, 157 passando, 0 falhas**.
Build: `npm run build` → **OK** (`built in ~3s`).

## Limitações

- O `437` ainda depende do `scope filter` persistido em `localStorage`; o subtexto
  agora explica que é subconjunto, mas o usuário precisa abrir o seletor de escopo
  para entender qual recorte está ativo.
- O texto de ajuda é estático (não há tooltip interativo); a página de ajuda
  (`HelpPageLink sectionId="dashboard"`) não foi alterada nesta entrega.

## Próximo patch recomendado

- **FRONTEND 1.1I — Dashboard scope badge**: exibir, junto ao card "Editais
  priorizados", um badge com o escopo ativo (Todos/Brasil/Internacional) para
  deixar explícito o recorte aplicado, e opcionalmente sincronizar o tooltip com a
  página de ajuda do Dashboard.
