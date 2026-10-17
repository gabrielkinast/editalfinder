# EditalFinder V2 — Desenho de schema V1

## Status e limites

Este documento é uma **decisão de desenho conceitual V1**. Ele não é uma migration, não contém DDL e não autoriza criação de objetos no Supabase.

- **Fato:** o projeto V2 terá um Supabase de staging separado do legado.
- **Decisão:** o schema mínimo contém as 12 tabelas descritas neste documento.
- **Proposta:** nomes de colunas, tipos PostgreSQL e índices abaixo são a base para uma futura revisão de implementação.
- **Fora de escopo:** SQL, políticas RLS concretas, grants, funções, triggers, carga de dados e alterações no legado.

## Convenções V1

| Tema | Convenção |
|---|---|
| Identificadores principais | `uuid` gerado no banco ou na aplicação por mecanismo aprovado na fase de implementação |
| Tabelas de junção | chave primária composta pelas FKs participantes |
| Datas e horas operacionais | `timestamptz`, representando instantes em UTC; interfaces podem converter para o fuso do usuário |
| Datas civis de editais | `date`, salvo quando a fonte fornecer horário relevante |
| Valores monetários | `numeric(18,2)` como ponto de partida; precisão deve ser validada com amostras |
| Códigos de país | `text`, validado como ISO 3166-1 alpha-2 com duas letras maiúsculas |
| Códigos de moeda | `text`, validado como ISO 4217 com três letras maiúsculas |
| Confiança | `numeric` em escala inclusiva de 0 a 1; precisão concreta será fechada na migration |
| Payload bruto e extensões | `jsonb` |
| Slugs e códigos taxonômicos | `text`, minúsculos, estáveis e sem significado de apresentação |
| Auditoria temporal | `criado_em` e `atualizado_em` em entidades mutáveis |
| Ausência de informação | `null`; não usar string vazia, `N/A`, `Não informado` ou valores geográficos inventados |
| Segurança | RLS habilitada; tabelas internas acessadas pelo pipeline com service role |

Defaults citados são comportamentos conceituais sugeridos, não definições SQL.

## Diagrama textual das relações

```text
fonte 1 ─── N execucao_coleta 1 ─── N item_coletado
  │                                      │
  │                                      └── N ─── N oportunidade, via item_oportunidade
  └────────────────────────────── 1 ─── N oportunidade
                                              │
organizacao 1 ─── N ──────────┤  (FK nullable)
tipo_oportunidade 1 ─── N ────┤
tipo_recurso 1 ─── N ─────────┤
                              ├── 1 ─── N oportunidade_identificador
                              ├── 1 ─── N oportunidade_localizacao
                              └── N ─── N area, via oportunidade_area
```

`item_coletado` pode existir sem associação enquanto estiver apenas coletado, rejeitado, em quarentena, ignorado ou com erro. Uma página agregadora pode originar várias oportunidades, e uma oportunidade pode ser sustentada por vários itens coletados ao longo de execuções sucessivas.

## 1. `fonte`

### Responsabilidade

Representar a fonte de coleta: portal, API, feed ou catálogo de onde o pipeline obtém itens. Fonte não é sinônimo de organização responsável.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `id` | `uuid` | sim | PK | Identificador interno da fonte |
| `codigo` | `text` | sim | UNIQUE | Código estável, sem finalidade de apresentação |
| `nome` | `text` | sim | — | Nome de apresentação |
| `url_base` | `text` | não | — | URL raiz oficial do portal ou API |
| `status_integracao` | `text` | sim | CHECK | Estado da fonte no portfólio V2 |
| `criado_em` | `timestamptz` | sim | — | Criação do cadastro |
| `atualizado_em` | `timestamptz` | sim | — | Última alteração do cadastro |

### Regras, índices e integridade

- `codigo` deve ser único, normalizado e imutável após uso em identificadores.
- `status_integracao` usa domínio pequeno e estável: `mvp_habilitada`, `piloto`, `futura`, `arquivada`, `bloqueada` ou `removida_v2`.
- Índices propostos: unique em `codigo`; índice em `status_integracao` se consultas operacionais justificarem.
- `url_base`, quando presente, deve ser uma URL HTTP(S) válida e não deve conter credenciais.
- Fontes japonesas e chinesas devem permanecer `removida_v2` ou fora da carga inicial, conforme o catálogo de escopo.

### Adiado

Credenciais, quotas, agendamento, configuração específica de crawler e histórico de mudanças da fonte. Segredos não pertencem a esta tabela.

## 2. `organizacao`

### Responsabilidade

