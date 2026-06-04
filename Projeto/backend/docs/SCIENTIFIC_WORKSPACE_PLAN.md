# Workspace Científico — Plano

## Objetivo

Central pessoal/acadêmica para estudantes e pesquisadores acompanharem temas científicos e estratégicos (física nuclear, materiais, computação científica, defesa, espaço, energia, quântica, IA científica, etc.), sem substituir o fluxo comercial do **Workspace do Consultor**.

## Diferença em relação ao Workspace do Consultor

| Workspace do Consultor | Workspace Científico |
|------------------------|-------------------|
| Cliente → carteira → triagem → pré-projeto → relatório | Interesses pessoais → feed → caderno → ideias → trilha |
| Permissões de cadastro / clientes | Qualquer usuário autenticado |
| Radar, oportunidades, export CSV consultivo | Reuso de notícias, pesquisas, editais, portais |
| Backend Supabase (clientes, favoritos) | **Sem schema novo** — `localStorage` |

---

## Fase 1 (concluída)

- Rota `/workspace-cientifico`, flag `VITE_ENABLE_SCIENTIFIC_WORKSPACE`
- Interesses, feed, caderno, ideias heurísticas simples, trilha plana, briefing
- Persistência: `scientific_workspace_interests`, `scientific_workspace_notebook`

---

## Fase 2 (concluída) — Níveis de estudo e projeto

### Níveis de projeto

| ID | Rótulo | Descrição |
|----|--------|-----------|
| `basico` | Básico | Fundamentos e exercícios introdutórios |
| `intermediario` | Intermediário | Projetos práticos (Python, simulação, revisão) |
| `avancado` | Avançado | IC/TCC leve, simulação mais séria |
| `ic_tcc` | IC/TCC | Iniciação científica / monografia |
| `mestrado` | Mestrado | Pesquisa orientada com base teórica maior |

Descrições de trilha (estudo): **Fundamentos**, **Projetos práticos**, **Pesquisa avançada**, **Mestrado/pesquisa orientada** — textos em `scientificProjectLevels.js` (`LEVEL_DESCRIPTIONS`).

### Catálogo local de trilhas

Arquivo: `src/utils/scientific/scientificStudyCatalog.js`

Por tema (`nuclear`, `fisico_quimica`, `materiais`, `computacao_cientifica`, `defesa`, `energia`, `quantica`, `espaco`, `ia_cientifica`):

- `fundamentals`, `intermediate`, `advanced`
- `books`, `practicalProjects`, `researchIdeas`
- `professorQuestions`

UI: `ScientificStudyPath` com acordeões `<details>` por interesse e subseções.

### Catálogo de ideias de projeto

Arquivo: `src/utils/scientific/scientificProjectCatalog.js`

Cada ideia: `title`, `level`, `type`, `why`, `disciplines`, `tools`, `expectedOutput`, `difficulty`, `nextSteps`, `needs` (interesses).

UI: `ScientificProjectIdeas` — cards compactos, filtro por nível.

Filtro persistido (opcional): `scientific_workspace_project_level_filter` (`todos` | nível).

### Projeto recomendado da semana

Heurística em `pickRecommendedProject.js`:

- Pontua aderência aos interesses ativos
- Preferência por intermediário/avançado se `computacao_cientifica` ativo
- Preferência nuclear/materiais quando aplicável
- Escolha estável por semana (seed por ano-semana)

Exibido no briefing e em Ideias de projeto.

### Briefing (Fase 2)

Inclui: interesses, feed, conceitos, projeto recomendado, sugestão avançada, leitura sugerida, contagem do caderno.

### Caderno (Fase 2)

Itens de projeto salvam também: `level`, `type`, `disciplines`, `tools`, `nextSteps`, `expectedOutput`, `contentCategory` (`feed` | `projeto` | `estudo`).

Itens antigos sem esses campos: fallback seguro em `scientificNotebookStorage.js`.

Modal: filtros por categoria, nível, tipo, interesse.

### Perguntas para professor

`buildScientificProfessorQuestions.js` — agrega perguntas do catálogo por interesse ativo. Seção em Ideias de projeto e dentro da trilha.

### Limitações (Fase 2)

- Sem IA externa — tudo heurístico/local
- Sem schema SQL / backend novo
- Sem progresso salvo na trilha
- Radar e Workspace do Consultor inalterados

---

## Fontes de dados (feed)

- `dataService.getNoticias()`, `getPesquisas()`, `getEditais()`, portais
- `scientificFeedLoader.js` + `scientificInterestMatcher.js`

## Interesses

14 chips; chave `scientific_workspace_interests`.

## Ativação

```env
VITE_ENABLE_SCIENTIFIC_WORKSPACE=true
```

## Arquivos principais

| Área | Caminho |
|------|---------|
| Página | `src/pages/ScientificWorkspace.jsx` |
| Componentes | `src/components/scientific/*` |
| Catálogos | `scientificStudyCatalog.js`, `scientificProjectCatalog.js` |
| Builders | `buildScientificStudyPath.js`, `buildScientificProjectIdeas.js`, `buildScientificBriefing.js`, `pickRecommendedProject.js` |
| Níveis | `scientificProjectLevels.js`, `scientificProjectLevelStorage.js` |

## Logs DEV

`[scientific-workspace]`: `interests_loaded`, `interests_changed`, `feed_loaded`, `item_saved`, `item_removed`, `briefing_generated`, `project_idea_saved`, `study_catalog_loaded`, `project_level_filter_changed`, `recommended_project_generated`, `professor_questions_generated`.

## Fase 2B (concluída) — Expansão de temas científicos e estratégicos

### Novos interesses (17 chips + 14 legados)

