# Contrato canônico de oportunidade — EditalFinder V2

Status: **proposta inicial de contrato conceitual**. Não é schema SQL nem migration.

## 1. Premissas e vocabulário

**Fatos decididos:** o V2 nasce em staging paralelo, não copia o schema legado e não importa diretamente os 1.387 registros legados.

**Decisão de contrato:** uma `oportunidade` representa uma chamada, linha, programa ou instrumento acionável para o público-alvo. Notícia, resultado isolado, documento auxiliar e portal agregador não devem ser forçados para essa entidade; a taxonomia final desses tipos ainda é uma decisão aberta.

Distinções obrigatórias:

- **Fonte de coleta:** conector/portal de onde o registro foi obtido (`fonte_id`).
- **Organização responsável:** entidade que publica, administra ou responde pela oportunidade. Não é preenchida automaticamente com a fonte.
- **Situação informada:** texto/estado declarado pela fonte, preservado sem substituir o cálculo temporal.
- **Status temporal calculado:** derivado de datas e instante de referência; não é fonte de verdade persistida obrigatória.
- **Prazo de submissão:** limite para enviar candidatura/proposta.
- **Data geral de encerramento:** outro encerramento administrativo/programático; não deve substituir prazo de submissão. Inclusão canônica ainda aberta.
- **Campo canônico:** dado normalizado e validado.
- **Campo de apresentação:** label, formatação, tradução ou badge derivado; não duplica o canônico.

## 2. Convenções gerais

- Ausência: `null`, não `""`, `"N/A"`, `"Não informado"`, `0` ou data sentinela.
- Datas: data civil ISO 8601 conceitual (`YYYY-MM-DD`) quando não houver horário relevante.
- Instantes de auditoria: UTC com timezone.
- Texto: Unicode limpo, sem NUL; preservar raw em rastreabilidade quando houver normalização material.
- Valores monetários: decimal, nunca float conceitual.
- Enums: valores canônicos estáveis, separados de labels traduzidos.
- Derivações registram versão da regra e confiança.

## 3. Identificadores

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `id` | identificador opaco; obrigatório após criação | Identidade interna estável; ex. UUID ou bigint positivo | ID de fonte usado sem namespace; reutilização | Gerado pelo V2; sem fallback. Estratégia UUID/bigint aberta | persistido |
| `fonte_id` | referência; obrigatório | Conector/fonte de coleta; ex. referência a `grants_gov` | nome livre duplicado; ID da organização | Registro controlado da fonte; deve existir e estar habilitado | persistido |
| `organizacao_responsavel_id` | referência nullable | Organização associada deterministicamente | primeira organização global; ID presumido por fonte/domínio | Somente associação determinística/revisada; fallback `null` | persistido |

## 4. Conteúdo

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `titulo` | texto; obrigatório | Título oficial específico; ex. `Edital FAPERGS 04/2026 – PROBIC/PROBITI` | `Home`, `Japanese`, menu genérico, HTML vazio | Campo oficial > detalhe/PDF. Sem fallback inventado; comprimento mínimo e sinal de oportunidade | persistido |
| `descricao` | texto nullable | Resumo factual da oportunidade | menu integral, credenciais, HTML bruto sem limpeza | Descrição oficial > resumo extraído; `null` permitido; sanitização e limite | persistido |
| `url_oficial` | URL absoluta; obrigatório | Página oficial canônica da oportunidade | URL relativa, tracking como identidade, portal sem relação | Campo/link oficial; PDF somente se ele for o único documento oficial. HTTP(S), normalização conservadora | persistido |
| `url_pdf` | URL absoluta nullable | Documento principal oficial | primeiro anexo arbitrário; arquivo não PDF | Documento identificado como PDF oficial; fallback `null`; validar HTTP(S)/tipo quando possível | persistido |

Labels curtos, títulos traduzidos, resumo para card e truncamento são **campos de apresentação derivados**, não substitutos de `titulo`/`descricao`.

