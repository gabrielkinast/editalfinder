# Validação pós-apply — Fundatec subset `valido` (staging)

Relatório gerado a partir de `loader_apply_staging/` **sem** novo apply e **sem** alteração ao código.

**Fonte:** `audit_reports_main_pipeline/concursos_wave1_fundatec_subset_valido/loader_apply_staging`

---

## 1. Resumo do apply (loader)

| Campo | Valor |
|--------|--------|
| Data execução (loader) | 2026-05-14T18:08:13Z |
| Modo | `apply_staging` |
| `apply_status` | `applied` |
| `staging_flag` | true |
| Total de itens no input | **2** |
| `inserted` | **2** |
| `updated` | **0** |
| `upserted_total` | **2** |
| `errors_count` | **0** |
| `map_errors_count` | **0** |
| `apply_errors_count` | **0** |
| Ficheiros de erro / aviso | `load_concursos_selecao_errors.json` → `[]`; `load_concursos_selecao_warnings.json` → `[]` |

---

## 2. Títulos aplicados

1. Prefeitura de Porto Alegre/RS abre inscrições para concursos públicos nas áreas de Farmácia e Medicina Veterinária - Fundatec  
2. Prefeitura de Morro Reuter/RS abre inscrições para Concurso Público - Fundatec  

**Links da notícia (chave `link` no payload):**

- `https://www2.fundatec.org.br/2026/05/07/prefeitura-de-porto-alegre-rs-abre-inscricoes-para-concursos-publicos-nas-areas-de-farmacia-e-medicina-veterinaria`  
- `https://www2.fundatec.org.br/2026/05/06/prefeitura-de-morro-reuter-rs-abre-inscricoes-para-concurso-publico`  

Detalhe completo dos payloads: `loader_apply_staging/load_concursos_selecao_payload_examples.json`.

---

## 3. Validação da view

A página **`/concursos`** do React usa `fetchConcursos()` → view configurada por **`VITE_VIEW_CONCURSOS`** (por omissão **`vw_concursos_front`**), sobre a tabela base **`public.concurso_selecao`**.

Critérios da view (recência e filtros) estão documentados em `docs/sql/UPDATE_VW_CONCURSOS_FRONT_RECENCY.sql`, em síntese:

- `ativo = true`  
- `validacao_status` em `('valido','incompleto')`  
- `status` fora de `cancelado` / `suspenso`  
- **Recência:** `data_fim_inscricao >= CURRENT_DATE` **ou** `data_prova >= CURRENT_DATE` **ou**, sem ambas as datas, janela de **90 dias** em `criado_em` / `data_publicacao`  

**Validação humana recomendada no Supabase (staging):** executar um `SELECT` em `vw_concursos_front` (ou na tabela) filtrando `fonte = 'fundatec'` e os dois `link` acima, e confirmar colunas visíveis na app (título, datas, links).

Exemplo (ajustar se o host do projeto usar outro esquema):

```sql
SELECT id_concurso, titulo, fonte, validacao_status, status,
       data_fim_inscricao, data_prova, link, link_edital, criado_em
FROM public.vw_concursos_front
WHERE fonte = 'fundatec'
  AND link IN (
    'https://www2.fundatec.org.br/2026/05/07/prefeitura-de-porto-alegre-rs-abre-inscricoes-para-concursos-publicos-nas-areas-de-farmacia-e-medicina-veterinaria',
    'https://www2.fundatec.org.br/2026/05/06/prefeitura-de-morro-reuter-rs-abre-inscricoes-para-concurso-publico'
  );
```

**Nota:** se a **data do servidor** já tiver ultrapassado fim de inscrições **e** prova **e** a janela de 90 dias não aplicar, o registo pode **existir na tabela** mas **deixar de aparecer** na view — nesse caso o card em `/concursos` pode sumir mesmo com apply bem-sucedido.

---

## 4. Checklist visual em `/concursos`

- [ ] Abrir o front **staging** e ir a **`/concursos`**.  
- [ ] Localizar os dois concursos (Porto Alegre — Farmácia/Vet.; Morro Reuter).  
- [ ] Conferir **banca** Fundatec, **UF** RS, **município**, **status** e **datas** alinhados ao JSON aplicado.  
- [ ] Se existir na UI, abrir **link da notícia** e **link do edital** (portal `index_concursos.php?concurso=1090` e `1053`).  
- [ ] Consola do browser: sem erros 401/403 ao listar (RLS / anon).  
- [ ] Se faltar card: validar na **view** vs **tabela** conforme secção 3.  

---

## 5. Limitações — Fundatec **fora** do subset aplicado

Critério do subset: **`validacao_status = valido`**, ou seja, **`link_edital` e `data_fim_inscricao`** presentes no standardized.

Dos **7** itens do standardized v4, **5** ficaram de fora (todos **`incompleto`** — em geral **sem `data_fim_inscricao`** capturada no corpo principal):

| Título (resumo) | Motivo de ficar fora |
|-----------------|----------------------|
| Polícia Penal do RS (213 vagas…) | `data_fim_inscricao` null; há `link_edital`. |
| IPE Prev (121 vagas…) | `data_fim_inscricao` null. |
| Assembleia Legislativa do RS (estágio…) | `data_fim_inscricao` null. |
| Câmara de Palhoça/SC | `data_fim_inscricao` null. |
| Exame POSCOMP 2026 | `data_fim_inscricao` null. |

**Limitações gerais desses registos:** o crawler v4 não infere fim de inscrições sem contexto explícito; **vagas** e **valores monetários** podem ficar vazios ou com notas (`valor_ambiguo`, `vagas_ambiguas`, etc.). **Não foram aplicados em staging** neste apply conservador.

**Crawl (wave1):** além disso, **3** notícias foram descartadas no crawl (`noticia_nao_oportunidade_ativa`) e não entram no standardized — ver `audit_reports_main_pipeline/concursos_wave1_fundatec/crawler_summary.json`.

---

## 6. JSON completo

Estrutura máquina-legível: `pos_apply_validation.json` (mesmo conteúdo ampliado).

---

*Nenhum novo apply foi executado na geração deste relatório.*
