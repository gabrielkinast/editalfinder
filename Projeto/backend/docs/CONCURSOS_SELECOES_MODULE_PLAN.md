# Plano de módulo — Concursos & Seleções (EditalFinder)

**Estado:** planeamento apenas — sem implementação, sem alterações a BD, frontend ou crawlers.

**Relação com o produto actual:** módulo **separado** de `public.edital` e do **Radar de Fomento**; público-alvo distinto (concursos públicos, seleções, vestibulares, bolsas de ingresso, etc.). Reutiliza padrões do ecossistema (Supabase Auth, clientes por utilizador, qualidade/validação) sem misturar entidades de fomento.

**Retenção e expiração (visibilidade pública):** [`DATA_RETENTION_AND_EXPIRATION_POLICY.md`](./DATA_RETENTION_AND_EXPIRATION_POLICY.md) — sem delete físico por vencimento; `ativo` + `status` + `vw_concursos_front`; certames com inscrição fechada e prova futura reservados para filtro futuro “em andamento”.

---

## 1. Nome do módulo

| Opção | Prós | Contras |
| --- | --- | --- |
| **Concursos** | Curto, memorável | Omite vestibulares, bolsas, residências |
| **Concursos & Seleções** | Cobre bem concurso + processo seletivo + vestibular como “seleção” | Nome mais longo no menu |
| **Seleções Públicas** | Abrangente para “público” | Soa menos natural para vestibular privado/comvest |

**Recomendação:** **Concursos & Seleções** como nome oficial do módulo e do documento; no menu lateral pode usar label curta **“Concursos”** com tooltip ou sublinhado “Concursos e seleções públicas” se necessário. Alternativa de marketing: manter slug/rota `concursos` e título de página “Concursos & Seleções”.

---

## 2. Modelo de dados

### 2.1 Tabela principal sugerida

**`public.concurso_selecao`**

Objetivo: uma linha por oportunidade de ingresso/seleção (concurso, edital de professor, vestibular, bolsa, etc.), com campos fixos para filtros rápidos e `extras` JSONB para extensibilidade sem migração constante.

| Campo | Tipo sugerido | Notas |
| --- | --- | --- |
| `id_concurso` | `bigint` PK, identity | |
| `titulo` | `text` not null | |
| `tipo_selecao` | `text` / `enum` app | Valores alinhados a §3 (ex.: `concurso_publico`, `vestibular`) |
| `categoria` | `text` nullable | Sub-tipo ou taxonomia secundária (ex.: “área saúde”, “nível superior”) |
| `orgao` | `text` nullable | Órgão responsável pela publicação |
| `instituicao` | `text` nullable | Empregador ou mantenedora |
| `banca` | `text` nullable | PCI, Cebraspe, Vunesp, etc. |
| `cargo` | `text` nullable | Para concursos; null em vestibular genérico |
| `curso` | `text` nullable | Vestibular / programa |
| `area` | `text` nullable | Área de conhecimento |
| `nivel_escolaridade` | `text` nullable | Ex.: médio, superior, pós |
| `estado` | `char(2)` ou `text` | UF |
| `municipio` | `text` nullable | |
| `modalidade` | `text` nullable | Presencial, online, híbrido |
| `numero_vagas` | `integer` nullable | |
| `salario_min` | `numeric` nullable | |
| `salario_max` | `numeric` nullable | |
| `taxa_inscricao` | `numeric` nullable | |
| `data_inicio_inscricao` | `timestamptz` nullable | |
| `data_fim_inscricao` | `timestamptz` nullable | |
| `data_prova` | `timestamptz` nullable | Ou primeira fase |
| `status` | `text` | Ex.: aberto, encerrado, homologado, cancelado |
| `link` | `text` | URL principal |
| `link_edital` | `text` nullable | PDF ou página do edital |
| `fonte` | `text` not null | Identificador legível |
| `fonte_tipo` | `text` nullable | `banca`, `instituicao`, `inep`, `aggregator`, etc. |
| `validacao_status` | `text` | Alinhado ao pipeline (ex.: válido, incompleto, suspeito) |
| `qualidade_dado` | `text` nullable | |
| `tags` | `text[]` ou `jsonb` | Normalização futura |
| `extras` | `jsonb` default `{}` | Campos específicos por fonte, hashes de dedupe, raw fields |
| `ativo` | `boolean` default true | Soft-delete / despublicação |
| `created_at` | `timestamptz` default now() | |
| `updated_at` | `timestamptz` | Trigger ou aplicação |

**Índices sugeridos (para quando implementar):** `(tipo_selecao)`, `(estado, municipio)`, `(data_fim_inscricao)`, `(data_prova)`, `(banca)`, `(fonte)`, GIN em `extras` se queries JSON forem frequentes; unique parcial em `(fonte, link)` ou `(fonte, id_externo)` em `extras` para dedupe.

**Relação com utilizador:** favoritos/alertas devem usar tabelas **dedicadas** (ex.: `concurso_favorito`) com `id_usuario` / `auth_user_id` e RLS — **não** reutilizar `edital_favorito` para não acoplar domínios.

---