Engenharia física, engenharia nuclear, química nuclear, radioquímica, engenharia de defesa, engenharia aeroespacial, física de plasmas, fusão nuclear, dosimetria, proteção radiológica, instrumentação, HPC, modelagem molecular, dinâmica molecular, Monte Carlo, sistemas autônomos, tecnologias estratégicas — sem remover ids antigos (`nuclear`, `defesa`, `aeroespacial`, etc.).

UI: chips agrupados por categoria (`INTEREST_CATEGORIES` em `scientificInterestsConfig.js`).

### Matcher

`scientificInterestMatcher.js` — palavras-chave para todos os novos ids.

### Catálogos locais

| Arquivo | Conteúdo |
|---------|----------|
| `scientificStudyCatalogPhase2B.js` | Trilhas completas por novo tema |
| `scientificProjectCatalogPhase2B.js` | 30+ ideias novas (básico → mestrado) |
| Mesclados em `scientificStudyCatalog.js` / `scientificProjectCatalog.js` |

### Rota sugerida

`buildSuggestedStudyRoute.js` — sequência heurística (ex.: Nuclear+Materiais+Computação; Aero+Defesa+Autonomia; fusão; radiação/saúde; química computacional; tecnologias estratégicas). Exibida na trilha e no briefing.

### Ideias de projeto (escala)

- `rankScientificProjectIdeas.js` — ordenação por aderência, top 18, busca textual, filtro por interesse
- Sem renderizar dezenas de cards sem filtro

### Trilha (muitos interesses)

- Priorização por feed/caderno; até 5 trilhas principais + “Ver todas”

### Briefing 2B

Rota sugerida da semana, projeto por nível (básico/intermediário/avançado-IC), pergunta para professor.

### Caderno

Tags visuais `notebookDisplayTag.js` — ex. `Projeto · Mestrado`, `Feed · Nuclear`.

### Limitações

Sem IA externa, sem schema, sem backend. Escalabilidade futura: sync Supabase, progresso por conceito.

---

## Fase 2C (concluída) — UX de rota científica e organização visual

### Header
- Menu com scroll horizontal **oculto** (scrollbar invisível); `overflow-x: hidden` em `html/body` e na página científica.

### Minha rota científica
- Card principal (`ScientificRouteCard`) com próximo passo, projeto, pergunta ao professor e CTAs (trilha, ideias, salvar rota/projeto).

### Briefing compacto
- Grid de 4 mini-cards + `<details>` “Ver briefing completo”.

### Ordem da página
Hero → Rota → Briefing → Interesses → Ideias → Trilha → Caderno → Feed (largura total, paginado).

### Interesses
- Modo compacto (lista de ativos + “Editar interesses”); categorias em `<details>` ao expandir.

### Ideias
- Faixa “Semana”, atalhos por nível, top 9 + “Ver mais”, cards com produto esperado em destaque.

### Trilha
- Rota em destaque no topo; primeira trilha aberta; salvar rota no caderno.

### Caderno
- Vazio: card baixo; com itens: últimos 3.

### Feed
- Cards compactos; filtros tipo/interesse/fonte; top 10 + “Mostrar mais”.

### Logs DEV
`route_card_rendered`, `interests_expanded`, `briefing_expanded`, `feed_show_more`, `study_route_saved`.

---

## Fase 2D (concluída) — Navegação interna, rota central e caderno expandido

### Navegação interna
- Barra sticky `[Rota] [Interesses] [Projetos] [Trilha] [Caderno] [Feed]` (`ScientificSectionNav.jsx`) abaixo do card de rota; scroll suave para `#scientific-route`, `#scientific-interests`, `#scientific-projects`, `#scientific-study-path`, `#scientific-notebook`, `#scientific-feed`.

### Minha rota científica (centro)
- Chips dos interesses ativos; linha **Seu próximo passo**; bloco **Próxima ação sugerida** (`buildScientificNextAction.js`); próximo conceito, projeto recomendado, pergunta ao professor; CTAs trilha / ideias / salvar rota.

### Próxima ação sugerida
- Heurística local (sem IA): caderno vazio, salvar projeto, salvar rota, estudar fundamentos, ler feed, projeto intermediário.

### Ideias — maturidade
- Badge derivado do nível (`projectMaturityFromLevel`): Ideia inicial → Potencial mestrado.

### Caderno agrupado
- Preview por grupo: Fontes, Projetos, Perguntas, Rotas/estudos (`scientificNotebookGroups.js`); modal com filtro por grupo; item `tipo: rota_estudo` com `conceitos`, `projetos`, `perguntas`, `routeSteps` (compatível com itens antigos).

### Feed curatorial
- Resumo, por que interessa, linha **Conecta com sua rota porque…** (`buildFeedRouteConnection.js`); botões Salvar fonte / Abrir fonte.

### Ritmo visual
- Ideias: máx. 9 + Ver mais; feed: máx. 10 + Mostrar mais; caderno vazio compacto.

### Logs DEV
`section_nav_click`, `next_action_generated`, `route_saved_to_notebook`, `notebook_group_filter_changed`.

---

## Fase 2D+ (concluída) — Correções UX e preparação IA

### Bug “Aprofundar: Aprofundar…”
- Causa: `buildScientificProjectIdeas` prefixava títulos do caderno que já tinham `Aprofundar:`.
- Correção: `cleanScientificTitle.js`, `withScientificPrefix`, sanitização em save/load do caderno.

### Caderno
- `sanitizeScientificNotebookEntry` — títulos limpos, sem `undefined`/arrays vazios desnecessários.
- Perguntas: `tipo: pergunta_professor`, `categoria: pergunta`.

### Briefing
- Botão **Recalcular briefing** + tooltip; texto “gerado localmente…”.

### Botões
- Classes `scientific-btn-primary` / `secondary` / `ghost` / `disabled` (sem cinza “desabilitado” em botões ativos).

