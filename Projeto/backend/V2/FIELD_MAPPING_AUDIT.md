# Auditoria de mapeamento de campos dos editais

Data da auditoria: 2026-07-17  
Escopo: inspeção estática do repositório, sem consulta ao Supabase remoto e sem alteração de código, SQL, schema ou configuração.

## Resumo executivo

O caminho operacional principal encontrado é:

```text
backend/<fonte>/outputs/*_editais.json
  -> CORE/transformer.py (aliases, limpeza, enriquecimento e classificação)
  -> CORE/transformer/<fonte>_standardized.json
  -> CORE/schema.py::normalizar
  -> CORE/loader.py::map_to_db_schema / extras_to_filter_columns
  -> Supabase public.edital
  -> public.vw_editais_front (preferencial) ou public.edital (fallback)
  -> frontend dataService.getEditais
  -> mapRawEditalRow
  -> EditaisPage/Dashboard
  -> components/dashboard/EditalCard
```

Os campos não percorrem todos o mesmo caminho. `titulo`, `link`, `fonte`, prazo e `situacao` têm caminho legado direto. `pais`, `estado`, `area`, `tipo_oportunidade`, `tipo_recurso` e `orgao_responsavel` dependem parcialmente de `extras` e do schema estendido. `abrangencia` é apenas alias de `regiao`. `escopo` não possui coluna nem mapeamento de UI no fluxo auditado. `id_organizacao` recebe um ID global obtido da primeira linha de `organizacao`, não um relacionamento resolvido por edital, e nem sequer é exposto pela view atual.

## 1. Caminho do JSON bruto ao card

1. Cada coletor grava JSON bruto em `backend/<fonte>/outputs/`. O formato varia por fonte. O normalizador de aliases aceita, entre outros, `title/name/nome/... -> titulo`, `url/href/... -> link`, `source/origem/portal/orgao/instituicao -> fonte`, `deadline/closing_date/prazo/... -> fim_inscricao` e `region/abrangencia -> regiao` (`backend/CORE/data_cleaning.py:15-120`).
2. `transform_generic` aplica `_transform_item_with_result`, rejeita itens pelo gate, limpa `titulo` e `descricao`, tenta enriquecer por PDF, normaliza datas, infere tipo de recurso e região e preserva campos não canônicos em `extras` (`backend/CORE/transformer.py:879-962`, `2281-2282`, `2755-2865`).
3. O resultado padronizado usa o núcleo `titulo`, `descricao`, `link`, `fonte`, `data_publicacao`, `fim_inscricao`, `situacao`, `tipo_recurso`, `regiao`, mais `extras` (`backend/CORE/transformer.py:2840-2854`). Arquivos reais em `backend/CORE/transformer/*_standardized.json` confirmam esse shape.
4. O loader lê esses arquivos, chama `schema.normalizar`, faz backfill de prazo e roteamento, e mapeia para o banco (`backend/CORE/loader.py:1075-1155`). `schema.normalizar` converte datas aceitas por `datetime.fromisoformat` para `YYYY-MM-DD` e move chaves fora do modelo-base para `extras` (`backend/CORE/schema.py:8-76`).
5. `map_to_db_schema` converte `fonte -> fonte_recurso`, `fim_inscricao -> prazo_envio`, preserva `regiao`, calcula o texto do órgão e monta as colunas legadas (`backend/CORE/loader.py:396-474`). Com `EDITALFINDER_EXTENDED_SCHEMA=true`, `extras_to_filter_columns` espelha campos ricos em colunas (`backend/CORE/loader.py:658-666`; `taxonomy_filtros.py:4476-4545`).
6. O frontend consulta por padrão `vw_editais_front`, paginada em lotes de 1.000. Se a view falhar ou vier vazia, consulta `edital` (`frontend/EditalFinder-React/src/config/env.js:53`; `services/dataService.js:99-171`).
7. Cada linha passa por `mapRawEditalRow`, que renomeia e deriva o modelo de UI (`frontend/EditalFinder-React/src/utils/edital/editalRowMapper.js:37-203`).
8. `EditalCard` apresenta título, uma fonte usada como órgão, tipos, localização, prazo, badges de status e links (`frontend/EditalFinder-React/src/components/dashboard/EditalCard.jsx:46-236`).

## 2. Mapeamento campo a campo