Representar uma organização canônica conhecida. O vínculo da oportunidade é opcional e nunca substitui o texto original coletado.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `id` | `uuid` | sim | PK | Identificador canônico |
| `codigo` | `text` | não | UNIQUE | Código editorial estável, quando atribuído deterministicamente |
| `nome_canonico` | `text` | sim | — | Nome revisado da organização |
| `pais_codigo` | `text` | não | CHECK | País principal da organização; não define a geografia da oportunidade |
| `site_oficial` | `text` | não | — | Site institucional |
| `ativo_administrativo` | `boolean` | sim | — | Permite desativar o cadastro sem apagá-lo |
| `criado_em` | `timestamptz` | sim | — | Criação |
| `atualizado_em` | `timestamptz` | sim | — | Última alteração |

### Regras, índices e integridade

- `codigo`, se presente, é único. Não impor unicidade simples a `nome_canonico`: homônimos são possíveis.
- `pais_codigo` deve ser ISO alpha-2 maiúsculo quando informado.
- Índices propostos: unique parcial/lógico em `codigo` não nulo; índice de busca normalizada em nome somente após definição da estratégia de extensão e acentos.
- Uma organização só pode ser associada por regra determinística. Sem associação confiável, a FK da oportunidade permanece nula.

### Adiado

Hierarquia organizacional, aliases formais, múltiplos sites, identificadores externos e fusão automática de organizações.

## 3. `tipo_oportunidade`

### Responsabilidade

Taxonomia administrável para a natureza da oportunidade, separada do mecanismo de recurso.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `id` | `uuid` | sim | PK | Identificador taxonômico |
| `codigo` | `text` | sim | UNIQUE | Código estável usado por integrações |
| `nome` | `text` | sim | — | Rótulo de apresentação |
| `descricao` | `text` | não | — | Definição editorial |
| `ativo` | `boolean` | sim | — | Disponibilidade para novas classificações |
| `ordem_exibicao` | `integer` | não | CHECK | Ordem editorial não negativa |
| `criado_em` | `timestamptz` | sim | — | Criação |
| `atualizado_em` | `timestamptz` | sim | — | Última alteração |

### Regras, índices e integridade

- `codigo` único, minúsculo e estável; desativação não permite reutilização do código.
- `ordem_exibicao`, quando presente, não pode ser negativa.
- Índices propostos: unique em `codigo`; índice composto em `ativo` e `ordem_exibicao` para catálogos.
- Alteração do rótulo não altera o significado histórico do código.

### Adiado

Versionamento da taxonomia, aliases, traduções e hierarquia.

## 4. `tipo_recurso`

### Responsabilidade

Taxonomia administrável para o recurso oferecido, por exemplo financiamento, bolsa, prêmio ou apoio não financeiro.

### Colunas conceituais

Mesma estrutura de `tipo_oportunidade`: `id uuid` (PK), `codigo text` (UNIQUE), `nome text`, `descricao text` opcional, `ativo boolean`, `ordem_exibicao integer` opcional, `criado_em timestamptz` e `atualizado_em timestamptz`.

### Regras, índices e integridade

- Aplicam-se as mesmas regras de código estável, ordem não negativa e desativação sem exclusão definidas para `tipo_oportunidade`.
- `tipo_recurso` não deve duplicar `tipo_oportunidade`; uma oportunidade pode ser uma chamada e oferecer financiamento, por exemplo.

### Adiado

Versionamento, aliases, traduções e classificação com múltiplos tipos de recurso. A necessidade de N:N será reavaliada com o piloto.

## 5. `area`

### Responsabilidade

Taxonomia de áreas temáticas associáveis em relação N:N às oportunidades.

### Colunas conceituais

Mesma base taxonômica: `id uuid` (PK), `codigo text` (UNIQUE), `nome text`, `descricao text` opcional, `ativo boolean`, `ordem_exibicao integer` opcional, `criado_em timestamptz` e `atualizado_em timestamptz`.

### Regras, índices e integridade

- Código único e estável; ordem não negativa; áreas inativas permanecem referenciáveis para preservar histórico.
- Índices propostos: unique em `codigo`; índice em `ativo` e `ordem_exibicao`.
- A classificação múltipla ocorre exclusivamente por `oportunidade_area`.

### Adiado

Hierarquia de áreas, setores estratégicos como taxonomia independente, sinônimos, traduções e versionamento.

## 6. `execucao_coleta`

### Responsabilidade

