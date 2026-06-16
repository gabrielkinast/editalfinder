# BACKEND 10.1C — Source-level Noise Profiles

Perfis de acionabilidade por fonte após Backend 10.1A.

## Problema

O gargalo pós-prioridade global era **classificação por fonte**:

- **BDMG:** portal institucional e notícias misturados com linhas de financiamento.
- **BNB/Eureka:** hubs `atividades financiadas` / `funding opportunities` sem perfil estável.
- **QST:** 100% ruído no fluxo edital (conteúdo notícia/pesquisa).
- **Suppliers:** páginas de fornecedor como `desconhecido`.
- **China MOFCOM/NSFC:** desconhecidos sem inflar ruído falso; notícias institucionais.
- **DoD SBIR/STTR:** portal vs oportunidade misturados.

## Fontes tratadas

| Fonte | Perfil (`kind`) | Ação principal |
|-------|-----------------|----------------|
| BDMG | `mixed_bank_portal` | portal_generico institucional; portal_util linhas de crédito |
| BNB | `bank_funding_portal` | portal_util atividades financiadas |
| Eureka Network | `funding_hub` | hub → portal_util; calls → oportunidade |
| QST | `news_research_source` | `block_as_edital` → noticia |
| China MOFCOM | `china_tender` | desconhecido sem evidência; notícia explícita |
| China NSFC | `china_research` | idem |
| DoD SBIR/STTR | `grant_like_with_portal` | Data Resources → portal_generico; SBIR → oportunidade |
| Suppliers (Lockheed, BAE, GD, …) | `supplier_portal` | portal_util; recomendar `portal_estrategico` |
| EMBRAPII | `mixed_calls_results` | marcadores resultado (complemento) |

## Arquivos

- `CORE/source_actionability_profiles.py` — perfis, `normalize_source_name`, `resolve_source_actionability_rule`
- `CORE/source_quality_profiles.py` — merge perfis + blocklist/portal_util
- `CORE/noise_classifier.py` — integração após retificação (passo 3b)
- `tests/test_noise_classifier.py` — 19 testes de perfil + regressão CNPq/Grants

## Exemplos por fonte

### BDMG

| Título | Tipo | is_noise |
|--------|------|----------|
| Sobre o BDMG / Eventos / English | portal_generico | true |
| Linhas Permanentes de Financiamento Municipal | portal_util | false |
| Trabalhe no BDMG | sem_oportunidade | true |

### BNB

| Título | Tipo |
|--------|------|
| Educação – atividades financiadas | portal_util |
| Crédito para Poder Público – financiamento de projetos | portal_util |

### Eureka

| Título | Tipo |
|--------|------|
| Open funding opportunities | portal_util |
| Eurostars call for projects | oportunidade_sem_prazo |

### QST

Títulos institucionais/japonês → `noticia` (não oportunidade no edital).

### Suppliers

`Supplier Portal`, `Become a Supplier`, `Procurement` → `portal_util`.

**Recomendação:** migrar módulo destino para `portal_estrategico` (não neste patch).

## Métricas antes/depois (1232 registros)

| Métrica | 10.1A | 10.1C | Δ |
|---------|------:|------:|--:|
| **is_noise=true** | 25 (2,0%) | **32 (2,6%)** | +7* |
| **Oportunidades acionáveis** | 170 | **186** | +16 |
| **oportunidade_principal** | 58 | **58** | 0 |
| **oportunidade_sem_prazo** | 112 | **128** | +16 |
| **portal_util** | 48 | **92** | +44 |
| **portal_generico** | 11 | **12** | +1 |
| **noticia** | 14 | **20** | +6 |
| **desconhecido** | 938 | **874** | −64 |
| **resultado** | 28 | **28** | 0 |

\* Aumento de `is_noise` explicado por reclassificação **desconhecido → noticia** em QST/MOFCOM/NSFC (ruído correto no fluxo edital, não inflação de portal_util/resultado).

### Efeito por fonte

| Fonte | 10.1A → 10.1C |
|-------|----------------|
| **BDMG** | portal_util 3→26; desconhecido 15→1; ruído 28,9%→23,7% |
| **BNB** | 17 portal_util; 0% ruído (mantido) |
| **Eureka** | +11 oportunidade_sem_prazo; 10 portal_util |
| **QST** | 5 noticia (block_as_edital) |
| **MOFCOM** | 125 desconhecido + 6 noticia; 4,6% ruído |
| **NSFC** | 21 desconhecido + 7 noticia |
| **Suppliers** | BAE 3 portal_util; GD 4 portal_util |
| **CNPq** | 13 principal; 0% ruído (sem regressão) |
| **Grants.gov** | 22 acionáveis; 0% ruído (sem regressão) |
| **DoD SBIR** | 10 oportunidade_sem_prazo |

## Invariantes mantidos

- `is_noise=false` → `noise_type=null`
- `desconhecido` → `is_noise=false`
- `portal_util`, `resultado`, `evento` → não ruído duro
- Oportunidade forte global vence perfil (exceto `block_as_edital` sem evidência)

## Limitações

- **MOFCOM/NSFC:** maioria permanece `desconhecido` (by design).
- **BDMG:** ainda ~24% ruído no fluxo edital (portal_generico + sem_oportunidade).
- **BNDES prazo:** Backend 10.1D.
- Campos não persistidos em `public.edital`.

## Próximo patch recomendado

**BACKEND 10.1D — Validity/Prazo Enrichment** (BNDES, DOE_ARPAE, Grants.gov close_date).

Alternativa paralela: roteamento **portal_estrategico** para suppliers/BDMG hubs (loader, fora do classificador).

## Comandos

```bash
cd backend
python -m pytest tests/test_noise_classifier.py tests/test_validity_resolver.py -q
python scripts/audit_noise_backend.py --from-db --limit 5000
python scripts/audit_validity_backend.py --from-db --limit 5000
python scripts/dry_run_quality_enrichment.py --from-db --limit 5000
```

**Não executado:** apply, migration, Supabase.