| Conceito | JSON bruto / aliases | JSON padronizado | Supabase `edital` | View `vw_editais_front` | Modelo do frontend | Uso no card |
|---|---|---|---|---|---|---|
| Título | `titulo`, `title`, `name`, `nome`, `chamada`, `edital`, `oportunidade`, `objeto` | `titulo` | `titulo` | `titulo` | `titulo_original_raw`; `titulo` passa por `getDisplayTitle` | cabeçalho `edital.titulo` |
| Link | `link`, `url`, `href`, `url_detalhe`, `detail_url`, etc. | `link`; também `extras.url_detalhe` | `link`; opcionalmente `url_detalhe`, `pdf_url`, `link_inscricao` | `link`, `url_detalhe`, `pdf_url` | `linkOriginal`, `link_raw`, `pdfUrl`, `linkInscricao` | botões resolvidos por `resolveActionLinks` |
| Fonte | `fonte`, `source`, `origem`, `portal`, `orgao`, `instituicao`; fallback `source_name.upper()` | `fonte` | `fonte_recurso` | **`fonte`** (`e.fonte_recurso as fonte`) | `orgao`, `fonte_recurso_display`, `fonte_raw` | badge de fonte e linha “Fonte recurso” |
| Órgão textual | normalmente `extras.orgao_responsavel`; fallbacks `agency`, `orgao_contratante`, `instituicao`, fonte | permanece em `extras.orgao_responsavel` | `orgao_responsavel` somente no schema estendido; também em `extras` | `orgao_responsavel` | **não mapeado por `mapRawEditalRow`** | **não usado**; card mostra `fonte` como `orgao` |
| FK organização | pode existir como chave órfã, mas não é resolvida por fonte | `extras.id_organizacao` se vier como órfã; não faz parte do modelo-base | `id_organizacao` = primeira organização retornada por lookup global, quando disponível | **não selecionado** | não mapeado | não usado |
| País | em geral `extras.pais` | `extras.pais` | `pais` apenas com espelhamento do schema estendido; `extras.pais` | `pais` | `pais_raw`; influencia `estado` derivado | badge Internacional e linha Local |
| Estado/UF | em geral `extras.estado`; possíveis `uf`/`cidade` em extras/colunas auxiliares | principalmente `extras.estado` | `estado`; há também `uf` e `cidade` na lista de colunas estendidas do loader, mas o espelho principal usa `estado`/`municipio` | `estado`, `municipio` (não `uf`/`cidade`) | tenta `m.uf ?? m.estado`; `uf_raw=m.uf`; `cidade_raw=m.cidade` | linha Local |
| Região | `regiao`, `region`, `abrangencia` | `regiao` no topo; alguns enriquecedores também mantêm `extras.regiao` | `regiao` legado | **não selecionado pela definição atual da view** | `regiao`, `regiao_raw`, `localidade` | linha Local, apenas no fallback direto ou outra view customizada |
| Abrangência | `abrangencia` | convertida em `regiao`; deixa de existir como conceito separado | não há coluna | não há campo | não há campo | não usado diretamente |
| Escopo | `escopo` ou `escopo_geografico`, tipicamente em extras/enriquecimento | `extras.escopo` / `extras.escopo_geografico` | somente `extras`/tabela de fragmentos; sem coluna dedicada | somente dentro de `extras` | apenas `extras_raw`, sem projeção | não exibido |
| Área | frequentemente `extras.area`; `temas` pode existir no topo | `extras.area`; `temas` pode permanecer como órfã/top-level | `area text[]` no schema estendido; legado `temas text` | `area` | `area = m.area ?? m.temas ?? classificação local` | não há linha “Área”; aparece indiretamente em resumo/filtros |
| Tipo de oportunidade | normalmente `extras.tipo_oportunidade` | `extras.tipo_oportunidade` | `tipo_oportunidade` no schema estendido | `tipo_oportunidade` | `tipo_oportunidade_raw` | linha “Oport./recurso”; também status de linha permanente |
| Tipo de recurso | `tipo_recurso` ou aliases `resource_type`, `modalidade`, `tipo`, `categoria`, `type`; pode vir em extras | `tipo_recurso` no topo e espelho em `extras` | `tipo_recurso` no schema estendido; **também gravado em `objetivo` como primeira opção** | `tipo_recurso` | `tipo_recurso_raw`; `tipoRecurso` é classificação local | linha “Oport./recurso” e badges de crédito/subvenção |
| Prazo/encerramento | `fim_inscricao`, `deadline`, `closing_date`, `prazo`, `prazo_envio`, `data_fim`, etc.; `data_encerramento` pode ficar em extras | `fim_inscricao`; raw preservado em extras quando aplicável | `prazo_envio`; `data_encerramento` só como espelho estendido quando presente em extras | `fim_inscricao` (`e.prazo_envio as fim_inscricao`); **não expõe `prazo_envio` nem `data_encerramento`** | `prazo_envio_raw=m.prazo_envio`; `dataLimite=m.prazo_envio || m.fim_inscricao`; `data_encerramento_raw=m.data_encerramento` | chip de prazo usa `prazo_envio_raw || dataLimite` |
| Status | `situacao` e metadados de validade/qualidade em extras | `situacao`; `extras.validade_status`, `sem_prazo_kind`, `validacao_status` quando enriquecidos | `situacao`; `ativo`; extras; schema antigo/migração menciona `status` legado | `situacao`, `ativo`, `extras`; não seleciona `status` | `situacao_raw`, `ativo`; `status_raw` cai para `situacao`; badges recalculados | `EditalStatusBadges`, prazo vencido e badges de qualidade |

## 3. Normalizações aplicadas

### Texto e aliases

- Aliases são copiados para a chave canônica somente quando esta está vazia; os campos originais não canônicos são preservados em `extras` (`data_cleaning.py:137-176`).
- `titulo` e `descricao` têm HTML/script/style removidos, entidades HTML decodificadas e espaços compactados (`data_cleaning.py:178-215`; chamada em `transformer.py:2281-2282`).
- Um título genérico pode ser substituído pela primeira frase útil extraída do PDF (`transformer.py:2728-2734`). No frontend, `getDisplayTitle` ainda pode produzir outro título de apresentação.
- Campos órfãos são movidos para `extras`; patches vazios não devem sobrescrever valores úteis (`transformer.py:62-82`; `schema.py:48-68`).

