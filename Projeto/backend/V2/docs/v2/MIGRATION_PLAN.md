# Plano de reconstrução paralela do EditalFinder V2

Status: **proposta de execução**. Não autoriza SQL, migrations, acesso remoto ou alterações no legado.

## 1. Estratégia

### Legacy

**Decisão:**

- permanece operacional durante a construção do V2;
- recebe somente hotfixes críticos de segurança, disponibilidade ou integridade;
- não recebe novas grandes features;
- não tem schema ou dados alterados por este plano;
- continua com deploy e rollback independentes.

### V2 staging

**Decisão:**

- usa o novo projeto Supabase de staging;
- parte de contrato e schema mínimo novos;
- executa pipeline estrito e versionado;
- usa dados sintéticos, fixtures e amostras reprocessadas;
- não recebe usuários reais inicialmente;
- não importa diretamente os 1.387 registros legados.

## 2. Princípios de migração

1. Reconstruir em paralelo; não reformar o banco legado in-place.
2. Fonte oficial e payload bruto são preferidos ao registro legado transformado.
3. Cada campo migrado deve satisfazer o contrato V2.
4. Nenhum valor é copiado apenas para preservar paridade de coluna.
5. Toda perda/descartabilidade deve ter justificativa auditável.
6. Promoção é feita por gates mensuráveis, não por calendário apenas.
7. Rollback mantém Legacy disponível até a conclusão da migração.

## 3. Fases e critérios de passagem

### Fase 0 — Contrato

Entregas:

- `DATA_CONTRACT.md` e `GEOGRAPHY_CONTRACT.md` aprovados;
- vocabulário inicial de tipos;
- decisões bloqueantes registradas;
- amostras de aceitação/rejeição.

Gate para fase 1:

- aprovação humana dos campos obrigatórios, identidade, geografia, datas e organização;
- UUID/bigint, taxonomias e localização múltipla decididos;
- nenhum conflito semântico bloqueante aberto.

### Fase 1 — Schema mínimo

Entregas futuras:

- modelo lógico e somente depois migrations revisadas;
- constraints coerentes com o contrato;
- tabelas auxiliares estritamente necessárias;
- fixtures sintéticas e rollback.

Gate para fase 2:

- revisão de schema por backend, dados e segurança;
- migrations aplicáveis do zero em staging descartável;
- constraints cobertas por testes;
- nenhuma dependência do schema legado.

### Fase 2 — Transformer V2

Entregas:

- entrada bruta imutável;
- normalizadores puros/versionados;
- validação do contrato;
- quarentena com motivos estruturados;
- proveniência/confiança por inferência;
- testes determinísticos.

Gate para fase 3:

- fixtures passam sem rede;
- campos obrigatórios nunca recebem placeholders;
- geografia inválida é rejeitada;
- idempotência e hash reproduzíveis;
- taxa de transformação das amostras acordada.

### Fase 3 — Piloto de fontes

Escopo: fontes de `SOURCE_SCOPE.md`, uma ou poucas por vez.

Entregas:

- adaptador por fonte;
- coleta limitada e segura;
- amostra revisada manualmente;
- métricas por fonte;
- runbook de falhas.

Gate para fase 4:

- readiness aprovado;
- nenhuma fonte japonesa/chinesa executada no MVP;
- identidade, URL e prazo com qualidade mínima definida;
- ruído e duplicidade abaixo dos limiares acordados.

### Fase 4 — Validação de qualidade

Entregas:

- conjunto ouro revisado;
- precision/recall ou métricas equivalentes para oportunidade, prazo, geografia e tipos;
- auditoria de nulos e inconsistências;
- limites por fonte e alertas de regressão.

Gate para fase 5:

- zero violação das invariantes obrigatórias;
- qualidade mínima aprovada por responsável humano;
- regressões bloqueiam promoção;
- quarentena explicável.

### Fase 5 — View V2

Entregas futuras:

- contrato de leitura mínimo e versionado;
- campos canônicos sem aliases ambíguos;
- status derivado claramente identificado;
- regras de visibilidade documentadas e testadas.

Gate para fase 6:

- uma definição canônica de view;
- testes de contrato e RLS;
- paginação/ordenação estáveis;
- explain/performance dentro do objetivo.

### Fase 6 — Mapper V2

Entregas:

- modelo de frontend tipado;
- mapeamento 1:1 documentado;
- labels derivados separados dos dados;
- sem reclassificação silenciosa no mapper.

Gate para fase 7:

- testes de contrato view -> mapper;
- nulos e enums tratados explicitamente;
- nenhuma dependência de aliases legados;
- cards e filtros usam a mesma semântica.

### Fase 7 — Frontend sob feature flag

Entregas:

- rota/cliente V2 isolado;
- feature flag por ambiente/coorte;
- estados vazio/erro/loading;
- telemetria sem dados pessoais;
- rollback instantâneo para Legacy.

Gate para fase 8:

- QA funcional e acessibilidade;
- nenhum usuário real por default;
- observação e rollback verificados;
- aprovação de produto.

### Fase 8 — Comparação Legacy x V2

Comparar:

- cobertura por fonte;
- oportunidades acionáveis;
- duplicidade/ruído;
- prazos e geografia;
- desempenho;
- divergências explicadas, sem exigir contagem idêntica.

Gate para fase 9:

- amostra V2 superior ou aceitável nos indicadores acordados;
- diferenças categorizadas;
- nenhum requisito depende de copiar o legado integralmente;
- plano de suporte/rollback aprovado.

### Fase 9 — Migração gradual

Entregas:

- coortes/fontes ativadas progressivamente;
- comunicação e suporte;
- monitoramento de qualidade e uso;
- caminho de retorno ao Legacy.

Gate para fase 10:

- período de estabilidade acordado;
- SLOs e qualidade atendidos;
- dados essenciais tratados nas categorias de migração;
- aprovação executiva/técnica.

### Fase 10 — Produção

Entregas:

- projeto/ambiente V2 de produção;
- migrations reproduzíveis e backup;
- RLS/Auth/observabilidade aprovados;
- runbooks, ownership e resposta a incidentes;
- plano separado para descontinuação futura do Legacy.

Legacy não é desligado automaticamente pela entrada em produção; isso exige decisão posterior.

## 4. Categorias de tratamento de registros legados

Cada registro avaliado deve ter exatamente uma categoria:

| Categoria | Uso | Evidência mínima |
|---|---|---|
| `reprocessado_da_fonte` | Fonte ainda acessível; cria registro V2 novo a partir do raw atual | URL/fonte, payload bruto, versão do pipeline e correspondência ao legado |
| `migrado_manualmente` | Registro essencial não reprocessável, revisado por humano | responsável, justificativa, campos revisados e timestamp |
| `descartado_com_justificativa` | Ruído, expirado irrelevante, duplicata ou fora de escopo | categoria e motivo auditáveis; nenhuma exclusão do Legacy por este ato |
| `pendente_de_revisao` | Evidência insuficiente | motivo, owner e próxima ação |

**Decisão:** não existirá categoria “copiado automaticamente do legado”.

## 5. Dados de teste

- fixtures sintéticas para invariantes;
- amostras públicas sanitizadas por fonte;
- casos negativos e quarentena;
- nenhuma credencial ou usuário real;
- nenhuma importação massiva do legado;
- retenção conforme decisão de payload bruto.

## 6. Governança

Cada fase deve registrar: owner, decisões, evidências, métricas, riscos, rollback e aprovação. Mudanças no contrato exigem versão e análise de compatibilidade; não devem ser introduzidas implicitamente por um crawler ou componente frontend.
