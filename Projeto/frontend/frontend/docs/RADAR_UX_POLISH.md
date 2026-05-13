# Radar de Fomento — polimento de UX (frontend)

**Data:** 2026-05-10  
**Âmbito:** apenas experiência de utilização e textos na interface. **Sem** alteração a backends, **sem** alteração à fórmula de score ou ao motor em `radarMatch.js` / `matchService.js` (exceto consumo existente de `meta` já devolvido pelo hook).

---

## O que foi alterado

### Loading (`RadarLoading.jsx`)

- Frase principal mais clara e em tom brasileiro: explica que se está a medir compatibilidade edital a edital.
- Linha de destaque com o **nome do cliente** e aviso para não fechar a página durante o cálculo.
- **Progresso principal:** “X de Y editais analisados com o score completo” + barra e percentagem.
- **Bloco técnico** menor e separado visualmente (`radar-loading-tech`): catálogo total, elegíveis após filtros rápidos, excluídos antes do score — alinhado aos números do hook, para não parecerem contraditórios com a barra.

### Contagens no cabeçalho (`RadarFomento.jsx`)

- Uso de **`radarMeta`** de `useRadarMatches` (já existente no hook) para mostrar, após o cálculo:
  - **Catálogo total** (`totalIn`)
  - **Elegíveis após filtros rápidos** (`afterPreFilter`) — são os editais sobre os corre o score completo
  - **Retirados antes do score** (`excludedPreScore`), só se &gt; 0
  - **Retornadas pelo radar** (`recomendacoes.length`) — linhas devolvidas pelo motor após cortes de score
- Linha principal: **oportunidades listadas** com os filtros da lista (busca/tipo/órgão/compat/favoritos), mais destaque para quantas têm **Alta** compatibilidade e favoritos.
- Durante o cálculo: resumo curto “Em andamento” + catálogo + contagem de elegíveis quando já conhecida.
- Quando a lista é **paginada** (cap progressivo): texto **“Exibindo X de Y na página”** com ponteiro para “Mostrar mais oportunidades”.

### Radar avançado

- Painel **colapsável** (fechado por defeito): botão “Opções avançadas do radar” com subtítulo a indicar que são **opcionais** e **alteram quem entra no cálculo**.
- Checkboxes com labels mais legíveis (sem mudar o significado das opções).

### Cards (`CardEditalRadar.jsx` + CSS)

- Hierarquia: **título** maior → **órgão/fonte** como texto secundário (sem uppercase agressivo).
- Bloco **Compatibilidade**: rótulo + badge Alta/Média/Baixa + barra de score alinhada.
- Linha de **match** (`matchLinha`) com peso visual um pouco mais leve e **até 4 linhas** (clamp).
- Critérios detalhados dentro de **`<details>`** (“Detalhe por dimensão (7) — opcional”) para não poluir o cartão por defeito.

### Estados vazios e erro

- **Erro** do radar: mensagem amigável em destaque + detalhe técnico em linha secundária.
- **Vazio**: títulos e parágrafos explicando o que fazer (filtros avançados, limpar filtros, favoritos).

### Estilos

- Novas classes em `src/styles/global.css` para loading, contagens, painel avançado, cards e estados vazios (prefixo `radar-`).

---

## O que **não** foi alterado

- Cálculo de score, pesos, pré-filtros, `recomendarEditaisAsync`, opções `incluirEncerrados` / `incluirSuspeitos` / `incluirAproximados` (apenas apresentação).
- Qualquer ficheiro da área **Portais Estratégicos**.
- APIs ou Supabase.

---

## Como testar

1. `cd EditalFinder-React` → `npm run dev` → abrir **Radar de Fomento** `/editalfinder/radar-fomento` (ajustar base URL se necessário).
2. Sem cliente: ver texto do placeholder renovado.
3. Selecionar um cliente: observar **loading** — texto principal, barra, bloco técnico pequeno.
4. Após carregar: conferir **duas linhas** de resumo (principal + micro-contagens) e coerência entre catálogo / elegíveis / retornadas.
5. Abrir **Opções avançadas do radar**, alterar checkboxes, **Recalcular** — confirmar que o comportamento do motor é o de sempre; só muda a UX do painel.
6. Expandir **Detalhe por dimensão** num card e comparar com o estado fechado (cartão mais limpo).
7. Forçar erro (ex.: desligar rede e Recalcular) se possível — ver faixa de erro.
8. Aplicar filtros até lista vazia — ver mensagens de vazio.
9. `npm run build` — deve concluir sem erro.

---

## Ficheiros tocados

| Ficheiro | Notas |
|----------|--------|
| `src/components/radar/RadarLoading.jsx` | Textos e estrutura do loading |
| `src/pages/RadarFomento.jsx` | `radarMeta`, contagens, painel avançado, vazio, erro |
| `src/components/radar/CardEditalRadar.jsx` | Hierarquia do card, `details` nos critérios |
| `src/styles/global.css` | Estilos do polimento |
| `docs/RADAR_UX_POLISH.md` | Este documento |
