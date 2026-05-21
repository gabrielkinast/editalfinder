# Dark mode — Fase 4 (Radar de Fomento)

Objetivo: alinhar a superfície visual do **Radar de Fomento** (`/radar-fomento`) ao tema escuro usando tokens já existentes (`--color-*`, `--badge-*`, `--nav-*`, etc.), sem alterar lógica de score, filtros, backend ou persistência.

## Arquivos alterados

| Arquivo | Alteração |
|---------|-----------|
| `frontend/EditalFinder-React/src/styles/global.css` | Bloco **RADAR DE FOMENTO**: cores legadas/`#fff`/`var(--text-*)` trocadas por tokens; novos tokens `--radar-score-*` e `--radar-match-link` em `:root` e `.theme-dark`; classes `.radar-score-bar--alta\|media\|baixa`; `accent-color` nos checkboxes do radar avançado; ícone da busca com `color: var(--color-muted)`. |
| `frontend/EditalFinder-React/src/components/radar/CardEditalRadar.jsx` | Removido mapa `COR` e cor inline na barra de score; largura continua inline; preenchimento da barra via classes CSS + tokens. |

## Áreas cobertas

1. **Layout geral** — faixa de título, página em duas colunas, painel de resultados.
2. **Sidebar de clientes** — fundo, bordas, cabeçalho, lista, hover/ativo/foco.
3. **Cards/lista de clientes** — tags, badge de favoritos na linha.
4. **Cabeçalho do radar** — título do resultado, subtítulos, pill “Em andamento”, botão Recalcular.
5. **Loading** — cartão, spinner, barra de progresso, textos técnicos.
6. **Erros** — `radar-load-erro`, banner de erro com detalhe.
7. **Busca e filtros** — input, clear, selects, limpar, filtro de favoritos.
8. **Radar avançado** — toggle, painel, labels e inputs (accent).
9. **Cards de oportunidade** — superfície, sombra, destaque “Alta”, score, match line.
10. **Badges** — compatibilidade, prazo, avisos (via `--badge-*`).
11. **Critérios / razões / meta / ações** — details, barras, tags, botões Site/PDF/Detalhes.
12. **Estados vazios** — mensagens centralizadas.
13. **Responsivo** — borda inferior do painel de clientes no mobile.

**Nota:** As classes `.radar-legenda-*` são compartilhadas com a página **Índice de Compatibilidade** (`IndiceCompatibilidade.jsx`); o ajuste de tokens beneficia as duas telas de forma coerente.

## Limitações remanescentes

- **Selects nativos** (`<select class="radar-select">`): aparência depende do SO/navegador; `color-scheme: dark` no `.theme-dark` ajuda, mas não há skin totalmente custom.
- **Botão PDF** do card: mantido `#ef4444` explícito para leitura consistente em ambos os temas (CTA vermelho).
- **Botão “Anexos / Detalhes”** (`#6366f1`): cor fixa; contraste aceitável no escuro, mas não passou por token dedicado.
- **Estrela favorito** ativa/hover (`#f59e0b`): mantida para reconhecimento imediato.
- **Contador** `.radar-favs-count`: fundo âmbar fixo `#d97706` + texto branco para legibilidade em qualquer tema.
- **`color-mix`**: usado em gradientes do card em destaque e nas barras de critério; navegadores muito antigos podem ignorar (fallback ainda legível).

## Checklist manual de teste

Tema **claro** e **escuro** (e **sistema**, se aplicável):

- [ ] `/radar-fomento` — faixa de título legível; contraste do subtítulo.
- [ ] Lista de clientes: hover, item ativo, contagem no badge, estado vazio “Carregando…” / “Nenhum cliente”.
- [ ] Painel direito: fundo distinto da sidebar; texto principal e secundário legíveis.
- [ ] Durante cálculo: bloco de loading, spinner, barra e “% concluído”.
- [ ] Simular erro (ou rede): banner vermelho e `radar-load-erro` legíveis.
- [ ] Busca: foco no input, botão ✕, ícone 🔍 visível mas discreto.
- [ ] Selects tipo/órgão/compatibilidade: texto e fundo legíveis.
- [ ] “Limpar” e filtro de favoritos: default, hover e estado ativo.
- [ ] Abrir “Opções avançadas”: painel, checkboxes com accent visível.
- [ ] Cards: borda/sombra no escuro; card “Alta” com destaque suave; barra de score com três níveis de cor.
- [ ] Badges (compatibilidade, prazo curto, expirado, avisos).
- [ ] Abrir “Detalhe por dimensão”: summary e barras.
- [ ] Links Site / PDF / Detalhes (estados disabled).
- [ ] Mensagens de lista vazia (vários motivos do `radar-empty`).
- [ ] Viewport &lt; 768px: coluna de clientes empilhada, borda entre painéis.

## Build

Comando (PowerShell):

```powershell
Set-Location "frontend/EditalFinder-React"
npm run build
```

**Última execução (esta entrega):** concluída com sucesso (`vite build`, ~1,5 s). Aviso apenas de chunk JS &gt; 500 kB (já existente no projeto), sem falhas.
