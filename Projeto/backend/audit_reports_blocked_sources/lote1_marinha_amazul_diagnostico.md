# Lote 1 — Diagnóstico Marinha + AMAZUL

## Estado atual do bruto (após correções)

| Fonte | Itens brutos | Transformados | Rejeitados |
|--------|-------------:|----------------:|-----------:|
| **marinha** | 0 | 0 | 0 |
| **amazul** | 0 | 0 | 0 |

Os ficheiros `marinha/outputs/marinha_editais.json` e `amazul/outputs/amazul_editais.json` estão **vazios** (`[]`): deixou de existir o **fallback de índice** (`fallback_public_index`) que gravava a página genérica `/editais` ou `/licitacoes` como se fosse oportunidade.

## Histórico (antes das correções)

- **1** item cada um, **hub institucional** (só listagem), `metodo_extracao: fallback_public_index`.
- O **transformer** rejeitava **100%** com o **opportunity_gate** global: *«Pontuacao abaixo do minimo (oportunidade nao evidenciada)»* — coerente com página sem objeto de licitação/chamada concreto.
- **Não** foi alterado o módulo `opportunity_gate`; apenas **relaxamentos locais** (`_marinha_soft_continue`, `_amazul_soft_continue`) e **calibrações** (`calibrate_marinha_extras`, `calibrate_amazul_extras`) para itens **futuros** com evidência, **excluindo** hubs rasos (`/editais`, `/licitacoes`, `/chamadas-publicas` isolados).

## Classificação de tipos (URLs / conteúdo)

| Tipo | Marinha / AMAZUL |
|------|-------------------|
| Licitação / contratação | Detalhe com pregão, licitação, UASG, modalidade, PDF de edital, etc. |
| Compra pública | Mesmo eixo, evidência em texto/URL. |
| Fornecedor / cadastro | Só quando o conteúdo for claramente compra para fornecedores (perfil em calibração). |
| Concurso / processo seletivo | Marcadores explícitos; sem misturar com compra. |
| Chamada pública / programa | Marcadores de chamada/fomento sem tratar como licitação sem evidência. |
| Notícia / página genérica / contato | **Excluídos** no crawler (`avoid_keywords`, `link_url_exclude_substrings`, `link_path_min_depth`, sem fallback). |

## Crawler (`main_marinha.py`, `main_amazul.py`)

- Removida a raiz `marinha.mil.br/` da listagem (reduz ruído).
- Filtros de URL: exclusão de notícias, concursos, multimídia, redes sociais, contacto, etc.
- `link_url_must_contain_any` + **`link_path_min_depth: 2`** para evitar links rasos sem detalhe.
- **Sem** fallback de índice quando a coleta não devolve itens.

## Classificação local (`transformer.py`, `taxonomy_filtros.py`)

- **Marinha / AMAZUL** fora de `build_defense_extras` genérico (evita nuclear/defesa forçados).
- **`calibrate_marinha_extras` / `calibrate_amazul_extras`**: `tipo_oportunidade` conforme evidência (licitação vs `processo_seletivo` vs chamada); **nuclear** na AMAZUL só com termos fortes ou nuclear + compra; `setor_estrategico` vazio se não houver contexto.

## Retransformação e auditorias

- **Retransformação:** `audit_reports_blocked_sources/lote1_fix_marinha_amazul/` — ver `retransform_summary.json` (0 brutos / 0 transformados).
- **Semântica:** `audit_reports_blocked_sources/lote1_fix_marinha_amazul_semantic/` — 0 itens (sem flags acumuladas).
- **Documentos:** `audit_reports_blocked_sources/lote1_fix_marinha_amazul_docs/` — 0 itens analisados.

## Exemplos (`lote1_marinha_amazul_examples.json`)

Inclui **itens sintéticos** (não são brutos reais) só para mostrar que, **com** URL de detalhe e texto com pregão/licitação/chamada, o pipeline **aceita** e aplica a calibração local.

## Readiness recomendado (por fonte)

| Fonte | Recomendação | Motivo |
|--------|----------------|--------|
| **marinha** | **`needs_manual_review`** (manter **blocked** no loader até haver dados) | Sem itens brutos após filtros honestos; é preciso **reexecutar o crawler** com rede acessível e validar links reais. |
| **amazul** | **`needs_manual_review`** (idem) | Idem. |

**Não** `ready` nem `ready_with_notes` enquanto `standardized` estiver vazio: não há oportunidades para carregar.

**Não** atualizar `source_readiness.json` / `readiness_for_loader.json` nesta tarefa (apenas relatório).

## Próximos passos sugeridos

1. `python marinha/main_marinha.py` e `python amazul/main_amazul.py` num ambiente com acesso estável aos `.mil.br`.
2. Revisar `*_editais.json` gerado; voltar a correr `retransform_all` e auditorias.
3. Se o volume e a qualidade forem bons, aí sim `ready_with_notes` ou `ready`.

JSON detalhado: `lote1_marinha_amazul_diagnostico.json`.
