# Filtros e escopo geográfico

## Arquivos e aplicação

- Motor único do catálogo: `frontend/EditalFinder-React/src/utils/edital/filtersEngine.js:381-507`.
- Estado/controles: `src/components/dashboard/EditaisFiltersSidebar.jsx`, aplicado por `src/pages/EditaisPage.jsx:230-260`.
- Escopo: não existe `geoScope.js` no repositório. Equivalentes: `utils/dashboard/dashboardClassification.js:197-232` e `utils/editais/editaisQueryFilters.js:19-43,172-177`.
- Busca: `utils/edital/search.js:5-45`.
- Prazo: `utils/editais/editalDeadlineStatus.js:10-36` e utilitários de dashboard/datas.
- Favoritos: `pages/EditaisPage.jsx:243-260`, `hooks/useEditalFavorites.js`, `services/favoritosService.js:110-150`.

## Ordem das regras

`filterCatalog` aplica: curadoria hidden -> status semântico -> ativo -> suspeito -> vencido -> título ruidoso -> somente PDF -> alta qualidade -> status cadastral -> busca -> bloco avançado (`filtersEngine.js:393-494`). Favoritos são aplicados **depois**, fora do motor (`EditaisPage.jsx:241-260`).

## Campos, valores e comparações

| Conceito | Valores esperados na UI | Normalização/comparação | Evidência |
|---|---|---|---|
| país | strings da coluna, ex. `Brasil`, `japao` | `normalizeText`, `includes`; opções derivadas de `pais_raw` não vazio | `filtersEngine.js:316-319`; `EditaisPage.jsx:396-405` |
| estado/UF | UF de 2 letras | uppercase e igualdade exata; lista usa somente `uf_raw` | `filtersEngine.js:320-323`; `EditaisPage.jsx:406-415` |
| região | string livre, ex. Sul/Sudeste | `normalizeText` e `includes` em `regiao_raw + regiao` | `filtersEngine.js:311-314` |
| abrangência | não existe na UI | sem comparação; backend a colapsa em região | `data_cleaning.py:113-120` |
| escopo | `todos,brasil,internacional,multilateral` | enum normalizado; classifica por heurística | `editaisQueryFilters.js:19-43,172-177`; `dashboardClassification.js:197-232` |
| área | arrays/string de `area` e `area_cientifica` | `coerceStringArray`, `normalizeText`, OR entre checkboxes por inclusão bidirecional | `filtersEngine.js:176-184,347-350` |
| tipo oportunidade | slug/string | remove `-` para `_`, normaliza, igualdade ou `includes` unilateral | `:299-303` |
| tipo recurso | raw + classificação local | normaliza; `cur.includes(target) || target.includes(cur)` | `:292-309` |
| status cadastral | ativo/inativo/sem_prazo/encerrado/aberto/validado/suspeito/incompleto/acesso_limitado | boolean, prazo e igualdade lowercase | `:148-171` |
| status semântico | aberto, vencendo, encerrado, sem prazo, resultado, permanente etc. | recalculado por `editalStatusBadges`; seleções em OR | `editalStatusBadges.js:253-470` |
| prazo | vencendo_7, vencendo_30, sem_prazo, encerrados, confortável, inválido e legados | data de `prazo_envio_raw ?? fim_inscricao_raw ?? dataLimite`; status derivado | `filtersEngine.js:58-60,246-270` |
| favoritos | remoto ou local | remoto: `isFavorite`; local: `Set` de IDs string | `EditaisPage.jsx:243-260` |
| texto | tokens com 2+ chars | remove acentos/caixa via `normalizeText`; **AND** de todos os tokens sobre haystack amplo | `search.js:5-45` |
| fonte | fonte selecionada/busca | `getFonte`, `normalizeText`, `includes` | `filtersEngine.js:328-335` |
| qualidade | >=70, 40-69, 1-39 ou status | Number + faixas; flags de status exatas | `:186-213,455-463` |
| documentos | com/sem PDF, código, link | booleans; todas as seleções ativas em AND | `:215-232` |

## Escopo geográfico

`getDashboardSourceScope` monta blob com fonte, link, país, estado, região e origem. Prioridade: multilateral -> Brasil -> internacional -> desconhecido (`dashboardClassification.js:197-219`). Brasil casa por lista de órgãos, `.br`, país Brasil/Brazil, estado Nacional ou região BR sem fonte internacional. Internacional casa por lista de termos, país não BR ou estado Internacional. Essas regras não usam `escopo` nem `abrangencia` do backend.

## Diagnósticos

- `filterDebug` registra contagem após cada etapa (`filtersEngine.js:387-494`).
- `computeHiddenHints` conta motivos potenciais (`:82-109`).
- `debugRuntimeDataSource.js` e `debugDataCounts.js` diagnosticam fonte/contagens somente quando habilitados; não alteram contrato.
- `EditaisPage` registra amostras em DEV e resultado de prazo (`EditaisPage.jsx:184-219,262-274`).

## Regras duplicadas e divergências

1. Escopo Brasil/internacional é heurístico, enquanto país/UF/região exigem campos estruturados; um item pode passar em escopo Brasil e falhar em país Brasil.
2. Status é calculado no backend, loader, mapper e badges/filtros.
3. Tipo de recurso usa raw + classificação frontend; tipo de oportunidade usa somente raw.
4. `estado_raw` é consultado pelo filtro mas não criado pelo mapper; `uf_raw` é criado.
5. Favoritos não fazem parte de `filterCatalog`, portanto não aparecem no `filterDebug`.
6. Busca é AND entre tokens, enquanto facetas multivaloradas normalmente usam OR internamente e AND entre blocos.
7. `regiaoLegacy` existe no estado, mas a sidebar visível privilegia o escopo agregado; a disponibilidade concreta do controle regional deve ser validada pela UI em runtime.

## Hipóteses/não confirmados

Valores reais de facetas, contagens, favoritos remotos, definição instalada da view e efeitos de RLS dependem do Supabase remoto.