### IA (só plano)
- `docs/SCIENTIFIC_WORKSPACE_AI_PLAN.md`, `VITE_ENABLE_SCIENTIFIC_AI=false`, placeholder na UI.

### Logs DEV
`title_cleaned`, `notebook_save_sanitized`, `briefing_recalculated`, `ai_placeholder_clicked`, `professor_question_saved`.

---

## Fase 2E (concluída) — QA funcional, botões e saneamento

### Títulos
- `displayScientificTitle()` — renderização sem prefixos duplicados; badge **Continuação** (sem “Aprofundar:” no título).
- Saneamento ao carregar caderno: `notebook_sanitized_on_load`.

### Botões e feedback
- `ScientificWorkspaceContext` + `ScientificSaveButton` + toast.
- Deduplicação ao salvar (atualiza em vez de duplicar).
- Botões `scientific-btn-primary` / `secondary` / `ghost` / `success` / `disabled`.
- Trilha: um único fluxo “Salvar rota no caderno” no card **Minha rota** (+ caderno).

### Briefing
- Recalcular com timestamp e nota de feedback.
- Card Projeto com título curto.

### Documentação QA
- [`SCIENTIFIC_WORKSPACE_QA_CHECKLIST.md`](./SCIENTIFIC_WORKSPACE_QA_CHECKLIST.md)

### Logs DEV
`button_click`, `notebook_item_saved`, `notebook_item_updated`, `notebook_item_already_saved`, `notebook_sanitized_on_load`, `briefing_recalculated_feedback`, `route_scroll_target_missing`.

---

## Fase 2F (concluída) — QA funcional, deduplicação e feedback de ações

### Botões
- Todo clique com feedback: toast tipado (`success`/`info`/`warning`/`error`), scroll com highlight na seção, logs `scientificButtonClick`.
- Padronização de rótulos; trilha sem segundo “Salvar rota”.

### Deduplicação
- `getScientificNotebookEntryKey` — tipo, título limpo, link, level, interesse.
- Caderno: dedup ao carregar e ao salvar (`notebook_deduplicated_on_load`).
- Ideias: `deduplicateProjectIdeas` — sem cards duplicados; máx. 3 continuações.

### UI
- Modal caderno: largura/altura, textarea 96px, lista espaçada.
- Títulos: `line-clamp` 2 linhas (sem cortes “Apro”).
- “Já salvo” só quando a chave existe no caderno.

### QA
- [`SCIENTIFIC_WORKSPACE_QA_CHECKLIST.md`](./SCIENTIFIC_WORKSPACE_QA_CHECKLIST.md) — mapa A–I + testes manuais.

### DEV
- `console.table` ao abrir workspace (métricas caderno/ideias).

---

## Fase 2G (concluída) — Catálogo profundo de teoria, livros e projetos

### Objetivo
Aumentar a profundidade acadêmica antes de planos semanais: mais projetos, trilhas com teoria em camadas, livros por nível, progressão do básico ao mestrado. **Sem schema SQL, sem backend, sem IA externa.**

### Arquivos novos

| Arquivo | Função |
|---------|--------|
| `scientificDeepStudyCatalog.js` | 14 áreas: pré-requisitos, teoria (4 camadas), livros, `projectTracks` |
| `scientificBookCatalog.js` | Livros com `title`, `author`, `level`, `area`, `why`, `useFor` |
| `scientificProjectCatalogDeep.js` | 60 ideias (10+15+15+10+10) com schema completo |
| `buildDeepStudyBlock.js` | Integra catálogo profundo na trilha |
| `buildScientificBasicToMasters.js` | Sequência Básico → Mestrado por interesses |
| `notebookEntryFromBook.js` / `notebookEntryFromTheory.js` | Salvar livro e bloco de teoria |

### Formato do catálogo profundo

```js
SCIENTIFIC_DEEP_STUDY_CATALOG[areaId] = {
  label, prerequisites: { math, physics, computation },
  theory: { foundations, intermediate, advanced, researchLevel },
  books: { introductory, intermediate, advanced, computational },
  projectTracks: { basic, intermediate, advanced, ictcc, masters }
}
```

Aliases de interesse (`DEEP_CATALOG_INTEREST_ALIAS`): ex. `radioquimica` → `quimica_nuclear`, `fusao` → `plasmas`.

### Áreas prioritárias (14)
Física nuclear, engenharia nuclear, química nuclear/radioquímica, físico-química, materiais, computação científica, Monte Carlo, modelagem molecular, plasmas/fusão, engenharia aeroespacial, engenharia de defesa, instrumentação, dosimetria/proteção radiológica, IA científica.

### UI
- **Trilha** (`ScientificStudyPath`): acordeões com pré-requisitos, teoria, livros, projetos por nível; salvar livro/teoria no caderno.
- **Ideias** (`ScientificProjectIdeas`): “Ver teoria necessária”; faixa **Do básico ao mestrado**.
- **Briefing**: projeto básico/intermediário/avançado, teoria da semana, livro sugerido.
- **Caderno**: grupos **Livros** e **Teoria** (`tipo`: `livro` | `teoria`).

### Ideias de projeto (schema 2G)
`title`, `level`, `maturity`, `type`, `interests`, `prerequisites`, `theoryTopics`, `tools`, `expectedOutput`, `difficulty`, `duration`, `nextSteps`, `possibleDeliverables`, `professorQuestions`.

### Expandir novas áreas
1. Adicionar entrada em `SCIENTIFIC_DEEP_STUDY_CATALOG`.
2. Opcional: livros em `SCIENTIFIC_BOOK_CATALOG`.
3. Projetos em `scientificProjectCatalogDeep.js` ou catálogo legado.
4. Registrar interesse em `scientificInterestsConfig.js` + alias se necessário.