Registrar cada execução do crawler ou importador para auditoria, métricas e diagnóstico.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `id` | `uuid` | sim | PK | Identificador da execução |
| `fonte_id` | `uuid` | sim | FK → `fonte.id` | Fonte executada |
| `iniciado_em` | `timestamptz` | sim | — | Início efetivo |
| `finalizado_em` | `timestamptz` | não | — | Fim efetivo |
| `status` | `text` | sim | CHECK | Estado operacional da execução |
| `versao_coletor` | `text` | sim | — | Versão ou revisão do coletor |
| `parametros` | `jsonb` | não | — | Parâmetros não secretos relevantes à reprodução |
| `metricas` | `jsonb` | não | — | Contagens e tempos operacionais |
| `erro_resumo` | `text` | não | — | Resumo sanitizado de falha |
| `criado_em` | `timestamptz` | sim | — | Registro da execução |

### Regras, índices e integridade

- `status`: `iniciada`, `sucesso`, `parcial`, `falha` ou `cancelada`.
- `finalizado_em` não pode anteceder `iniciado_em`; estados terminais devem possuir término.
- Índices propostos: (`fonte_id`, `iniciado_em` descendente), `status`, `iniciado_em`.
- `parametros`, `metricas` e erros não podem conter tokens, cookies, credenciais ou dados pessoais desnecessários.
- Exclusão de fonte não deve apagar seu histórico de execução.

### Adiado

Orquestração, filas, retentativas por item, logs completos e observabilidade externa.

## 7. `item_coletado`

### Responsabilidade

Preservar o item bruto obtido da fonte e seu estado de processamento. É a fronteira auditável entre coleta e transformação.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `id` | `uuid` | sim | PK | Identificador do item bruto |
| `execucao_coleta_id` | `uuid` | sim | FK → `execucao_coleta.id` | Execução que coletou o item |
| `chave_origem` | `text` | não | — | Identificador do item dentro da fonte |
| `url_coletada` | `text` | não | — | URL observada antes da canonicalização |
| `payload_bruto` | `jsonb` | sim | — | Conteúdo bruto sanitizado no MVP |
| `hash_payload` | `text` | sim | — | Hash determinístico do payload normalizado para hash |
| `coletado_em` | `timestamptz` | sim | — | Instante da coleta |
| `estado_processamento` | `text` | sim | CHECK | Estado controlado do transformer/loader |
| `motivo_rejeicao` | `text` | não | — | Justificativa quando rejeitado |
| `erro_codigo` | `text` | não | — | Código estável e sanitizado da falha |
| `erro_detalhes` | `jsonb` | não | — | Contexto estruturado e sanitizado da falha |
| `processado_em` | `timestamptz` | não | — | Instante UTC da última transição de processamento concluída |
| `versao_transformer` | `text` | não | — | Versão usada no processamento |

### Regras, índices e integridade

- `estado_processamento`: `coletado`, `normalizado`, `aceito`, `rejeitado`, `erro`, `quarentena` ou `ignorado`.
- `motivo_rejeicao` é obrigatório para `rejeitado`; `erro_codigo` deve existir em `erro`; quarentena deve preservar justificativa auditável.
- `processado_em` permanece nulo em `coletado` e registra o instante UTC da transição relevante nos demais estados, conforme regra a fechar na implementação.
- Unique proposto em (`execucao_coleta_id`, `chave_origem`) quando a chave existir. O mesmo payload em execuções diferentes deve poder ser preservado.
- Índices propostos: `execucao_coleta_id`, `hash_payload`, (`estado_processamento`, `coletado_em`) e `processado_em` quando métricas operacionais justificarem.
- `payload_bruto` não pode receber segredos e deve respeitar política futura de retenção.
- `fonte_id` não é repetido: é derivado de `execucao_coleta.fonte_id`, evitando duas autoridades para a mesma informação.
- Associações com oportunidades existem somente em `item_oportunidade`; não há FK direta singular neste registro.

### Adiado

Storage para documentos grandes, retenção definitiva, compressão, versionamento de schema do payload e trilha detalhada de todas as tentativas de transformação.

## 8. `item_oportunidade`

### Responsabilidade

Materializar a relação N:N auditável entre itens coletados e oportunidades. Permite que uma página agregadora gere várias oportunidades e que vários itens sustentem a mesma oportunidade.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `item_coletado_id` | `uuid` | sim | PK composta, FK → `item_coletado.id` | Item de evidência |
| `oportunidade_id` | `uuid` | sim | PK composta, FK → `oportunidade.id` | Oportunidade relacionada |
| `papel` | `text` | sim | CHECK proposto | Papel do item na formação ou sustentação da oportunidade |
| `confianca` | `numeric` | sim | CHECK | Confiança da associação, entre 0 e 1 inclusive |
| `criado_em` | `timestamptz` | sim | — | Instante UTC em que a associação foi criada |

### Regras, índices e integridade

