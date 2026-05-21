# Pré-projeto consultivo — melhorias (Cadastros > Clientes)

**Data:** 2026-05-18  
**Escopo:** fazedor consultivo + **integração no Workspace** (modal, card de status, gerar a partir de oportunidade). Cadastros mantém acesso admin legado.

**Esteira Workspace (2026-05):** perfil → carteira (Radar) → triagem/seleção (lista ou tabela no modal) → pré-projeto consultivo → relatório/exportação (*em breve*). Ver secção 14 em [`CONSULTOR_WORKSPACE_PLAN.md`](./CONSULTOR_WORKSPACE_PLAN.md).

---

## 1. Estado atual (auditoria)

### Artefatos principais

| Artefato | Caminho | Função |
|----------|---------|--------|
| Formulário | `frontend/EditalFinder-React/src/components/admin/ProjetoPrecadastroForm.jsx` | Modal em Cadastros; abas consultivas + formulário completo |
| Componentes UI | `src/components/admin/precadastro/*` | Header, abas, escopo, aderência, completude, PDF toolbar |
| Draft inteligente | `src/utils/precadastro/buildPreCadastroDraft.js` | Autofill cliente + edital + Radar (sem alterar score) |
| Estado inicial | `src/utils/precadastroProjetoInitialState.js` | Campos `bloco_*`, envelope v2, `migratePrecadForm` |
| Completude | `src/utils/precadastro/calculatePreCadastroCompleteness.js` | Score + pendências consultivas |
| Textos | `src/utils/precadastro/preCadastroTemplates.js`, `projectIntel.js`, `consultorAutofill.js` | Linguagem consultiva |
| PDF | `src/services/precadastroProjetoPdf.js`, `precadastroPdf/buildPreCadastroPdfModel.js`, `renderPreCadastroPdf.js` | Capa + resumo + seções legado |
| Integração Workspace (1 opp.) | `openPreProjetoFromOpportunity.js` | Wrapper → `openPreProjetoFromOpportunities` |
| Integração Workspace (N opp.) | `openPreProjetoFromOpportunities.js`, `multiOpportunityAutofill.js`, `opportunitySelection.js` | 1–20 oportunidades; principal por score; PDF enxuto |

### Persistência local

- **Rascunho:** `precadastro_draft_{id_cliente}_{fingerprint}` (envelope v2: `form`, `fieldIntel`, `draftMeta`)
- **Legado:** `precadastro_projeto_{id_cliente}` (ainda lido como fallback)
- **Contexto oportunidade:** `precadastro_context_{id_cliente}` em `sessionStorage` (título, score, id edital)

### O que já era preenchido automaticamente

- Dados do **cliente** (CNPJ, razão, porte, setor, receita, empregados, contato, etc.) — ver perfil consultivo em `docs/CLIENTE_PROFILE_CONSULTIVO.md` (`extras.perfil_consultivo` + colunas legadas)
- **Edital** (título, tipo recurso, refs financeiras quando existem na ficha)
- **Radar** (nível aderência derivado do score, razões, penalidades — sem recalcular score)
- Sugestões **heurísticas** (título, resumo, finalidades A–G, linhas de crédito sugeridas)

### Lacunas antes desta melhoria

- Abas pouco alinhadas ao fluxo consultivo (A–H)
- Documentos e riscos num único bloco genérico
- Pendências listavam só “campo vazio”, pouco acionáveis
- PDF sem página dedicada ao resumo consultivo estruturado
- Integração Workspace ainda manual via `sessionStorage`

---

## 2. Melhorias implementadas

### 2.1 Modelo consultivo (seções A–H)

| Seção | Campos principais (form) | Aba UI |
|-------|--------------------------|--------|
| **A) Resumo executivo** | `bloco_estr_*`, `bloco2_recursos_adicionais_valor`, status, score | Resumo |
| **B) Aderência** | `bloco_estr_motivo_recomendacao`, `principais_aderencias`, `lacunas`, etc. | Aderência |
| **C) Escopo** | problema, solução, diferencial, resultados | Escopo e plano |
| **D) Plano de trabalho** | `bloco_estr_plano_trabalho` + metas no formulário completo | Escopo e plano |
| **E) Orçamento** | `bloco_estr_orcamento_*`, `bloco_estr_ref_fin_texto` | Orçamento |
| **F) Documentos** | `bloco_estr_docs_cliente/tecnicos/financeiros/edital` + agregado legado | Riscos e passos |
| **G) Riscos** | `bloco_estr_riscos_pendencias`, `alertas_radar`, checklist | Riscos e passos |
| **H) Próximos passos** | `bloco_estr_proximos_passos` | Riscos e passos |