---

## Fase 2H (concluída) — Trilhas profundas e deduplicação

### Problema resolvido
Trilhas duplicadas na UI (ex.: várias “Físico-química”, “Plasmas/fusão”) por interesses distintos apontando ao mesmo catálogo sem `canonicalKey`.

### Canonicalização
Arquivo: `scientificInterestAliases.js` — `SCIENTIFIC_INTEREST_CANONICAL`, `resolveCanonicalInterest`, `groupActiveInterestsByCanonical`.

Exemplos: `fusao`/`plasmas` → `plasmas_fusao`; `radioquimica` → `quimica_nuclear`; `modelagem_molecular` → `dinamica_molecular`; `hpc` e `computacao_cientifica` separados.

### Catálogo profundo (24 áreas)
Mínimos por área (via `defineDeepArea` em `deepStudyCatalogHelpers.js`):
- ≥6 pré-requisitos (math/physics/chemistry/computation);
- ≥10 fundamentos, ≥10 intermediários, ≥10 avançados, ≥8 pesquisa/mestrado;
- ≥4 livros; ≥3 projetos por nível (basic → masters).

Arquivos: `scientificDeepStudyCatalogEntries.js` (nuclear, físico-química, materiais, computação — conteúdo completo), `scientificDeepStudyCatalogRemaining.js` (demais áreas), merge em `scientificDeepStudyCatalog.js`.

### Build da trilha
`buildScientificStudyPath` agrupa por `canonicalKey` → `dedupeStudyPathBlocks` (log DEV `study_path_duplicate_merged`) → uma trilha por área com `matchedInterests` / `matchedInterestLabels`.

### UI
`ScientificStudyPath`: abas (Visão geral, Pré-requisitos, Teoria, Livros, Projetos, Perguntas); contadores por camada; busca “Buscar na trilha…”; salvar teoria com título `Teoria — Área: Nível`.

### Expandir novas áreas
1. Adicionar entrada em `scientificDeepStudyCatalogRemaining.js` ou `Entries.js` com `defineDeepArea`.
2. Registrar mapeamento em `SCIENTIFIC_INTEREST_CANONICAL`.
3. Opcional: livros em `scientificBookCatalog.js` com `area` = chave canônica.

---

## Fase 2H-A (concluída) — Física, Química e Nuclear (trilhas de formação)

### Objetivo
Transformar 10 interesses de UI em **7 trilhas canônicas** com conteúdo de graduação avançada → IC/TCC → mestrado, sem alterar schema/SQL nem o Workspace do Consultor.

### Canonicalização (10 → 7)

| Interesses de UI | `canonicalKey` |
|------------------|----------------|
| `fisico_quimica`, `quimica_fisica` | `fisico_quimica` |
| `quantica` | `quantica` |
| `plasmas`, `fusao`, `fusao_nuclear`, `fisica_plasmas` | `plasmas_fusao` |
| `modelagem_molecular`, `dinamica_molecular` | `dinamica_molecular` |
| `nuclear`, `fisica_nuclear` | `nuclear` |
| `engenharia_nuclear` | `engenharia_nuclear` |
| `quimica_nuclear`, `radioquimica` | `quimica_nuclear` |

### Mínimos de conteúdo (`defineDeepArea` + `phase2HA: true`)
- Teoria: ≥12 fundamentos, ≥12 intermediários, ≥12 avançados, ≥10 pesquisa/mestrado.
- Projetos: ≥4 por nível (`basic` … `masters`).
- ≥8 `professorQuestions` por área; pré-requisitos em math/physics/chemistry/computation.

### Arquivos
- `scientificDeepStudyCatalogPhase2HA.js` — sobrescreve as 7 chaves no merge final de `scientificDeepStudyCatalog.js`.
- `scientificProjectCatalogDeep.js` — bloco `2ha-*` (físico-química, nuclear, plasmas, MD).
- `scientificBookCatalog.js` — livros Atkins, Krane, Chen, Choppin, Glasstone, etc.
- `buildDeepStudyBlock.js` — propaga `professorQuestions` do catálogo.
- UI: `ScientificStudyPath` lê perguntas de `deep.professorQuestions`.

### QA manual sugerido
1. Selecionar Físico-química + Química nuclear + Engenharia física + Monte Carlo → uma trilha por chave, sem duplicata visual.
2. Fusão nuclear + Física de plasmas → uma trilha `plasmas_fusao`.
3. Nuclear + Engenharia nuclear + Radioquímica → três trilhas distintas (`nuclear`, `engenharia_nuclear`, `quimica_nuclear`).
4. Abas com contadores ≥ mínimos; primeira trilha aberta por padrão.

---

## Fase 2H-B (concluída) — Computação, Simulação, Dados e Autonomia

### Objetivo
Aprofundar 7 trilhas que sustentam projetos computacionais em nuclear, físico-química, materiais, defesa e aeroespacial — sem schema/SQL e sem duplicar trilhas na UI.

### Canonicalização

| Interesses de UI | `canonicalKey` |
|------------------|----------------|
| `computacao_cientifica`, `scientific_computing` | `computacao_cientifica` |
| `hpc`, `supercomputacao`, `computacao_alto_desempenho` | `hpc` |
| `monte_carlo`, `simulacao_monte_carlo` | `monte_carlo` |
| `ia_cientifica`, `machine_learning_cientifico`, `ml_cientifico` | `ia_cientifica` |
| `ciencia_dados`, `data_science` | `ciencia_dados` |
| `sistemas_autonomos`, `autonomia` | `sistemas_autonomos` |
| `robotica`, `robotics` | `robotica` |

### Mínimos
Iguais à 2H-A: ≥12/12/12/10 teoria; ≥4 projetos por nível; 8 `professorQuestions`.