### Datas e status

- O transformer aceita diversos aliases, tenta `normalize_date_str` e, como fallback, extrai prazo do texto completo/PDF (`transformer.py:2755-2779`; `date_parser.py:191-270`).
- `schema.normalizar` faz uma segunda validação, mais estrita, via `datetime.fromisoformat`; valores não parseáveis viram `null` (`schema.py:8-16`, `69-73`).
- Na carga, prazo passado define `situacao="Encerrado"` se não houver situação e, com schema estendido, `ativo=false` (`loader.py:1138-1143`).
- O backend também calcula `validade_status`: `encerrado`, `vencendo_7`, `vencendo_30`, `aberto`, `sem_prazo`, `prazo_invalido` ou `nao_aplicavel` (`validity_resolver.py:60-121`).
- O frontend volta a derivar status pelo prazo e por `extras`: vencido, 7 dias, 30 dias, aberto, prazo em detalhe, a definir, linha permanente, sem prazo, resultado e pós-resultado (`editalStatusBadges.js:253-332`, `338-432`).

### Geografia, área e taxonomias

- `abrangencia` e `region` colapsam em `regiao` (`data_cleaning.py:113-120`).
- Sem região explícita, o transformer infere por palavras-chave e retorna regiões brasileiras, `Internacional` ou, por default, `Nacional` (`transformer.py:320-356`).
- `extras_to_filter_columns` converte `area` e outras taxonomias em listas de strings e limita strings escalares antes do upsert (`taxonomy_filtros.py:4476-4545`). Não há vocabulário único aplicado nessa função; valores calibrados e livres coexistem.
- No frontend, `estado` de apresentação vira UF/estado, senão `Internacional` para país não Brasil, senão `Nacional` (`editalRowMapper.js:58-96`).

### Organização, fonte e links

- `orgao_responsavel` textual usa a prioridade: campo top-level, extras homônimo, `agency`, `orgao_contratante`, `instituicao`, `fonte`, `fonte_recurso`, por fim `"Não informado"` (`loader.py:255-271`).
- `id_organizacao` é omitido se nulo. Quando a tabela existe, `get_default_org_id` seleciona apenas uma linha com `limit(1)` e reutiliza esse ID global (`loader.py:301-331`, `470-472`).
- PDF é escolhido de `extras.pdf_url`, primeiro anexo/documento PDF ou do próprio link quando termina em `.pdf`; URLs relativas são descartadas (`loader.py:406-436`).

## 4. Valores esperados e exemplos observados

| Campo | Forma esperada | Exemplos observados no repositório |
|---|---|---|
| `titulo` | string não vazia, texto limpo | `EDITAL AGRO 4.0 - EDIÇÃO 2026` |
| `link` | URL absoluta HTTP(S), chave de upsert/dedup prática | `https://www.abdi.com.br/wp-content/...pdf` |
| `fonte` / `fonte_recurso` | rótulo curto da origem | `ABDI`, `JSPS`, `BNDES` |
| `orgao_responsavel` | nome/sigla textual | `ABDI`, `JSPS`; fallback `Não informado` |
| `id_organizacao` | bigint opcional | qualquer primeiro `id_organizacao` retornado por `organizacao`; não há exemplo determinístico sem o banco |
| `pais` | texto, em geral nome do país | `Brasil` |
| `estado` | texto/UF, quando conhecido | `SP`, `São Paulo` são formas que o frontend tolera, mas não há canonização única neste fluxo |
| `regiao` | `Nacional`, `Internacional`, `Norte`, `Nordeste`, `Centro-Oeste`, `Sudeste`, `Sul`, ou valor de fonte | `Internacional`, `brasil` e string vazia coexistem nos artefatos |
| `abrangencia` | alias de entrada, sem valor persistido próprio | um valor como `Nacional` termina em `regiao=Nacional` |
| `escopo` | string livre ou `escopo_geografico` enriquecido em extras | string vazia aparece em artefatos; `escopo_geografico` pode ser gerado pelo enriquecedor |
| `area` | `text[]` no schema estendido | `Agro`, `Tecnologia e inovação`, `Indústria` |
| `tipo_oportunidade` | string taxonômica | `chamada_publica`, `grant`, `noticia_institucional` |
| `tipo_recurso` | string taxonômica ou inferida | `fomento`, `Oportunidade Publica`; a UI também infere uma classe local |
| prazo | ISO `YYYY-MM-DD` ou `null` | `null` no exemplo ABDI; raws textuais podem ficar em extras |
| `situacao` | texto operacional | `Aberto`, `Em andamento`, `Encerrado` |
| `ativo` | boolean | `true`; prazo expirado pode forçar `false` no schema estendido |
| `validade_status` | enum semântico em extras | `aberto`, `vencendo_7`, `vencendo_30`, `encerrado`, `sem_prazo`, `prazo_invalido`, `nao_aplicavel` |

