# Diagnóstico — classificação em cards (FAPESC e similares)

## Contexto

Vários editais da **FAPESC** apareciam na página **Editais** com valores técnicos em **Setor / Área tech**, por exemplo:

- `defesa_industrial` / `defensa_industrial`
- `aeroespacial`
- `cyber_defesa`

Para editais **gerais** de inovação ou pesquisa, esses rótulos parecem **desalinhados** com o conteúdo percebido pelo utilizador.

## Origem dos campos no card (frontend)

| Ficheiro | Comportamento |
|----------|----------------|
| `src/utils/edital/editalRowMapper.js` | `mapRawEditalRow` lê da view/tabela `setor_estrategico`, `area_tecnologica`, `setor_economico`, `perfil_ideal`, `tags`, `extras` e normaliza em `*_raw` / listas. |
| `src/components/dashboard/EditalCard.jsx` | **Antes:** uma única linha **«Setor / Área tech»** juntava `setor_estrategico_raw` e `area_tecnologica_raw` **em bruto** (snake_case), sem humanização. **Não** lia `extras` nem `tags` nessa linha. |
| `src/components/dashboard/EditalDetailsModal.jsx` | Detalhes com listas de setor/área (também em bruto antes da correção). |
| `src/pages/Dashboard.jsx` | Export Excel usa campos crus; listagem principal usa o objeto já mapeado. |
| `dataService.getEditais()` | Lê `VITE_VIEW_EDITAIS` (padrão `vw_editais_front`); o mapper consome as colunas expostas pela view. |

### Respostas objetivas

- **O card mostrava `setor_estrategico` directamente?** Sim, via `edital.setor_estrategico_raw` (derivado de `setor_estrategico` na view).
- **Mostrava `setor_economico`?** Não na linha resumida do card; o campo existia no objecto (`setor_economico_raw`) mas **não** era exibido na meta compacta.
- **Lia de `extras`?** Não na linha de setor/área do card.
- **Juntava campos?** Sim: **setores estratégicos** e **áreas tecnológicas** na mesma etiqueta, sem distinção nem labels legíveis.

## Erro: banco/view ou frontend?

| Camada | Papel |
|--------|--------|
| **Banco / pipeline** | Se `public.edital` (ou a view) contém arrays `setor_estrategico` / `area_tecnologica` com slugs de defesa/aeroespacial para chamadas genéricas FAPESC, os **dados estão contaminados ou sobre-classificados** na origem. |
| **Frontend (antes)** | Exibia esses valores **literalmente**, o que **amplificava** a percepção de erro e misturava dois conceitos (estratégico vs tecnológico) numa só etiqueta. |

**Conclusão:** a causa é **mista** — dados possivelmente agressivos ou herdados na BD **e** apresentação cru/inadequada no UI. A correção de **exibição** não apaga dados errados no servidor; apenas deixa de misturar conceitos e humaniza slugs.

## Hipóteses de causa (dados)

1. Classificador automático (loader/LLM/regras) atribuiu **setores estratégicos** amplos a editais FAPESC.
2. **`extras`** antigos ou mesclas preservaram tags que depois foram copiadas para colunas tipadas (menos provável sem ver o pipeline).
3. **`setor_estrategico`** preenchido por regra **demasiado sensível** a palavras-chave partilhadas com defesa/ciber.

## Correção aplicada no frontend (exibição)

- Nova função `humanizeTaxonomyList` em `src/utils/edital/formatEditalUi.js` (usa `humanizeTechnicalLabel`).
- **EditalCard:** linhas separadas **«Setor econômico»**, **«Setores estratégicos»**, **«Áreas tecnológicas»** (só aparecem se houver conteúdo); removida a etiqueta única enganadora.
- **EditalDetailsModal:** listas humanizadas; linha **«Setor(es) econômico(s)»** adicionada.
- **Overrides** em `portaisDisplayLabels.js` para slugs frequentes (`cyber_defesa`, `aeroespacial`, `defesa_industrial`, variantes `defensa_*`).
- **DEV:** após carregar editais, o `Dashboard` regista no consola uma amostra de linhas FAPESC com campos de classificação (ver `Dashboard.jsx`).

## Diagnóstico local / SQL manual

Ver queries na secção **PARTE C** de [`EDITAIS_FAVORITOS_ALERTAS_MVP.md`](EDITAIS_FAVORITOS_ALERTAS_MVP.md) (ficheiro partilhado com diagnóstico de favoritos) ou directamente:

```sql
SELECT id_edital, titulo, fonte_recurso, setor_economico, setor_estrategico, area, area_tecnologica, tags, extras
FROM public.edital
WHERE fonte_recurso ILIKE '%FAPESC%'
ORDER BY id_edital DESC
LIMIT 30;
```

Para o caso só FAPESC, ver também [`EDITAIS_CLASSIFICACAO_FAPESC_DIAGNOSTICO.md`](EDITAIS_CLASSIFICACAO_FAPESC_DIAGNOSTICO.md). Para **todas as fontes**, use [`EDITAIS_CLASSIFICACAO_GLOBAL_DIAGNOSTICO.md`](EDITAIS_CLASSIFICACAO_GLOBAL_DIAGNOSTICO.md) e o plano [`RECOVERY_CLASSIFICACAO_SETOR_GLOBAL_PLAN.md`](RECOVERY_CLASSIFICACAO_SETOR_GLOBAL_PLAN.md).

## Exemplos de editais afetados

Preencher manualmente após correr a query SQL no ambiente (titulos e `id_edital` reais):

| id_edital | titulo (resumo) | setor_estrategico (amostra) |
|-----------|------------------|------------------------------|
| _a preencher_ | _a preencher_ | _a preencher_ |

## Próximos passos

- Se os dados na BD continuarem inadequados após validação humana: **plano de recovery** em `docs/CLASSIFICACAO_FAPESC_RECOVERY_PLAN.md` (sem executar automaticamente neste repositório).