### Arquivos
- `scientificDeepStudyCatalogPhase2HB.js` — merge após 2H-A em `scientificDeepStudyCatalog.js`
- `scientificInterestAliases.js` — aliases 2H-B
- `scientificProjectCatalogDeep.js` — projetos `2hb-*`
- `scientificBookCatalog.js` — livros HPC, MC, IA, dados, robótica

### QA manual
1. Computação científica + Monte Carlo + HPC → três trilhas, sem duplicata.
2. IA científica + Ciência dos dados → três trilhas distintas.
3. Sistemas autônomos + Robótica → duas trilhas (sem alias cruzado IA↔autonomia).
4. Busca na trilha e salvar teoria/livro no caderno.

---

## Fase 2H-C (concluída) — Materiais, Energia, Eng. Física, Instrumentação, Biotecnologia

### Objetivo
Aprofundar 5 trilhas que conectam físico-química, nuclear, computação, defesa, aeroespacial e laboratório — sem schema/SQL e sem duplicar trilhas.

### Canonicalização

| Interesses de UI | `canonicalKey` |
|------------------|----------------|
| `materiais`, `ciencia_materiais`, `materiais_avancados` | `materiais` |
| `energia`, `sistemas_energia`, `energia_nuclear_aplicada` | `energia` |
| `engenharia_fisica`, `fisica_aplicada`, `applied_physics` | `engenharia_fisica` |
| `instrumentacao`, `sensores`, `detectores`, `instrumentacao_cientifica` | `instrumentacao` |
| `biotecnologia`, `biotech`, `bioengenharia` | `biotecnologia` |

### Mínimos
≥12/12/12/10 teoria; ≥4 projetos por nível; 8 `professorQuestions`; livros por nível.

### Arquivos
- `scientificDeepStudyCatalogPhase2HC.js` — merge após 2H-B
- `scientificInterestAliases.js` — aliases 2H-C (remove cruzamento `instrumentacao`↔`robotica` via override)
- `scientificProjectCatalogDeep.js` — 25 projetos `2hc-*` (5 por área)
- `scientificBookCatalog.js` — livros Shewmon, MacKay, Taylor, Nelson & Cox, etc.

### QA manual
1. Materiais + Energia + Engenharia física → três trilhas únicas.
2. Instrumentação + Materiais → duas trilhas.
3. Biotecnologia + IA científica → trilhas distintas.
4. Contadores, busca, salvar teoria/livro no caderno; feed intacto.

---

## Fase 2H-D (concluída) — Defesa, Espaço, Aeroespacial, Tecnologias Estratégicas

### Objetivo
Quatro trilhas estratégicas com **Espaço** separado de **Engenharia aeroespacial**; sem novas trilhas para autonomia/robótica (2H-B).

### Canonicalização

| Interesses de UI | `canonicalKey` |
|------------------|----------------|
| `defesa`, `engenharia_defesa`, `defense_engineering` | `engenharia_defesa` |
| `espaco`, `space`, `satelites`, `orbital` | `espaco` |
| `aeroespacial`, `engenharia_aeroespacial`, `aerospace`, `aeronautica` | `engenharia_aeroespacial` |
| `tecnologias_estrategicas`, `dual_use`, `soberania_tecnologica`, `critical_technologies` | `tecnologias_estrategicas` |

### Arquivos
- `scientificDeepStudyCatalogPhase2HD.js` — merge após 2H-C
- `scientificInterestAliases.js` — `espaco` ≠ `engenharia_aeroespacial` (antes ambos iam a `aeroespacial`)
- +24 projetos `2hd-*`; livros Skolnik, Wertz, Sutton, Mazzucato, etc.

### QA manual
1. Defesa + Engenharia de defesa + Tecnologias estratégicas → 2 trilhas (`engenharia_defesa`, `tecnologias_estrategicas`).
2. Espaço + Aeroespacial + Eng. aeroespacial → 2 trilhas (`espaco`, `engenharia_aeroespacial`).
3. Aeroespacial + Sistemas autônomos + Robótica → 3 trilhas distintas.
4. Projetos `2hd-aero-uav-ic` referencia autonomia sem duplicar catálogo.

---

## Fase 2H-E (concluída) — Medicina nuclear, Dosimetria, Proteção radiológica

### Objetivo
Três trilhas de saúde/radiação com **proteção radiológica** separada de **dosimetria** (antes ambas iam a `dosimetria`).

### Canonicalização

| Interesses de UI | `canonicalKey` |
|------------------|----------------|
| `medicina_nuclear`, `nuclear_medicine`, `radiofarmacos`, `radiofarmacia` | `medicina_nuclear` |
| `dosimetria`, `dosimetry`, `dose` | `dosimetria` |
| `protecao_radiologica`, `radiological_protection`, `radioprotecao`, `seguranca_radiologica` | `protecao_radiologica` |

### Arquivos
- `scientificDeepStudyCatalogPhase2HE.js` — merge após 2H-D
- +18 projetos `2he-*` (6 por área); livros Cherry, Attix, Cember, Shultis, IAEA, etc.

### QA manual
1. Medicina nuclear + Dosimetria + Proteção radiológica → **3 trilhas**.
2. Medicina nuclear + Química nuclear + Biotecnologia → trilhas distintas.
3. Dosimetria + Monte Carlo + Instrumentação → conexão por projetos, sem duplicar trilhas.
4. Proteção radiológica + Engenharia nuclear → trilhas distintas.

---

## Fase 2H-F (concluída) — Polimento final das trilhas profundas

### Objetivo
Qualidade de uso após 2H-A–E: canonicalização auditada, deduplicação e ordenação de trilhas, busca rica, UI navegável, rotas por objetivo, caderno profundo e exportação Markdown — **sem alterar schema SQL**.