- PK composta: (`item_coletado_id`, `oportunidade_id`).
- `confianca` deve estar no intervalo inclusivo de 0 a 1 e não substitui a proveniência dos campos da oportunidade.
- `papel` deve ser controlado, mas seu vocabulário definitivo permanece aberto; candidatos iniciais incluem `origem`, `evidencia`, `atualizacao` e `agregador`.
- Índices propostos: PK composta e índice inverso em (`oportunidade_id`, `item_coletado_id`).
- Uma associação só pode ser criada após existir evidência rastreável; rejeição ou quarentena posterior do item exige política explícita, não exclusão silenciosa do vínculo.

### Adiado

Versionamento da associação, histórico de revisão, autoria humana da decisão e múltiplos papéis simultâneos para o mesmo par.

## 9. `oportunidade`

### Responsabilidade

Armazenar o registro canônico da oportunidade, separado do payload bruto, das taxonomias e das localizações múltiplas.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `id` | `uuid` | sim | PK | Identificador canônico |
| `fonte_id` | `uuid` | sim | FK → `fonte.id` | Fonte primária do registro canônico |
| `organizacao_responsavel_id` | `uuid` | não | FK → `organizacao.id` | Associação determinística, quando conhecida |
| `organizacao_responsavel_texto` | `text` | não | — | Texto original preservado |
| `tipo_oportunidade_id` | `uuid` | não | FK → `tipo_oportunidade.id` | Classificação canônica |
| `tipo_recurso_id` | `uuid` | não | FK → `tipo_recurso.id` | Classificação canônica |
| `titulo` | `text` | sim | — | Título canônico |
| `descricao` | `text` | não | — | Descrição canônica |
| `url_oficial` | `text` | sim | — | URL oficial canonicalizada |
| `url_pdf` | `text` | não | — | Documento oficial direto, se houver |
| `programa` | `text` | não | — | Programa informado, sem entidade própria no MVP |
| `data_publicacao` | `date` | não | — | Publicação pela fonte |
| `data_abertura` | `date` | não | — | Início de submissões |
| `prazo_submissao` | `date` | não | — | Último dia para submissão |
| `motivo_sem_prazo` | `text` | condicional | CHECK | Razão controlada para prazo ausente |
| `data_resultado` | `date` | não | — | Resultado previsto ou informado |
| `situacao_informada` | `text` | não | — | Situação declarada pela fonte, sem cálculo temporal |
| `ativo_administrativo` | `boolean` | sim | — | Visibilidade/validade editorial persistida |
| `escopo_geografico` | `text` | sim | CHECK | `brasil`, `internacional`, `misto` ou `nao_identificado` |
| `valor_minimo` | `numeric(18,2)` | não | CHECK | Limite inferior informado |
| `valor_maximo` | `numeric(18,2)` | não | CHECK | Limite superior informado |
| `moeda` | `text` | não | CHECK | ISO 4217 com três letras maiúsculas quando houver valor |
| `qualidade_dado` | `smallint` | não | CHECK proposto | Escore proposto de 0 a 100; contrato ainda aberto |
| `qualidade_detalhes` | `jsonb` | não | — | Dimensões, fórmula e versão que explicam o escore |
| `confianca_classificacao` | `numeric` | não | CHECK | Confiança numérica entre 0 e 1 inclusive |
| `proveniencia` | `jsonb` | sim | — | Evidências estruturadas dos campos inferidos |
| `hash_conteudo` | `text` | não | — | Hash da representação canônica versionada |
| `dados_extras` | `jsonb` | não | — | Metadados sem coluna canônica aprovada |
| `criado_em` | `timestamptz` | sim | — | Criação |
| `atualizado_em` | `timestamptz` | sim | — | Última alteração canônica |

### Regras, índices e integridade