Os exemplos de conteúdo foram confirmados em `backend/abdi/outputs/abdi_editais.json` e `backend/CORE/transformer/abdi_standardized.json`.

## 5. Divergências confirmadas

1. **Órgão exibido não é `orgao_responsavel`.** A view expõe ambos `fonte` e `orgao_responsavel`, mas o mapper define `orgao` exclusivamente de `fonte_recurso || fonte || 'Manual'`. O card exibe esse `orgao`. Portanto, o órgão responsável persistido é ignorado no card (`schema_sql_completo.sql:319,342`; `editalRowMapper.js:66-69`; `EditalCard.jsx:104-105`).
2. **`id_organizacao` não representa a organização do edital no pipeline automático.** O loader escolhe a primeira organização da tabela sem filtro por fonte e aplica o mesmo ID em todos os itens da sessão (`loader.py:301-331`, `470-472`).
3. **A view omite `id_organizacao`.** A tabela possui a coluna, mas o `select` da view não a inclui (`schema_sql_completo.sql:9-36`, `313-367`).
4. **A view renomeia prazo e fonte, mas o mapper espera os dois vocabulários.** `prazo_envio` chega como `fim_inscricao` e `fonte_recurso` como `fonte`; no fallback direto à tabela chegam os nomes originais. Isso produz shapes diferentes conforme a fonte da consulta (`schema_sql_completo.sql:319-324`; `editalRowMapper.js:48-58`).
5. **A view atual omite `regiao`.** O campo existe na tabela e é gravado pelo loader, mas não aparece no `select` da view. Assim, o caminho preferencial perde `regiao` antes do mapper/card (`schema_sql_completo.sql:9-28`, `313-367`).
6. **A view expõe `municipio`, mas o mapper/card procuram `cidade`.** No caminho preferencial, `cidade_raw` fica nulo mesmo com `municipio` preenchido (`schema_sql_completo.sql:340`; `editalRowMapper.js:102`; `EditalCard.jsx:205`).
7. **A view expõe `estado`, mas `uf_raw` procura somente `m.uf`.** O valor ainda alimenta `estado` de fallback, mas não entra na composição detalhada `cidade_raw, uf_raw, regiao_raw, pais_raw`; com país presente, a linha Local pode mostrar apenas o país e omitir o estado (`editalRowMapper.js:58,101`; `EditalCard.jsx:205-207`).
8. **`abrangencia` perde identidade semântica.** Ela é tratada como alias de `regiao`, embora abrangência e região possam ser conceitos diferentes (`data_cleaning.py:113-120`).
9. **`escopo` não chega estruturado ao card.** Ele permanece em `extras`; não existe coluna, projeção no mapper nem renderização no card auditado.
10. **`data_encerramento` não é a data canônica do card.** O card usa `prazo_envio_raw || dataLimite`; `data_encerramento_raw` é apenas diagnóstico e a view atual nem o seleciona (`editalRowMapper.js:58-59,107-112`; `EditalCard.jsx:74`).
11. **`tipo_recurso` também ocupa `objetivo`.** No mapeamento legado, `objetivo` recebe primeiro `item.tipo_recurso`, antes de `extras.objetivo` ou descrição, misturando dois conceitos (`loader.py:456-458`).
12. **O status mostrado não é uma simples leitura de `situacao`/`status`.** O card deriva badges novamente de prazo e extras. Assim, um registro pode ter `situacao="Aberto"` e badge “Encerrado” se o prazo estiver passado (`editalStatusBadges.js:253-432`).
13. **Schema estendido é condicional em runtime.** Sem `EDITALFINDER_EXTENDED_SCHEMA=true`, o loader remove `orgao_responsavel`, `pais`, `estado`, `area`, tipos e `extras` do payload de upsert, embora o transformer os produza (`loader.py:52-58`, `60-181`, `286-294`).
14. **Artefato real contraditório de geografia.** O padronizado ABDI para um edital localizado na RIDE-DF registra `regiao="Internacional"`, enquanto `extras.pais="Brasil"`. A divergência está confirmada no arquivo, ainda que a causa exata da inferência não tenha sido reproduzida.

## 6. Regras duplicadas

- **Aliases/prazo:** aliases são normalizados em `data_cleaning`, e o transformer volta a testar explicitamente `fim_inscricao`, `prazo_envio`, `deadline` e `inscricoes_fim`.
- **Normalização de data:** `date_parser.normalize_date_str` no transformer; `schema.parse_date` no loader; parsing novamente no frontend.
- **Validade/status:** `validity_resolver` no backend; expiração adicional no loader; `inferAtivo` no mapper; `resolveValidityStatus`/`getEditalStatusBadges` e `prazoVencido` no frontend.
- **Fonte/órgão:** transformer define `fonte`; loader deriva `orgao_responsavel` com fallbacks; frontend volta a transformar fonte em `orgao`.
- **Tipo de recurso:** pode vir do scraper, de alias, de extras, de inferência textual no transformer e de `classificarEdital` no frontend (`tipoRecurso`).
- **Área:** pode vir de `extras.area`, `temas`, classificadores/calibradores do backend ou da classificação local do frontend.
- **Geografia:** alias `abrangencia -> regiao`, inferência textual no transformer e fallback `Nacional/Internacional` no mapper.
- **Preservação/merge:** transformer preserva extras não vazios, `schema.normalizar` move órfãos e loader faz novo merge com a linha existente.