### Canonicalização e auditoria
- `auditScientificCanonicalKeys.js` — log DEV `study_path_canonical_audit` com `interests`, `canonicalKeys`, `missingCatalogKeys`, `duplicateLabels`.
- Todo interesse visível na UI mapeia para `canonicalKey` com catálogo profundo em `ALL_DEEP_CATALOG_CANONICAL_KEYS`.

### Deduplicação e ordenação
- `dedupeScientificStudyBlocks.js` — por `canonicalKey` e label normalizado; merge de `matchedInterests`; mantém trilha mais profunda; log `study_path_duplicate_merged`.
- `sortScientificStudyBlocks.js` — interesse direto do usuário → engajamento feed/caderno → base antes de aplicada.
- Integrado em `buildScientificStudyPath.js` (`allBlocks` exposto).

### Busca na trilha
- `searchStudyPathBlocks.js` — label, description, formationGoal, prerequisites, theory, books, projectTracks, professorQuestions.
- UI: contagem “N resultados em M trilhas”, highlight `.scientific-search-highlight`, expandir trilhas com match.

### UI da trilha (`ScientificStudyPath.jsx`)
- Índice **Trilhas ativas** (chips com scroll para `#trail-{canonicalKey}`).
- Resumo compacto por trilha (objetivo, pré-requisitos, contadores Fund/Inter/Avanç/Pesq/Proj/Livros).
- Abas: Visão geral, Pré-requisitos, Teoria, Livros, Projetos, Perguntas.
- **Rotas por objetivo** via `buildScientificGoalRoutes.js` + salvar com `notebookEntryFromGoalRoute.js`.
- Botão **Exportar rota em Markdown** → `rota_cientifica_<data>.md` (`exportScientificRouteMarkdown.js`).

### Rotas por objetivo (heurísticas)
| ID | Match (canônico) |
|----|------------------|
| `nuclear_computational` | nuclear + (monte_carlo \| computacao_cientifica) |
| `phys_chem_computational` | fisico_quimica + (dinamica_molecular \| monte_carlo) |
| `reactor_materials` | materiais + (nuclear \| engenharia_nuclear) |
| `aero_defense` | engenharia_aeroespacial + engenharia_defesa |
| `nuclear_medicine_dosimetry` | medicina_nuclear + dosimetria |
| `radiation_protection` | protecao_radiologica + (dosimetria \| nuclear \| eng. nuclear) |
| `space_systems` | espaco |

### Minha rota científica
- `buildRouteCardSummary.js` usa `pickPrimaryGoalRoute` quando há match; card mostra título da rota, livro recomendado, próximos passos.

### Caderno profundo
- `buildNotebookPreview.js` — preview: 2 projetos, 2 livros/teoria, 1 pergunta, recentes agrupados.
- Modal: filtro grupo (incl. **Perguntas**), nível, área, busca textual, contagem por grupo.
- `ScientificSaveButton` + `getScientificNotebookEntryKey` — teoria, livro, pergunta, rota sem duplicar após F5.

### QA manual (2H-F)
1. Fusão + Plasmas → 1 trilha (`plasmas_fusao`).
2. Química nuclear + Radioquímica → 1 trilha.
3. Defesa + Eng. defesa → 1 trilha.
4. Espaço + Aeroespacial → **2** trilhas.
5. Buscar “Monte Carlo” → resultados com highlight.
6. Salvar teoria/livro/pergunta → sem duplicar.
7. Caderno filtra Livros / Teoria / Perguntas.
8. Nuclear + Monte Carlo → rota “Nuclear computacional”.
9. Exportar Markdown baixa arquivo.
10. Feed e projetos intactos.

---

## Fase 2I (concluída) — Progresso de estudo local

### Objetivo
Marcar tópicos, livros, projetos, perguntas e passos de rota com status local — sem schema SQL.

### Persistência
- `localStorage`: `scientific_workspace_study_progress`
- Chave: `canonicalKey::kind::segment::slug` (ex. `nuclear::theory::foundations::decaimento-radioativo`)
- Status: `a_estudar` | `estudando` | `dominado` | `ignorar_agora`

### Arquivos
- `scientificStudyProgressStorage.js`, `scientificStudyProgressKeys.js`, `scientificStudyProgressConstants.js`
- `buildStudyProgressSummary.js` — resumo por trilha e global
- `ScientificStudyProgressSelect.jsx`, `ScientificStudyProgressGlobal.jsx`
- `ScientificWorkspaceContext.jsx` — `studyProgress`, `getStudyProgressStatus`, `setStudyProgressStatus`
- `ScientificStudyPath.jsx` — controle por item, barra de progresso, filtro por status
- `exportScientificRouteMarkdown.js` — seção **Progresso**
- Caderno: `withStudyProgressOnNotebookEntry` em teoria/livro/pergunta

### Logs DEV
- `study_progress_loaded`, `study_progress_changed`, `study_progress_summary_generated`, `study_progress_filter_changed`

### QA manual
1. Marcar tópicos Estudando/Dominado na trilha.
2. F5 — status persiste.
3. Resumo da trilha e “Seu progresso” atualizam.
4. Filtro por status oculta itens.
5. Exportar Markdown inclui progresso.
6. Salvar livro com status `estudando` no resumo do caderno.

---

## Fase 2J (concluída) — Teoremas e ideias poderosas

### Objetivo
Camada editorial separada da teoria comum: teoremas, princípios, leis, métodos e conceitos que mudam o jeito de pensar cada área (graduação avançada → mestrado).

### Catálogo
- `scientificPowerIdeasCatalog.js` — merge de `scientificPowerIdeasCatalogA/B/C`
- `scientificPowerIdeasHelpers.js` — `definePowerIdea`, rótulos de tipo/nível
- 26 `canonicalKeys` com ≥8 ideias (12+ em áreas centrais); ~256 ideias no total

