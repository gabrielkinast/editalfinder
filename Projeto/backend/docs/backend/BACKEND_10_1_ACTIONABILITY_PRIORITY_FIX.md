# Backend 10.1 — Prioridade de acionabilidade e semântica de ruído

Correção cirúrgica após dry-run Backend 10 (1232 registros).

## Problema no Backend 10

| Sintoma | Causa |
|---------|--------|
| Chamadas CNPq classificadas como `resultado` | `selecionados` e `resultado` fracos competiam antes da oportunidade forte |
| `ruido_provavel` ≈ 890 (73%) | `resultado`, `retificacao`, `evento` tinham `is_noise=true` |
| `sem_oportunidade` = 845 confundido com ruído no relatório | `noise_type` preenchido mesmo com `is_noise=false` em versões anteriores |

### Métricas Backend 10 (referência)

- Acionáveis: 175
- Ruído provável (`is_noise`): 930
- `sem_oportunidade`: 845

## Correções 10.1

### 1. Ordem de prioridade em `noise_classifier.py`

1. Oportunidade forte (`has_opportunity_strong`)
2. Resultado forte explícito (`has_resultado_strong`) — só vence se marcador explícito; se ambos, resultado
3. Retificação
4. Portal útil
5. Portal genérico (blocklist por fonte)
6. Evento institucional (não confunde com “promoção de eventos” em chamada)
7. Notícia
8. Documento auxiliar
9. `sem_oportunidade` / `desconhecido`

### 2. Oportunidade forte

Inclui: `chamada pública`, `chamada cnpq`, `seleção de fundos`, `auxílio`, `prêmio`, `dispensa de licitação`, `DE-FOA-*`, etc.

### 3. Resultado forte

Só: `resultado final`, `homologação`, `lista de selecionados`, título iniciando com `Resultado -`, etc.

**Não** classifica por `chamada`, `programa` ou `seleção` isolados.

Com **oportunidade forte no título**, marcadores de resultado em descrição/PDF **não** contam — evita falso positivo em chamadas CNPq cujo texto extraído menciona “resultado” genérico.

### 4. Semântica `is_noise` (10.1)

| actionability_type | is_noise |
|--------------------|----------|
| oportunidade_* | false |
| portal_util | false |
| resultado, retificacao, documento_auxiliar | false |
| evento | false |
| portal_generico, noticia, sem_oportunidade | true |

`noise_type` **sempre** `null` quando `is_noise=false`.

### 5. classification_bucket

- `resultado` / `retificacao` → `documento_auxiliar` (não `ruido_provavel`)
- `portal_util` → `portal_util`
- `portal_generico`, `noticia`, `sem_oportunidade` → `nao_aplicavel`

## Testes de regressão

`backend/tests/test_noise_classifier.py` — casos CNPq, resultado final, portal útil/genérico, invariantes.

## Comandos

```bash
cd backend
python -m pytest tests/test_noise_classifier.py tests/test_validity_resolver.py tests/test_quality_score.py -q
python scripts/audit_noise_backend.py --from-db --limit 5000
python scripts/audit_validity_backend.py --from-db --limit 5000
python scripts/dry_run_quality_enrichment.py --from-db --limit 5000
```

## Métricas pós-10.1 (dry-run 1232 registros, staging)

| Métrica | Backend 10 | Backend 10.1 |
|---------|--------------|--------------|
| `oportunidade_acionavel` | 175 | **136** |
| `ruido_provavel` (`is_noise=true`) | 930 | **25** (2,0%) |
| `oportunidade_principal` | 43 | **54** |
| `oportunidade_sem_prazo` | 132 | **82** |
| `resultado` (não ruído) | 35 | **22** |
| `portal_util` | 51 | **58** |
| CNPQ: principal + sem_prazo | misto com `resultado` | **13 principal**, 0 `resultado` falso |

Nota: acionáveis totais podem variar vs B10 porque `desconhecido` (968) permanece o maior bucket — crawlers internacionais sem marcadores PT/EN no título.

## Resultado esperado pós-10.1

- `ruido_provavel_count` alinhado a `is_noise=true` (portal genérico, notícia, sem_oportunidade)
- `resultado` / `portal_util` / `retificacao` fora do ruído duro
- Chamadas CNPq/BNDES dos exemplos de regressão não viram `resultado` por texto de apoio

## Enriquecimento

Versão: **`backend_10.1`**

## Próximo gargalo

Oportunidades acionáveis **sem prazo estruturado** (~100+): melhorar parsers/crawlers por fonte, não inflar `nao_aplicavel`.
