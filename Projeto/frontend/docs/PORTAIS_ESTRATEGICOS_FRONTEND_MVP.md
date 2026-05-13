# Portais Estratégicos — MVP frontend

**Data:** 2026-05-10  
**Rota:** `/portais-estrategicos` (relativo ao `basename` `/editalfinder`, i.e. URL completa `…/editalfinder/portais-estrategicos`)

---

## Objetivo

Área dedicada a **portais, hubs e cadastros estratégicos**, separada de **Editais** (`/dashboard`) e **Radar de Fomento** (`/radar-fomento`). Consome apenas as vistas configuradas em `.env`:

- `VITE_VIEW_FORNECEDORES` → `vw_fornecedores_front`
- `VITE_VIEW_INVESTIMENTOS` → `vw_investimentos_front`

**Não** consulta `public.edital` nesta página.

---

## Arquivos criados

| Caminho | Descrição |
|---------|-----------|
| `src/pages/PortaisEstrategicos/PortaisEstrategicosPage.jsx` | Página com abas Fornecedores / Investimentos, stats, ordenação, integração com filtros e cards |
| `src/pages/PortaisEstrategicos/PortaisEstrategicosPage.css` | Estilos locais (stats, subtítulo, toolbar) |
| `src/components/cards/PortalEstrategicoCard.jsx` | Card com linguagem de portal/hub; botões Abrir portal / Copiar link |
| `src/components/filters/PortalEstrategicoFilters.jsx` | Filtros laterais + `getInitialPortalFilters()` |
| `src/utils/portaisEstrategicos.js` | Helpers: extras, tipo visível, datas, hub/doc, texto resumo |

## Arquivos alterados

| Caminho | Alteração |
|---------|-----------|
| `src/router/index.jsx` | Rota protegida `/portais-estrategicos` → `PortaisEstrategicosPage` |
| `src/components/layout/Header.jsx` | NavLink **🌐 Portais** após Pesquisas |
| `src/utils/labels.js` | Mapas `PORTAL_TIPO_MAP` ampliados; `labelPortaisValidacaoBadge()` para badges de produto |
| `src/services/portaisEstrategicosService.js` | Comentário atualizado (rota existente) |
| `src/components/cards/index.js` | Reexport `PortalEstrategicoCard` |

---

## Componentes reutilizados (Fase 1)

- `LoadingState`, `ErrorState`, `EmptyState`
- `StatusBadge`

---

## Views / dados

| Aba | Função no service | Origem Supabase (via `dataService`) |
|-----|-------------------|--------------------------------------|
| Fornecedores | `fetchFornecedoresFront()` | `getPortaisFornecedoresFront()` → view `VIEW_FORNECEDORES` |
| Investimentos | `fetchInvestimentosFront()` | `getPortaisInvestimentosFront()` → view `VIEW_INVESTIMENTOS` |

Carregamento: **ambas** as vistas são pedidas em paralelo ao montar a página (lista em memória por aba).

---

## Filtros implementados

- Busca por texto (título, resumo, descrição, link, fontes, tags, tipo legível, categoria)
- Fonte (`fonte_recurso` ou `fonte`)
- Tipo de portal (rótulo de `extras.portal_tipo_wave1` ou `portal_tipo`)
- Validação (`validacao_status`)
- Acesso: todos / consulta pública / login cadastro limitado
- Setor estratégico (arrays achatados)
- Qualidade do dado
- Checkbox **Incluir itens em revisão (suspeito)** — por defeito os `suspeito` estão **excluídos** se não for escolhido filtro nem o checkbox
- **Limpar filtros**
- Linhas com **`ativo === false`** são sempre excluídas da lista

---

## Ordenação

Select: Mais recentes · Fonte · Tipo de portal · Qualidade do dado · Acesso público primeiro.

---

## Limitações / notas

- **Tipos “hub/documentação”** no contador usam heurística em `isHubOrDocTipo()` (portal_tipo + `portal_tipo_wave1`); ajustar se a taxonomia evoluir.
- Campos opcionais: se a view não expuser `ativo`, linhas sem campo são tratadas como ativas (`ativo !== false`).
- **Clipboard:** “Copiar link” usa `navigator.clipboard`; em contextos não seguros pode cair em `window.prompt`.
- O menu global usa **“Radar”** como rótulo curto (tooltip: “Radar de Fomento”) para evitar compressão do header; **Editais**, **Notícias**, **Pesquisas** e **Cadastros** não foram alterados em lógica de dados.

---

## QA visual / ajustes finais

**Escopo verificado (frontend apenas):** rota `/portais-estrategicos`, consumo de `vw_fornecedores_front` e `vw_investimentos_front` via serviços existentes (sem mudança de queries ou backend).

