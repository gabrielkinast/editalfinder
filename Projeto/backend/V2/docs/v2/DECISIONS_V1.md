# Decisões arquiteturais V1 — EditalFinder V2

Status: **aprovado para orientar o desenho do MVP V2**.  
Escopo: contrato e modelo conceitual. Este documento não é SQL, migration nem autoriza alteração remota.

## 1. Objetivo da baseline

Esta V1 encerra as decisões estruturais necessárias para desenhar o schema mínimo do staging V2 sem copiar o modelo legado. Mudanças posteriores devem ser registradas como nova decisão, com impacto, compatibilidade e plano de migração.

## 2. Decisões aprovadas

### Identidade e relacionamentos

1. **UUID nas entidades principais.** Entidades com identidade própria usarão UUID. Identificadores externos não substituem a identidade interna.
2. **Chaves compostas nas tabelas de junção.** Relações puras N:N não receberão UUID artificial no MVP; sua identidade será o par de FKs.
3. **Identificadores externos normalizados.** URL canônica, identificador oficial e outros identificadores ficarão em `oportunidade_identificador`. A identidade e a unicidade serão controladas por tipo, namespace, fonte e valor normalizado; `oportunidade.url_oficial` não terá necessariamente UNIQUE direto.
4. **Item coletado e oportunidade em relação N:N.** A relação será materializada por `item_oportunidade`, com chave composta. Uma página agregadora pode gerar várias oportunidades e uma oportunidade pode ser sustentada por vários itens coletados.

### Taxonomias

5. **Tabelas taxonômicas** para `tipo_oportunidade`, `tipo_recurso` e `area`.
6. **CHECK constraints somente para domínios pequenos e estáveis**, como escopo, papel de localização, tipo de identificador, estado de processamento e motivo sem prazo. Taxonomias evolutivas não serão enums rígidos.
7. **Área em relação N:N** por `oportunidade_area`.

### Organização

8. **FK nullable + texto original preservado.** `organizacao_responsavel_id` só será preenchida por associação determinística. `organizacao_responsavel_texto` preservará o valor publicado/coletado.
9. **Nenhuma organização global/default.** Ausência de match produz FK nula; fonte de coleta não vira automaticamente organização responsável.

### Geografia

10. **`escopo_geografico` pertence à oportunidade.** Valores V1: `brasil`, `internacional`, `misto`, `nao_identificado`.
11. **Localizações em relação 1:N** por `oportunidade_localizacao`, com `regiao_brasil` opcional.
12. **País em ISO 3166-1 alpha-2**, armazenado conceitualmente como `text` e validado como duas letras maiúsculas.
13. **Estado em UF brasileira** somente quando o país for `BR`; município é opcional.
14. **`papel_localizacao` controlado** para expressar a função semântica da localização. Valores V1: `elegibilidade`, `execucao`, `beneficiarios`, `origem`, `organizacao_responsavel` e `nao_especificado`.
15. Continuam obrigatórias as invariantes de `GEOGRAPHY_CONTRACT.md`: localização estrangeira não pode ter UF brasileira; ausência vira `null`; fonte/domínio não são evidência definitiva.

### Coleta, payload bruto e documentos

16. **Payload bruto no PostgreSQL no MVP**, em `item_coletado.payload_bruto` do tipo conceitual JSONB.
17. **Supabase Storage adiado** para documentos grandes e uma futura política de objetos imutáveis. PDF/binário não deve ser embutido no JSONB; no MVP preserva-se a URL/metadado permitido.
18. Cada item bruto pertence a uma execução e fonte, recebe hash e metadados suficientes para reprocessamento/auditoria.
19. **Estado de processamento controlado.** `item_coletado.estado_processamento` usa `coletado`, `normalizado`, `aceito`, `rejeitado`, `erro`, `quarentena` ou `ignorado`, acompanhado pelos campos de diagnóstico aplicáveis.

### Deduplicação

20. **Deduplicação determinística inicial** por URL canônica e identificador oficial, representados em `oportunidade_identificador` com fonte e namespace explícitos.
21. **Similaridade textual adiada.** Ela poderá gerar candidatos para revisão no futuro, mas não fará merge automático no MVP.
22. Hash de conteúdo serve para mudança/auditoria, não como única identidade da oportunidade.

