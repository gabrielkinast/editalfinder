# Política de retenção, expiração e visibilidade pública — EditalFinder

Documento de **política de produto e dados** (não é especificação de implementação nesta fase). Define o que permanece no banco, o que deixa de aparecer nas **views públicas** do frontend e como tratar conteúdo institucional.

**Princípio geral:** o EditalFinder **não apaga fisicamente** oportunidades, notícias, pesquisas ou editais por terem passado prazo ou janela temporal. O histórico fica nas tabelas base; a **listagem pública** é controlada por views (`vw_*_front`), flags (`ativo`) e, quando aplicável, `status` operacional.

---

## Objetivos

| Objetivo | Descrição |
|----------|-----------|
| **Histórico** | Auditoria, favoritos futuros, alertas, reprocessamento e análises internas |
| **Clareza para o utilizador** | Listagens mostram sobretudo oportunidades e conteúdos **ainda relevantes** |
| **Sem delete em massa** | Evitar `DELETE` automático por vencimento; preferir despublicação lógica via view + metadados |
| **Domínios separados** | Regras distintas para concursos, editais/fomento, notícias e pesquisas |

---

## Modelo conceitual

```text
┌─────────────────┐     sempre persiste      ┌──────────────────────┐
│  Tabela base    │ ────────────────────────► │  Histórico completo   │
│  (concurso,     │                           │  (consultas admin,    │
│   edital,       │                           │   reprocessamento)    │
│   noticia,       │                           └──────────────────────┘
│   pesquisa)     │
└────────┬────────┘
         │
         │  filtro de recência / status / ativo
         ▼
┌─────────────────┐
│  View pública   │  ◄── Frontend (Editais, Radar, Concursos, Notícias, Pesquisas)
│  vw_*_front     │
└─────────────────┘
```

| Mecanismo | Uso |
|-----------|-----|
| **View SQL** | Critério canónico do que o utilizador anónimo/autenticado vê na listagem padrão |
| **`ativo = false`** | Despublicação explícita (erro de fonte, duplicado, pedido legal) — fora de qualquer view pública |
| **`status` (domínio)** | Estado de negócio do certame/chamada (ex.: `encerrado`, `inscricoes_encerradas`) — não substitui a view, complementa UX e filtros futuros |
| **Janela por data** | Aplicada na view (ou equivalente no cliente **apenas** se documentado como exceção) |

**Não confundir:**

- **`ativo` (coluna)** — registo publicado no produto sim/não (soft delete).
- **`status` (concurso/edital)** — fase do processo (aberto, encerrado, em andamento).
- **“Expirado”** — conceito de política: deixa de cumprir critérios da view pública; o registo **permanece** na tabela.

---

## 1. Concursos e seleções (`public.concurso_selecao`)

Módulo **Concursos & Seleções** — separado de `public.edital` e do Radar. Consumo público típico: `vw_concursos_front` (ver [`CONCURSOS_FRONTEND_MVP.md`](./CONCURSOS_FRONTEND_MVP.md)).

### 1.1 Sair da view pública (oportunidade principal encerrada)

Um registo **deixa de aparecer** na listagem pública padrão quando **todas** as condições abaixo forem verdadeiras:

1. `ativo = true` (continua no banco; se `ativo = false`, já está fora por despublicação).
2. `validacao_status` continua nos valores aceites pela view (`valido`, `incompleto`, etc. — ver DDL vigente).
3. **Inscrição encerrada:** `data_fim_inscricao` existe e é **anterior a hoje** (data de referência: timezone do produto / `CURRENT_DATE` no SQL, a alinhar em implementação).
4. **Prova também passada ou ausente:** `data_prova` é **anterior a hoje** **ou** `data_prova` é `NULL`.

Interpretação:

| `data_fim_inscricao` | `data_prova` | View pública padrão |
|----------------------|--------------|---------------------|
| futura ou hoje | qualquer | **Pode aparecer** (oportunidade ativa ou prova futura) |
| passada | futura ou hoje | **Pode aparecer** (ainda há marco temporal relevante) |
| passada | passada ou ausente | **Não aparece** (encerrado para listagem principal) |
| ausente | passada ou ausente | Seguir regra de **recência alternativa** já usada no loader/view (ex.: `data_publicacao` ou `created_at` nos últimos 90 dias) **até** política única ser consolidada — ver §1.4 |