### UI
- Nova aba **Teoremas & Ideias** em cada trilha (`ScientificPowerIdeasPanel.jsx`)
- Filtros por nível e tipo; busca global da trilha inclui ideias poderosas
- Cards com `details` para explicação completa; progresso `powerIdea`

### Integrações
- Progresso: `canonicalKey::powerIdea::level::id`
- Caderno: `notebookEntryFromPowerIdea.js`, grupo **Ideias poderosas**, dedup por `powerIdeaId`
- **Minha rota:** `pickPowerIdeaForGoalRoute.js` — ideia relevante por rota por objetivo
- Export Markdown: seção **Teoremas e ideias poderosas** com status

### QA manual
1. Físico-química → aba Teoremas & Ideias com ≥10 itens.
2. Salvar Função de partição no caderno (grupo Ideias poderosas).
3. Marcar Teorema equipartição como Dominado → F5 persiste.
4. Buscar “ergodicidade” → highlight na trilha.
5. Nuclear + Monte Carlo → ideia poderosa na rota (transporte/seção de choque).
6. Exportar Markdown inclui ideias poderosas.
7. Feed/projetos/trilhas intactos.

---

## Fase 2K (concluída) — Verificação de domínio, XP e níveis

### Objetivo
Checagem ativa antes de marcar **Dominado**; gamificação local (XP, níveis, badges); progresso detalhado de livros.

### localStorage
| Chave | Conteúdo |
|-------|----------|
| `scientific_workspace_mastery_checks` | Perguntas, respostas, confirmação por `progressKey` |
| `scientific_workspace_xp` | `totalXp`, `byArea`, `byKind`, `awardedKeys`, `events` |
| `scientific_workspace_book_progress` | Status de leitura, %, capítulo, notas |

### Verificação de domínio
- `buildMasteryCheckQuestions.js` — 3 perguntas heurísticas por `kind`
- `ScientificMasteryCheckModal.jsx` — autoavaliação; Confirmar / Estudando / Depois
- Ao selecionar **Dominado** no select → abre modal (não obrigatório preencher tudo)

### XP (sem duplicar por `progressKey`)
| Tipo | XP |
|------|-----|
| Teoria | 10 |
| Ideia poderosa | 15 |
| Livro (após verificação) | 30 |
| Projeto | 40 |
| Rota salva | 20 |
| Bônus respostas preenchidas | +5 |

### Níveis globais
Faixas 1–10 (0–99 … 5000+ XP) via `buildScientificLevelSummary.js`; subníveis por área a cada 60 XP.

### Badges
`buildScientificBadges.js` — Primeiros passos, Leitor científico, Caçador de teoremas (5), Nuclear/Compute/MC iniciante, etc.

### UI
- `ScientificXpLevelCard`, `ScientificXpHistoryModal`, `ScientificBadgesCard`
- `ScientificBookProgressModal` — Quero ler / Lendo / Lido / Pausado
- Contexto: `requestStudyStatusChange`, mastery/XP/book state

### Export Markdown
Seções: Nível e XP, Badges, Verificações de domínio, Livros (progresso).

### QA manual
1. Dominado → modal → confirmar → XP + status.
2. F5 persiste; mesmo item não duplica XP.
3. Livro Lido → verificação → 30 XP.
4. Badge Caçador de teoremas após 5 ideias dominadas.
5. Export inclui XP e verificações.

---

## Fase 2L (concluída) — Sessões de estudo e revisão ativa

### Objetivo
Rotina de estudo local: sessões com cronômetro, reflexão, XP moderado, metas por área e revisão heurística.

### localStorage
| Chave | Conteúdo |
|-------|----------|
| `scientific_workspace_study_sessions` | `{ sessions: [...] }` — id, área, duração, itens, reflexão, `xpAwarded` |

### Sessão de estudo
- `scientificStudySessionStorage.js`, `suggestSessionItems.js`, `scientificSessionXp.js`
- `ScientificStudySessionModal.jsx` — fases setup / running / finish
- Botão **Iniciar sessão de estudo** na rota, trilha geral e cada trilha individual
- Ao salvar: marca itens como **Estudando**; opcional verificação de domínio; pergunta ao professor → caderno

### XP de sessão (uma vez por `session::id`)
| Condição | XP |
|----------|-----|
| 15 min | +5 |
| 30 min | +10 |
| 45+ min | +15 |
| Reflexão preenchida (≥2 campos) | +5 |
| Pergunta para professor | +5 |

### Revisão ativa
- `buildActiveReviewItems.js` — estudando, dominado >7 dias, livros lendo, ideias não dominadas
- `ScientificActiveReviewCard.jsx` — botão **Revisar o que estou estudando** (foco Revisão)

### Metas por área
- `buildScientificAreaGoals.js` — 3 fundamentos, 1 ideia, 1 livro, 1 projeto, 2 sessões
- `ScientificAreaGoalsCard.jsx` — checklist “Próximo nível em {área}”

### Histórico
- `ScientificStudySessionsCard.jsx`, `ScientificStudySessionsModal.jsx` — filtros área/período/foco

### Export Markdown
Seções: **Sessões de estudo**, **Próximas metas por área**.

### QA manual
1. Iniciar sessão em Física nuclear → 3 tópicos → finalizar com reflexão.
2. XP de sessão no card e histórico XP.
3. Histórico de sessões lista a sessão.
4. Metas por área atualizam (sessões contadas).
5. Revisão ativa lista itens estudando/antigos.
6. Export Markdown inclui sessões e metas.

---

## Fase 2L-B (concluída) — Pool completo de itens estudáveis