## 7. Documentação desatualizada

1. `docs/PROJECT_TECHNICAL_MAP.md:264` afirma que `vw_editais_front` não possui `orgao_responsavel`/`id_organizacao`. A definição SQL atual **possui `orgao_responsavel`**, mas continua sem `id_organizacao` (`backend/CORE/schema_sql_completo.sql:313-367`). A afirmação está parcialmente desatualizada.
2. `frontend/EditalFinder-React/schema_sql_completo.sql` termina no schema legado e não contém as colunas estendidas nem `vw_editais_front`, enquanto `backend/CORE/schema_sql_completo.sql` contém ambas. Portanto, há dois arquivos chamados “schema completo” com contratos diferentes.
3. `frontend/EditalFinder-React/src/types/edital.js` documenta apenas uma fração do shape real e não inclui geografia detalhada, organização, área, `tipo_recurso_raw`, `data_encerramento_raw`, `situacao_raw`, `status_raw` nem `extras_raw`.
4. O comentário de `mapRawEditalRow` diz normalizar a view ou tabela para a “listagem dashboard”, mas a diferença de aliases entre view e fallback não está documentada no tipo de referência (`editalRowMapper.js:36`; `types/edital.js:1-14`).

## 8. Riscos suspeitos, ainda não confirmados

Estes itens dependem do schema/dados efetivamente implantados ou de execução e, por isso, não foram classificados como divergências confirmadas:

- A view criada sem `security_invoker=true` pode ter comportamento de RLS diferente do esperado conforme a versão/configuração do PostgreSQL/Supabase. A auditoria não consultou o ambiente remoto.
- O schema remoto pode não corresponder a nenhum dos dois `schema_sql_completo.sql`; nesse caso, campos estendidos podem falhar, ser omitidos ou vir por uma view diferente configurada em `VITE_VIEW_EDITAIS`.
- Se a view existir mas retornar zero linhas por RLS/filtros, o frontend faz fallback para `edital`; isso pode mudar silenciosamente nomes disponíveis e a apresentação geográfica.
- `select('*')` em páginas de 1.000 inclui `extras` potencialmente grandes. Pode haver impacto de rede/memória, mas não foi medido.
- Valores livres e listas em `area`, `tipo_oportunidade`, `tipo_recurso`, `pais`, `estado` e `regiao` podem fragmentar filtros por caixa, acento, idioma e singular/plural. Há exemplos heterogêneos, mas o impacto agregado exige dados do banco.
- O lookup da “primeira organização” não tem `order`; o ID escolhido pode variar conforme o plano/estado do banco. O uso incorreto do mesmo ID é confirmado; a variabilidade concreta não.
- `getDisplayTitle` pode fazer o título mostrado divergir do persistido. Isso é intencional no código, mas não foi avaliado sobre todo o catálogo.
- A inferência de região por regex pode produzir falsos positivos por siglas curtas (`PR`, `SC`, `RS`, `SP`, etc.). O artefato ABDI prova uma classificação contraditória, mas não prova qual regex ou etapa a causou.
- `fim_inscricao` e `data_encerramento` podem representar eventos distintos em algumas fontes. O pipeline privilegia `fim_inscricao/prazo_envio`, mas a perda semântica precisa ser validada fonte a fonte.

## Conclusão

O contrato efetivo do card é mais estreito que o contrato produzido pelo backend. Os maiores pontos de ruptura são: `orgao_responsavel` ignorado em favor de fonte, `id_organizacao` global e ausente da view, `regiao`/`municipio` incompatíveis com o mapper, `escopo` sem projeção, prazo renomeado entre view e tabela, e status recalculado em múltiplas camadas. Nenhuma correção foi aplicada nesta auditoria.

## 9. Estudos de caso: registros reais até os filtros do frontend

### Método e limite da evidência

Foram escolhidos registros que existem nos artefatos de coleta e nos JSONs padronizados do repositório. O trecho Supabase abaixo é a projeção determinística das funções de carga e do SQL versionado; o banco remoto não foi consultado. Portanto:

- valores de origem e do padronizado são **observados**;
- valores de `edital`, da view e do modelo do frontend são **derivados do código versionado**;
- a existência, o `id_edital`, eventuais merges anteriores e flags de curadoria no Supabase implantado permanecem não confirmados.

A data de referência para prazo nesta análise é 2026-07-17. O filtro principal executa, nesta ordem relevante: curadoria, status semântico, `ativo`, suspeito, prazo vencido, título ruidoso, demais toggles, busca e filtros avançados (`frontend/EditalFinder-React/src/utils/edital/filtersEngine.js:381-494`). Por default, `toggleMostrarInativos`, `toggleIncluirSuspeitos` e `toggleIncluirEncerrados` são `false` (`filtersEngine.js:14-55`).

### Caso A — brasileiro: FAPESP – Chamadas de Propostas

Identidade: link `https://fapesp.br/chamadas/`.

#### Valores por etapa