Esta regra alinha-se ao espírito de `recency_should_discard` nos crawlers e aos avisos de `expired_items_count` no loader ([`CONCURSOS_LOADER_MVP.md`](./CONCURSOS_LOADER_MVP.md)).

### 1.2 Status operacional

Quando o critério §1.1 se aplica e o payload **não** fixa `status` explicitamente:

- O loader pode normalizar para **`status = encerrado`** (comportamento já documentado no loader MVP).
- Na view pública, registos com `status` em valores de fim (`encerrado`, `cancelado`, `suspenso` — conjunto exato conforme CHECK SQL) **não** devem ser promovidos como oportunidade principal.

Se o ficheiro standardized ou o operador definir `status`, **respeitar** o valor gravado.

### 1.3 Concursos em andamento sem inscrição aberta

Certames **em andamento** (prova futura, homologação, segunda fase) mas com **inscrições já fechadas**:

| Aspeto | Política |
|--------|----------|
| **Listagem pública padrão** | **Não** tratar como oportunidade principal (mesma lógica: inscrição passada + sem prova futura → fora; com prova futura → pode permanecer) |
| **`status` sugerido** | `inscricoes_encerradas` ou equivalente documentado no enum de produto, quando existir |
| **Futuro** | Filtro ou aba **“Em andamento”** pode incluir estes registos de forma explícita, sem misturá-los com “Inscrições abertas” |

### 1.4 Exceção de recência (transição)

Enquanto coexistir a regra legada na view (`data_publicacao` / `created_at` nos últimos 90 dias sem datas de inscrição/prova), documentar como **exceção temporária**:

- Itens **sem** `data_fim_inscricao` e **sem** `data_prova` podem ainda aparecer se forem “recentes”.
- Meta de consolidação: §1.1 como regra única; exceção 90 dias apenas para dados incompletos com `validacao_status = incompleto`.

### 1.5 O que nunca fazer automaticamente

- `DELETE` em `public.concurso_selecao` por vencimento.
- Remover linhas do banco porque o crawler deixou de as enviar num lote (upsert não implica delete — já documentado no loader).

---

## 2. Notícias (`public.noticia`)

Módulo **Notícias** — conteúdo jornalístico / institucional de atualidade. **Não** é edital; **não** entra no Radar. Consumo: `vw_noticias_front` ([`FRONTEND_BACKEND_CONTEXT.md`](./FRONTEND_BACKEND_CONTEXT.md)).

### 2.1 Janela pública padrão

| Parâmetro | Valor |
|-----------|--------|
| **Janela** | **12 meses** rolling a partir de `data_publicacao` (ou data canónica equivalente na view) |
| **Campo de referência** | `data_publicacao` (ISO date); se ausente, política de qualidade: `validacao_status = incompleto` e tendência a **não** promover na view até haver data |
| **Histórico** | Registos mais antigos permanecem em `public.noticia` |

### 2.2 Crawlers e pipelines

- Crawlers news/research usam `time_window_months: 12` na config ([`config/news_research_sources.json`](../config/news_research_sources.json), [`audit_reports_news_research/expansion_plan.md`](../audit_reports_news_research/expansion_plan.md)).
- Itens fora da janela no crawl podem ser **descartados no standardized** ou ingeridos com flag em `extras` — a **view pública** é a fronteira final de 12 meses.

### 2.3 Conteúdo institucional

Ver §6 — notícias institucionais **não** seguem a mesma regra de expiração que notícia editorial comum quando forem classificadas como tal no `extras` / taxonomia.

---

## 3. Pesquisas e artigos (`public.pesquisa`)

Módulo **Pesquisas** — publicações, relatórios técnicos, documentos de P&D. Consumo: `vw_pesquisas_front`.

### 3.1 Janela pública padrão

| Parâmetro | Valor |
|-----------|--------|
| **Janela** | **24 meses** rolling |
| **Campo de referência** | `data_publicacao` (ou `data_publicacao` + fallback documentado na view) |
| **Histórico** | Mantido na tabela |

### 3.2 Relação com BRISA Artigos e fontes longas

- Feed **BRISA Artigos** (`brisa_artigos`, `https://brisabr.com.br/artigos/feed/`) mapeia para **`pesquisa`** com janela **24m** — não `noticia`; permalinks WordPress podem ser slug na raiz (sem `/artigos/` no path). Ver piloto em `audit_reports_news_research/brisa_artigos_dryrun/` ([`STRATEGIC_NEWS_RESEARCH_SOURCES.md`](./STRATEGIC_NEWS_RESEARCH_SOURCES.md)).
- Janela de **24 meses** aplica-se a esses itens na aba Pesquisas.

