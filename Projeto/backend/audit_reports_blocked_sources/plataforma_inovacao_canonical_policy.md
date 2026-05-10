# Política canónica — Plataforma Inovação

## Decisão proposta

- **Fonte canónica:** `senai`
- **Alias:** `plataforma_industria`
- **Regra de URL:** contém `plataforma-inovacao-para-industria/categoria`
- **Política no loader:** `skip_alias_if_canonical_exists` (ver `config/source_canonicalization.json`)

## Porquê SENAI como canónico

1. Alinhamento institucional: o produto é a Plataforma Inovação operada no ecossistema SENAI/Sistema Indústria.
2. Nos 22 pares com mesma URL, **título**, **content_hash** e **descrição** (hash) coincidem — não há ganho de riqueza textual ao preferir a alias.
3. **Documentos** e campos semânticos principais coincidem nos pares; não há motivo para duplicar ingestão no mesmo `link`.
4. O upsert por `link` faria a última fonte sobrescrever `fonte_recurso`; uma fonte canónica reduz ambiguidade.
5. A alias continua útil para **URLs exclusivas** (ex.: categoria `inova-mes` ausente no crawl SENAI) e para rastreio futuro em `extras` se `preserve_alias_in_extras` for implementado.

## Agregados (22 URLs comuns)

- Títulos iguais: **22** / 22
- Descrição (sha256) igual: **22** / 22
- Docs: SENAI > alias: **0**, alias > SENAI: **0**, igual: **22**
- tipo_oportunidade igual: **22** / 22
- qualidade_dado igual: **22** / 22

## URLs só na plataforma_industria

- `https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/categoria/inova-mes`

## Comparação detalhada

Lista completa em `plataforma_inovacao_canonical_policy.json` (`pares_detalhe`: fonte, título, link, métricas de descrição, documentos, classificação, validacao_status, qualidade_dado, `extras` podado para relatório, content_hash, datas).

## Dry-run com canonização

Ver `plataforma_inovacao_canonical_dryrun.md` e `plataforma_inovacao_canonical_dryrun.json` (comando `senai,plataforma_industria` com `config/source_canonicalization.json`).

## Recomendação final

Carregar SENAI como canónico para hubs /categoria/; aplicar canonização para ignorar alias duplicado; permitir plataforma_industria apenas para URLs não cobertas pelo SENAI (ex.: inova-mes) ou fundir extras no futuro se preserve_alias_in_extras for implementado.