| Etapa | Valores concretos relevantes |
|---|---|
| Origem | `titulo="FAPESP - Chamadas e Oportunidades"`; `fonte="FAPESP"`; `fim_inscricao=null`; `situacao="Em andamento"`; `tipo_recurso="fomento"`; `extras.pais="Brasil"`; `extras.regiao="brasil"`; `extras.tipo_oportunidade="chamada_publica"` |
| Padronizado | `titulo="FAPESP - Chamadas de Propostas"`; `fonte="FAPESP"`; `fim_inscricao="2026-05-07"`; `situacao="Aberto"`; `tipo_recurso="Subvenção (Não Reembolsável)"`; `regiao="Internacional"`; `extras.pais="Brasil"`; `extras.regiao=""`; `extras.tipo_oportunidade="licitacao"`; `extras.area=["Agro", "Tecnologia e inovação", "Saúde", "Petróleo e gás", "Educação e pesquisa", "Bolsas"]` |
| `edital` projetado | `titulo` padronizado; `link` preservado; `fonte_recurso="FAPESP"`; `prazo_envio="2026-05-07"`; `situacao="Aberto"`; `regiao="Internacional"`; no schema estendido: `pais="Brasil"`, `tipo_oportunidade="licitacao"`, `tipo_recurso="Subvenção (Não Reembolsável)"`, `area` como `text[]`, `ativo=false` ao carregar após o prazo |
| View projetada | `fonte="FAPESP"`; `fim_inscricao="2026-05-07"`; `pais="Brasil"`; tipos e `area` preservados; **sem `regiao`** |
| Modelo UI | `orgao="FAPESP"`; `fonte_recurso_display="FAPESP"`; `pais_raw="Brasil"`; `regiao_raw=null`; `prazo_envio_raw=null`; `fim_inscricao_raw="2026-05-07"`; `dataLimite="2026-05-07"`; tipos e `area` preservados; `ativo=false` se assim gravado |

Evidências: origem em `backend/fapesp/outputs/fapesp_editais.json:3-23`; padronizado em `backend/CORE/transformer/fapesp_standardized.json:3-17`, com tipo de oportunidade em `:36` e área em `:110-117`. A carga converte `fonte -> fonte_recurso` e `fim_inscricao -> prazo_envio` em `backend/CORE/loader.py:442-469`; o espelho de `pais`, tipo e área vem de `extras_to_filter_columns` em `backend/CORE/taxonomy_filtros.py:4476-4545`. A view renomeia fonte/prazo e omite região em `backend/CORE/schema_sql_completo.sql:313-366`. O mapper está em `frontend/EditalFinder-React/src/utils/edital/editalRowMapper.js:37-122`.

#### Por que aparece ou deixa de aparecer

- **Escopo Brasil:** aparece. `getDashboardSourceScope` classifica como `brasil` por três sinais independentes: fonte FAPESP consta entre os órgãos brasileiros, o link contém `.br` e `pais_raw="Brasil"` (`dashboardClassification.js:10-30`, `197-218`). Isso prevalece sobre o `regiao="Internacional"` do padronizado; além disso, essa região nem chega pela view.
- **Escopo Internacional:** não aparece, pois a função retorna no primeiro ramo brasileiro antes de testar sinais internacionais (`dashboardClassification.js:206-218`).
- **País Brasil:** aparece se o schema estendido e a view versionada estiverem implantados, porque `pais_raw="Brasil"` e o filtro faz `includes` normalizado (`filtersEngine.js:316-319`).
- **Região Internacional:** não aparece no caminho preferencial da view, apesar do valor padronizado, porque `regiao` não é selecionado pela view; `regiao_raw` fica nulo. No fallback direto para `edital`, apareceria nesse filtro legado (`filtersEngine.js:311-314`).
- **Fonte FAPESP, tipo `licitacao`, tipo de recurso e áreas listadas:** aparecem quando as colunas estendidas existem, pois o mapper as preserva e os filtros usam os valores normalizados (`filtersEngine.js:299-309`, `328-335`, `347-350`).
- **Lista padrão em 2026-07-17:** deixa de aparecer. O prazo `2026-05-07` está vencido. A carga atual marca `ativo=false` no schema estendido (`loader.py:1151-1155`), e o frontend remove primeiro inativos e depois vencidos (`filtersEngine.js:420-438`). Para reaparecer, seriam necessários `Mostrar inativos` **e** `Incluir encerrados`, salvo diferença no estado real persistido.
- **Filtro sem prazo:** não aparece, pois `dataLimite` recebe `fim_inscricao` da view. **Filtro encerrados:** aparece somente quando a aplicação habilita a inclusão de encerrados; o preset de query `encerrados` liga esse toggle automaticamente (`editaisQueryFilters.js:145-165`).

Resultado importante: o registro é corretamente classificado como brasileiro pelo filtro de escopo, mas a classificação geográfica armazenada (`Internacional`) é contraditória e invisível no caminho da view.

### Caso B — internacional: JSPS/KAKENHI – `Japanese`

Identidade: link `https://www.jsps.go.jp/j-grantsinaid/index.html`.

#### Valores por etapa

