# Rollback parcial — Assistente guiado (Pré-cadastro Fase 2)

## Contexto

A Fase 2 trouxe um “assistente guiado” mais denso (visão geral expandida, pendências em três níveis com navegação, impactos em cinco eixos, toolbar vertical com textos longos, subseções na aba Contexto). O feedback foi que a **área de preenchimento/projeto** ficou visualmente pior e menos direta.

Este rollback **não** afeta a tela **Cadastros / Clientes** nem o **cabeçalho do modal** nem o **fluxo de PDF** intencionalmente.

## O que foi revertido

| Área | Mudança |
|------|---------|
| **Visão geral** | Removidos o bloco “intro” longo, o card de snapshot do cliente (`PrecadClienteSnapshot`), o card **Próximos passos** (`PrecadProximosPassos`), e a grade de três colunas extra. Restaurada a ordem enxuta: impactos (3 colunas) → completude + status + faixa empresa → âncora de pendências → lista simples de pendências → recomendações. |
| **Assistente de preenchimento** | Volta ao layout **compacto**: título, um parágrafo curto, **botões em linha** (`flex-wrap`). Removidos textos longos sob cada botão e a coluna “detailed”. |
| **Pendências** | Volta ao painel simples: obrigatórias / recomendadas em lista, sem tiers coloridos, sem “Abrir no formulário” por item. Mantidos atalhos “Ir aos campos-chave”. |
| **Impactos sugeridos** | Volta ao grid **três eixos** (econômico, social, ambiental). Removidos tecnológico e estratégico na UI e `padCincoImpactos` em `preCadastroTemplates.js`. |
| **Contexto e projeto** | `PrecadProjectScope` volta ao **único bloco “Projeto / escopo”** com os campos na ordem original, sem subseções e callout de setor. |
| **`calculatePreCadastroCompleteness.js`** | Removidos `getPendenciasGuiadas` e metadados de navegação por pendência; mantida apenas a lógica de score/listas como antes da Fase 2. |
| **CSS** | Removido o bloco “Pré-cadastro — assistente (Fase 2)” (snapshot, proximos, tiers, intel-help, 5 colunas impactos, etc.). |
| **Componentes** | Arquivos removidos: `PrecadClienteSnapshot.jsx`, `PrecadProximosPassos.jsx`. |
| **Confirmações extra** | “Preencher lacunas” e “Limpar sugestões” voltam a executar **sem** segundo `confirm` (o “Gerar rascunho inteligente” continua com confirmação). |

## O que foi preservado (fora do escopo deste rollback)

- **Tela Clientes** (`Cadastros.jsx`, `AdminTable`, estilos `cad-*`): cards, filtros, tabela, botão “Abrir pré-cadastro”.
- **Header do modal de pré-cadastro** (`PrecadastroHeader.jsx`): organização de ações, chips, Fechar, etc., conforme já ajustado antes deste rollback.
- **`Modal`**: tecla Escape, clique fora — se já estavam implementados no componente, **não foram alterados** aqui.
- **Salvar rascunho**, **pré-visualizar PDF**, **baixar PDF**: mesmos handlers e serviços (`savePrecadEnvelope`, `exportPrecadastroProjetoPdf`, `buildPrecadastroProjetoPdfBlob`).
- **IDs no formulário completo** (`PrecadLegacyFormBody` em `<details>`) e em `PrecadFitSection` / `PrecadObservations`: mantidos; não aumentam ruído na UI e ajudam scroll/âncoras futuras.
- **Navegação “Ir aos campos-chave”**: ao clicar em “Linhas de produto”, a aba **Contexto** é ativada (junto com “Projeto / narrativa”) para o scroll funcionar.

## Por que

- Priorizar **densidade e fluxo direto** na edição do projeto, alinhado ao pedido do produto.
- Manter ganhos já validados (Clientes, header do modal, PDF estável) sem reverter o que não foi criticado.

## Como testar

1. `npm run build` — deve concluir sem erro.
2. **Cadastros → Clientes**: confirmar que cards/filtros/tabela seguem como antes.
3. **Abrir pré-cadastro**: header com ações no topo; **Fechar** à direita; Escape / clique fora conforme o app já fazia.
4. **Assistente**: uma faixa baixa com botões em linha; sem coluna de explicações longas por botão.
5. **Visão geral**: impactos em 3 colunas; completude + status + faixa da empresa; pendências em listas simples.
6. **Contexto e projeto**: um único card “Projeto / escopo”, campos contínuos.
7. Salvar rascunho, pré-visualizar e baixar PDF.

## Documentação relacionada

- `docs/PRE_CADASTRO_ASSISTENTE_AUDIT.md` e `docs/PRE_CADASTRO_ASSISTENTE_IMPROVEMENTS.md` descrevem a Fase 2 original; este arquivo documenta o **recuo parcial** da experiência do assistente, não apaga o histórico.