## 3. Categorias (`tipo_selecao` / taxonomia)

Valores canónicos propostos:

1. `concurso_publico` — concursos públicos federais/estaduais/municipais amplos  
2. `processo_seletivo` — PS genérico (não professor) quando distinguir de concurso  
3. `professor` — seleção para docência  
4. `coordenador` — cargos de coordenação académica ou equivalente  
5. `tecnico_administrativo` — técnico/administrativo  
6. `estagio` — estágios com seleção pública  
7. `residencia` — residência médica/multi-profissional  
8. `vestibular` — ingresso via vestibular  
9. `bolsa_estudo` — bolsas ligadas a ingresso/seleção (diferenciar de bolsa CNPq no Radar)  
10. `programa_ingresso` — programas especiais (enem unificado, transferência, etc.)

**Nota:** `categoria` (campo livre) pode refinhar sem proliferar `tipo_selecao` (ex.: `tipo_selecao = professor` + `categoria = substituto`).

---

## 4. Fontes iniciais por prioridade

### 4.1 Bancas e agregadores (concursos)

| Prioridade | Fonte |
| --- | --- |
| Alta | PCI Concursos |
| Alta | Cebraspe |
| Alta | Fundação Carlos Chagas (FCC) |
| Alta | FGV Conhecimento |
| Alta | Vunesp |
| Alta | Quadrix |
| Alta | IBFC |
| Alta | Instituto AOCP |
| Média | IDECAN |
| Média | Fundatec |
| Média | Legalle |
| Média | Objetiva Concursos |

### 4.2 Vestibulares e ingresso

| Prioridade | Fonte |
| --- | --- |
| Alta | INEP / ENEM |
| Alta | SISU / MEC |
| Alta | PROUNI / MEC |
| Alta | FIES / MEC |
| Alta | Vunesp Vestibulares |
| Alta | Fuvest |
| Alta | Comvest (Unicamp) |
| Média | UFRGS (processo seletivo / vestibular conforme portal) |
| Média | UFSC (Coperve) |
| Média | UFPR (Núcleo de Concursos) |
| Média | ACAFE |
| Média | PUCRS |

**Estratégia de dados:** muitas bancas têm **API inexistente ou instável** — esperar HTML + listagem + detalhe; `extras.id_externo`, `extras.codigo_concurso` para dedupe. Fontes MEC (SISU/PROUNI/FIES) podem exigir leitura de **APIs ou dumps oficiais** e atenção a **termos de uso**.

---

## 5. Views (Supabase / PostgREST)

| View | Público-alvo | Conteúdo sugerido |
| --- | --- | --- |
| **`vw_concursos_front`** | Cliente anon/authenticated | Colunas mínimas + não sensíveis; `WHERE ativo = true`; filtrar `validacao_status` aceitável; opcionalmente mascarar `extras` pesado |
| **`vw_concursos_admin`** | Admin / backoffice | Colunas completas, incl. qualidade, fonte técnica, flags de moderação |
| **`vw_vestibulares_front`** | Opcional | **Só se** quiserem URL ou cache separado; caso contrário filtrar `tipo_selecao = 'vestibular'` na mesma `vw_concursos_front` com parâmetro ou view materializada para performance |

**Recomendação:** começar com **uma** `vw_concursos_front` + filtros por `tipo_selecao`; criar `vw_vestibulares_front` apenas se métricas ou RLS exigirem particionamento lógico.

---

## 6. Frontend (especificação — não implementar)

### 6.1 Rota e menu

- **Rota:** `/concursos`  
- **Menu:** entrada **“Concursos”** (ou “Concursos & Seleções” se couber no design system).

### 6.2 Abas (tabs)

1. **Todos**  
2. **Concursos públicos** (`tipo_selecao` in concurso público / processo seletivo amplo)  
3. **Professores** (professor, coordenador se quiserem sub-aba depois)  
4. **Técnicos / Administrativos**  
5. **Vestibulares**  
6. **Residências**  
7. **Bolsas**

**Implementação futura:** tabs mapeiam para query string (`?tipo=vestibular`) ou estado React + mesma listagem com filtros.

### 6.3 Filtros

- Texto livre (título, órgão, cargo, curso)  
- Estado (UF)  
- Município  
- Banca  
- Instituição  
- Escolaridade (`nivel_escolaridade`)  
- Área / cargo  
- Faixa salarial (`salario_min` / `salario_max`)  
- Número de vagas  
- **Inscrições abertas** (regra: `data_fim_inscricao >= hoje` e `data_inicio_inscricao <= hoje` com tolerância timezone)  
- **Prova próxima** (`data_prova` em janela, ex. 30 dias)  
- Modalidade  

**Radar:** não partilhar motor de score do Radar de Fomento; opcionalmente “alertas por data” só na camada de favoritos/notificações.

---

## 7. Favoritos e alertas

### 7.1 Favoritar concurso

- Nova entidade: **`concurso_favorito`** (ou nome equivalente) com `id_usuario`, `id_concurso`, `ativo`, `created_at`.  
- RLS: utilizador só lê/escreve as próprias linhas (padrão igual ao de `edital_favorito` documentado no projeto).