### Objetivo
Sessão e revisão usam o catálogo completo (trilhas 2H, ideias 2J, livros, projetos, rotas, caderno) com filtros, ranking e deduplicação.

### Utils
| Arquivo | Função |
|---------|--------|
| `buildStudySessionItemPool.js` | Pool único por área/fonte |
| `dedupeStudySessionItems.js` | Dedup por `progressKey` e título |
| `rankStudySessionItems.js` | Ranking por área, foco, status |
| `filterStudySessionPool.js` | Filtros foco/nível/status/busca |
| `getStudySessionPipeline.js` | Pool → rank → filter → limit |
| `buildMixedStudySessionRecommendation.js` | Seleção equilibrada (Misto) |
| `scientificStudySessionConstants.js` | Focos, níveis, status, quantidade |

### Focos
Teoria, Ideias, Livros, Projetos, **Perguntas**, Revisão, **Misto** — filtro estrito por `kind` (corrige Teoria mostrando livros).

### UI
- Modal: busca, nível, status, quantidade (5/10/20/Todos), contador, selecionar recomendados/todos/limpar
- Revisão ativa: até 8 itens agrupados + **Ver mais revisão**
- Abertura contextual: trilha, rota, revisão, livro (foco Livros)

### Logs DEV
`study_session_pool_built`, `study_session_items_filtered`, `study_session_recommended_selected`, `active_review_pool_built`

### Export Markdown
Sessões com foco, tipos, área, status antes/depois por item.

---

## Fase 2L-C (concluída) — UX e lógica do seletor de sessão

### Objetivo
Modal de sessão orientado a “o que estudar agora”, com áreas completas, escopos especiais e filtros avançados recolhidos.

### Escopos de área
| Valor | Comportamento |
|-------|----------------|
| `all_active` | Pool de todas as trilhas ativas (`studyBlocks`) |
| `goal_route` | Prioriza áreas e passos da rota sugerida (`goalRoutes[0]`) |
| `canonicalKey` | Filtra/prioriza uma área específica |

### Utils
| Arquivo | Função |
|---------|--------|
| `buildStudySessionAreaOptions.js` | Opções especiais + áreas de `studyBlocks` e `activeInterests` (dedup) |
| `resolveStudySessionModalDefaults.js` | Estado inicial por `openSource` (route / trail / study_path / review) |
| `buildStudySessionRecommendedSelection.js` | Seleção moderada por foco (3–6 teoria, misto 2+1+1+1, etc.) |
| `formatStudySessionCounter.js` | Contador contextual (“N itens em M áreas ativas”) |
| `studySessionAreaScope.js` | Constantes `all_active`, `goal_route` |

### UI
- Título: “O que você quer estudar agora?”
- Linha 1: Área, Duração, Foco (+ descrição do foco)
- Linha 2: Nível, Quantidade, Busca
- **Filtros avançados** (fechado): Status, Origem
- Labels PT: Teoria, Ideia poderosa, Livro, **Novo** (em vez de Sem status)
- Origem por item: “Origem: Trilha profunda / …”

### Abertura contextual
| Origem | Área | Foco | Quantidade |
|--------|------|------|------------|
| Minha rota | `goal_route` | Misto recomendado | 10 |
| Trilha geral | `all_active` | Misto recomendado | 10 |
| Trilha específica | área da trilha | Teoria | 10 |
| Revisão | `all_active` | Revisão ativa | Todos / 20 |

### Logs DEV
`study_session_area_options_built`, `study_session_pool_built` (byArea), `study_session_items_filtered` (areaSelection)

### QA manual
1. Várias áreas de interesse → modal lista Todas + Rota + N áreas individuais.
2. `all_active` → itens de múltiplas áreas no contador e na lista.
3. `goal_route` → itens da rota.
4. Foco Teoria/Livros/Ideias/Misto filtra kinds corretamente.
5. Status só em Filtros avançados; recomendados não seleciona 20 itens.
6. `npm run build` passa.

---

## Fase 2M (concluída) — QA, auditoria e estabilidade

### Objetivo
Estabilizar o Workspace sem novas features: auditoria local, reparo seguro, labels consistentes, export robusto e checklist de QA.

### Utils
| Arquivo | Função |
|---------|--------|
| `auditScientificWorkspaceState.js` | `ok`, `warnings`, `errors`, `stats` |
| `repairScientificWorkspaceState.js` | Dedup caderno, progresso/sessões/XP/livros inválidos |
| `displayScientificLabels.js` | Status/kind em PT (“Novo”, Teoria, etc.) |

### UI DEV
- `ScientificWorkspaceDiagnosticsPanel` — só `import.meta.env.DEV`
- Botões: Copiar diagnóstico, Reparar dados locais, Limpar cache, Reportar problema

### Produção
- Rodapé: **Reportar problema neste Workspace** (`origem: workspace_cientifico`, stats agregados sem dados sensíveis)

### XP e sessões
- `xp_duplicate_prevented` quando `awardedKeys` já contém `progressKey`
- Sessão sem itens não salva; `statusBefore`/`statusAfter` normalizados
- Cronômetro para ao fechar modal

### Export
- `buildScientificRouteMarkdown` com try/catch — arquivo válido mesmo vazio ou com erro parcial
- Log `markdown_exported` / `markdown_export_failed`

### Documentação QA
- [`SCIENTIFIC_WORKSPACE_QA_CHECKLIST.md`](./SCIENTIFIC_WORKSPACE_QA_CHECKLIST.md) — fluxo completo 18 passos + regressões 2M

---

## Fases futuras (sugestão)

1. Sincronizar caderno/interesses com Supabase (RLS)
2. Progresso da trilha por conceito
3. Alertas por tema
4. Integração com Radar pessoal (sem alterar score consultivo)
