# Reorganização do frontend — Fase 1 (concluída)

**Data:** 2026-05-10  
**Escopo:** `EditalFinder-React` — reorganização leve, sem alterar fluxos visuais nem lógica do Radar.

---

## Resumo

- **Centralização:** `env.js` reforçado com avisos em **dev** se faltar Supabase; novos **services** por domínio fazem wrap ao `dataService` sem alterar páginas existentes.
- **UI reutilizável:** componentes `LoadingState`, `ErrorState`, `EmptyState`, `StatusBadge` criados (ainda **não** ligados às páginas para minimizar diff).
- **Utilitários:** `formatArray` em `formatters.js`; novo `labels.js` para rótulos de validação, qualidade e portal.
- **Tipos:** pasta `src/types/` com JSDoc `@typedef` + objetos exemplo.
- **Portais:** métodos em `dataService` + `portaisEstrategicosService.js` — **sem rota/página** (conforme pedido).

---

## Arquivos criados

| Caminho | Descrição |
|---------|-----------|
| `src/components/states/LoadingState.jsx` | Estado de carregamento genérico |
| `src/components/states/ErrorState.jsx` | Estado de erro (usa `.empty-state`) |
| `src/components/states/EmptyState.jsx` | Estado vazio |
| `src/components/badges/StatusBadge.jsx` | Badge com variantes discretas |
| `src/components/cards/index.js` | Barrel reservado |
| `src/components/filters/index.js` | Barrel reservado |
| `src/utils/labels.js` | `labelValidacaoStatus`, `labelQualidadeDado`, `labelPortalTipo` |
| `src/types/edital.js` | JSDoc + `EDITAL_SHAPE_EXAMPLE` |
| `src/types/noticia.js` | JSDoc + exemplo |
| `src/types/pesquisa.js` | JSDoc + exemplo |
| `src/types/portalEstrategico.js` | JSDoc + exemplo |
| `src/services/editaisService.js` | Wrap: catálogo editais / detalhe / anexos |
| `src/services/noticiasService.js` | Wrap: `getNoticias` |
| `src/services/pesquisasService.js` | Wrap: `getPesquisas` |
| `src/services/portaisEstrategicosService.js` | Wrap: fornecedores / investimentos (futuro) |

---

## Arquivos alterados

| Caminho | Alteração |
|---------|-----------|
| `src/config/env.js` | `warnMissingCriticalEnvInDev()` — `console.error` em **DEV** listando apenas **nomes** de variáveis em falta (sem URLs/chaves) |
| `src/services/dataService.js` | Imports `VIEW_FORNECEDORES`, `VIEW_INVESTIMENTOS`; novos métodos `getPortaisFornecedoresFront`, `getPortaisInvestimentosFront` (mesmo padrão de fetch que feeds; erros → `[]`) |
| `src/utils/formatters.js` | Nova função `formatArray` |

---

## O que foi centralizado

| Área | Situação |
|------|----------|
| Ambiente | `src/config/env.js` — já lia todas as `VITE_*` pedidas; agora validação amigável em dev |
| Supabase | Continua **único** em `src/services/supabaseClient.js` (`api.js` reexporta) |
| Dados por domínio | Novos `*Service.js` delegam em `dataService` — páginas **continuam** a usar `dataService` diretamente |

---

## Deixado para fases futuras

- Migrar `Dashboard`, `FeedListaPage`, etc. para importar `editaisService` / `noticiasService` em vez de `dataService`.
- Substituir blocos inline de loading/erro/vazio pelos componentes em `components/states/`.
- Mover cards (`EditalCard`, `FeedItemCard`) para `components/cards/` e atualizar imports.
- Extrair filtros duplicados para `components/filters/`.
- Dividir `dataService.js` em módulos por domínio **depois** de todos os imports apontarem para wrappers.
- Path alias `@/` no Vite.
- Página `/portais-estrategicos` e UI que use `portaisEstrategicosService`.

---

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Novos métodos em `dataService` para portais | Só chamados pelo novo service; não alteram `getEditais` / feeds |
| Aviso `console.error` em dev sem `.env` | Pode parecer “agressivo”; é intencional para evitar silêncio com listas vazias |
| Tree-shaking | Componentes novos ainda não importados — não entram no bundle até uma página os use (aceitável para Fase 1) |

---

## Como testar

1. **`npm run dev`** na pasta `EditalFinder-React` — abrir `/editalfinder/dashboard`, Notícias, Pesquisas, Radar: comportamento esperado **inalterado**.
2. **Sem** `.env.local`: em dev, consola deve mostrar erro de config **sem** revelar chaves.
3. **Com** `.env.local` válido: editais/notícias/pesquisas carregam como antes; logs `[dataService.*]` em dev permanecem.
4. **`npm run build`** — deve concluir sem erro (executado na Fase 1).

---

## Status dos comandos (ambiente do agente)

| Comando | Resultado |
|---------|-----------|
| `npm run build` | **OK** (Vite 8, ~720 ms) |
| `npm run dev` | Não mantido em execução aqui — validar localmente |

---

## Referência

- Auditoria prévia: `docs/FRONTEND_STRUCTURE_AUDIT.md`
