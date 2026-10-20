# EditalFinder V2 — Revisão independente da M2.3d

**Resultado:** `NOT READY`, confirmado para os dois bloqueadores documentados (M23D-F01 e M23D-F03). A auditoria permanece estritamente offline; não se atribui exploração remota, bypass de autorização ou promoção automática.

## Material e ambiente

- Pacote analisado: `V2.tar(20261019-002226).gz` (arquivos-fonte e testes extraídos em diretório isolado; nenhum arquivo do usuário modificado).
- Ambiente de revisão adicional: Python do container e Pydantic 2.13.5, pytest 9.0.2. Não substitui a execução relatada em Python 3.11.16 / Pydantic 2.14.1.
- Comando: `PYTHONPATH=src:tests python -B -m pytest -q -p no:cacheprovider`.
- Resultado independente: **1810 passed in 22.62s**.
- Ruff, mypy e inspeção Git não foram repetidos neste ambiente: não estão disponíveis como executáveis instalados na revisão; os resultados verdes correspondem aos gates reportados pelo Hermes.

## F01 — Overflow UTC não encapsulado — confirmado

Arquivos e funções: `src/editalfinder_v2/domain/models.py`, `RawSnapshot.utc_timestamp()` (linhas 76–79) e `ReviewAttestation.utc_review()` (linhas 260–263).

Reprodução mínima:

```python
from uuid import UUID
from editalfinder_v2.domain.models import RawSnapshot

RawSnapshot(
    id=UUID(int=1), source_id=UUID(int=3), source_code="fapergs",
    execution_id=UUID(int=2),
    collected_at="0001-01-01T00:00:00+23:59",
    collector_version="audit-local", url="https://example.org/",
    payload_json="{}",
)
```

Resultado observado independentemente: `OverflowError: date value out of range`, não `pydantic.ValidationError`. O timestamp `9999-12-31T23:59:59-23:59` reproduz o mesmo defeito. Valores de controle adjacentes (`0001-01-02T00:00:00+23:59` e `9999-12-30T23:59:59-23:59`) são aceitos e convertidos para UTC corretamente.

**Correção proposta:** tratar explicitamente `OverflowError` da conversão `astimezone(UTC)` nos dois validators e transformá-lo em `ValueError` estável, para a validação Pydantic emitir `ValidationError`. Não inventar timestamp alternativo, não permitir `NaiveDatetime` e não afrouxar a validação de offset. Cobrir construtores Python, `model_validate`, `model_validate_json` e aninhamento em entradas do pipeline.

## F03 — Restauração silenciosa de metadados aninhados — confirmado

Em `models.py` (`SnapshotAudit`, `ValidationAudit`), `identity_models.py` (`IdentityAudit`), `semantic_common.py` (`NormalizationAudit`) e `m22b_common.py` (`M22BAudit`), vários metadados têm valores padrão. A auditoria externa `IntegrationAudit` já exige metadados explícitos, mas os envelopes internos continuam preenchendo omissões recebidas.

Reprodução independente com o cenário congelado `M23C-I-005`:

```python
import json
from m23c_fixtures import build, case_by_id
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegrationReport

report = integrate(build(case_by_id("M23C-I-005")))
wire = json.loads(report.model_dump_json())
wire["identity_results"][0]["audit"].pop("hash_version")
restored = IntegrationReport.model_validate_json(json.dumps(wire))
assert restored == report  # passou indevidamente para verificação histórica estrita
```

Resultados: envelope aceito; `hash_version` reintroduzido pelo default (`identity-pydantic-json-utf8-v1`); digest superior retido e idêntico. Repeti omissões de `algorithm` em auditoria de snapshot, `limits_version` em auditoria financeira e `hash_version` em auditoria M1; todas foram aceitas com digest superior inalterado.

**Natureza do defeito:** não há quebra da função SHA-256, mas sim perda de fidelidade dos metadados originalmente recebidos em wire. O hash superior é recalculado sobre a representação canônica após a restauração dos defaults. Para verificação histórica, presença explícita deve ser comprovável.

**Correção proposta:** todos os metadados obrigatórios de um envelope de auditoria **recebido** devem estar presentes. O projeto pode (a) tornar os campos dos modelos de auditoria efetivamente obrigatórios e passar as constantes explicitamente na geração local, ou (b) adicionar validação prévia de presença para envelopes recebidos em fronteiras de verificação, inclusive aninhados. Justificar a escolha frente ao contrato de reprocessamento. Proibir preenchimento silencioso de versões antigas e manter `audit=None` como caminho distinto de **nova avaliação**, não restauração histórica. Cobrir `schema_version` herdado, versões de hash/política/limites, digest e todos os tipos de audit.

## Achados não bloqueantes

- **F02, oráculo M2.3c:** projeção E2E não verifica `normalized_name` nem `classification` de diagnósticos quando os códigos são mantidos. Reforçar expectativas literais e testes de mutação numa correção posterior ou junto da correção direcionada, sem mudar os resultados congelados sem justificativa.
- **F04, divergência de URL:** `safety.valid_url()` da M1 aceita `https://example.org/path<bad>` e `http://0x7f000001/`; o normalizador M2.1 rejeita. É inconsistência sintática, não prova de SSRF. Alinhar políticas com testes, sem adicionar requisições HTTP, numa correção separada.

## Condições de aprovação sugeridas para M2.3d.1

1. Reproduzir F01 e F03 como testes que falham na versão atual; depois executar RED → GREEN.
2. Não ocorrer `OverflowError` não estruturado na conversão dos dois timestamps extremos, incluindo entrada aninhada JSON.
3. Metadados omitidos de qualquer auditoria recebida serem rejeitados por `ValidationError`, mesmo com envelope superior retido.
4. Geração local de auditorias e reprocessamento histórico por nova avaliação continuarem funcionando, sem confusão com verificação do original.
5. Manter **1810 testes** anteriores e adicionar regressões específicas, mantendo o oráculo congelado.
6. Ruff lint/format **globais** em src/tests, mypy, git diff --check e inspeção de untracked passarem.
7. Nenhuma alteração em Legacy, SQL, Supabase, crawling, persistência, merging ou promoção; nenhuma alteração staged ou commit.
8. Revisão adversarial read-only dos dois bloqueadores após a correção; READY apenas para escopo offline.

**Próximo passo:** implementar M2.3d.1 de hardening de contratos, depois executar auditoria direcionada de encerramento da M2.3d. A M3 permanece bloqueada até aprovação.