### 7.2 Alertas (fase 1 sugerida)

| Alerta | Gatilho |
| --- | --- |
| Fim de inscrição | `data_fim_inscricao` a T-1, T-3 dias (configurável em `extras` do favorito) |
| Data de prova | `data_prova` a T-7, T-1 dias |
| Resultado / gabarito | **Fase futura** — requer fonte estável ou campo `data_resultado` + crawler |

**Nota:** job de notificação (e-mail/push/in-app) pode reutilizar infraestrutura de “alertas de prazo” dos favoritos de edital, mas **tabelas e rotas separadas** para não acoplar.

---

## 8. Plano de crawlers em waves

### Wave 1 — cobertura nacional alta + vestibular core

- PCI Concursos  
- Cebraspe  
- Vunesp  
- FGV Conhecimento  
- FCC  
- Quadrix  
- IBFC  
- AOCP  
- INEP / ENEM (e divulgação agregada quando aplicável)  
- Vunesp Vestibulares  

**Meta:** prova de conceito de pipeline (listagem → detalhe → normalização → `concurso_selecao`).

### Wave 2 — bancas regionais e universidades grandes

- Fundatec  
- IDECAN  
- Fuvest  
- Comvest  
- UFRGS  
- UFSC (Coperve)  
- UFPR (Núcleo de Concursos)  
- ACAFE  

### Wave 3 — long tail

- Portais municipais e estaduais  
- Universidades menores / consórcios  
- Legalle, Objetiva, outras bancas conforme demanda de utilizadores  

**Por fonte:** pasta `concursos_pci/`, `concursos_cebraspe/`, etc., seguindo o padrão do mono-repo; **standardized JSON** + loader dedicado (tabela `concurso_selecao`, não `edital`).

---

## 9. Visão do produto

**Visão:** o EditalFinder passa a cobrir, além de fomento e oportunidades de I&D, o **mercado de seleções públicas e de ingresso** (carreira, docência, técnico, saúde-residência, vestibular e bolsas de ingresso), com listagem única, filtros fortes por prazo e localização, e alertas pessoais.

**Diferenciais:**

- Separação clara **Fomento (edital + Radar)** vs **Seleção (concurso_selecao)** — evita poluir o utilizador que só quer ENEM ou só quer concurso público.  
- Foco em **datas acionáveis** (inscrição, prova).  
- Mesma barra de qualidade: `validacao_status`, `qualidade_dado`, `extras` para auditoria.  
- Reuso de **Auth e multi-cliente** sem misturar permissões de editais.

---

## 10. Backend / crawlers (arquitectura)

- **Ingestão:** crawlers Python → `audit_reports_concursos/standardized/*.json` → script de carga (`load_concursos_sources.py` futuro) → UPSERT em `concurso_selecao`.  
- **Transformação:** módulo tipo `CORE/concursos_normalizer.py` (futuro) para mapear HTML heterogéneo → campos canónicos + `extras`.  
- **Gate:** reutilizar filosofia de `opportunity_gate` **adaptada** (ruído de “curso online genérico” vs concurso real), **código separado** do gate de editais.  
- **API:** PostgREST sobre views front; **sem** `service_role` no browser (manter anon + RLS).

---

## 11. Riscos

| Risco | Mitigação |
| --- | --- |
| Termos de uso / robots em bancas e MEC | Due diligence legal; cache conservador; respeitar `robots.txt` |
| HTML instável | Testes de regressão por fonte; `extras.raw_hash` |
| Sobreposição com `public.edital` | Regra de negócio: “bolsa CNPq” → Radar; “bolsa ingresso PUCRS” → Concursos |
| Volume de dados | Índices por data; paginação obrigatória; eventual particionamento por ano |
| Duplicados entre PCI e instituição | Dedupe por `link` + normalização de URL |
| Falsos positivos em vestibular | `tipo_selecao` + validação manual amostral nas waves |

---

## 12. Próximos passos (ordem sugerida)

1. Validar nome do módulo e lista de campos com stakeholders.  
2. Fechar **ERD** (concurso_selecao + concurso_favorito + concurso_alerta opcional).  
3. Escrever **DDL** e **RLS** em `docs/sql/` (sem aplicar).  
4. Definir **contrato** da `vw_concursos_front` (lista de colunas).  
5. Spike técnico: **uma** fonte Wave 1 (ex.: PCI ou Cebraspe) só leitura + standardized.  
6. Desenhar **wireframes** `/concursos` (abas + filtros).  
7. Plano de **migração zero** para utilizadores actuais (menu novo, sem dados até Wave 1).  

---

## Referências internas

- Autenticação e padrão anon: `frontend/EditalFinder-React/src/config/env.js`, `services/supabaseClient.js`  
- Padrão de favoritos editais: `favoritosService.js` / tabelas existentes (inspiração, não reutilização directa de PK)  
- RLS cliente: `docs/sql/RLS_CLIENTE.sql`  

---

*Documento gerado para planeamento do módulo **Concursos & Seleções**. Nenhuma alteração foi feita a código, frontend ou base de dados.*