- FK de organização é nullable e jamais deve receber uma organização global por fallback. O texto original permanece independente da FK.
- Se `prazo_submissao` estiver preenchido, `motivo_sem_prazo` deve ser nulo. Se o prazo estiver ausente, o motivo deve usar `nao_informado`, `a_definir`, `fluxo_continuo` ou `nao_aplicavel`.
- `valor_minimo` e `valor_maximo` não podem ser negativos; quando ambos existirem, mínimo não pode exceder máximo. `moeda` é obrigatória quando qualquer valor existir.
- `moeda`, quando presente, deve conter exatamente três letras maiúsculas e corresponder a código ISO 4217 reconhecido pelo contrato.
- Datas não devem ser reordenadas automaticamente. Inconsistências da fonte devem reduzir qualidade e ser auditáveis, não silenciosamente corrigidas.
- `url_oficial` precisa ser HTTP(S), sem parâmetros de rastreamento após canonicalização, mas não recebe necessariamente UNIQUE direto. Identidade e unicidade são controladas em `oportunidade_identificador`.
- `confianca_classificacao` deve estar no intervalo inclusivo de 0 a 1.
- `proveniencia` deve registrar, por campo inferido, origem, método, confiança numérica e `item_coletado_id` de evidência. Seu schema JSON e versionamento precisam ser fechados antes da migration.
- Se `qualidade_dado` for adotado como `smallint` de 0 a 100, `qualidade_detalhes` deve registrar versão da fórmula, dimensões e justificativas. O número isolado não constitui contrato suficiente.
- Índices propostos: `fonte_id`, `organizacao_responsavel_id`, `tipo_oportunidade_id`, `tipo_recurso_id`, (`ativo_administrativo`, `prazo_submissao`), `escopo_geografico`, `atualizado_em` e `hash_conteudo`.
- Índice textual para título/descrição depende de decisão posterior sobre busca e extensão PostgreSQL.
- Status temporal e dias restantes não são persistidos; serão derivados pela view.

### Adiado

Eventos, histórico completo de versões, programa como entidade, similaridade textual, conteúdo editorial rico, usuários, favoritos e status temporal materializado.

## 10. `oportunidade_identificador`

### Responsabilidade

Registrar identificadores determinísticos usados na deduplicação e rastreabilidade: URL canônica, identificador oficial e identificador específico da fonte.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `tipo_identificador` | `text` | sim | PK composta, CHECK | Natureza do identificador |
| `namespace` | `text` | sim | PK composta | Autoridade ou espaço do identificador |
| `fonte_id` | `uuid` | sim | PK composta, FK → `fonte.id` | Fonte no contexto da qual o identificador foi observado/normalizado |
| `valor_normalizado` | `text` | sim | PK composta | Valor usado para igualdade |
| `oportunidade_id` | `uuid` | sim | FK → `oportunidade.id` | Dona do identificador |
| `valor_original` | `text` | não | — | Forma observada antes da normalização |
| `criado_em` | `timestamptz` | sim | — | Primeiro registro do identificador |

### Regras, índices e integridade

- PK composta: (`tipo_identificador`, `namespace`, `fonte_id`, `valor_normalizado`). Isso impede que o mesmo identificador contextual pertença a duas oportunidades.
- `tipo_identificador`: `url_canonica`, `identificador_oficial` ou `identificador_fonte`.
- Para URL canônica, o namespace deve identificar a regra/versionamento de canonicalização; para identificador oficial, deve identificar a autoridade emissora.
- Índices propostos: PK composta, índice em `oportunidade_id` para navegação inversa e índice de apoio por (`fonte_id`, `tipo_identificador`).
- Colisões não devem ser resolvidas automaticamente por similaridade textual; exigem regra determinística ou revisão.

### Adiado

Fingerprint textual, merge probabilístico, grafo de equivalência e histórico de fusões/separações.

## 11. `oportunidade_localizacao`

### Responsabilidade

Representar uma ou mais localizações relacionadas à oportunidade, distinguindo geografia de escopo e explicitando o papel semântico da localização.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `id` | `uuid` | sim | PK | Identificador da localização |
| `oportunidade_id` | `uuid` | sim | FK → `oportunidade.id` | Oportunidade relacionada |
| `papel_localizacao` | `text` | sim | CHECK | Papel semântico controlado da localização |
| `pais_codigo` | `text` | não | CHECK | ISO alpha-2 com duas letras maiúsculas |
| `regiao_brasil` | `text` | não | CHECK | Região brasileira controlada |
| `estado_codigo` | `text` | não | CHECK | UF brasileira com duas letras maiúsculas |
| `municipio` | `text` | não | — | Município como texto no MVP |
| `origem_inferencia` | `text` | não | — | Campo, regra ou evidência que gerou a localização |
| `confianca` | `numeric` | não | CHECK | Confiança da localização inferida, entre 0 e 1 inclusive |
| `criado_em` | `timestamptz` | sim | — | Criação |

### Regras, índices e integridade