| Etapa | Valores concretos relevantes |
|---|---|
| Origem | `titulo="Japanese"`; descrição em japonês; `fonte="JSPS"`; `fim_inscricao=null`; `situacao="Aberto"`; `tipo_recurso="Oportunidade Publica"`; `extras.regiao="asia"`; `extras.pais="japao"`; `extras.tipo_oportunidade="grant"`; `extras.orgao_responsavel="JSPS"` |
| Padronizado | conserva os valores acima, mas cria `regiao="Nacional"`; mantém `extras.regiao="asia"`, `extras.pais="japao"`, `extras.tipo_oportunidade="grant"`; `extras.area=[]` |
| `edital` projetado | `fonte_recurso="JSPS"`; `prazo_envio=null`; `situacao="Aberto"`; `regiao="Nacional"`; no schema estendido: `pais="japao"`, `tipo_oportunidade="grant"`, `tipo_recurso="Oportunidade Publica"`, `orgao_responsavel="JSPS"`, `ativo=true` |
| View projetada | `fonte="JSPS"`; `fim_inscricao=null`; `pais="japao"`; tipos preservados; **sem `regiao`** |
| Modelo UI | `orgao="JSPS"`; `pais_raw="japao"`; `estado="Internacional"` derivado do país; `regiao_raw=null`; `dataLimite=null`; `tipo_oportunidade_raw="grant"`; `tipo_recurso_raw="Oportunidade Publica"`; `area=""` |

Evidências: origem em `backend/japan_jsps/outputs/japan_jsps_editais.json:3-34`; padronizado em `backend/CORE/transformer/japan_jsps_standardized.json:3103-3133`, com `area=[]` em `:3208`. O estado de UI é derivado como `Internacional` para país diferente de Brasil em `editalRowMapper.js:97-111`.

#### Por que aparece ou deixa de aparecer

- **Escopo Internacional:** aparece por `pais_raw="japao"`. Fonte JSPS e link `.go.jp` não pertencem à lista brasileira, mas também não são regras internacionais explícitas; o ramo decisivo é “país preenchido e diferente de Brasil/Brazil” (`dashboardClassification.js:197-218`).
- **Escopo Brasil:** não aparece. O `regiao="Nacional"` contraditório não chega pela view. Mesmo no fallback direto, a regra brasileira compara `estado === "nacional"`, não `regiao === "nacional"`; logo esse valor isolado não basta para classificá-lo como Brasil.
- **País `japao`:** aparece se a coluna estendida estiver implantada; o filtro normaliza acentos/caixa e testa inclusão (`filtersEngine.js:316-319`). Um filtro digitado como `Japão` tende a casar após `normalizeText`.
- **Tipo de oportunidade `grant` e recurso `Oportunidade Publica`:** aparecem porque são espelhados e comparados no bloco avançado (`filtersEngine.js:299-309`).
- **Área:** não aparece em nenhuma faceta temática específica, pois o valor concreto é lista vazia. Se qualquer checkbox de área estiver ativo, `checkboxOrMatches` rejeita o registro por falta de tokens (`filtersEngine.js:176-184`, `347-350`).
- **Sem prazo:** aparece nesse filtro, pois `prazoReferencia` resulta em `null` e `sem_prazo` casa por ausência de prazo (`filtersEngine.js:58-60`, `153-164`; `editalDeadlineStatus.js:18-33`).
- **Lista padrão:** em princípio aparece: não está vencido, `Japanese` não contém nenhum dos tokens de ruído da UI e o artefato não traz `validacao_status="suspeito"` (`noise.js:3-21`; `editalFieldHelpers.js:30-35`). Pode ainda desaparecer se o banco remoto tiver curadoria `hidden_*`, suspeição posterior, RLS ou se o opportunity gate da carga atual rejeitá-lo; essas condições não constam do artefato auditado.
- **Somente PDF / alta qualidade / área selecionada:** deixa de aparecer. Não há PDF no registro, não há qualidade projetada na view para o mapper e a área é vazia (`filtersEngine.js:448-463`, `347-350`).

Resultado importante: o registro internacional é recuperado pelo país/fonte/link, não pela região top-level, que foi incorretamente transformada em `Nacional` e depois descartada pela view.

### Caso C — regional/estadual: FAPERGS 04/2026 – PROBIC/PROBITI

Identidade: link final `https://fapergs.rs.gov.br/edital-fapergs-04-2026-probic-probiti-edicao-2026-2028`.

#### Valores por etapa

| Etapa | Valores concretos relevantes |
|---|---|
| Origem | `titulo="EDITAL FAPERGS 04/2026 - PROBIC/PROBITI ... Estado do RS"`; `url_pagina` com domínio `rs.gov.br`; `pdf_url` preenchido; `prazo_envio="2026-06-15"`; `situacao="Aberto"`; `numero_edital="04/2026"`; sem `fonte`, `link`, `pais`, `estado`, `regiao` ou `abrangencia` top-level |
| Padronizado | `link` vem do alias `url_pagina`; `fonte="FAPERGS"`; `fim_inscricao="2026-06-15"`; `situacao="Aberto"`; `tipo_recurso="Bolsa / Auxílio"`; `regiao="Sul"`; `extras.pais=""`; `extras.regiao=""`; `extras.tipo_oportunidade="noticia_institucional"`; `extras.area=["Tecnologia e inovação", "Bolsas"]`; `extras.publico_alvo=["ICTs", "estudantes"]` |
| `edital` projetado | `fonte_recurso="FAPERGS"`; `prazo_envio="2026-06-15"`; `regiao="Sul"`; `pdf_url` preenchido; tipo e área espelhados; `pais` e `estado` permanecem vazios/nulos; `ativo=false` ao carregar após o prazo |
| View projetada | fonte, prazo, PDF, tipos e área preservados; `pais` vazio; `estado` nulo; **sem `regiao`** |
| Modelo UI | `orgao="FAPERGS"`; `fim_inscricao_raw="2026-06-15"`; `dataLimite="2026-06-15"`; `pdfUrl` preenchido; `pais_raw=""`; `uf_raw=null`; `regiao_raw=null`; `estado="Nacional"` por fallback; tipo e área preservados |

