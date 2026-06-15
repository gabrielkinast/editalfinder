# FRONTEND 1.1D — Correção de layout PDF (editais)

## Bug observado

O PDF de editais saía desconfigurado: tabela descentralizada, colunas cortadas, links enormes quebrando o layout.

## Causa provável

`EditaisPage` exportava **13 colunas** (incluindo Link e PDF com URLs longas) via `exportLandscapeTablePdf` com `tableWidth: 'auto'` e **sem larguras fixas**. Em A4 paisagem isso estoura a largura útil e desalinha a tabela.

## Solução

- **Não** capturar screenshot da UI (`html2canvas`).
- Layout **dedicado** com `jsPDF` + `jspdf-autotable`.
- Função `exportEditaisToPdf` com **9 colunas compactas** e larguras fixas em mm.
- Orientação **paisagem** (`jsPDF('l', 'mm', 'a4')`).
- Títulos e textos truncados; links **excluídos** da tabela principal.

## Colunas exportadas

| Coluna | Origem |
|--------|--------|
| Título | `titulo` (truncado) |
| Fonte | `getFonte()` |
| Tipo | oportunidade/recurso |
| Área | áreas tecnológicas/setor |
| Local | UF / país / região |
| Situação | validação + situação |
| Prazo | `prazo_envio_raw` etc. |
| Valor | moeda BRL ou texto |
| Qual. | `qualidade_dado_raw` |

## Cabeçalho do relatório

- EditalFinder + título
- Data/hora de geração
- Total exportado
- Resumo de filtros em uma linha (`buildPdfFiltersSummary`)

## Rodapé

- `Gerado pelo EditalFinder`
- `Página X de Y`

## O que não foi alterado

- Exportação **XLSX** de editais (inalterada)
- PDF de **notícias** (`FeedListaPage` → `exportLandscapeTablePdf`)
- **Concursos** (sem export PDF)
- Backend, banco, Tauri, feedback, links externos

## Como testar manualmente

1. `npm run dev` ou EXE
2. Ir em **Editais**, aplicar filtros opcionais
3. **Exportar PDF**
4. Verificar: paisagem, 9 colunas alinhadas, cabeçalho com filtros, rodapé com páginas
5. Confirmar XLSX e PDF de notícias ainda funcionam

## Limitações restantes

- Links do edital não entram na tabela (use XLSX para URLs completas).
- Descrições longas não são exportadas no PDF tabular.
- Relatório detalhado por edital continua no fluxo de pré-cadastro (`precadastroProjetoPdf`).

## Arquivos

- `src/services/pdfExportService.js` — `exportEditaisToPdf`
- `src/utils/pdf/editaisPdfFormatters.js` — formatadores e linhas
- `src/pages/EditaisPage.jsx` — chama `exportEditaisToPdf`