- `papel_localizacao`: `elegibilidade`, `execucao`, `beneficiarios`, `origem`, `organizacao_responsavel` ou `nao_especificado`.
- `regiao_brasil`: `norte`, `nordeste`, `centro_oeste`, `sudeste` ou `sul`; nunca `Nacional` ou `Internacional`.
- País diferente de `BR` implica região e estado nulos. Estado preenchido implica país `BR`. Município brasileiro com estado conhecido deve carregar a UF.
- Ausência de evidência permanece nula. Domínio ou fonte pode sustentar apenas inferência de baixa confiança, nunca certeza definitiva.
- `confianca` é obrigatória quando a localização for inferida e deve estar no intervalo inclusivo de 0 a 1; localização diretamente declarada pode mantê-la nula se a proveniência distinguir esse caso.
- A unicidade lógica é (`oportunidade_id`, `papel_localizacao`, país, região, estado, município) após normalização de nulos e texto. A forma exata da constraint depende da versão PostgreSQL e será decidida na migration.
- Índices propostos: `oportunidade_id`; (`pais_codigo`, `estado_codigo`); `regiao_brasil`; (`papel_localizacao`, `pais_codigo`).
- Escopo permanece em `oportunidade.escopo_geografico`; não deve ser recalculado silenciosamente a partir de uma única localização.

### Adiado

Código IBGE, geometrias, coordenadas, município canônico, alcance supranacional estruturado e hierarquia territorial genérica.

## 12. `oportunidade_area`

### Responsabilidade

Implementar a relação N:N entre oportunidade e área, preservando eventual indicação de área principal e a proveniência da classificação.

### Colunas conceituais

| Coluna | Tipo PostgreSQL sugerido | Obrigatória | Chave | Significado |
|---|---|---:|---|---|
| `oportunidade_id` | `uuid` | sim | PK composta, FK → `oportunidade.id` | Oportunidade |
| `area_id` | `uuid` | sim | PK composta, FK → `area.id` | Área |
| `principal` | `boolean` | sim | — | Indica classificação primária |
| `origem_classificacao` | `text` | não | — | Fonte da classificação |
| `confianca` | `numeric` | não | CHECK | Confiança numérica entre 0 e 1 inclusive |
| `criado_em` | `timestamptz` | sim | — | Criação da associação |

### Regras, índices e integridade

- PK composta: (`oportunidade_id`, `area_id`).
- `confianca`, quando presente, deve estar no intervalo inclusivo de 0 a 1.
- No máximo uma área principal por oportunidade; a implementação futura deve usar uma garantia de unicidade apropriada.
- Índices propostos: PK composta; índice em `area_id`; índice para a associação principal.
- Desativar uma área não apaga associações históricas.

### Adiado

Peso por área, classificação hierárquica, múltiplos classificadores versionados e revisão colaborativa.

## Fluxo crawler → `item_coletado` → `item_oportunidade` → `oportunidade`

```text
1. Scheduler/orquestrador inicia uma execucao_coleta para uma fonte.
2. Crawler coleta cada item e grava payload_bruto, URL observada e hash.
3. Transformer valida e normaliza o item sem destruir o bruto, atualizando seu estado e diagnóstico.
4. Um item agregador pode ser decomposto em zero, uma ou várias oportunidades candidatas.
5. Para cada candidata, o deduplicador procura, nesta ordem conceitual:
   a. URL canônica;
   b. identificador oficial no namespace correto;
   c. identificador próprio da fonte.
6. Se houver correspondência determinística, atualiza/reconcilia a oportunidade.
7. Sem correspondência, cria uma nova oportunidade canônica.
8. Registra identificadores, localizações, áreas e proveniência em suas estruturas próprias.
9. Cria uma associação `item_oportunidade` para cada par sustentado, com papel e confiança.
10. Atualiza `item_coletado.estado_processamento`; um item aceito pode estar ligado a várias oportunidades.
11. A futura view deriva status temporal e forma o contrato de leitura do frontend.
```

Regras do fluxo:

- O crawler não grava diretamente no contrato público da view.
- O bruto é imutável do ponto de vista semântico; correções geram nova transformação ou nova coleta rastreável.
- Um erro de classificação não deve alterar o payload bruto.
- A associação N:N é a fonte de verdade da rastreabilidade entre bruto e canônico; não existe `oportunidade_id` singular em `item_coletado`.
- Nenhum item recebe organização por fallback global.
- Similaridade textual não participa da deduplicação V1.
- O pipeline usa service role apenas em ambiente servidor controlado; essa credencial nunca chega ao frontend.

## Contrato futuro de `vw_oportunidades_front_v2`

### Responsabilidade

Fornecer ao frontend uma linha estável por oportunidade, sem expor tabelas internas, payload bruto ou detalhes operacionais. O nome é reservado para uma implementação futura; nenhuma view é criada nesta etapa.

### Colunas propostas