Evidências: origem em `backend/fapergs/outputs/fapergs_editais.json:3-15` e restante do primeiro objeto; padronizado em `backend/CORE/transformer/fapergs_standardized.json:3-20`, tipo de oportunidade/país em `:94-97` e área em `:139-142`. `url_pagina` é alias de `link` em `backend/CORE/data_cleaning.py:45-64`; a região é inferida por texto em `backend/CORE/transformer.py:320-356`.

#### Por que aparece ou deixa de aparecer

- **Escopo Brasil:** aparece quando os bloqueios de prazo/inatividade são liberados. Fonte FAPERGS está na lista brasileira e o link contém `.br`; ambos bastam (`dashboardClassification.js:10-30`, `197-214`).
- **Região Sul:** **não aparece no caminho preferencial**, embora `regiao="Sul"` exista no padronizado e na tabela. A view omite a coluna; o mapper recebe `m.regiao=undefined`; o filtro regional testa somente `regiao_raw/regiao` e falha (`schema_sql_completo.sql:313-366`; `editalRowMapper.js:102-111`; `filtersEngine.js:311-314`). No fallback direto para `edital`, o registro aparece em Sul.
- **UF RS:** não aparece. O texto e o domínio provam a abrangência estadual, mas o pipeline não extrai `estado="RS"`. Além disso, o mapper cria `uf_raw` somente de `m.uf`, enquanto a view expõe `estado`; o filtro tenta `uf_raw || estado_raw`, mas `estado_raw` nem existe no objeto retornado pelo mapper (`editalRowMapper.js:51,97-111`; `filtersEngine.js:320-323`).
- **País Brasil:** não aparece no filtro de país, porque `extras.pais` está vazio. A classificação de escopo Brasil ainda funciona por fonte/domínio, demonstrando que os dois filtros usam regras diferentes.
- **Fonte FAPERGS, tipo `Bolsa / Auxílio`, áreas Tecnologia/Bolsas e com PDF:** aparecem, pois esses valores chegam à view/mapper e os filtros correspondentes os consomem (`filtersEngine.js:305-309`, `328-335`, `347-350`; `editalFieldHelpers.js:21-27`).
- **Tipo de oportunidade:** aparece sob `noticia_institucional`, embora o registro seja um edital. Se o usuário filtrar por uma categoria como `chamada_publica` ou `edital`, ele deixa de aparecer, pois a comparação usa o valor exato/inclusão de `tipo_oportunidade_raw` (`filtersEngine.js:299-303`).
- **Lista padrão em 2026-07-17:** deixa de aparecer por prazo vencido e, no schema estendido, também por `ativo=false`. Assim como no caso FAPESP, requer `Mostrar inativos` e `Incluir encerrados` para ultrapassar as duas etapas (`loader.py:1151-1155`; `filtersEngine.js:420-438`).
- **Filtro encerrados:** aparece depois que a inclusão de encerrados está ativa. **Sem prazo:** não aparece. **Somente PDF:** aparece, porque `pdf_url` é preservado.

Resultado importante: a abrangência estadual está evidente na origem e o backend chega a inferir `Sul`, mas o frontend não consegue filtrar nem por Sul nem por RS no caminho normal da view. O registro só é recuperado como “Brasil” pela heurística de fonte/domínio.

### Comparativo final dos três casos

| Registro | Brasil | Internacional | País | Região/UF | Prazo em 2026-07-17 | Visibilidade default projetada |
|---|---:|---:|---|---|---|---|
| FAPESP Chamadas | sim, por fonte + `.br` + `pais=Brasil` | não | `Brasil` funciona | `Internacional` armazenado, mas perdido na view | vencido em 2026-05-07 | oculto por inativo e vencido |
| JSPS `Japanese` | não | sim, por `pais=japao` | `japao` funciona | `Nacional` armazenado, mas perdido na view | sem prazo | visível em princípio; entra em “Sem prazo” |
| FAPERGS 04/2026 | sim, por fonte + `.br` | não | vazio; filtro Brasil falha | `Sul` perdido na view; `RS` nunca estruturado | vencido em 2026-06-15 | oculto por inativo e vencido |

Os casos confirmam que “Escopo geográfico”, “País” e “Região/UF” não são facetas equivalentes: o primeiro usa heurísticas de fonte/link/país, enquanto os outros exigem campos estruturados que podem estar vazios ou ser removidos pela view.
