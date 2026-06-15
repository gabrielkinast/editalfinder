# BACKEND 10.1A — Actionability Priority Fix

Consolidação da prioridade de acionabilidade após inventário 2026-06 e dry-run Backend 10.1.

## Problema

- Chamadas reais (CNPq, Embrapii) podiam virar `resultado` por marcadores fracos no corpo.
- `desconhecido` (78,6%) dominava o corpus — especialmente Grants.gov e fontes internacionais.
- Hubs de funding (`Open funding opportunities`) competiam com oportunidades nomeadas do Grants.gov.
- `desconhecido` com link válido podia receber `is_noise=true` (incorreto para 10.1A).

## Prioridade implementada (`noise_classifier.py`)

1. Oportunidade forte  
2. Resultado forte  
3. Retificação  
4. Portal útil  
5. Portal genérico  
6. Evento  
7. Notícia  
8. Documento auxiliar  
9. Sem oportunidade  
10. Desconhecido  

**Regra central:** marcadores fortes de oportunidade no **título** vencem `resultado`/`evento`/`notícia` no corpo.

Se **oportunidade forte + resultado forte** no título → `resultado`.

## Marcadores fortes de oportunidade

### Português (ampliado)

`chamada pública/publica`, `chamada cnpq`, `seleção/selecao pública`, `seleção de fundos`, `subvenção/subvencao`, `auxílio/auxilio`, `edital`, `financiamento`, `fomento`, `bolsa`, `prêmio/premio`, `licitação/licitacao`, `pregão/pregao`, `dispensa de licitação`, `chamada regional/nacional`, etc.

### Inglês (ampliado)

`funding opportunity`, `grant`, `call for proposals/applications`, `notice of funding opportunity`, `NOFO`, `BAA`, `solicitation`, `RFP`, `tender`, `procurement notice`, `funding call`, `research opportunity`, `application deadline`, `DE-FOA-*`.

### Evidência no corpo

Padrões EN **explícitos** no corpo só contam com título substantivo (≥8 chars): NOFO, call for proposals, notice of funding opportunity, etc.

### Fontes grant-like

Grants.gov, NSF, DOE, SBIR, Horizon, EIC, ERC: títulos com `funding opportunity`, `grant`, `NOFO`, `solicitation` classificam como oportunidade.

### Hub vs oportunidade nomeada

`Open funding opportunities` → `portal_util`.  
`SBIR/STTR Funding Opportunity: Advanced Propulsion` → oportunidade (não hub).

## Marcadores fortes de resultado

`resultado final/preliminar`, `homologação`, `lista de selecionados`, `resultado da seleção`, título iniciando com `Resultado -`, `final/preliminary result`, `awardees`, `selected projects`, etc.

**Não** usa `resultado` genérico no corpo quando o título tem chamada forte.

## Semântica `is_noise` (10.1A)

| actionability_type | is_noise |
|--------------------|----------|
| oportunidade_* | false |
| portal_util, resultado, retificacao, documento_auxiliar, evento | false |
| **desconhecido** | **false** |
| portal_generico, noticia, sem_oportunidade | true |

Invariante: `is_noise=false` → `noise_type=null`.

## Testes adicionados (`tests/test_noise_classifier.py`)

- Chamadas CNPq (6 casos) + Embrapii  
- Resultados finais + lista de selecionados  
- Chamada real não vira resultado por texto no corpo  
- BNB/Eureka portal_util sem ruído  
- Grants.gov funding opportunity  
- Invariante desconhecido não é ruído  
- Invariante tipos não-ruído → `noise_type=null`  

**33 testes** passando (+ `test_validity_resolver.py`).

## Métricas antes/depois (dry-run 1232 registros)

| Métrica | Backend 10.1 (pré-10.1A) | Backend 10.1A |
|---------|--------------------------:|--------------:|
| `is_noise=true` | 25 (2,0%) | **25 (2,0%)** |
| Oportunidades acionáveis | 136 | **170 (+34)** |
| `oportunidade_principal` | 54 | **58** |
| `oportunidade_sem_prazo` | 82 | **112** |
| `resultado` | 22 | **28** |
| `portal_util` | 58 | **48** |
| `desconhecido` | 968 (78,6%) | **938 (76,1%)** |

### Fontes afetadas

| Fonte | Antes → Depois (acionáveis) | Observação |
|-------|----------------------------|------------|
| **Grants.gov** | ~8 → **22** | 16 sem_prazo + 6 principal; desconhecido 119→105 |
| **CNPq** | 13 principal | 0 falso `resultado` |
| **DOE_ARPAE** | 11 → **14** | sem_prazo |
| **BNDES** | 20 | mantido; prazo ainda gargalo (10.1D) |
| **EMBRAPII** | 10 | 10 resultado histórico separados |
| **BNB/Eureka** | portal_util | sem ruído duro |
| **MOFCOM/NSFC** | desconhecido | sem inflar ruído (conforme escopo) |

## Limitações

- **938 desconhecidos** — fontes asiáticas/MOFCOM ainda sem marcadores fortes (10.1C).
- **BDMG/QST** — ruído residual alto; requer perfis por fonte (10.1C) + mover módulo.
- **Prazo estruturado** — 112 `oportunidade_sem_prazo`; 10.1D.
- Campos **não persistidos** em `public.edital` — apenas dry-run/enricher.

## Comandos (executados neste patch)

```bash
cd backend
python -m pytest tests/test_noise_classifier.py tests/test_validity_resolver.py -q
python scripts/audit_noise_backend.py --from-db --limit 5000
python scripts/audit_validity_backend.py --from-db --limit 5000
python scripts/dry_run_quality_enrichment.py --from-db --limit 5000
```

**Não executado:** apply, migration, alteração Supabase.

## Próximo patch recomendado

**BACKEND 10.1C — Source-level Noise Profiles** (BDMG, BNB, China, suppliers)  
ou **BACKEND 10.1B** se ainda houver casos de `portal_util`/`resultado` contados como ruído em relatórios legados.

## Arquivos alterados

- `CORE/noise_classifier.py`
- `CORE/source_quality_profiles.py`
- `CORE/opportunity_enricher.py` (`ENRICHMENT_VERSION=backend_10.1a`)
- `scripts/audit_noise_backend.py` (rótulo 10.1A)
- `tests/test_noise_classifier.py`
- `outputs/audit_noise_backend/*` (regenerados)
- `outputs/audit_validity_backend/*` (regenerados)
- `outputs/backend_9_quality_dry_run/*` (regenerados)
