# Escopo de fontes do EditalFinder V2

Status: **proposta de portfólio**. Readiness técnica de todas as fontes abaixo: **a validar**.

## 1. Estados do portfólio

| Estado | Definição |
|---|---|
| MVP habilitada | Aprovada para entrar no piloto MVP após passar o gate de readiness. |
| piloto | Avaliada em staging com volume limitado; não garante promoção. |
| futura | Relevante, fora do horizonte imediato. |
| arquivada | Integração preservada apenas como referência histórica. |
| bloqueada | Não pode operar enquanto um bloqueio explícito não for resolvido. |
| removida do V2 | Deliberadamente excluída do produto V2 atual. |

Uma fonte só se torna “MVP habilitada” depois de validação; a lista inicial abaixo é uma indicação de piloto, não declara prontidão.

## 2. Piloto inicial proposto

### Brasil

| Fonte | Estado proposto | Readiness | Observação |
|---|---|---|---|
| FAPERGS | piloto | a validar | Prioridade para chamadas estaduais e teste geográfico RS/Sul. |
| FAPESP | piloto | a validar | Alto valor, exige separar página agregadora de chamada individual. |
| CNPq | piloto | a validar | Fonte nacional prioritária. |
| Finep | piloto | a validar | Diversidade de instrumentos e recursos. |
| BNDES | piloto | a validar | Requer distinguir linha permanente, chamada e conteúdo institucional. |

### Internacional

| Fonte | Estado proposto | Readiness | Observação |
|---|---|---|---|
| Grants.gov | piloto | a validar | Estados Unidos; priorizar campos estruturados e URL oficial. |
| Horizon Europe | piloto | a validar | União Europeia; validar calls, deadlines e programas. |
| ERC | piloto | a validar | Pesquisa europeia; taxonomia e calendário específicos. |
| NSF | piloto | a validar | Estados Unidos; diferenciar programas, solicitations e páginas institucionais. |
| ARPA-E | piloto | a validar | Estados Unidos; validar concept paper versus full application deadline. |

**Decisão proposta:** promover uma fonte de cada grupo por vez, somente após amostra revisada e métricas mínimas.

## 3. Fora do MVP V2

### Removidas do V2 nesta etapa

- JSPS;
- KAKENHI;
- NEDO;
- RIKEN;
- ATLA;
- demais fontes japonesas;
- MOFCOM;
- NSFC;
- portais chineses;
- demais fontes chinesas.

Classificação: **removida do V2** para o ciclo MVP. Isso não apaga código legado nem impede reavaliação futura formal.

Motivos decididos:

- baixa prioridade atual;
- idiomas e necessidade de tradução;
- alto ruído documental;
- classificações ruins observadas no legado;
- maior custo de validação;
- foco inicial em Brasil, Estados Unidos e União Europeia.

## 4. Gate de readiness

Antes de habilitar uma fonte, validar:

1. acesso permitido e estável;
2. unidade de coleta definida: oportunidade individual, não menu/portal genérico;
3. URL oficial e identidade determinística;
4. título e organização responsável confiáveis;
5. prazo distinguido de publicação, abertura e resultado;
6. geografia conforme contrato, sem defaults inventados;
7. tipo de oportunidade/recurso dentro do vocabulário aprovado;
8. deduplicação reproduzível;
9. payload bruto retido de forma segura;
10. amostra revisada manualmente;
11. testes determinísticos e observabilidade;
12. taxa de erro/ruído dentro do limite definido na fase de qualidade.

## 5. Critério para fontes futuras

Novas fontes entram como `piloto`, nunca diretamente como `MVP habilitada`. Mudança de estado exige registro de decisão com responsável, evidência, data, versão do coletor e plano de rollback.

## 6. Não objetivos

- Não assumir que integrações legadas estão prontas.
- Não portar todas as fontes por paridade numérica.
- Não usar quantidade coletada como substituto de qualidade.
- Não executar fontes removidas para preencher o staging V2.