| Área | Verificação |
|------|-------------|
| Contadores | Labels legíveis (“Nesta lista”, “Ativos na aba”, fornecedores, investimentos, acesso limitado, hubs/docs); destaque visual na aba ativa (Fornecedores vs Investimentos). |
| Separação Fornecedores / Investimentos | Datasets carregados em paralelo; listagem e filtros por aba; cards recebem contexto de aba para tonalidade de badges de tipo. |
| Filtros e ordenação | Com lista vazia, com dados reais e com campos opcionais ausentes: não deve quebrar; estado vazio distingue “sem dados na aba” de “nenhum resultado com filtros”. |
| Linguagem | Cards evitam vocabulário de edital; resumo com clamp de linhas; botões **Abrir portal** / **Copiar link** visíveis. |
| Badges | Acesso limitado, documentação, hub, cadastro, investimento, dados parciais e validação usam rótulos humanizados (`humanizeTechnicalLabel`, mapas em `labels.js` / `portaisDisplayLabels.js`). |
| Login | Aviso discreto quando `requer_login === true` / acesso limitado. |
| Responsividade | Grid de cards: ~3 colunas (desktop largo), 2 (tablet), 1 (mobile); painel de filtros não desloca o layout de forma crítica. |
| Menu | Label curto **Radar** + faixa de título “Radar de Fomento” na própria página do radar; item **Portais** mantido curto. |

**Build:** `npm run build` deve passar após estas alterações.

---

## Polimento visual pós-MVP

Aprimoramentos focados em legibilidade e consistência com o EditalFinder, sem reestruturar a página:

- **`src/utils/portaisDisplayLabels.js`:** `humanizeTechnicalLabel` e helpers para fonte, setor, tipo, categoria, qualidade e validação (incluindo slugs como `lockheed_martin_suppliers`, `market_access`, `access_limited`).
- **`src/utils/portaisEstrategicos.js`:** chave semântica de tipo para classes CSS (`getPortalTipoSemanticKey`).
- **`PortalEstrategicoCard` (+ CSS):** hierarquia título → fonte, faixa de badges por contexto fornecedor/investimento, metadados em lista compacta, resumo com line-clamp, CTA primário/secundário, indicação de login/acesso especial.
- **`PortaisEstrategicosPage` (+ CSS):** métricas no topo, chip de destaque por aba, grid responsável (`portais-cards-grid`), mensagens de vazio (“Nenhum portal encontrado com os filtros atuais…” + subtexto para limpar filtros ou mudar de aba).
- **`PortalEstrategicoFilters.jsx`:** placeholders e labels amigáveis; opções de select humanizadas; botão **Limpar filtros** com classe dedicada estilizada em `PortaisEstrategicosPage.css` (`.portais-filters-clear-btn`).
- **`Header.jsx`:** `🎯 Radar` + `title="Radar de Fomento"`.
- **`RadarFomento.jsx` + `global.css`:** faixa compacta com título completo “Radar de Fomento”; layout flex (`radar-fomento-page` / `radar-fomento-below-header`) para o painel principal continuar a preencher a altura útil sem quebrar `calc(100vh)`.

---

## QA responsivo (revisão final)

Checklist manual em **três larguras** (viewport aproximado):

| Largura | Colunas de cards | Filtros laterais |
|--------|-------------------|------------------|
| Desktop (≥992px) | 3 (`portais-cards-grid` + `editais-grid`) | Coluna fixa; rótulos “Buscar”, “Fonte”, etc. em tipografia sem uppercase forçado (classe `portais-layout`) para evitar corte visual. |
| Tablet (640px–991px) | 2 | `portais-layout` remove `max-height: 300px` da sidebar global nesta rota, mantém filtros em **coluna única** (sem flex em linha que espreme labels). |
| Mobile (≤639px) | 1 | Mesmo comportamento; botão móvel “Abrir/Fechar Filtros” inalterado. |

**Ajustes finos na mesma revisão:** cards portais um pouco mais baixos (padding, resumo em 3 linhas, CTAs com altura 36px); bloco de metadados com fundo neutro e ordem **Categoria → Consulta → Qualidade do dado → Setores estratégicos**; CTAs com `margin-top: auto` para ficarem no rodapé do card na grelha.

---

## Como testar

1. `cd EditalFinder-React` → `npm run dev` → abrir `http://localhost:5173/editalfinder/portais-estrategicos` (ajustar host/porta se necessário).
2. Confirmar menu **🌐 Portais** e navegação nas outras rotas.
3. Aba **Fornecedores** / **Investimentos**: deve haver dados se as views no Supabase têm linhas e RLS permite anon.
4. Testar filtros, ordenação, copiar link, abrir portal.
5. `npm run build` — deve concluir sem erro.

---

## Status build (CI local)

Executar `npm run build` no ambiente de desenvolvimento após pull; o relatório foi validado no ambiente do agente na mesma alteração.
