# EditalFinder V2 — Revisão independente da M2.3a

**Parecer: NOT READY para encerrar a M2.3a como pipeline com recursos limitados.** O núcleo semântico offline e as barreiras de autorização passaram nos testes examinados; foi identificada **uma lacuna operacional reproduzível de amplificação de memória/serialização**. Não há evidência, nesta revisão, de promoção ou fusão automática indevida. Não é parecer sobre M2.3b, produção ou a eficácia sobre fontes reais.

## Escopo da revisão

Origem: arquivo recebido `V2.tar(6).gz`. Leitura dos contratos, `integration_models.py`, `integration.py`, dependências de evidência/normalização/identidade, fixtures e `test_m23_core.py`. Nenhuma alteração no código original, nenhuma conexão de rede, banco de dados, crawler, staging ou commit.

Ambiente da revisão: Python **3.13.5**. Os resultados do Hermes em Python 3.11.16 são independentes desta execução. Não reexecutei Ruff/mypy, ausentes no ambiente, e o TAR não incluiu `pyproject.toml` ou `uv.lock`.

## Verificações confirmadas

- **Suíte completa:** `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider` → **1.402 passed**.
- Cinco cenários sintéticos (`grant`, `credit`, `investment`, `mixed`, `ambiguous`) reproduziram relatórios determinísticos, round-trips estáveis e `promotable=False`.
- Nove adulterações dirigidas — incluindo data de referência, diagnóstico, catálogo, auditorias aninhadas, payload do snapshot e digest externo — foram rejeitadas pelo contrato. Permaneceram rejeitadas após a remoção do digest externo, pela reavaliação dos resultados e validações aninhadas.
- O código mantém identidade por pares solicitados explicitamente e não realiza merge, crawling, persistência ou promoção.
- As regras de consistência entre domínios não foram implementadas em M2.3a, conforme o escopo declarado; `diagnostics=()` é deliberado.

## Achado 1 — Amplificação de saída não coberta pelo limite de snapshots

**Severidade: alta para segurança operacional; prioridade: corrigir antes de integrar ingestão externa.**

### Causa

`src/editalfinder_v2/domain/integration.py`, linhas 63–73, limita o batch a 32 candidatos, 64 comparações, 4.800 claims e **16 MiB de representações únicas de snapshots**. A contagem de snapshots usa um `set`, contabilizando corretamente a mesma representação compartilhada uma única vez. Entretanto, o relatório devolvido embute esse mesmo snapshot nos objetos de entrada e nos relatórios individuais de cinco normalizadores e do validador M1. A revalidação de `IntegrationReport`, em `integration_models.py`, linhas 123–141, repete a avaliação completa.

Assim, a política limita o volume **de entrada única**, mas não limita a **memória nem os bytes emitidos** pelo relatório. Essa diferença pode ser explorada por batches ainda dentro dos limites válidos.

### Reprodução realizada

Usando `tests/m23_fixtures.py::adapt_records`, repetindo o registro sintético `grant` N vezes, com IDs de candidatos distintos e um snapshot compartilhado contendo N registros:

| Candidatos | JSON do snapshot único | Ocorrências de `payload_json` no relatório | Relatório JSON |
|---:|---:|---:|---:|
| 1 | 1.087 bytes | 8 | 147.692 bytes |
| 4 | 4.309 bytes | 32 | 705.887 bytes |
| 16 | 17.197 bytes | 128 | 4.689.467 bytes |
| 32 | **34.381 bytes** | **256** | **14.355.403 bytes** |

Em todos os casos, `integrate(...)` retornou `IntegrationReport`, não `OperationalError`. Com 32 candidatos, a execução da integração foi aproximadamente **4,1 s** e a reconstrução com `IntegrationReport.model_validate_json(...)` mais **3,4 s** nesta execução pontual. Os tempos não são benchmark controlado e não devem ser usados para comparar com o hardware do Hermes.

A multiplicação do payload pode crescer para gigabytes sob entradas próximas do teto de bytes permitido, **sem extrapolar o limite de 32 candidatos**. Trata-se de projeção de risco sobre o mecanismo observado, não de um teste de alocação de gigabytes; nenhum teste desse tamanho foi executado.

### Reprodução mínima

```python
from m23_fixtures import adapt_records, records_for
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegrationReport

record = records_for('grant')[0]
request = adapt_records([record] * 32)
report = integrate(request)
assert isinstance(report, IntegrationReport)
print(len(request.candidates[0].context.snapshots[0].payload_json.encode('utf-8')))
print(report.model_dump_json().count('"payload_json"'))
print(len(report.model_dump_json().encode('utf-8')))
# 34381, 256, 14355403 (neste ambiente)
```

### Correção recomendada

Preferência de longo prazo: **um registro compartilhado de snapshots** e referências por UUID em relatórios individuais, em vez de repetir objetos completos e seu `payload_json` em todos os DTOs aninhados; preservar a correspondência e a integridade de cada referência.

Correção pontual se a estrutura atual for mantida: impor, **antes de construir grandes relatórios**, um orçamento conservador de saída/memória que considere a multiplicidade do snapshot por candidato e o custo dos claims/relatórios. Um limite aplicado somente **depois** de serializar o relatório não evita o pico de memória. Excedentes devem resultar em `OperationalError`, sem truncamento e sem rejeição semântica.

Adicionar teste de regressão com múltiplos candidatos e snapshot compartilhado inflado, incluindo casos abaixo e acima do novo orçamento; medir `integrate` e `model_validate_json` separadamente. Não construir cargas de gigabytes nos testes automatizados.

## Decisão técnica

O pipeline mantém as fronteiras semânticas e de autorização nos cenários examinados, e os **1.402 testes passam**. Entretanto, a afirmação de que os limites globais de M2.3a controlam a execução não se sustenta para o tamanho efetivo dos relatórios. **NOT READY para fechar M2.3a com garantia de recursos limitados**; recomendar **M2.3a.1 — Output/Memory Budget Hardening**, corretiva e offline, antes de M2.3b.

Pendências já conhecidas e não bloqueantes deste recorte: regras de consistência entre domínios, projeção M2→M1, autenticidade/autorizações e políticas de transporte/persistência. Não modificar essas responsabilidades na correção dirigida.
