# EditalFinder V2 — Revisão independente da M2.3a.1

**Escopo:** `V2.tar(7).gz`, revisão offline e somente leitura de `integration.py`, `integration_models.py`, `integration_budget.py`, testes e documentação associados. Nenhum arquivo do repositório do usuário foi modificado, nem houve acesso a Legacy, Supabase ou rede.

**Parecer:** a **correção de orçamento de saída funciona nos cenários examinados** e o núcleo da M2.3a.1 pode ser considerado **READY para o mecanismo offline de admissão**, com uma **ressalva de integridade do protocolo de auditoria** que recomendo corrigir antes de declarar o conjunto de contratos integralmente encerrado. Não é certificação de produção nem de teto de RSS.

## 1. Ambiente e testes reproduzidos

- Python 3.13.5; Pydantic 2.13.5; pytest 9.0.2 (verificação adicional ao Python 3.11.16 e Pydantic 2.14.1 informados pelo Hermes).
- `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider` → **1.437 passed in 8.95s**.
- Ruff e mypy **não foram reexecutados neste ambiente**, por ausência dos executáveis. O relatório do Hermes declara mypy e Ruff dos cinco arquivos da correção aprovados. O gate **global** de Ruff permanece não aprovado, devido a sete ocorrências e formatação em `tests/m23_fixtures.py`, explicitamente preservadas pelo implementador.
- O pacote traz `integration_budget.py` com política `m2.3a.1-output-budget-v1`, reserva de 64 MiB, cobrança saturante, multiplicidade de snapshots e corpo, limites de visita/profundidade e recusa antecipada.

## 2. Reproduções próprias do orçamento

| Fixture / candidatos | Resultado | Custo projetado | JSON final | Pico de alocação adicional (tracemalloc, execução local) |
|---|---|---:|---:|---:|
| Fomento, 1 | `IntegrationReport` | 6.277.808 | 147.743 B | 602.897 B |
| Fomento, 4 | `IntegrationReport` | 25.530.368 | 705.938 B | 2.663.638 B |
| Fomento, 16 | `OperationalError: integration_output_budget_exceeded` | 67.108.865 (saturado) | 163 B | 129.946 B |
| Fomento, 32 | `OperationalError: integration_output_budget_exceeded` | 67.108.865 (saturado) | 163 B | 117.214 B |
| Crédito, 4 | `IntegrationReport` | 15.338.752 | 444.770 B | 1.663.892 B |
| Investimento, 4 | `IntegrationReport` | 16.969.216 | 501.850 B | 1.890.702 B |

Essas medidas são locais e não comparáveis diretamente ao benchmark do notebook do usuário. **O ganho nos lotes recusados advém de não gerar o relatório**, não de reduzir a representação serializada anterior. A admissão é deliberadamente conservadora: 16 candidatos podem ser recusados mesmo quando o relatório real antigo tinha apenas ~4,7 MB.

Outras verificações independentes:
- `grant`, `credit`, `investment`, `mixed` e `ambiguous`: relatórios admitidos e round-trip Python→JSON→Pydantic preservados;
- comparação de identidade explícita entre dois candidatos: um resultado emitido, preservado após round-trip;
- adulteração de diagnóstico com e sem envelope externo: rejeitada pela recomputação;
- tentativa de construir diretamente relatório acima do orçamento: rejeitada antes da construção de DTOs internos;
- sem evidência de merge ou promoção automáticos.

## 3. Achado novo — versões ausentes no envelope são preenchidas automaticamente

**Severidade:** baixa na operação atual (sem promoção ou persistência), **média para proveniência/auditoria histórica futura**.

**Local:** `src/editalfinder_v2/domain/integration_models.py`, contrato `IntegrationAudit` e validação `IntegrationReport.verify_outputs`.

`IntegrationAudit` define valores padrão para `output_budget_version`, `algorithm`, `hash_version` e `limits_version`. Quando um relatório JSON recebido inclui o digest do corpo, mas **omite esses metadados**, o Pydantic os recria a partir dos defaults e aceita o relatório. Assim, a informação de qual versão veio de fato no arquivo de origem se perde.

### Reprodução independente

```python
import json
from m23_fixtures import adapt_records, records_for
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegrationReport

original = integrate(adapt_records([records_for("grant")[0]]))
payload = json.loads(original.model_dump_json())
payload["audit"] = {"report_digest": original.audit.report_digest}
restored = IntegrationReport.model_validate_json(json.dumps(payload))

assert restored.audit.output_budget_version == "m2.3a.1-output-budget-v1"
assert restored == original
```

**Resultado observado:** ambos os `assert` passaram. Remover isoladamente `output_budget_version`, `algorithm`, `hash_version` ou `limits_version` também é aceito; remover `report_digest` é rejeitado.

**Limite do achado:** não permite alterar o corpo do relatório sem que a recomputação detecte o conflito; não prova assinatura/autoria, não desativa o orçamento, não permite `promotable=True`. É uma inconsistência entre o **envelope recebido** e os **metadados posteriormente apresentados como se estivessem no envelope original**. A decisão de permitir revalidação de relatórios históricos sob uma política nova deve ser explicitamente diferenciada de afirmar que eles foram **produzidos originalmente** sob essa política.

**Correção recomendada:** quando um envelope de auditoria for fornecido, exigir explicitamente os metadados obrigatórios (`Field(...)`/campos sem defaults ou validator de presença), inclusive na validação JSON. Na geração local do relatório, criar explicitamente todos os campos. Preservar, se desejado, a rota intencional `audit=None` para reavaliação e um marcador específico que identifique o reprocessamento; não fazer backfill silencioso do envelope de origem. Acrescentar regressões para remoção de cada campo, round-trip e compatibilidade/migração de relatórios antigos.

## 4. Restrições e decisões não resolvidas

1. O teto de 64 MiB é uma **estimativa de admissão** baseada no layout atual: não é prova formal de tamanho de saída, limite de memória residente ou de alocação na construção dos inputs.
2. `model_validate_json` precisa decodificar o JSON **antes** de executar `model_validator(mode="before")`. Uma camada de transporte deve limitar bytes/estrutura antes dessa operação.
3. A multiplicação de snapshots no relatório ainda existe para lotes admitidos. A recusa antecipada é correta, mas para aumentar capacidade será necessário um formato compartilhado de snapshots por ID, sem perder auditoria nem evidência.
4. O overhead de admissão e de reavaliação completa pode impactar throughput; tratar em etapa específica com benchmarks e parâmetros de produto.
5. O gate global de Ruff ainda não está totalmente verde; o problema é anterior e explícito, mas deverá ser resolvido antes de um gate de CI realmente abrangente.
6. Sem conexão com documentos reais, persistência, autorização humana, scraping ou medição de precisão/recall do produto.

## 5. Recomendação de sequência

**Correção pequena antes da M2.3b:** tornar explícita e verificável a presença dos campos de versão do `IntegrationAudit` recebidos, com regressões de serialização, sem alterar a política do orçamento. Em seguida, iniciar M2.3b (consistência entre domínios), mantendo a promoção desabilitada. Não é necessário reconstruir a M2.3a.1 nem reescrever os normalizadores.

**Veredito:** núcleo de orçamento **READY offline com ressalva documentada**; **integridade estrita dos metadados de proveniência ainda não está totalmente READY** até a correção pontual acima. Esta revisão não constitui autorização de produção ou persistência.
