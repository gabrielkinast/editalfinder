# Melhorias — Assistente de Pré-cadastro (Fase 2)

## Arquivos alterados

- `src/components/admin/ProjetoPrecadastroForm.jsx` — visão geral recomposta; `getPendenciasGuiadas`; confirmações no assistente; `navigatePendencia`; imports novos.
- `src/utils/precadastro/calculatePreCadastroCompleteness.js` — definições com `motivo`, `acaoSugerida`, `tab`, `anchorId`; export `getPendenciasGuiadas`.
- `src/utils/precadastro/preCadastroTemplates.js` — `hintImpactsForSector` retorna cinco eixos (`padCincoImpactos`); tecnologia com tecnológicos/estratégicos explícitos.
- `src/components/admin/precadastro/PrecadProjectScope.jsx` — seções: problema, objetivo, solução, público, maturidade, setor (callout), identificação (título/resumo), diferencial, resultados.
- `src/components/admin/precadastro/PrecadPendenciasPanel.jsx` — três níveis (alta / média / baixa) com motivo, ação e botão de navegação.
- `src/components/admin/precadastro/PrecadIntelToolbar.jsx` — texto explicativo por ação.
- `src/components/admin/precadastro/PrecadImpactHints.jsx` — cinco colunas + aviso de que são sugestões.
- `src/components/admin/precadastro/PrecadFitSection.jsx` — `id="precad-fit-aderencia"`.
- `src/components/admin/precadastro/PrecadObservations.jsx` — `id="precad-observacoes"`.
- `src/components/admin/precadastro/PrecadLegacyFormBody.jsx` — IDs em `<details>` para âncoras (cadastro, contato, econômicos, PD&I, recursos, impactos, licenças, fontes, metas).
- `src/components/admin/precadastro/PrecadClienteSnapshot.jsx` — **novo** (resumo cliente + strip).
- `src/components/admin/precadastro/PrecadProximosPassos.jsx` — **novo** (passos sugeridos + prévia de `bloco_estr_proximos_passos`).
- `src/styles/global.css` — estilos assistente, pendências, snapshot, próximos passos, subseções, intel detalhado.
- `docs/PRE_CADASTRO_ASSISTENTE_AUDIT.md`, `docs/PRE_CADASTRO_ASSISTENTE_IMPROVEMENTS.md`.

## Melhorias feitas

- **Visão geral**: intro do assistente; card de resumo do cliente (empresa, edital, aderência, strip); grade com completude, status do pré-cadastro e **Próximos passos**; pendências priorizadas; impactos em cinco dimensões; recomendações mantidas ao final.
- **Pendências**: alta = obrigatórias em falta; média = recomendadas; baixa = opcionais; cada item com motivo, ação e **Abrir no formulário** (troca de aba + scroll).
- **Assistente**: descrição sob cada botão; confirmação em **Preencher lacunas** e **Limpar sugestões** (alinhado a não alterar dados sem consentimento).
- **Contexto e projeto**: campos iguais, reorganizados em subseções com títulos e nota sobre setor cadastral.
- **Impactos**: econômico, social, ambiental, tecnológico, estratégico; texto reforçando que são sugestões.
- **Formulário completo**: IDs para navegação a partir das pendências.

## O que não foi alterado

- Backend, banco de dados, APIs.
- Lógica do Radar, Portais Estratégicos, geração binária do PDF (jsPDF) — sem mudança funcional intencional.
- `ProjetoPrecadastroForm` continua a usar os mesmos serviços de PDF e `savePrecadEnvelope`.

## Como testar

1. `npm run build` (deve passar).
2. Abrir **Cadastros → Clientes → Abrir pré-cadastro**.
3. Aba **Visão geral**: conferir snapshot, cards, pendências em três colunas, impactos em cinco blocos.
4. Clicar **Abrir no formulário** em uma pendência de aba **Formulário completo**: deve mudar de aba e rolar até a seção.
5. **Assistente**: testar confirmações em Preencher lacunas / Limpar sugestões; Gerar rascunho inteligente continua com confirmação.
6. **Salvar rascunho**, **Pré-visualizar PDF**, **Baixar PDF** como antes.

## Limitações restantes

- Regras de completude permanecem heurísticas locais.
- `scrollIntoView` pode falhar se o elemento ainda não estiver montado em condições muito lentas (mitigado com duplo frame).
- PDF não recebeu ajuste visual dedicado nesta fase (apenas fluxo preservado).
