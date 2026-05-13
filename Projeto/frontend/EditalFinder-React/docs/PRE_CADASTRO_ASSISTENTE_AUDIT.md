# Auditoria — Pré-cadastro de projeto (assistente)

## Componentes localizados

| Papel | Arquivo |
|-------|---------|
| Shell do modal, estado, PDF, envelope, abas | `src/components/admin/ProjetoPrecadastroForm.jsx` |
| Cabeçalho (cliente, edital, chips, salvar/PDF) | `src/components/admin/precadastro/PrecadastroHeader.jsx` |
| Abas (Visão geral, Contexto, Formulário completo) | `src/components/admin/precadastro/PrecadNavTabs.jsx` |
| Visão geral — snapshot cliente | `src/components/admin/precadastro/PrecadClienteSnapshot.jsx` |
| Visão geral — completude | `src/components/admin/precadastro/PrecadCompletionStatus.jsx` |
| Visão geral — próximos passos | `src/components/admin/precadastro/PrecadProximosPassos.jsx` |
| Pendências priorizadas + navegação | `src/components/admin/precadastro/PrecadPendenciasPanel.jsx` |
| Impactos sugeridos (setor) | `src/components/admin/precadastro/PrecadImpactHints.jsx` |
| Assistente (botões inteligentes) | `src/components/admin/precadastro/PrecadIntelToolbar.jsx` |
| Contexto — linhas de produto | `src/components/admin/precadastro/PrecadProductLines.jsx` |
| Contexto — projeto / narrativa (seções) | `src/components/admin/precadastro/PrecadProjectScope.jsx` |
| Contexto — aderência | `src/components/admin/precadastro/PrecadFitSection.jsx` |
| Contexto — observações | `src/components/admin/precadastro/PrecadObservations.jsx` |
| Recomendações / cartões | `src/components/admin/precadastro/PrecadRecommendationCard.jsx` |
| Resumo empresa (somente leitura) | `src/components/admin/precadastro/PrecadCompanyStrip.jsx` |
| Formulário completo legado | `src/components/admin/precadastro/PrecadLegacyFormBody.jsx` |
| Completude e pendências guiadas | `src/utils/precadastro/calculatePreCadastroCompleteness.js` |
| Rascunho inteligente / limpar auto | `src/utils/precadastro/buildPreCadastroDraft.js` |
| Impactos por setor (texto) | `src/utils/precadastro/preCadastroTemplates.js` |
| PDF (modelo + render) | `src/services/precadastroProjetoPdf.js`, `src/services/precadastroPdf/renderPreCadastroPdf.js`, `buildPreCadastroPdfModel.js` |

## Fluxo atual

1. Abre o modal a partir de **Clientes**; carrega envelope local (`loadPrecadEnvelope`) ou gera primeiro rascunho (`buildPreCadastroDraft`).
2. **Visão geral**: lê resumo do cliente, completude, status do pré-cadastro, pendências em três níveis, impactos sugeridos, recomendações.
3. **Contexto e projeto**: linhas de produto, narrativa em seções, enquadramento, observações.
4. **Formulário completo**: todas as seções técnicas; IDs de âncora para navegação a partir das pendências.
5. **Salvar rascunho** / **Pré-visualizar PDF** / **Baixar PDF** — mesma pipeline `exportPrecadastroProjetoPdf` / `buildPrecadastroProjetoPdfBlob`.

## Problemas corrigidos nesta fase (antes)

- Visão geral pouco narrativa; pendências só em listas simples.
- Assistente sem explicação por botão; “Preencher lacunas” sem confirmação.
- Impactos só em 3 colunas; falta clareza tecnológica/estratégica.
- Projeto/escopo sem agrupamento temático.

## Riscos

- **Somente front**: completude e pendências derivam de regras locais; podem divergir de validação futura no servidor.
- **Navegação por âncora** em outra aba depende de `setTab` + duplo `requestAnimationFrame` para o DOM montar.
- **Listas grandes de pendências** em telas estreitas: uso de grid responsivo.

## Plano aplicado (Fase 2)

- Enriquecer `getPendenciasGuiadas` com motivo, ação e navegação.
- Reorganizar Visão geral (snapshot, cards, impactos, recomendações).
- Confirmar ações destrutivas/preenchimento em massa no assistente.
- Seções em `PrecadProjectScope` e cinco eixos em impactos sugeridos.
- IDs estáveis no formulário completo para saltos das pendências.
