# Pré-cadastro de projeto — auditoria UX/PDF (frontend)

**Data:** 2026-05-10

## Ficheiros envolvidos

| Área | Caminho |
|------|---------|
| Entrada (Cadastros + modal) | `src/pages/Cadastros.jsx` — botão “Pré-cadastro projeto”, modal `modal-large modal-precad` |
| Formulário shell | `src/components/admin/ProjetoPrecadastroForm.jsx` |
| Cabeçalho e ações | `src/components/admin/precadastro/PrecadastroHeader.jsx` |
| Assistente / toolbar | `src/components/admin/precadastro/PrecadIntelToolbar.jsx` |
| Abas | `src/components/admin/precadastro/PrecadNavTabs.jsx` |
| Secções de conteúdo | `PrecadCompanyStrip`, `PrecadProductLines`, `PrecadProjectScope`, `PrecadFitSection`, `PrecadObservations`, `PrecadLegacyFormBody`, `PrecadCompletionStatus`, `PrecadPendenciasPanel`, etc. |
| Estado / rascunho | `src/utils/precadastroProjetoInitialState.js`, `src/utils/precadastro/buildPreCadastroDraft.js` |
| PDF — API | `src/services/precadastroProjetoPdf.js` — `exportPrecadastroProjetoPdf`, `buildPrecadastroProjetoPdfBlob` |
| PDF — render | `src/services/precadastroPdf/renderPreCadastroPdf.js` (`jsPDF` + `jspdf-autotable`) |
| Modelo PDF | `src/services/precadastroPdf/buildPreCadastroPdfModel.js`, `src/utils/precadastro/pdfModel.js` |
| Estilos modal / precad | `src/styles/global.css` (blocos `.modal-precad`, `.precad-*`) |

## Fluxo atual

1. Utilizador em **Cadastros** → separador com clientes → **Pré-cadastro projeto** abre modal com `ProjetoPrecadastroForm`.
2. Form carrega envelope em `localStorage` ou gera rascunho inteligente (`buildPreCadastroDraft`).
3. Três abas principais: **Visão geral**, **Contexto e projeto**, **Formulário completo** (`PrecadNavTabs` + `tab` state).
4. **Salvar rascunho** → `savePrecadEnvelope` (localStorage, sem backend).
5. **Baixar PDF** / **Pré-visualizar PDF** → `exportPrecadastroProjetoPdf` / `buildPrecadastroProjetoPdfBlob` → `renderPreCadastroDocument` → `stampFooters` → ficheiro ou `blob` para nova aba.

## Onde o PDF é gerado

- **Bibliotecas:** `jspdf`, `jspdf-autotable` (não é captura html2canvas da UI).
- Desenho vetorial: texto, retângulos, tabelas — ver `renderPreCadastroDocument` em `renderPreCadastroPdf.js`.

## Causa provável da sobreposição (antes do fix)

1. **Declaração e assinatura:** o `banner` “Declaração e assinatura” era desenhado numa posição Y, mas o `doc.text` da declaração usava `doc.lastAutoTable.finalY + 18` **sem** considerar o fim do banner — sobreposição banner ↔ texto.
2. **Texto longo:** `splitTextToSize` gerava várias linhas, mas o código tratava como um único bloco Y — linhas adicionais invadiam a caixa de assinatura.
3. **Assinatura:** `boxTop = Math.max(..., ph - 90)` e `rect(..., boxTop - 68, ...)` posicionavam a caixa de forma independente do fim real do texto da declaração → sobreposição.
4. **Impactos / condições:** `startY` de algumas tabelas não seguia o retorno do `banner` anterior (só `lastAutoTable`), podendo sobrepor faixas coloridas.

## Riscos antes de alterar

- Alterar `buildPreCadastroPdfModel` muda conteúdo semântico do PDF.
- Alterações amplas em `jspdf-autotable` podem deslocar quebras de página.
- Mudanças no `Header` não podem remover a rota `/indice` do router (apenas menu).
- `Portais Estratégicos` e motor do Radar não devem ser tocados.
