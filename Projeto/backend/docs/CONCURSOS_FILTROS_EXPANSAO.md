# Concursos & Seleções — Filtros (Fase 2 — implementado no frontend)

Expansão dos filtros na rota `/concursos`, **somente no cliente** (sem alteração de schema, Supabase ou crawlers).

**Implementação:** `frontend/EditalFinder-React/src/pages/Concursos/ConcursosPage.jsx`, lógica em `src/utils/concursos/concursosFilters.js`, estilos em `ConcursosPage.css`.

---

## Filtros laterais (Fase 2)

| Filtro | Campo(s) | Tipo |
|--------|----------|------|
| Busca textual | vários (ver abaixo) | texto |
| Fonte / banca | `fonte` | select fixo (Quadrix, Legalle, AOCP, Fuvest, …) |
| Tipo de seleção | `tipo_selecao` | select |
| Status | `status` | select |
| Instituição ou órgão | `orgao`, `instituicao`, `titulo` | **texto** (substring) |
| Tipo de instituição | heurística em órgão/instituição/título | select |
| Estado | `estado` | select |
| Município | `municipio` | select |
| Escolaridade | `nivel_escolaridade` | select |
| Área / cargo / curso | `area`, `cargo`, `curso` | substring |
| Somente dados válidos | `validacao_status === 'valido'` | checkbox |
| Somente com edital | `link_edital` preenchido | checkbox |
| Somente com data fim de inscrição | `data_fim_inscricao` | checkbox |
| Somente inscrições abertas | `inscricoes_abertas` (view) | checkbox |
| Somente prova próxima | `prova_proxima` (view) | checkbox |
| Somente com salário/bolsa | `salario_min` / `salario_max` > 0 | checkbox |
| Somente com taxa | `taxa_inscricao` > 0 | checkbox |

**Limpar filtros** repõe o estado inicial (não altera a aba ativa).

---

## Busca textual (Fase 2)

A busca faz `includes` em minúsculas sobre:

- `titulo`, `orgao`, `instituicao`, `banca`, `cargo`, `curso`, `area`, `municipio`, `estado`, `fonte`, `tags[]`

---

## Abas

| Aba | `tipo_selecao` incluídos |
|-----|--------------------------|
| Todos | (sem filtro de tipo) |
| Concursos públicos | `concurso_publico`, `processo_seletivo` |
| Professores | `professor` |
| Técnicos/Administrativos | `tecnico_administrativo` |
| Vestibulares | `vestibular`, `programa_ingresso` |
| Residências | `residencia` |
| Bolsas | `bolsa_estudo` |

`programa_ingresso` aparece em **Vestibulares** (ingresso / vagas olímpicas / pós via Fuvest até aba dedicada «Ingresso»).

---

## Contadores no topo

| Chip | Origem |
|------|--------|
| Total | todos os registos carregados |
| Inscrições abertas | `inscricoes_abertas === true` |
| Com edital | `link_edital` não vazio |
| Dados válidos | `validacao_status === 'valido'` |
| Provas próximas | `prova_proxima === true` |
| Vestibulares / ingresso | `vestibular` + `programa_ingresso` |

Contadores refletem o **dataset completo** (não só a aba/filtros ativos).

---

## UX

- **Chips de filtros ativos** acima da grelha (removíveis com ×; aba aparece como chip bloqueado).
- **Estado vazio** com texto explicando aba + filtros que restringem o resultado.
- **Botão «Limpar filtros»** na sidebar (desativado quando não há filtros laterais).
- **Dark mode:** tokens `--color-*`, `--portais-*`, `--stat-*` existentes.

---

## Testes

`src/utils/concursos/concursosFilters.test.js` (Node `node:test`) — abas, busca, checkboxes, chips.

---

## Residências e formação (diferencial do módulo)

Além de concursos públicos e vestibulares, o módulo **Concursos & Seleções** cobre **residências tecnológicas**, programas de formação e bolsas mapeados em `public.concurso_selecao` (`tipo_selecao = residencia`, `categoria` = `residencia_tecnologica`, `residencia_saude`, etc.).

- Aba **Residências** na UI filtra por `tipo_selecao` / `categoria`.
- Wave 2 piloto: EmbarcaTech — [CONCURSOS_WAVE2_RESIDENCIAS_FONTES.md](./CONCURSOS_WAVE2_RESIDENCIAS_FONTES.md).
- Filtros de bolsa/salário aplicam-se a valores de bolsa/auxílio (`salario_min`/`max`, `extras.valor_tipo`).

---

## Fora de escopo (ainda)

- Favoritos / alertas.
- Filtro server-side (continua paginação client-side na view).
- Nova aba «Ingresso» (só `programa_ingresso`); hoje agrupado em Vestibulares.
- Alteração de `public.edital` ou Radar.