| Coluna da view | Origem | Forma esperada |
|---|---|---|
| `id` | `oportunidade.id` | UUID |
| `titulo` | `oportunidade.titulo` | texto |
| `descricao` | `oportunidade.descricao` | texto nullable |
| `url_oficial` | `oportunidade.url_oficial` | URL |
| `url_pdf` | `oportunidade.url_pdf` | URL nullable |
| `fonte_id` | `oportunidade.fonte_id` | UUID |
| `fonte_codigo` | `fonte.codigo` | código estável |
| `fonte_nome` | `fonte.nome` | rótulo |
| `organizacao_responsavel_id` | oportunidade | UUID nullable |
| `organizacao_responsavel_nome` | organização canônica | texto nullable |
| `organizacao_responsavel_texto` | oportunidade | texto original nullable |
| `tipo_oportunidade_codigo` | taxonomia | código nullable |
| `tipo_oportunidade_nome` | taxonomia | rótulo nullable |
| `tipo_recurso_codigo` | taxonomia | código nullable |
| `tipo_recurso_nome` | taxonomia | rótulo nullable |
| `programa` | oportunidade | texto nullable |
| `data_publicacao` | oportunidade | data nullable |
| `data_abertura` | oportunidade | data nullable |
| `prazo_submissao` | oportunidade | data nullable |
| `motivo_sem_prazo` | oportunidade | código nullable |
| `data_resultado` | oportunidade | data nullable |
| `situacao_informada` | oportunidade | texto nullable |
| `ativo_administrativo` | oportunidade | booleano persistido |
| `status_temporal` | derivado | código calculado, não persistido |
| `dias_para_prazo` | derivado | inteiro nullable |
| `escopo_geografico` | oportunidade | código controlado |
| `localizacoes` | localizações agregadas | array JSON estável |
| `areas` | áreas agregadas | array JSON estável |
| `valor_minimo` | oportunidade | decimal nullable |
| `valor_maximo` | oportunidade | decimal nullable |
| `moeda` | oportunidade | código nullable |
| `qualidade_dado` | oportunidade | inteiro 0–100 nullable, somente se o contrato for aprovado |
| `qualidade_detalhes` | oportunidade | objeto JSON nullable com fórmula, versão e dimensões |
| `confianca_classificacao` | oportunidade | número nullable entre 0 e 1 |
| `atualizado_em` | oportunidade | timestamp |

### Derivações e garantias propostas

- `status_temporal` será calculado a partir de `prazo_submissao`, `motivo_sem_prazo` e data de referência, sem sobrescrever `situacao_informada`.
- Vocabulário inicial proposto para status temporal: `aberta`, `vence_hoje`, `encerrada`, `sem_prazo` e `nao_determinada`. A regra exata de abertura ainda depende da semântica de `data_abertura` e do fuso de corte.
- `dias_para_prazo` é nulo quando não existe prazo e deve usar a mesma data de referência do status.
- `localizacoes` deve conter objetos com `papel_localizacao`, país, região brasileira opcional, estado, município e confiança numérica; ordenação precisa ser determinística.
- `areas` deve conter ao menos código, nome, indicação de principal e confiança numérica, também com ordenação determinística.
- `proveniencia` detalhada e relações `item_oportunidade` são internas por padrão. A view pode expor apenas um resumo de qualidade/proveniência após decisão explícita de segurança e produto.
- A view não expõe `payload_bruto`, erros, parâmetros de coleta, hash de payload nem credenciais.
- A política de visibilidade pública — por exemplo, se filtra apenas `ativo_administrativo = true` — permanece aberta e deve ser compatível com RLS.

## RLS e fronteiras de acesso

- RLS permanece habilitada em staging e produção.
- `execucao_coleta`, `item_coletado` e `item_oportunidade` são tabelas internas do pipeline e não devem ser lidas diretamente por clientes públicos.
- Service role é exclusiva do backend/pipeline e contorna RLS apenas dentro do seu papel operacional controlado.
- A futura view deve ter política explícita de leitura; sua criação não pode presumir que views herdariam automaticamente todas as garantias pretendidas.
- Escrita editorial, quando existir, deverá usar papéis distintos do acesso público.
- Políticas concretas e testes de autorização serão definidos junto da migration, não neste documento.

## Riscos de desenho