### 3.3 Crawlers

- Config pode usar `time_window_months: 24` para fontes predominantemente pesquisa/publicação.
- NASA/DARPA/IAEA mistos (notícia + pesquisa) roteiam por `tipo_conteudo` no standardized; a janela da view segue o **destino** (`noticia` → 12m, `pesquisa` → 24m).

---

## 4. Editais e chamadas de fomento (`public.edital`)

Oportunidades com **prazo de submissão / inscrição** (Finep, CNPq, FAPESP, chamadas internacionais, etc.). Alimentam **Editais** e **Radar de Fomento** via `vw_editais_front` — **não** misturar com `portal_estrategico` nem com notícias.

### 4.1 Sair da view pública

Um edital **deixa de aparecer** na listagem pública quando:

1. `ativo = true` (registo ainda “publicado” no sistema).
2. O **prazo de submissão/inscrição** está encerrado: campo canónico **`prazo_envio`** (ou alias na view: `fim_inscricao`) **anterior a hoje**.
3. Opcionalmente, regras complementares já existentes no produto (ex.: status cancelado, `validacao_status` excluído da view) permanecem vigentes.

Se **não** existir `prazo_envio` / data fim:

- Tratar como dado incompleto; manter política conservadora (pode permanecer visível com flag de qualidade ou sair por regra de “sem prazo há X meses” — a definir em implementação alinhada ao Radar).
- **Não** inventar prazo na política de retenção.

### 4.2 Histórico e Radar

- Registos fora da view **permanecem** para histórico, favoritos ([`EDITAIS_FAVORITOS_ALERTAS_MVP.md`](./EDITAIS_FAVORITOS_ALERTAS_MVP.md)) e auditoria.
- Radar agrega **editais com oportunidade ainda relevante**; edital “expirado” não deve poluir o feed principal.

### 4.3 Promoção desde news/research

Itens do módulo notícias/pesquisas com BAA/RFI/edital explícito vão para **`review_for_edital`**, não para `public.noticia` ([`audit_reports_news_research/expansion_plan.md`](../audit_reports_news_research/expansion_plan.md)). Após aprovação e carga em `public.edital`, aplicam-se as regras desta secção.

### 4.4 Ruído e visibilidade (curadoria)

Além do prazo, a listagem pública pode excluir ruído institucional, resultados antigos, links quebrados e conteúdo que não é oportunidade via:

- **`extras.curadoria_front`** — preenchido por auditoria (`scripts/audit_editais_visibility_noise.py`), aplicado manualmente;
- **View** `vw_editais_front` — DDL em [`sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql`](./sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql);
- **Política completa:** [`EDITAIS_VISIBILITY_AND_NOISE_POLICY.md`](./EDITAIS_VISIBILITY_AND_NOISE_POLICY.md).

**Não** usar `DELETE` para “limpar” a aba Editais.

### 4.5 Aplicação da curadoria (etapa 1 segura)

Metadados em `extras.curadoria_front` (e `extras.link_health` para Grants quebrados) aplicados **manualmente** via SQL:

- **Etapa 1:** [`sql/APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql`](./sql/APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql) — institucional, resultado, duplicata, link inválido (sem `hidden_historical` nem `review_*`).
- **Plano:** `audit_reports_main_pipeline/editais_visibility_noise_global/step1_apply_plan.md`
- Depois da etapa 1, ativar filtro na view: [`sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql`](./sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql).

Registros permanecem em `public.edital`; apenas deixam de aparecer na listagem pública quando a view e a curadoria assim o indicam.

---

## 5. Portais estratégicos (`public.portal_estrategico`)

Fornecedores, investimentos, procurement — **não** são concursos nem editais com prazo. Regras em documentação de portais ([`FRONTEND_BACKEND_CONTEXT.md`](./FRONTEND_BACKEND_CONTEXT.md), loaders dedicados).

| Aspeto | Política |
|--------|----------|
| **Expiração automática por data** | **Não** aplicar as janelas 12m/24m de notícias/pesquisas |
| **Despublicação** | `ativo = false` ou flags `mostrar_em_*` conforme produto |
| **Radar** | `mostrar_no_radar = false` por defeito para não misturar com fomento |

