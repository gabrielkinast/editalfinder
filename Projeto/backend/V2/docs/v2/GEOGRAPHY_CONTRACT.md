# Contrato de geografia do EditalFinder V2

Status: **proposta inicial de contrato**. Este documento não define schema SQL.

## 1. Princípios

**Fatos decididos para o V2:**

- escopo geográfico, país, região brasileira e estado são conceitos distintos;
- ausência de evidência vira `null` ou `nao_identificado`, nunca uma localização inventada;
- toda inferência deve registrar evidência, método e confiança;
- fonte e domínio podem sustentar apenas fallback de baixa confiança;
- valores de apresentação, como “Nacional” e “Internacional”, não pertencem ao campo de região brasileira.

## 2. Campos canônicos

### `escopo_geografico`

Enum conceitual obrigatório:

| Valor | Significado |
|---|---|
| `brasil` | Elegibilidade/aplicação restrita ao Brasil ou a localizações brasileiras. |
| `internacional` | Oportunidade estrangeira sem componente brasileiro afirmado. |
| `misto` | Envolve explicitamente Brasil e exterior, ou aceita participantes/localizações de ambos. |
| `nao_identificado` | Evidência insuficiente para classificar. |

O escopo responde “onde/para quem a oportunidade se aplica?”. Não responde onde a fonte está hospedada.

### `pais_codigo`

- Tipo conceitual: string nullable.
- Formato: ISO 3166-1 alpha-2, duas letras maiúsculas, por exemplo `BR`, `US`, `DE`, `JP`.
- `null`: país não identificado ou oportunidade genuinamente multinacional sem país principal.
- Não aceitar nomes (`Brasil`), alpha-3 (`BRA`), lowercase (`br`) nem rótulos (`Internacional`). Valores reconhecidos podem ser normalizados antes da validação, preservando o raw na rastreabilidade.

### `regiao_brasil`

Enum conceitual nullable:

- `norte`
- `nordeste`
- `centro_oeste`
- `sudeste`
- `sul`
- `null`

Somente descreve macrorregião oficial brasileira. Nunca recebe `Nacional`, `Internacional`, `Brasil`, `América Latina`, `global` ou nomes de países.

### `estado_codigo`

- Tipo conceitual: string nullable.
- Formato: UF brasileira oficial com duas letras maiúsculas, por exemplo `RS`, `SP`, `MG`.
- `null` para oportunidades estrangeiras, nacionais sem estado específico ou sem evidência.
- O preenchimento implica `pais_codigo = BR`.

### `municipio`

- Tipo conceitual: string nullable.
- Nome oficial ou suficientemente identificável do município brasileiro.
- Proposta: futuramente associar a código IBGE; decisão ainda aberta.
- Município preenchido exige `pais_codigo = BR` e, preferencialmente, `estado_codigo`.

## 3. Invariantes obrigatórias

1. `pais_codigo != BR` implica `regiao_brasil = null`.
2. `pais_codigo != BR` implica `estado_codigo = null`.
3. `estado_codigo != null` implica `pais_codigo = BR`.
4. `municipio != null` implica `pais_codigo = BR`.
5. `regiao_brasil` nunca recebe `Nacional` ou `Internacional`.
6. Ausência de informação vira `null`, não default `BR`, `nacional`, `internacional` ou região inferida.
7. `escopo_geografico` não é derivado automaticamente de `regiao_brasil` sem evidência do edital.
8. Domínio `.br`, `.gov`, `.eu` ou fonte conhecida não é prova definitiva de escopo.

## 4. Evidência e confiança

**Proposta:** cada valor geográfico inferido deve ser acompanhado em rastreabilidade ou `dados_extras` estruturados por:

- campo inferido;
- valor;
- origem: campo estruturado, texto oficial, PDF, cadastro da fonte, domínio ou regra manual;
- trecho/caminho de evidência quando aplicável;
- método/versão da regra;
- confiança: `alta`, `media`, `baixa`;
- instante de processamento.

Ordem recomendada de evidência:

1. campo estruturado oficial;
2. texto inequívoco do edital/PDF;
3. cadastro manual revisado;
4. metadado da fonte;
5. domínio/fonte, somente baixa confiança.

## 5. Exemplos válidos

| Caso | escopo | país | região | estado | Justificativa |
|---|---|---|---|---|---|
| Fomento estadual RS | `brasil` | `BR` | `sul` | `RS` | Recorte estadual explícito. |
| Chamada nacional | `brasil` | `BR` | `null` | `null` | Não restringe macrorregião/UF. |
| Grant federal dos EUA | `internacional` | `US` | `null` | `null` | Campos brasileiros não se aplicam. |
| Cooperação Brasil–Alemanha | `misto` | `null` | `null` | `null` | Mais de um país, sem país principal. |
| Portal sem elegibilidade clara | `nao_identificado` | `null` | `null` | `null` | Não inventar pelo domínio. |
| Chamada paulista | `brasil` | `BR` | `sudeste` | `SP` | Estado determina região coerente. |

## 6. Exemplos inválidos

| Valores | Motivo |
|---|---|
| `pais_codigo=JP`, `regiao_brasil=sudeste` | País estrangeiro não pode ter região brasileira. |
| `pais_codigo=US`, `regiao_brasil=centro_oeste` | Mesma violação. |
| `pais_codigo=BR`, `regiao_brasil=internacional` | Valor fora do enum e mistura de conceitos. |
| `pais_codigo=JP`, `estado_codigo=RS` | UF implica Brasil. |
| `pais_codigo=Brasil` | Não é ISO alpha-2. |
| `pais_codigo=br` persistido | Deve ser normalizado para `BR` antes da persistência. |
| `regiao_brasil=Nacional` | Nacional é apresentação/escopo, não macrorregião. |
| `escopo_geografico=sul` | Sul pertence a `regiao_brasil`. |
| sem evidência + `pais_codigo=BR` por domínio `.br` | Inferência definitiva indevida. |

## 7. Campos de apresentação

Rótulos como “Brasil”, “Internacional”, “Misto”, “Sul” e “Rio Grande do Sul” devem ser derivados no frontend/i18n dos valores canônicos. Não devem ser persistidos como substitutos dos códigos.

## 8. Questão estrutural aberta

Este contrato assume uma localização principal. O suporte a múltiplos países, estados ou municípios por oportunidade deve ser decidido antes do schema mínimo; ver `OPEN_DECISIONS.md`.
