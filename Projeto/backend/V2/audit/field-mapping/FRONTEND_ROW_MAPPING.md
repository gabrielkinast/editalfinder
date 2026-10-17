# Mapeamento de linha no frontend

## Consulta e adaptação

`dataService.getEditais` consulta `VIEW_EDITAIS`, default `vw_editais_front`, e faz fallback para `edital`; depois aplica `mapRawEditalRow` e `filterPublicVisibleEditais` (`frontend/EditalFinder-React/src/services/dataService.js:99-173`). O mapper está em `src/utils/edital/editalRowMapper.js:37-203`.

| Campo da view/tabela | Campo frontend | Conversão | Fallback | Consumidores |
|---|---|---|---|---|
| id/id_edital | id, id_edital, idNumerico | prefixa `manual-`; Number | um ou outro | card, favoritos, detalhe |
| titulo | titulo_original_raw, titulo | trim + `getDisplayTitle` | dados de link/descrição/tema/fonte | card, busca, filtros de ruído |
| descricao | descricao | direto | null | card, busca, detalhes |
| fonte_recurso/fonte | orgao, fonte_recurso_display, fonte_raw | trim | `Manual` para orgao | card, busca, escopo, fonte |
| link | linkOriginal, link_raw | direto | null | ações, escopo, favoritos |
| pdf_url | pdfUrl, pdf_url_raw | direto | null | card/filtro PDF |
| valores | valor, valorMaximo, valorMinimo, raws | `Number`, primeiro de estimado/total/máx/mín | 0 | card, faixa de valor |
| uf/estado | estado | string | país não BR -> Internacional; senão Nacional | card/escopo |
| uf | uf_raw | direto | null | filtro UF |
| cidade | cidade_raw | direto | null | filtro cidade |
| pais | pais_raw | direto | null | escopo/país/card |
| regiao | regiao, regiao_raw, localidade | direto | país para localidade | região/escopo/card |
| prazo_envio | prazo_envio_raw | direto | null | prazo/status |
| fim_inscricao | fim_inscricao_raw, dataLimite | direto | prazo_envio primeiro | prazo/status/card |
| data_encerramento | data_encerramento_raw | direto | null | diagnóstico; não é prazo principal |
| tipo_recurso | tipo_recurso(_raw) | direto | null | filtros/card |
| linha completa | tipoRecurso | `classificarEdital` local | classificação textual | filtros/card/radar |
| tipo_oportunidade | tipo_oportunidade_raw | direto | null | filtros/card/status permanente |
| area/temas | area | trim; aceita classificação local | temas ou classificação | filtros/busca |
| arrays taxonômicos | `*_raw/list/flat` | `coerceStringArray` + join | [] | filtros/card/busca |
| validacao_status | validacao_status(_raw) | direto | null | qualidade/suspeito |
| qualidade_dado | qualidade_dado(_raw) | Number | null | qualidade/card |
| ativo/situacao/status | ativo, situacao_raw, status_raw | `inferAtivo`; status fallback situação | ativo=true se indeterminado | filtros/status |
| extras | extras_raw, curadoria_visibility_raw | direto + acesso aninhado | null | curadoria, links, status |
| score e derivados | homônimos camelCase | direto/defaults | score 0 | ranking/radar |

Evidência detalhada: `editalRowMapper.js:37-203`; consumidores principais `components/dashboard/EditalCard.jsx:46-236`, `pages/EditaisPage.jsx:184-260`, `pages/EditalDetalhes.jsx` e `pages/RadarFomento.jsx`.

## Classificação semântica refeita no frontend

- `classificarEdital` recalcula tipo/área antes do card (`editalRowMapper.js:42-50,119-135`).
- `inferAtivo` interpreta boolean/número/string e `situacao/status` (`:12-34`).
- `getDashboardSourceScope` classifica Brasil/internacional/multilateral por fonte, link e geografia (`utils/dashboard/dashboardClassification.js:197-232`).
- `getEditalStatusBadges` recalcula validade/resultado/sem prazo por datas e extras (`utils/edital/editalStatusBadges.js:253-432`).
- `getDisplayTitle` pode substituir o título de apresentação.

## Divergências

- Mapper tolera dois contratos porque view e fallback usam aliases distintos.
- `orgao_responsavel` não é mapeado: `orgao` recebe fonte.
- View atual local fornece `id`, mas fallback de ordenação tenta `id_edital` (`dataService.js:128-148`); o sucesso depende da versão da view.
- `municipio` não é consumido; mapper procura `cidade`.
- `estado` não vira `uf_raw`; mapper procura `uf`.