## 5. Origem e organização responsável

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `fonte_id` | ver identificadores | De onde coletamos | confundir com responsável | Configuração controlada do coletor | persistido |
| `organizacao_responsavel_id` | referência nullable | Vínculo normalizado | ID global/default | Match determinístico ou revisão; caso contrário `null` | persistido |
| `organizacao_responsavel_texto` | texto nullable | Nome como publicado; ex. `Fundação de Amparo à Pesquisa do Estado do RS` | `Não informado`; fonte copiada sem evidência | Campo oficial, texto do edital ou cadastro revisado; fallback `null`; trim/Unicode | persistido |

**Proposta:** manter texto junto da FK para preservar a declaração da fonte e operar enquanto a normalização organizacional evolui. Decisão final aberta.

## 6. Classificação

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `tipo_oportunidade` | vocabulário controlado nullable | Forma da oportunidade; exemplos propostos: `chamada_publica`, `grant`, `bolsa`, `licitacao`, `linha_financiamento` | `noticia_institucional` em oportunidade; label livre | Campo oficial > regra versionada > revisão; fallback `null`; vocabulário final aberto | persistido |
| `tipo_recurso` | vocabulário controlado nullable | Natureza do apoio; ex. `nao_reembolsavel`, `reembolsavel`, `bolsa`, `premio`, `contratacao` | `Oportunidade Publica`, `Não Especificado`, mistura com tipo de oportunidade | Campo oficial > classificador; fallback `null`; validar enum/taxonomia | persistido |
| `confianca_classificacao` | enum nullable | Confiança agregada ou da classificação principal: `alta`, `media`, `baixa` | percentuais sem escala; texto livre | Regra/manual com evidência; `null` se não classificado | persistido ou derivado materializado; decisão aberta |

Labels amigáveis e traduções são derivados. Área/setor não entrou no núcleo inicial porque o modelo N:N/taxonomia ainda deve ser decidido.

## 7. Geografia

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `escopo_geografico` | enum; obrigatório | `brasil`, `internacional`, `misto`, `nao_identificado` | `sul`, `Nacional`, nome de país | Evidência oficial; fallback `nao_identificado`; regras em `GEOGRAPHY_CONTRACT.md` | persistido |
| `pais_codigo` | ISO alpha-2 nullable | `BR`, `US`, `DE` | `Brasil`, `BRA`, `Internacional` | Campo/texto oficial; fallback `null`; uppercase e lista ISO | persistido |
| `regiao_brasil` | enum nullable | `norte`, `nordeste`, `centro_oeste`, `sudeste`, `sul` | Nacional/Internacional; região com país não BR | Evidência ou derivação confiável de UF; fallback `null` | persistido ou derivado de UF; decisão aberta |
| `estado_codigo` | UF nullable | `RS`, `SP` | nome completo persistido, UF estrangeira | Campo/texto oficial; fallback `null`; exige BR | persistido |
| `municipio` | texto nullable | `Porto Alegre` | cidade estrangeira neste campo; placeholder | Evidência oficial; fallback `null`; validação futura por IBGE | persistido |

## 8. Datas

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `data_publicacao` | data nullable | Data em que a oportunidade foi publicada | primeira data do texto sem contexto | Campo oficial > contexto inequívoco; fallback `null`; plausibilidade | persistido |
| `data_abertura` | data nullable | Início de submissões/inscrições | data de publicação assumida | Campo/cronograma oficial; fallback `null` | persistido |
| `prazo_submissao` | data ou instante conceitual nullable | Limite para enviar proposta; ex. `2027-05-31` | data de resultado, execução ou publicação | Campo deadline oficial > texto inequívoco; fallback `null`; registrar origem/confiança | persistido |
| `data_resultado` | data nullable | Previsão/publicação do resultado | usar como prazo | Cronograma oficial; fallback `null` | persistido |
| `situacao_informada` | texto/valor normalizado nullable | Estado declarado pela fonte, ex. `aberta`, `encerrada`, `suspensa` | sobrescrever por cálculo temporal | Campo oficial; fallback `null`; preservar raw na rastreabilidade | persistido |

**Proposta adicional em avaliação:** `data_encerramento_geral`, separada de `prazo_submissao`, somente se fontes realmente apresentarem outro encerramento relevante. Não incluí-la automaticamente no schema mínimo.

**Derivado:** `status_temporal` deve ser calculado com `prazo_submissao`, data atual e regras versionadas, por exemplo `aberta`, `vencendo`, `encerrada`, `sem_prazo`, `nao_aplicavel`. Não deve mascarar `situacao_informada`.

