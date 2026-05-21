# Perfil consultivo do cliente

## Objetivo

Enriquecer o cadastro de clientes no **Workspace do Consultor** para reduzir “Não informado” no pré-projeto e no PDF, sem obrigar preenchimento completo e sem quebrar clientes antigos nem o score do Radar.

## Armazenamento

| Origem | Onde salva |
|--------|------------|
| Dados já existentes na tabela `cliente` | Colunas diretas (`nome_empresa`, `cnpj`, `cidade`, `estado`, `cnae_principal`, `faturamento_anual`, `numero_funcionarios`, `area_inovacao`, `descricao_projeto`, `interesse_*`, etc.) |
| Perfil consultivo estendido | `extras.perfil_consultivo` (JSONB) |

Se a coluna `extras` não existir no banco, aplicar manualmente:

`docs/sql/ALTER_CLIENTE_ADD_PERFIL_CONSULTIVO.sql`

## Estrutura `extras.perfil_consultivo`

- `contato` — nome, cargo, e-mail, telefone, CPF, observações  
- `localizacao` — país, unidade de execução, início de operação  
- `dados_economicos` — EBITDA, grupo econômico, faixa, contrapartida  
- `perfil_tecnologico` — atividades, áreas, maturidade, P&D, ICTs, portfólio  
- `preferencias_fomento` — tipos de recurso, internacional, licitação, prazos, fontes  
- `documentacao` — flags sim/não + observações  
- `diagnostico_consultor` — diagnóstico, lacunas, riscos, próximas ações  

## Código frontend

| Módulo | Função |
|--------|--------|
| `utils/cliente/clientePerfilConsultivo.js` | Estado do form, payload de gravação, merge de `extras`, `clienteEnrichedForApps` |
| `utils/cliente/calculateClientProfileCompleteness.js` | Score 0–100% e lacunas recomendadas |
| `utils/normalizeCliente.js` | Expõe `perfilConsultivo`, `contatoPrincipal`, etc. |
| `components/admin/ClientForm.jsx` | Formulário em abas (Workspace + Cadastros admin) |
| `components/consultor/ConsultorClientProfileCard.jsx` | Card no painel do cliente |

## Uso no Workspace

1. **Briefing rápido (entrada principal para perfil incompleto)** — callout (completude &lt; 50%), card **Perfil do cliente** e esteira (etapa 1). Botão **Fazer briefing rápido** é CTA principal quando completude &lt; 70%; vira **Atualizar briefing** com menos destaque quando ≥ 70%.  
2. **Cadastro completo** — **Novo / Editar cliente** / **Completar cadastro** via `ClientForm` (abas, badge de completude).  
3. **Briefing rápido (modal)** — `ConsultorClientBriefingModal`: 8 blocos A–H, tempo estimado 3–5 min, merge em `extras.perfil_consultivo`; footer: Cancelar, Salvar briefing, Salvar e abrir cadastro completo.  
4. **Salvar cliente** — mínimo: nome fantasia ou razão social.  
5. **Card “Perfil do cliente”** — % completo, lacunas, CTAs ordenados por completude.  

### Briefing rápido vs cadastro completo

| | Briefing rápido | Cadastro completo (`ClientForm`) |
|--|-----------------|----------------------------------|
| Objetivo | Coletar o essencial em minutos | Perfil consultivo completo (8 abas) |
| Quando usar | Perfil baixo, início da consultoria, antes da triagem/pré-projeto | Complementar dados, abas específicas, revisão profunda |
| UI | Uma tela, seções A–H | Abas, muitos campos |
| Obrigatório | Não | Não |
| Persistência | `mergeClientWritePayload` + campos legados (`descricao_projeto`, `area_inovacao`, `interesse_valor_*`) |
| Campos extras | `contexto_cliente`, `descricao_projeto`, `temas_prioritarios`, `faixa_valor_interesse`, `criterios_aceite`, `documentos_disponiveis` em `perfil_consultivo` |

Textos vazios no briefing **não** sobrescrevem valores já preenchidos (merge conservador em textareas).

**Sinal de briefing salvo (sem schema novo):** `hasBriefingContent()` em `clientBriefingSignals.js` — contexto, projeto, temas, tipos de recurso, faixa de valor, critérios, documentos ou observações em `extras.perfil_consultivo`.

**Efeito esperado:** melhora completude no card; badge na esteira (Briefing recomendado / pendente / salvo); `buildPreCadastroDraft` usa dados para sugestões e reduz pendências; carteira/triagem se beneficiam de temas e critérios (Radar score inalterado).

**Plano de ação:** com perfil &lt; 70% e sem briefing, o card **Plano de ação do consultor** sugere “Fazer briefing” (ação alta). Após salvar briefing, a ação some ou o consultor pode marcá-la como concluída em `localStorage`.

Logs DEV: prefixo `[cliente-briefing]` — `cta_visible`, `cta_click_profile_card`, `cta_click_callout`, `modal_open`, `save_success`, `save_and_open_full_form`, `profile_completion_updated`.

## Uso no pré-projeto e PDF

- `buildPreCadastroDraft` e `buildInitialPrecadastroState` usam `clienteEnrichedForApps` para preencher blocos 1 e consultivos (contato, CNAE, receita, empregados, etc.).  
- Campos vazios viram pendências no rascunho, não “Não informado” repetido no relatório executivo do PDF.  
- Anexo técnico: se não houver dados econômicos, **uma** linha “Dados econômicos ainda não informados.”  

## Radar (futuro)

O score do Radar **não foi alterado**. Campos do briefing (temas, tipos de recurso, faixa de valor, critérios de aceite, internacional/licitação/contrapartida) ficam em `cliente` normalizado para evolução futura: afinidade temática, filtros e valor de interesse.

## Compatibilidade

- Clientes antigos sem `extras` continuam listando e abrindo; perfil vazio com defaults.  
- Edição preserva outras chaves em `extras` via `mergeClientWritePayload`.  
- Cadastros (admin) usa o mesmo `ClientForm` e o mesmo payload.  

## Logs DEV

Prefixo `[cliente-profile]`: `form_open`, `form_section_change`, `save_*`, `completeness_calculated`.
