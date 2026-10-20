# Mapeamento do loader/persistência

## Entrada e campos aceitos

`load_standardized_json` espera objeto ou lista JSON de `CORE/transformer/*_standardized.json`, aplica `schema.normalizar`, backfill opcional e roteamento (`backend/CORE/loader.py:1075-1165`). O modelo-base aceito por `schema.normalizar` está em `backend/CORE/schema.py:18-44`; chaves fora dele são movidas para `extras` (`:47-73`).

O payload final é limitado por `_LEGACY_EDITAL_COLUMNS` e, somente com `EDITALFINDER_EXTENDED_SCHEMA=true`, `_EXTENDED_EXTRA_COLUMNS` (`loader.py:52-181,197-200,275-282`). Chaves `organizacao`, `organizacao_responsavel`, `organization`, `org` são sempre descartadas; `id_organizacao` nulo é omitido.

## Tabela principal

| Campo transformado | Campo no banco | Conversão | Obrigatório | Evidência |
|---|---|---|---|---|
| titulo | titulo | direto; merge prefere não vazio | não no DDL | `loader.py:442-446,679-680` |
| descricao | descricao | merge escolhe texto mais longo | não | `:444,676-678`; `merge_utils.py:93-102` |
| link | link | trim indireto; chave de conflito | **sim no snapshot** | `loader.py:445,943-959`; `schema_current.sql:58,122` |
| fonte | fonte_recurso | renomeia; merge não vazio | não | `loader.py:446,679-680` |
| data_publicacao | data_publicacao | ISO validado antes por `schema.parse_date` | não | `loader.py:447`; `schema.py:8-16,69-73` |
| fim_inscricao/prazo_envio | prazo_envio | prioridade `fim_inscricao` | não | `loader.py:448` |
| situacao | situacao | direto; vazio preserva antigo | não | `:449,686-687` |
| valor | valor_maximo | `clean_monetary_value` para float | não | `:349-387,450` |
| valor_minimo | valor_minimo | top-level ou extras | não | `:451` |
| regiao | regiao | direto | não | `:457` |
| tipo_recurso | tipo_recurso | espelho estendido, até 200 chars | não | `taxonomy_filtros.py:4507-4510` |
| extras.tipo_oportunidade | tipo_oportunidade | espelho estendido, até 200 chars | não | `:4505-4508` |
| extras.area | area | string/lista -> lista de strings | não | `:4478-4491` |
| extras.pais | pais | string, até 2.000 chars | não | `:4514-4534` |
| extras.estado | estado | string, até 2.000 chars | não | `:4514-4534` |
| extras.municipio | municipio | string, até 2.000 chars | não | `:4514-4534` |
| org fields/fonte | orgao_responsavel | prioridade textual; somente estendido | não | `loader.py:255-271,439-440,473-474` |
| qualquer item | id_organizacao | primeiro ID de `organizacao`, se lookup funcionar | não | `:301-331,470-472` |
| extras.pdf_url/anexos/documentos | pdf_url | primeiro PDF HTTP(S); link PDF como fallback | não | `:409-433,458` |
| programa/acao | programa/acao | espelho estendido | não | `taxonomy_filtros.py:4546-4550` |
| extras | extras | merge profundo não destrutivo | não; coluna NOT NULL se estendido | `loader.py:644-713`; `merge_utils.py:117-139` |
| score e derivados | homônimos | direto/default score 0 | não | `loader.py:464-468` |

Demais campos estendidos aceitos estão enumerados literalmente em `loader.py:91-181` e espelhados por `extras_to_filter_columns` em `taxonomy_filtros.py:4476-4630`. Campos não enumerados ficam apenas em `extras` ou em `edital_extra_campo`; com schema legado, `extras` também é removido do upsert.

## Defaults, validações e merge

- `score=0`; `ativo=true` para linha nova no schema estendido (`loader.py:464,667-670`).
- Link ausente pula o registro (`:1146-1149`). Opportunity gate pode rejeitar antes do mapeamento (`:1114-1131`).
- Datas expiradas: `is_expired_deadline`; na carga define `ativo=false` e mantém `situacao` existente ou usa `Encerrado` (`:551-560,1151-1155`). `main` também faz update em massa antes da carga (`:563-590,1223-1225`).
- Merge preserva valores antigos não vazios, descrição mais longa, extras profundos/listas deduplicadas (`loader.py:644-745`; `merge_utils.py:77-139`).
- Sanitização remove NUL recursivamente e converte datas, UUID, Decimal, Enum e bytes (`merge_utils.py:17-74`).

## Escrita, dry-run, staging e erros

- Upsert em `public.edital` com `on_conflict="link"`; retorno sem linha é tratado como erro (`loader.py:943-959`). Histórico e tabelas de detalhe podem gerar inserts/deletes adicionais (`:822-941`).
- Não há modo dry-run no CLI; o único argumento é `--workers` (`:1206-1216`). Executar `loader.py` escreve no Supabase.
- Staging é escolhido por arquivos de ambiente no `db.py`, incluindo `.env.staging` (`backend/CORE/db.py:10-18`). O alvo efetivo e os secrets são **não confirmados** e não foram lidos/copiados.
- Erros de upsert são logados e convertidos em `("erro", None)`; a carga continua por item (`loader.py:956-959,1175-1203`). Ausência da tabela `organizacao` desativa o lookup para a sessão (`:203-253,301-334`).
- **Nesta auditoria o loader não foi executado.**
