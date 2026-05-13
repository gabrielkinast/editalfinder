# Pré-cadastro de projeto — correções UX + PDF

**Data:** 2026-05-10

## Problema original

1. **Menu:** item “Índice” ocupava espaço sem valor para o utilizador final.
2. **Modal pré-cadastro:** demasiados botões com a mesma hierarquia visual; assistente sem título claro; texto de ajuda longo.
3. **PDF:** blocos e texto **sobrepostos** no fim do documento (declaração / assinatura) e risco de sobreposição em secções longas.

## Ficheiros alterados

| Ficheiro | Alteração |
|----------|-----------|
| `src/components/layout/Header.jsx` | Item “Índice” só aparece se `VITE_ENABLE_INDICE === 'true'` (default oculto). |
| `.env.example` | Comentário documentando `VITE_ENABLE_INDICE`. |
| `src/components/admin/precadastro/PrecadastroHeader.jsx` | Reordenação: Fechar (discreto, `margin-right: auto`) · grupo com Pré-visualizar · **Salvar rascunho** (primário) · **Baixar PDF** (`.precad-btn-outline`). |
| `src/components/admin/precadastro/PrecadIntelToolbar.jsx` | Título **“Assistente de preenchimento”**; texto curto conforme especificação; rótulos de botões ligeiramente encurtados. |
| `src/styles/global.css` | `.precad-header-actions-group`, `.precad-header-btn-fechar`, `.precad-btn-outline`, `.precad-assistente-titulo`. |
| `src/services/precadastroPdf/renderPreCadastroPdf.js` | Helpers `contentMaxY`, `ensureVerticalSpace`, `renderMultilineParagraph`; correção fluxo Y em impactos, **Condições complementares** (usa retorno do `banner`), declaração + assinatura sem `Math.max` enganoso; rodapé “Gerado pelo EditalFinder”. |

**Não alterado:** Portais Estratégicos, Radar, backend, Supabase, fórmulas de score, `buildPreCadastroPdfModel` (conteúdo semântico).

## Causa da sobreposição no PDF

- Posicionamento da **declaração** usava `lastAutoTable.finalY` **sem** o deslocamento do **banner** recém-desenhado.
- Texto da declaração em **várias linhas** não avançava Y linha a linha.
- Caixa de **assinatura** calculada com `Math.max(..., ph - 90)` **independente** do fim do texto → sobreposição no fundo da página.

## Solução aplicada

1. **Parágrafo da declaração:** `splitTextToSize` + loop com `renderMultilineParagraph`, com **quebra de página** quando Y ultrapassa `contentMaxY(doc)`.
2. **Assinatura:** retângulo e linhas desenhados **após** o fim do texto (`yAfterText`), com `ensureVerticalSpace` antes do bloco (~70 mm).
3. **Condições complementares:** `yPos = banner(...)` e `autoTable` com `startY: yPos + 4` (não reusa `lastAutoTable` ignorando o banner).
4. **Impactos:** loop com `yImpactNext` por tabela, sem usar `lastAutoTable` da página anterior.
5. **Rodapé global:** `stampFooters` inclui **“Gerado pelo EditalFinder · Pre-cadastro de projeto · …”** e data.

## Melhorias de UI (modal)

- Hierarquia de ações no cabeçalho (Fechar, pré-visualizar, Salvar primário, Baixar em contorno), alinhadas à **direita** no desktop.
- Painel do assistente com título e copy mais curta.
- Classes CSS dedicadas para agrupar botões e evitar competição visual no topo.

### Ajuste — botão Fechar no grupo de ações

- **Fechar** deixou de usar `margin-right: auto` (que o isolava à esquerda da coluna de ações) e passou a integrar o mesmo flex que **Pré-visualizar PDF**, **Salvar rascunho** e **Baixar PDF**, com `justify-content: flex-end` e `justify-self: end` na grelha do header.
- Em ecrãs &lt; 920px, a barra de ações ocupa a largura total abaixo do bloco de título/badges, com quebra de linha e sem sobreposição.

### Ajuste final — duplicidade de fechamento

- Removido o botão **×** do canto do `Modal` no fluxo **Pré-cadastro de projeto** (`hideCloseButton` em `Cadastros.jsx` + suporte em `Modal.jsx`).
- Mantido apenas o botão **Fechar** no cabeçalho do formulário (`PrecadastroHeader`).
- **Tecla Escape** fecha o modal (listener global no `Modal`). Clicar **fora** do conteúdo (overlay) continua a chamar `onClose`, como antes.
- **PDF** e `renderPreCadastroPdf.js` não foram alterados neste passo.

## Como testar

1. `npm run build` (obrigatório).
2. Cadastros → cliente (ex.: sem edital / incompleto / texto longo em contexto) → **Pré-cadastro projeto**.
3. **Assistente:** gerar rascunho, limpar sugestões, revisar pendências.
4. **Abas:** Visão geral ↔ Contexto ↔ Formulário completo.
5. **Salvar rascunho** (alert de confirmação).
6. **Pré-visualizar PDF** e **Baixar PDF** — verificar últimas páginas: declaração, linha de assinatura, sem sobreposição.
7. Menu:** confirmar ausência de “Índice”; opcionalmente definir `VITE_ENABLE_INDICE=true` em `.env.local` e voltar a ver o item.
8. Navegar diretamente a `/editalfinder/indice` (ou rota equivalente ao basename) — deve continuar a abrir se a rota existir no router.

## Limitações restantes

- PDF continua a ser gerado por **jsPDF** (não é WYSIWYG da tela); textos extremamente longos podem aumentar muito o número de páginas.
- `maybeWarnIncomplete` ainda usa `window.alert` para pendências críticas (comportamento preexistente).
- Índice só está oculto no **menu**; não há feature flag server-side.

## Próximos passos (opcional)

- Pré-visualização HTML do PDF em modal (sem nova aba).
- Telemetria leve (erro ao gerar PDF).
- Testes E2E no fluxo de pré-cadastro.
