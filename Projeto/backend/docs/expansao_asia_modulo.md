# Modulo Expansao Asia (Japao + China)

## Relatorio tecnico

- Arquitetura preservada: `main.py` orquestra crawlers por fonte e em
  seguida `CORE/transformer.py` e `CORE/loader.py`.
- Padrao preservado: uma pasta por fonte, `main_<fonte>.py`, JSON bruto em
  `outputs/<prefixo>_editais.json` com `ensure_ascii=False`.
- Persistencia preservada: `loader.py` faz upsert no Supabase por `link`.
- Tratamento de erro preservado: cada crawler roda em subprocess isolado;
  falha em uma fonte japonesa ou chinesa nao derruba todas as outras.
- Modelo de dados padronizado mantido. Informacoes especificas de regiao,
  pais, idioma, tradutores, classificacao tematica vivem em `extras`.

## Novos modulos compartilhados

- `asia_intel.py` - palavras-chave PT/EN/JA/ZH, regras de setor estrategico,
  subtemas, exclusoes sensiveis, deteccao de idioma e `build_asia_extras`.
- `asia_source_common.py` - `safe_get` (User-Agent identificavel, robots.txt,
  timeout, decodificacao UTF-8), `scrape_asia_html_portal`, `save_outputs_asia`
  (somente JSON, UTF-8, ensure_ascii=False).
- `asia_translate.py` - stub de tradutor com interface estavel
  (`translate_text`, `enrich_asia_translation`). Backend padrao = `noop`
  (nao faz chamada externa). Pode ser ativado via env vars
  `EDITALFINDER_ASIA_TRANSLATOR=deepl` +
  `EDITALFINDER_ASIA_TRANSLATOR_KEY=<chave>` apos descomentar o bloco
  de chamada real em `DeepLTranslator.translate`.

## Validador

`scripts/validate_asia.py` faz 4 fases de checagem:

  1. Smoke test offline de `asia_intel`.
  2. Smoke test offline de `asia_source_common`.
  3. Sanity check do patch no `transformer` (rotas Asia vs defesa).
  4. (Opcional) executa 1 crawler ao vivo e valida UTF-8/CJK.

Uso:

```
python scripts/validate_asia.py            # so offline (rapido)
python scripts/validate_asia.py --live     # default japan_jetro_procurement
python scripts/validate_asia.py --live japan_jst
```

Saida codigo 0 se tudo OK; 1 se qualquer assert falhar.

## Estrutura de `extras` para fontes asiaticas

```json
{
  "regiao": "asia",
  "pais": "japao | china",
  "idioma_original": "ja | zh | en",
  "titulo_original": "...",
  "descricao_original": "...",
  "titulo_traduzido": "",
  "descricao_traduzida": "",
  "setor_estrategico": "ciencia_tecnologia | nuclear | materiais_avancados | semicondutores | tecnologias_quanticas | aeroespacial | defesa_industrial | dual_use | procurement_publico | energia | pesquisa_basica | pesquisa_aplicada",
  "subtema": ["fisica", "fisica_nuclear", "..."],
  "tipo_oportunidade": "funding_opportunity | grant | chamada_publica | procurement | licitacao | bolsa | pesquisa_colaborativa | programa_pdi | noticia_institucional | ...",
  "orgao_responsavel": "...",
  "instituicao": "...",
  "empresa_prime": "",
  "orgao_contratante": "...",
  "nivel_sensibilidade": "publico_institucional",
  "origem": "<URL>",
  "palavras_chave_detectadas": ["..."],
  "necessita_traducao": true
}
```

## Roteamento no transformer

`CORE/transformer.py::_transform_single_item` foi alterado para detectar
fontes asiaticas (prefixo `japan_` / `china_` ou `extras.regiao == "asia"`)
e aplicar `build_asia_extras` no lugar de `build_defense_extras`. Os valores
preenchidos pelo crawler tem precedencia sobre os defaults.

Comportamento das 60 fontes nao-asiaticas existentes nao mudou.

## Tradicao

Tradicao automatica nao foi implementada nesta fase. O crawler preserva
`titulo_original` e `descricao_original`, deixa `titulo_traduzido` e
`descricao_traduzida` em branco e marca `necessita_traducao=true` quando o
idioma original e `ja` ou `zh`. Integracao futura com DeepL/Google Translate
pode ser adicionada como pos-processamento sem mudar o contrato.

## Fontes implementadas (resumo)

Japao (16):
- `japan_jst`, `japan_jsps`, `japan_kakenhi`, `japan_e_rad`, `japan_mext`,
  `japan_qst`, `japan_jaea`, `japan_nims`, `japan_riken`, `japan_kek`,
  `japan_jetro_procurement`, `japan_atla`, `japan_mod`, `japan_jaxa`,
  `japan_nedo`, `japan_aist`.

China (10):
- `china_nsfc`, `china_most`, `china_cas`, `china_caea`, `china_cnnc`,
  `china_cgn`, `china_mofcom_tendering`, `china_tendering_bidding`,
  `china_university_procurement`, `china_mod_public`.

