# Links removidos — Onda A (semantic_fix → ruido_fix)

Comparação por **URL canónica** (`link` normalizado: minúsculas, sem barra final): entradas presentes no standardized antigo e **ausentes** no novo.

- **Antigo:** `audit_reports_credito/lote_credito_brasil_onda_a_semantic_fix/standardized/`
- **Novo:** `audit_reports_credito/lote_credito_brasil_onda_a_ruido_fix/standardized/`

Dados completos: `credito_brasil_onda_a_removed_links.json`.

## Totais

| Fonte | Antigo | Novo | Removidos |
|-------|-------:|-----:|----------:|
| bnb | 24 | 24 | 0 |
| banco_da_amazonia | 26 | 26 | 1 |
| bdmg | 27 | 18 | 20 |
| agerio | 2 | 7 | 1 |
| desenvolve_sp | 4 | 4 | 0 |
| **Total links removidos (únicos por fonte)** | | | **22** |

Fontes **aprovadas** para o loader nesta onda: `bnb`, `banco_da_amazonia`, `bdmg`. `agerio` e `desenvolve_sp` estão em revisão; o diff inclui AgeRio para transparência.

## Exemplos pedidos (ruído / institucional)

### BDMG — “Entre em contato”

- `https://www.bdmg.mg.gov.br/investimento` — título *Entre em contato*.

### Banco da Amazônia — “Conta PJ”

- `https://www.bancoamazonia.com.br/empresas/conta-pj` — título *Conta PJ*.

### AgeRio — educação financeira

- `https://www.agerio.com.br/educacaofinanceira/` — título *Escola Virtual .Gov (EVG)*.

### Outros ruídos / páginas não-crédito (BDMG)

Exemplos na lista de removidos: correspondentes (`/sejaparceiro`), sobre o banco e abas, sala de imprensa, concursos, licitações administrativas, documentação genérica, versão em inglês (`/en`), etc.

## Notas de interpretação (evitar falso positivo em staging)

1. **`/linhaspermanentes` como `link` principal:** no antigo existia um item cujo `link` era o hub municipal; no novo conjunto as linhas municipais usam **URLs de detalhe** como `link`, mantendo o hub em `url_listagem` / `url_pagina` onde aplicável. Tratar como **reestruturação de link canónico**, não necessariamente como “oportunidade sumiu”.
2. **`labagrominas`:** saiu do crawl atual; se for oportunidade desejada, reintroduzir com seed curado em ciclo futuro — **não** desativar em staging sem confirmar intenção.
3. **Staging:** candidatos naturais a `ativo = false` são URLs que **não** voltam no standardized limpo **e** que correspondem a ruído confirmado (contato, conta PJ, educação financeira, sobre/imprensa/concurso, etc.). Revisar manualmente os casos hub vs. produto antes de qualquer script de desativação.

## Estratégia recomendada

1. **Preferido:** marcar `ativo = false` nos registros de staging cujo `link` + `fonte` batem com ruído removido, preservando histórico e escondendo no frontend.
2. **Alternativa equivalente:** manter registro como histórico com `ativo = false` (sem DELETE).
3. **Automação:** usar o script explícito `scripts/deactivate_removed_credito_onda_a_staging.py` — por defeito só **dry-run**; `--apply --staging` exige os mesmos guards do loader **mais** `ALLOW_CREDITO_ONDA_A_DEACTIVATE=1`. **Não** apaga linhas.

**Nesta tarefa:** não foi executado apply do loader nem apply do script de desativação.