### 2.2 Campos novos (compatíveis com rascunhos antigos)

Defaults vazios via `migratePrecadForm()` ao carregar `localStorage`:

- `bloco_estr_oportunidade_fonte`, `_prazo`, `_link`
- `bloco_estr_score_compatibilidade`, `bloco_estr_alertas_radar`
- `bloco_estr_plano_trabalho`
- `bloco_estr_orcamento_resumo`, `_contrapartida`, `_categorias`, `_observacoes`
- `bloco_estr_docs_cliente`, `_tecnicos`, `_financeiros`, `_edital_regulamento`
- `bloco_estr_riscos_pendencias`, `bloco_estr_checklist_inicial`

**Nenhum campo antigo foi removido.**

### 2.3 Autofill (`buildPreCadastroDraft`)

Quando há `cliente` + `edital` + `radarMatch`:

- Resumo executivo e narrativa de aderência em linguagem consultiva
- Meta da oportunidade (fonte, prazo, link)
- Score/compatibilidade como texto (não altera o motor do Radar)
- Alertas e razões positivas do Radar
- Documentos por categoria + checklist inicial
- Plano de trabalho, orçamento preliminar, riscos, próximos passos

Logs DEV: `[precadastro] draft_autofill_start|success|missing_context`

### 2.4 Completude

- Pesos revisados (obrigatório / recomendado / seções consultivas)
- `consultivePendencies[]` — ações (“Completar resumo para apresentar ao cliente”, etc.)
- Badges na UI: aderência, documentos, riscos, orçamento, cronograma

### 2.5 UX

- Abas: Visão geral · Resumo · Aderência · Escopo e plano · Orçamento · Riscos e passos · Formulário completo
- Botão **Gerar sugestões automáticas** (toolbar)
- Painel de pendências com bloco “Para fechar com o cliente”
- Hints curtos por seção (`PrecadSectionHint`)

### 2.6 PDF

- Nova página **Proposta consultiva (resumo)** com seções A–H no PDF (`consultorSections` no model)
- Capa e fluxo legado preservados

### 2.7 Integração Workspace (implementada)

| Fluxo | Onde |
|-------|------|
| Abrir pré-projeto do cliente | `ConsultorWorkspace` → card Pré-projeto / botão no topo |
| Gerar por oportunidade | `ConsultorOpportunityPipeline` → `openPreProjetoFromOpportunity` + modal |
| Resumo rascunho | `getClientPrecadSummary` (localStorage, sem apagar chaves antigas) |
| Cadastros consultor | Banner “Ir para Workspace”; aba Clientes só para **admin** |

```javascript
import { openPreProjetoFromOpportunity } from '../utils/precadastro/openPreProjetoFromOpportunity';
import { radarRowToPrecadPayload } from '../utils/consultor/radarRowToPrecad';
```

### 2.4 Pré-projeto a partir de várias oportunidades (Workspace)

| Regra | Comportamento |
|-------|----------------|
| Seleção | 1 a `MAX_PREPROJECT_OPPORTUNITIES` (20) no painel top 20 ou no modal “todas as oportunidades” (mesmo estado) |
| Principal | Maior `scorePct`; com uma só, ela é a principal |
| Complementares | Até 5 prioritárias (maior score após a principal) — detalhe no resumo/aderência/documentos |
| Em observação | Restantes selecionadas — título/score/fonte resumidos (evita PDF gigante) |
| Campo local | `bloco_estr_oportunidades_selecionadas` — JSON com id, título, fonte, score, prazo, link |
| UI | `PrecadOpportunitiesConsidered` na aba **Visão geral** |
| Fluxo antigo | `openPreProjetoFromOpportunity({ cliente, edital, radarMatch })` inalterado para Cadastros e chamadas legadas |
| Schema | Nenhuma alteração em Supabase |

---

## 3. Riscos e próximos passos

| Item | Notas |
|------|--------|
| Edital rico no contexto | Hoje `sessionStorage` costuma trazer só título/score; passar objeto edital completo melhora autofill |
| PDF longo | Formulário completo no PDF inalterado; possível sumário interativo em fase posterior |
| Testes E2E | Validar clientes com rascunho v1 no `localStorage` após deploy |
| Workspace multi | Definir principal manualmente na UI (fase futura); hoje automático por score |

---

## 4. Critérios de aceite

- [x] Pré-projeto em Cadastros continua abrindo
- [x] Rascunhos antigos migrados com defaults (`migratePrecadForm`)
- [x] Seções consultivas A–H na UI
- [x] Autofill enriquecido com Radar/edital
- [x] Completude e pendências consultivas
- [x] Build frontend OK
- [x] Seleção múltipla no Workspace (1–10) com rascunho multi e compatibilidade single-opp