Fase 2 - Suppliers privados (5):
- `japan_mitsubishi_heavy`, `japan_kawasaki_heavy`, `japan_ihi`,
  `china_norinco`, `china_avic`.

Total: 31 crawlers asiaticos.

## Fontes em roadmap

- `dsei_japan` (evento privado, sem feed publico estruturado).
- `pla_equipment_procurement` (depende de revisao de legalidade e robots.txt).
- Outros primes JP (Toshiba Energy Systems, Hitachi Energy/Power) e CN
  (CASC, CASIC, CSSC) - terceira onda.

## Execucao

Crawler isolado:

```
python japan_jst/main_japan_jst.py
python china_nsfc/main_china_nsfc.py
python japan_jetro_procurement/main_japan_jetro_procurement.py
```

Pipeline completo (raiz):

```
python main.py
```

Apenas transformer (apos os crawlers terem rodado):

```
python CORE/transformer.py
```

## Como adicionar uma nova fonte asiatica

1. Criar pasta `japan_<nome>/` ou `china_<nome>/`.
2. Criar `main_<nome>.py` chamando `scrape_asia_html_portal(...)` de
   `asia_source_common`. Definir `country` (`"japao"` / `"china"`),
   `accept_language`, `instituicao`, `orgao_responsavel` e
   `tipo_oportunidade_hint`.
3. Adicionar a entrada em `main.py` (lista `SCRAPERS`) e em
   `CORE/transformer.py::main()` (lista `sources`, usando `transform_bndes`).
4. Validar saida em `outputs/<prefixo>_editais.json` (UTF-8, CJK preservado).

## Como funciona a classificacao por pais, idioma e subtema

- `asia_intel.detect_language` usa heuristica por caracteres CJK:
  hiragana/katakana => `ja`; Han sem kana => `zh`; caso contrario => `en`.
- `asia_intel.classify_strategic_sector` aplica `SECTOR_RULES` em ordem
  (mais especifico primeiro: nuclear, semicondutores, quanticas,
  aeroespacial, materiais, defesa, dual_use, procurement, energia,
  default = ciencia_tecnologia).
- `asia_intel.classify_subthemes` percorre `SUBTHEME_PATTERNS` multilingue.
- `asia_intel.has_sensitive_content` filtra textos que mencionam fabricacao
  de armamento, municao, agentes quimicos ou radiologicos.

## Deduplicacao

Mantida a logica do transformer: chave composta `link | titulo | fonte |
data_publicacao | fim_inscricao`. Conteudo CJK e normalizado pelo
`generate_content_hash` (que ja usa `lower()` + remocao de espacos e
pontuacao basica via regex `\w` Unicode-friendly).

## Cuidados de scraping responsavel

- User-Agent identificavel (`EditalFinderBot/1.0`).
- Respeito a `robots.txt` por dominio (`urllib.robotparser`), com
  fail-open conservador (igual ao defense module) para nao derrubar fontes.
- Delay default 0.8s entre requests (`DEFAULT_DELAY_S`).
- Timeout de 25s por request.
- Sem bypass de login, captcha, paywall, bloqueio anti-bot ou bloqueio
  regional.
- API oficial seria preferida quando disponivel; nesta fase, todas as
  fontes asiaticas usam HTML publico (poucas APIs estaveis sem chave).
- Em caso de bloqueio temporario, o crawler retorna `0 itens` sem propagar
  erro.

## Indices Supabase (opcional)

Para acelerar queries por regiao/pais/setor_estrategico/idioma_original,
foi criada a migration `CORE/migration_asia_indexes.sql`. Ela:

- e idempotente (pode rodar varias vezes);
- adiciona indices parciais em `edital_extra_campo` para as chaves
  asiaticas (regiao, pais, setor_estrategico, idioma_original,
  tipo_oportunidade, nivel_sensibilidade, orgao_responsavel);
- cria view `vw_edital_asia` que pivota essas chaves em colunas, filtrando
  apenas registros onde `regiao='asia'`;
- (opcional) adiciona coluna `extras_jsonb` em `edital` com indice GIN.

Aplicacao via psql ou no Supabase SQL editor:

```
psql "$SUPABASE_DB_URL" -f CORE/migration_asia_indexes.sql
```

Exemplo de query usando a view:

```sql
select id_edital, fonte_recurso, pais, setor_estrategico, tipo_oportunidade
from public.vw_edital_asia
where pais = 'japao'
  and setor_estrategico in ('nuclear', 'tecnologias_quanticas', 'semicondutores')
order by data_publicacao desc nulls last
limit 50;
```

## Limitacoes conhecidas

- Sites .cn antigos podem servir conteudo declarado como GB2312/GBK; o
  `safe_get` ja tenta decodificacao com `apparent_encoding`, mas em casos
  raros pode haver mojibake.
- Algumas chamadas KAKENHI sao publicadas anualmente, fora desse periodo
  o crawler pode retornar 0 itens.
- O portal `cebpubservice.com` aplica anti-bot ocasionalmente; o crawler
  registra warning e continua sem falhar.
- ATLA, Japan MoD e China MoND tem suas listagens limitadas a
  comunicados publicos. Procurement do PLA permanece no roadmap.