---

## 6. Conteúdo institucional

Páginas estáveis: “Sobre”, “Como participar”, regulamentos permanentes, hubs informativos sem data de notícia, landing de programa sem ciclo fechado.

| Regra | Detalhe |
|-------|---------|
| **Classificação** | Marcar em `extras` (ex.: `conteudo_institucional: true`, `tipo_conteudo: institucional`) na ingestão |
| **Expiração automática** | **Não** expirar por janela 12m/24m |
| **View Notícias** | **Não** listar como notícia comum; rota dedicada, rodapé, ou CMS estático fora do feed |
| **Concursos** | Páginas índice de órgão sem edital ativo não geram linha em `concurso_selecao` |

---

## 7. Resumo por domínio

| Domínio | Tabela base | View pública típica | Sai da view quando | Janela histórica no banco |
|---------|-------------|---------------------|--------------------|---------------------------|
| Concursos / seleções | `concurso_selecao` | `vw_concursos_front` | Inscrição passada **e** (prova passada ou ausente); status de encerramento | Ilimitado (`ativo`) |
| Em andamento s/ inscrição | idem | idem (não como “abertas”) | Inscrição passada, prova futura → filtro futuro “em andamento” | idem |
| Notícias | `noticia` | `vw_noticias_front` | `data_publicacao` anterior a hoje − 12 meses | Ilimitado |
| Pesquisas / artigos | `pesquisa` | `vw_pesquisas_front` | `data_publicacao` anterior a hoje − 24 meses | Ilimitado |
| Editais / chamadas | `edital` | `vw_editais_front` | `prazo_envio` (fim inscrição) anterior a hoje | Ilimitado |
| Portais estratégicos | `portal_estrategico` | filtros por categoria | Despublicação manual / `ativo` | Ilimitado |
| Institucional | vários | fora do feed | N/A (não entra no feed) | Ilimitado |

---

## 8. Implementação futura (fora do âmbito deste documento)

Quando for hora de codificar, priorizar:

1. **SQL único** por view (`vw_concursos_front`, `vw_noticias_front`, `vw_pesquisas_front`, `vw_editais_front`) alinhado a este doc.
2. **Testes** de regressão: registo encerrado permanece em `SELECT * FROM tabela` mas ausente em `vw_*_front`.
3. **Admin / arquivo** (opcional): ecrã ou filtro “Ver histórico / encerrados” sem alterar a listagem padrão.
4. **Documentar** `data_referencia` (UTC vs America/Sao_Paulo) num único sítio técnico.

**Explicitamente fora de escopo nesta política:** política de backup, LGPD/anonymização, e retenção de logs de crawler.

---

## 9. Documentos relacionados

| Documento | Ligação |
|-----------|---------|
| [`CONCURSOS_LOADER_MVP.md`](./CONCURSOS_LOADER_MVP.md) | Upsert sem delete; `encerrado`; avisos `expired_items_count` vs view |
| [`CONCURSOS_FRONTEND_MVP.md`](./CONCURSOS_FRONTEND_MVP.md) | Consumo de `vw_concursos_front` |
| [`CONCURSOS_SELECOES_MODULE_PLAN.md`](./CONCURSOS_SELECOES_MODULE_PLAN.md) | Modelo `concurso_selecao`, `status`, `ativo` |
| [`CONCURSOS_SELECOES_SCHEMA.md`](./CONCURSOS_SELECOES_SCHEMA.md) | Diferença face a `public.edital` |
| [`FRONTEND_BACKEND_CONTEXT.md`](./FRONTEND_BACKEND_CONTEXT.md) | Tabelas e views por módulo |
| [`audit_reports_news_research/expansion_plan.md`](../audit_reports_news_research/expansion_plan.md) | Governança news/research; janelas de crawl |
| [`STRATEGIC_NEWS_RESEARCH_SOURCES.md`](./STRATEGIC_NEWS_RESEARCH_SOURCES.md) | Fontes BR; roteamento notícia vs pesquisa vs edital |
| [`sql/UPDATE_VW_CONCURSOS_FRONT_RECENCY.sql`](./sql/UPDATE_VW_CONCURSOS_FRONT_RECENCY.sql) | Implementação atual (parcial) da recência de concursos |

---

*Versão: 2026-05-17. Política aprovada em documentação; implementação SQL/frontend pode divergir até alinhamento explícito.*
