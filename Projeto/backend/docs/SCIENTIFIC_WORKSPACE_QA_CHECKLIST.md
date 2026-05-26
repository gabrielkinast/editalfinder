# QA — Workspace Científico

Rota: `/workspace-cientifico` · Flag: `VITE_ENABLE_SCIENTIFIC_WORKSPACE=true`

**Legenda:** OK = comportamento esperado verificado manualmente.

---

## Fase 2M — Fluxo completo de estudo (checklist obrigatório)

Marque cada item após testar no navegador (F5 entre persistência e recarga).

| # | Passo | Critério de sucesso |
|---|--------|---------------------|
| 1 | Selecionar interesses | Chips persistem; trilhas aparecem |
| 2 | Gerar rota | Card “Minha rota” com passos e CTA |
| 3 | Abrir trilha | Acordeão expande; abas Teoria/Livros/etc. |
| 4 | Buscar tópico | Filtro de busca na trilha reduz lista |
| 5 | Marcar tópico como Estudando | Select de status; toast/log opcional |
| 6 | Marcar ideia poderosa como Dominado | Abre modal de verificação |
| 7 | Verificar modal de domínio | Perguntas + confirmar; não crash |
| 8 | Confirmar XP | Toast +XP; histórico XP atualiza |
| 9 | Salvar livro no caderno | Toast “Salvo”; item no caderno |
| 10 | Atualizar progresso do livro | Modal livro; % e status Lendo/Lido |
| 11 | Iniciar sessão de estudo | Modal setup; ≥1 item selecionado |
| 12 | Finalizar sessão | Reflexão salva; cronômetro para ao fechar |
| 13 | Conferir histórico | Card sessões lista a sessão |
| 14 | Conferir revisão ativa | Itens estudando/antigos visíveis |
| 15 | Exportar Markdown | Arquivo `.md` baixa (vazio ou completo) |
| 16 | Reportar problema manual | AppFeedback abre; origem workspace |
| 17 | Recarregar página (F5) | Sem erro; dados locais mantidos |
| 18 | Confirmar persistência | Progresso, XP, caderno, sessões intactos |

### Regressões 2M

- [ ] Caderno: salvar 2× o mesmo item → “Já salvo” ou atualiza, **sem duplicar**
- [ ] XP: dominar o mesmo item 2× → “XP já concedido”, log `xp_duplicate_prevented` (DEV)
- [ ] Sessão: botão iniciar desabilitado sem itens selecionados
- [ ] UI: status **Novo** / A estudar / Estudando (nunca `theory`, `none` cru)
- [ ] UI: tipos **Teoria**, **Livro**, **Ideia poderosa** (nunca `powerIdea` cru)
- [ ] DEV: painel Diagnóstico visível; produção **sem** painel
- [ ] DEV: Copiar diagnóstico → JSON no clipboard
- [ ] DEV: Reparar dados locais → não apaga dados válidos
- [ ] Export com workspace vazio → `.md` válido mínimo

---

## Fase 2F — Botões e dedup (referência)

| Área | Dedup / feedback |
|------|------------------|
| Caderno | `getScientificNotebookEntryKey`, `deduplicateNotebookItems` |
| Ideias | `deduplicateProjectIdeas` |
| Rota | Um salvar no card Minha rota |
| Scroll | `scientificScrollToSection` + toast |

---

## Diagnóstico DEV (Fase 2M)

| Ferramenta | Arquivo |
|------------|---------|
| Auditoria | `auditScientificWorkspaceState.js` |
| Reparo | `repairScientificWorkspaceState.js` |
| Painel | `ScientificWorkspaceDiagnosticsPanel.jsx` |

Logs padronizados: `[scientific-workspace]` + eventos:

- `workspace_audit_completed`
- `workspace_state_repaired`
- `xp_duplicate_prevented`
- `study_session_saved`
- `markdown_exported`
- `app_feedback_opened`

---

## Build

```bash
cd frontend/EditalFinder-React
npm run build
```
