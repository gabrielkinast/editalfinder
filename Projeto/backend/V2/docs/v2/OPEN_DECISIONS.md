# Decisões abertas do EditalFinder V2

Todos os itens deste documento têm status **aberta**. Recomendações são propostas iniciais, não decisões aprovadas.

## 1. Identificador: UUID ou bigint

- Alternativas: UUID gerado pela aplicação/banco; bigint sequencial; identificador distribuído alternativo.
- Vantagens: UUID desacopla ambientes/importações; bigint é compacto, legível e eficiente.
- Riscos: UUID aumenta tamanho de índices; bigint exige coordenação em migrações/replicação.
- Recomendação inicial: UUID para entidades V2, mantendo IDs externos em campos próprios com namespace.
- Status: **aberta**.

## 2. Enums PostgreSQL, tabelas taxonômicas ou CHECK

- Alternativas: enum nativo; tabelas referenciadas; texto + CHECK versionado.
- Vantagens: enum é forte/simples; tabela é extensível e documentável; CHECK é leve.
- Riscos: enum é mais rígido; tabela adiciona JOIN/governança; CHECK exige migration para evoluir.
- Recomendação inicial: tabelas para taxonomias evolutivas; CHECK para enums pequenos e estáveis como escopo.
- Status: **aberta**.

## 3. Organização textual junto com FK

- Alternativas: somente FK; FK + texto declarado; somente texto no MVP.
- Vantagens: FK normaliza; texto preserva evidência e permite operação antes do match.
- Riscos: FK + texto pode divergir; somente FK perde declaração; somente texto dificulta agregação.
- Recomendação inicial: manter ambos, com FK nullable e texto como evidência; nunca preencher FK por default global.
- Status: **aberta**.

## 4. Uma ou várias localizações

- Alternativas: localização principal na oportunidade; array/JSON; relação N:N de localizações.
- Vantagens: campo único simplifica MVP; N:N representa chamadas multiestado/multipaís corretamente.
- Riscos: campo único perde informação; JSON dificulta constraints; N:N aumenta complexidade.
- Recomendação inicial: decidir com amostra das dez fontes piloto; preferir N:N se multi-localidade for frequente/material.
- Status: **aberta**.

## 5. Áreas e setores em N:N

- Alternativas: uma área principal; array controlado; tabelas N:N versionadas.
- Vantagens: N:N evita strings livres e suporta hierarquia; array simplifica leitura.
- Riscos: taxonomia prematura; JOINs; fragmentação de labels.
- Recomendação inicial: taxonomia pequena versionada + N:N, após conjunto ouro; não portar listas legadas automaticamente.
- Status: **aberta**.

## 6. Política de deduplicação

- Alternativas: URL canônica; identificador oficial por fonte; hash; chave composta; matching probabilístico com revisão.
- Vantagens: ID oficial/URL são explicáveis; matching cobre republicações.
- Riscos: URLs mudam; hashes mudam com texto; fuzzy merge pode unir oportunidades distintas.
- Recomendação inicial: chave determinística por fonte quando disponível, URL canônica como segunda opção, candidatos fuzzy sem merge automático.
- Status: **aberta**.

## 7. Oportunidade, notícia e portal estratégico

- Alternativas: tabelas separadas; supertipo de conteúdo; uma tabela com discriminador.
- Vantagens: separação evita contaminar filtros; supertipo facilita feed unificado.
- Riscos: tabelas separadas duplicam infraestrutura; tabela única acumula nulos e regras condicionais.
- Recomendação inicial: entidades separadas com contrato/base de rastreabilidade compartilhada; oportunidade exige acionabilidade.
- Status: **aberta**.

## 8. Estratégia de RLS

- Alternativas: leitura pública da view e escrita service-role; leitura autenticada; policies por papel/tenant.
- Vantagens: pública simplifica catálogo; autenticada melhora controle; por papel suporta operação/admin.
- Riscos: views/grants podem contornar intenção; policies complexas falham silenciosamente ou degradam performance.
- Recomendação inicial: deny-by-default nas tabelas, views/queries de leitura explicitamente revisadas, testes por papel.
- Status: **aberta**.

## 9. Auth no V2

- Alternativas: reutilizar Auth/projeto legado; Auth do novo Supabase; camada externa; sem Auth no piloto.
- Vantagens: novo Auth isola V2; reutilização reduz fricção.
- Riscos: migração de identidade, dupla conta, acoplamento ao legado.
- Recomendação inicial: sem usuários reais no staging; desenhar identidade antes da fase frontend e testar migração separadamente.
- Status: **aberta**.

## 10. Payload bruto no PostgreSQL ou Storage

- Alternativas: JSONB no banco; objeto imutável no Storage; ambos com metadado/ponte.
- Vantagens: JSONB facilita consulta; Storage reduz peso e preserva artefato original.
- Riscos: banco cresce/custa; Storage exige integridade, versionamento e controle de acesso.
- Recomendação inicial: Storage imutável para payload/documentos + metadado e hash no PostgreSQL; pequenas respostas estruturadas podem ter snapshot controlado.
- Status: **aberta**.