## 9. Valores

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `valor_minimo` | decimal nullable | Menor valor elegível/concedido; `50000.00` | float impreciso, texto `R$ 50 mil`, negativo | Campo oficial; parser com raw/evidência; fallback `null`; >=0 | persistido |
| `valor_maximo` | decimal nullable | Limite superior; `900000.00` | ano/número de edital capturado como dinheiro | Campo oficial; fallback `null`; >= mínimo quando ambos | persistido |
| `moeda` | ISO 4217 nullable | `BRL`, `USD`, `EUR` | `R$`, `$`, `real`, moeda presumida silenciosamente | Campo/símbolo inequívoco; fallback `null`; uppercase/lista ISO | persistido |

Valores formatados (`R$ 900 mil`) são derivados de decimal + moeda. Se apenas um total global estiver disponível e não for limite por proposta, não deve preencher min/max sem semântica definida.

## 10. Qualidade

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `qualidade_dado` | inteiro nullable, escala proposta 0–100 | Completude/confiabilidade operacional | score sem versão; usar relevância como qualidade | Regra versionada; fallback `null`; faixa 0–100 | derivado materializado |
| `confianca_classificacao` | enum nullable | Confiança na taxonomia | confundir com qualidade geral | Classificador/manual; fallback `null` | persistido/derivado materializado |
| `ativo_administrativo` | boolean; obrigatório | Controle editorial do V2 | mudar automaticamente porque prazo venceu | Default proposto `true` na criação; somente processo administrativo altera | persistido |

`ativo_administrativo` não equivale a oportunidade temporalmente aberta.

## 11. Rastreabilidade

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `hash_conteudo` | hash criptográfico nullable | Impressão reproduzível do conteúdo canônico selecionado | hash usado como ID sem política; algoritmo implícito | Pipeline V2; algoritmo/versão registrados; fallback `null` antes do processamento | persistido |
| `criado_em` | instante UTC; obrigatório | Criação no V2 | data da fonte | Sistema; imutável | persistido |
| `atualizado_em` | instante UTC; obrigatório | Última alteração canônica | instante de coleta sem mudança | Sistema; monotônico | persistido |

**Proposta:** rastrear ainda `coletado_em`, versão do coletor/transformer, identificador do payload bruto, origem/confiança por campo e histórico. O formato depende das decisões de retenção/histórico.

## 12. Metadados extras

| Campo | Tipo / req. | Significado e exemplos válidos | Proibido | Origem, fallback e validação | Natureza |
|---|---|---|---|---|---|
| `dados_extras` | objeto JSON conceitual; obrigatório ou default vazio a decidir | Metadados específicos de fonte sem campo canônico | secrets, PII desnecessária, duplicata permanente de todo contrato, valores sem namespace | Transformer V2; fallback `{}`; JSON serializável, limites e namespaces por fonte | persistido |

Promover um valor de `dados_extras` para campo canônico exige decisão de contrato, migration futura e plano de backfill; não deve ocorrer por conveniência de uma fonte.

## 13. Validação cruzada mínima

1. `titulo`, `url_oficial` e `fonte_id` presentes.
2. URL oficial absoluta e permitida.
3. IDs sem defaults globais.
4. `valor_minimo <= valor_maximo` quando ambos existirem.
5. Valor monetário exige moeda quando a moeda for conhecida; não inventar moeda.
6. `data_abertura <= prazo_submissao` quando comparáveis, salvo exceção documentada.
7. Geografia cumpre `GEOGRAPHY_CONTRACT.md`.
8. Enums pertencem à versão taxonômica ativa.
9. Inferências possuem origem, método e confiança.
10. Falha de campo opcional produz `null`; falha de campo obrigatório rejeita/quarentena, não placeholder.

## 14. O que não portar do legado por padrão

- aliases duplicados de um mesmo conceito;
- status persistidos que podem ser derivados;
- rótulos de apresentação;
- campos vazios específicos de uma fonte;
- organização global/default;
- geografia inferida sem evidência;
- JSON e coluna espelho sem regra de autoridade;
- scores sem versão/semântica.