### Oportunidade, datas e status

23. **`programa` como texto opcional no MVP.** Não haverá entidade/taxonomia de programa nesta fase.
24. **Prazo de submissão nullable**, acompanhado por `motivo_sem_prazo` quando aplicável.
25. **Situação informada persistida** separadamente do cálculo temporal.
26. **Ativo administrativo persistido.** Curadoria administrativa não será alterada automaticamente por vencimento.
27. **Status temporal e dias para o prazo derivados na futura view.** A regra deve ser única, testada e baseada em `prazo_submissao` e data de referência.
28. **Confiança numérica.** Confianças de classificação, associação item–oportunidade, área e localização inferida usam escala numérica inclusiva de 0 a 1.
29. **Proveniência estruturada.** `oportunidade.proveniencia` em JSONB explicará origem, método, confiança e item de evidência dos campos inferidos.
30. **Qualidade exige contrato.** A proposta inicial é `qualidade_dado smallint` de 0 a 100 acompanhada de `qualidade_detalhes JSONB`; fórmula, dimensões e versionamento permanecem abertos.
31. **Temporalidade explícita.** Timestamps operacionais representam instantes em UTC; datas civis de editais permanecem `date`.
32. **Moeda como texto validado.** Código ISO 4217 com três letras maiúsculas, evitando `char(n)`.
33. `oportunidade_evento` está adiada. No MVP persistem apenas datas canônicas aprovadas na oportunidade.

### Segurança e acesso

34. **RLS permanece habilitada.** O staging V2 não operará sem RLS.
35. **Pipeline acessa tabelas internas via service role**, somente em ambiente server-side controlado. Credenciais nunca pertencem ao crawler distribuído, frontend, payload ou log.
36. A futura view pública terá contrato e permissões mínimas; sua política exata ainda exige desenho e testes por papel.

### Escopo funcional e de fontes

37. **Profiles, favoritos e usuários de aplicação adiados.** Auth/personalização não fazem parte do schema mínimo.
38. **Fontes japonesas e chinesas fora do MVP**, incluindo JSPS, KAKENHI, NEDO, RIKEN, ATLA, MOFCOM, NSFC e demais portais desses países.
39. O piloto continua focado em fontes selecionadas de Brasil, Estados Unidos e União Europeia, todas com readiness a validar.

## 3. Schema mínimo aprovado

O primeiro desenho contempla somente:

- `fonte`
- `organizacao`
- `tipo_oportunidade`
- `tipo_recurso`
- `area`
- `execucao_coleta`
- `item_coletado`
- `item_oportunidade`
- `oportunidade`
- `oportunidade_identificador`
- `oportunidade_localizacao`
- `oportunidade_area`

A definição conceitual está em `SCHEMA_DESIGN_V1.md`.

## 4. Itens explicitamente fora da V1

- SQL e migrations;
- Storage e ingestão de documentos binários;
- similaridade textual/fuzzy merge;
- `oportunidade_evento` e calendário arbitrário;
- entidade `programa`;
- profiles, favoritos, usuários e Auth da aplicação;
- frontend e mapper V2;
- importação integral do legado;
- fontes japonesas/chinesas;
- limpeza ou alteração do Legacy.

## 5. Regras de governança

- Uma FK nunca é preenchida por fallback semântico.
- Nulos não viram placeholders.
- Campo derivado não duplica silenciosamente a fonte de verdade.
- JSONB não substitui campos canônicos nem recebe secrets/PII desnecessária.
- Taxonomia possui slug estável, label de apresentação e estado administrativo.
- Toda inferência material registra origem, método e confiança.
- Mudança desta baseline exige decisão arquitetural versionada.

## 6. Decisões ainda abertas, não bloqueantes para este desenho

- valores finais de `motivo_sem_prazo`;
- contrato, fórmula, dimensões e versão de `qualidade_dado`;
- schema interno e versionamento de `proveniencia` e `qualidade_detalhes`;
- semântica dos valores de `papel` em `item_oportunidade`;
- política de versionamento/imutabilidade de `item_coletado`;
- retenção de payload bruto;
- estratégia de histórico de alterações canônicas;
- política de leitura anônima/autenticada da futura view;
- timezone e regra de corte para status temporal;
- código IBGE para municípios;
- taxonomia inicial e governança de seeds.