## 11. Retenção de payloads

- Alternativas: indefinida; janela temporal; última versão; amostragem após prazo.
- Vantagens: retenção longa melhora auditoria/reprocessamento; janela reduz custo/risco.
- Riscos: custo, direitos, PII acidental e obrigações de exclusão.
- Recomendação inicial: política por classe de dado, com prazo mínimo para reproduzir transformações e expurgo de PII/secrets.
- Status: **aberta**.

## 12. Atualização e histórico

- Alternativas: overwrite; histórico por evento; snapshots versionados; temporal tables/auditoria.
- Vantagens: overwrite é simples; eventos/snapshots explicam mudanças e prazos.
- Riscos: histórico cresce; eventos incompletos; overwrite perde evidência.
- Recomendação inicial: estado atual + eventos de mudança para campos materiais, com hash e origem da coleta.
- Status: **aberta**.

## 13. Oportunidades sem prazo

- Alternativas: `prazo_submissao=null`; enum de motivo; entidade de calendário separada.
- Vantagens: null é correto para desconhecido; motivo distingue permanente, a definir e ausente.
- Riscos: null sozinho é ambíguo; enum mal inferido cria falsa certeza.
- Recomendação inicial: prazo nullable + motivo controlado opcional (`nao_informado`, `a_definir`, `fluxo_continuo`, `nao_aplicavel`) somente com evidência.
- Status: **aberta**.

## 14. Chamadas recorrentes ou permanentes

- Alternativas: uma oportunidade atualizada; instância por ciclo; programa pai + chamadas filhas.
- Vantagens: instância por ciclo preserva prazos/histórico; pai/filho modela continuidade.
- Riscos: uma linha sobrescreve ciclos; pai/filho complica ingestão; duplicidade aparente.
- Recomendação inicial: programa/linha permanente como entidade pai e cada ciclo acionável como oportunidade distinta quando houver datas/identidade próprias.
- Status: **aberta**.

## 15. Data geral de encerramento

- Alternativas: não incluir; incluir `data_encerramento_geral`; modelar eventos de calendário.
- Vantagens: campo separado evita contaminar prazo; eventos suportam cronogramas complexos.
- Riscos: sem semântica uniforme vira duplicata de prazo; eventos aumentam escopo.
- Recomendação inicial: não colocar no schema mínimo até haver casos validados; nunca usar como alias automático de prazo.
- Status: **aberta**.

## 16. Persistir ou derivar região brasileira

- Alternativas: persistir; derivar de UF; persistir somente quando escopo regional sem UF.
- Vantagens: derivação evita inconsistência; persistência suporta oportunidades multiestaduais regionais.
- Riscos: UF nula não representa região; dois campos podem divergir.
- Recomendação inicial: permitir região explícita com evidência e validar coerência quando UF existir.
- Status: **aberta**.

## 17. Materialização de status temporal

- Alternativas: calcular em query/frontend; view; coluna atualizada por job.
- Vantagens: derivar evita staleness; materializar melhora filtro/desempenho.
- Riscos: frontend pode duplicar regra; job pode atrasar; timezone/data de referência.
- Recomendação inicial: uma regra backend compartilhada, exposta pela view; materializar apenas se medição justificar.
- Status: **aberta**.

## 18. Estrutura de proveniência por campo

- Alternativas: JSON de evidências; tabela por campo; logs externos; apenas proveniência do registro.
- Vantagens: por campo explica inferências; por registro é simples.
- Riscos: volume/complexidade; JSON sem constraints; logs podem expirar.
- Recomendação inicial: proveniência do registro obrigatória e evidência por campo para geografia, prazo, organização, tipo e valor.
- Status: **aberta**.

## 19. Escala e semântica de qualidade

- Alternativas: 0–100; categorias; dimensões separadas; sem score agregado.
- Vantagens: agregado facilita triagem; dimensões são explicáveis.
- Riscos: score único mascara falhas críticas; pesos envelhecem.
- Recomendação inicial: dimensões/flags explicáveis e score agregado versionado apenas para ordenação.
- Status: **aberta**.

## 20. Política de exclusão e quarentena

- Alternativas: soft delete; estado administrativo; tabela de quarentena; exclusão física com auditoria.
- Vantagens: quarentena preserva evidência; soft delete facilita rollback.
- Riscos: dados ocultos podem reaparecer; retenção indevida; complexidade de visibilidade.
- Recomendação inicial: quarentena separada para falhas de ingestão e `ativo_administrativo` para curadoria; exclusão física sob política explícita.
- Status: **aberta**.

## Decisões humanas bloqueantes para a Fase 1

1. UUID ou bigint.
2. Modelo de taxonomias/enums.
3. FK + texto de organização.
4. Localização única ou N:N.
5. Modelo de oportunidade/notícia/portal.
6. Política inicial de deduplicação.
7. Onde e por quanto tempo reter payload bruto.
8. Estratégia de histórico/proveniência.
9. Representação de sem prazo/recorrência.
10. Estratégia inicial de RLS/Auth para staging e produção.
