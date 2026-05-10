# Resumo da auditoria (dry-run)

## Interpretação (importante)
- **Ruído que passou = 0** não prova ausência de ruído no mundo real: só significa que, na amostra, nenhum título da lista negra entrou como aceite.
- Com **`--no-skip-pdf` desligado** (default), muitos itens perdem sinais de PDF e o **`opportunity_gate`** pode rejeitar mais — o contador **«quebrado»** mistura *crawler vazio*, *gate agressivo* e *amostra pequena*; **não** implica «consertar N crawlers».
- Rejeições **«login/autenticação»** podem ser páginas inúteis **ou** falsos positivos; o gate foi afinado para **suprimir login fraco** em `gov.br`/bancos públicos quando há contexto de chamada/edital ou descrição longa (ver `CORE/opportunity_gate.py`).
- Para isolar **loader vs transformer**, use **`--only-loader`** sobre `*_standardized.json`.
- Para PDF real só em poucas fontes: **`--no-skip-pdf --sources fonte1,fonte2`**.
- Para tirar score/relevância do caminho crítico no transformer: **`EDITALFINDER_SKIP_SCORING=true`**.

- Ficheiros processados: **4**
- Itens analisados (amostra): **68** (máx. 25 por ficheiro)
- Fontes com dados na amostra: **4**
- PDFs na auditoria: **ativos**

## Matriz (resumo)

| Crawler | Categoria | Status | Qualidade | Ruído |
|---------|-----------|--------|-----------|-------|
| aneel|aneel_editais.json | energia | fraco | alta | baixo |
| bndes|bndes_editais.json | credito | quebrado | n/d | baixo |
| cnpq|cnpq_editais.json | fomento | quebrado | n/d | baixo |
| finep|finep_editais.json | fomento | fraco | alta | baixo |

## Ruído que passou o transformer
Total registos: **0** (ver `audit_noise_examples.json`).

## Top correções sugeridas (automático)
1. Rever fontes classificadas como **ruidoso** ou **quebrado** em `audit_by_source.json`.
2. Reduzir campos vazios nas fontes no topo de `audit_empty_fields.json`.
3. Tratar perdas PDF/descrição em `audit_data_loss_examples.json`.
4. Afinar `tipo_recurso` para crédito (BNDES/BRDE/Caixa) com base nos exemplos de classificação.
5. Inferir `perfil_ideal` para fontes estratégicas listadas em `audit_profile_issues.json`.
6. Corrigir datas/prazo vs `situacao` nos casos de `audit_classification_issues.json` / datas.
7. Rever duplicados de link no mesmo JSON (`audit_duplicates.json`).
8. Planejar deprecação de score/relevância com base em `audit_score_legacy.json`.

Detalhe completo das 22 secções pedidas: consolidar a partir dos JSON em `audit_reports/` + este ficheiro.