1. **Deduplicação por URL:** páginas agregadoras ou URLs reutilizadas podem causar colisões. Namespace e regra de canonicalização precisam ser versionados.
2. **Identificador oficial:** o mesmo número pode existir em órgãos ou anos diferentes; namespace insuficiente produzirá falso merge.
3. **Fonte no identificador:** incluir `fonte_id` evita colisões contextuais, mas pode deixar de reconhecer o mesmo identificador republicado por fontes diferentes; regras de equivalência entre namespaces continuam necessárias.
4. **Relação item–oportunidade N:N:** processamento parcial de agregadores pode criar associações incompletas ou duplicar oportunidades se a operação não for idempotente.
5. **Localização 1:N:** agregação na view pode gerar linhas duplicadas se áreas e localizações forem unidas antes de agregações independentes.
6. **Confiança numérica:** números sem calibração, método e versão criam falsa precisão e não são comparáveis entre classificadores.
7. **Proveniência JSONB:** flexibilidade sem schema versionado pode produzir formatos incompatíveis e evidências órfãs.
8. **Qualidade do dado:** um escore 0–100 sem fórmula e dimensões publicadas é opaco e não deve orientar decisões sozinho.
9. **Prazo como `date`:** fontes com horário e fuso explícitos podem perder precisão. O piloto deve medir essa ocorrência.
10. **Taxonomias:** códigos alterados após publicação quebrariam filtros e integrações; devem ser estáveis.
11. **Organização nullable:** melhora a honestidade semântica, mas exige que o frontend trate corretamente texto sem FK.
12. **JSONB bruto:** crescimento, dados pessoais incidentais e retenção podem elevar custo e risco de conformidade.
13. **Hash de conteúdo:** sem contrato de serialização e versão, mudanças irrelevantes podem parecer alterações materiais.
14. **RLS em views:** configuração incorreta pode expor registros ou impedir o pipeline; requer testes dedicados antes de qualquer cliente real.
15. **Campos monetários:** chamadas com orçamento total, valor por projeto e faixas múltiplas podem não caber em um único par mínimo/máximo.

## Decisões ainda abertas

| Decisão | Impacto | Recomendação inicial | Status |
|---|---|---|---|
| Vocabulário de `papel` em `item_oportunidade` | Rastreabilidade N:N | Validar `origem`, `evidencia`, `atualizacao`, `agregador` e suas semânticas com casos reais | aberta |
| Regra e versão de canonicalização de URL | Deduplicação | Definir por fonte com núcleo comum e registrar versão no namespace | aberta |
| Namespace e fonte de identificadores oficiais | Prevenção de falso merge e reconhecimento entre fontes | Compor autoridade emissora e, quando necessário, programa/ano; definir equivalência entre fontes | aberta |
| Precisão do tipo numérico de confiança | Armazenamento e comparabilidade | Definir casas decimais após calibrar classificadores; manter intervalo 0–1 | aberta |
| Contrato de calibração da confiança | Evitar falsa precisão | Versionar método e interpretar faixas somente após validação | aberta |
| Contrato de `proveniencia` | Auditoria de inferências | Definir schema JSON versionado com campo, origem, método, confiança e item de evidência | aberta |
| Contrato de `qualidade_dado` | Transparência do escore | Só adotar 0–100 com fórmula, dimensões, versão e `qualidade_detalhes` | aberta |
| Precisão temporal do prazo | Status e experiência do usuário | Medir fontes do piloto antes de escolher entre `date` e `timestamptz` em casos específicos | aberta |
| Política exata de `motivo_sem_prazo` | Validação e filtros | Começar pelo conjunto V1 e revisar após amostras reais | aberta |
| Visibilidade da view | RLS e catálogo público | Expor somente registros administrativamente ativos ao papel público, mantendo acesso interno separado | aberta |
| Busca textual | Índices e extensões | Adiar até medir idioma, acentos e volume | aberta |
| Retenção de `payload_bruto` | Custo e conformidade | Definir prazo por fonte e classe documental antes da produção | aberta |
| Atualização versus histórico canônico | Auditoria | Preservar itens brutos e projetar versionamento da oportunidade após o piloto | aberta |
| Representação monetária complexa | Fidelidade de editais | Manter extras rastreáveis no MVP e não fingir uma faixa quando houver múltiplas modalidades | aberta |
| Exclusão e cascatas | Retenção e rastreabilidade | Preferir restrição/desativação; definir caso a caso antes do DDL | aberta |
| Política de geração de UUID | Portabilidade e operação | Escolher mecanismo suportado nativamente pelo PostgreSQL/Supabase na fase de migration | aberta |

## Critérios para transformar o desenho em migration futura

Uma migration só deve ser proposta depois de:

1. aprovar vocabulários controlados, inclusive `item_oportunidade.papel`, e regras condicionais;
2. validar o desenho com amostras das dez fontes piloto candidatas;
3. resolver as decisões de URL e identificador oficial;
4. definir políticas RLS e seus testes por papel;
5. revisar índices com consultas reais esperadas;
6. confirmar a versão PostgreSQL do staging e recursos disponíveis;
7. aprovar retenção e sanitização de payload bruto;
8. fechar os schemas versionados de proveniência e qualidade;
9. calibrar e documentar as medidas numéricas de confiança;
10. fechar o contrato V1 da view e dos consumidores.
