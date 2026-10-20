# IntegrationAudit — metadados explícitos e reprocessamento histórico

## Contrato recebido versus geração local

Esta correção substitui a descrição de compatibilidade histórica de
`EDITALFINDER_V2_M23A1_RESULTADOS.md` quanto à aceitação automática de envelopes
antigos sem a versão de orçamento. Não altera os registros históricos.

Quando `audit` é fornecido como objeto, TODOS estes campos são obrigatórios:

- `schema_version`: 2;
- `report_digest`: SHA-256 do corpo completo sem `audit`;
- `algorithm`: `sha256`;
- `hash_version`: `integration-pydantic-json-utf8-v1`;
- `limits_version`: `m2.3-integration-limits-v1`;
- `output_budget_version`: `m2.3a.1-output-budget-v1`.

Não há defaults nesses campos, inclusive na construção Python e validação JSON.
Um objeto `{report_digest: ...}`, `{}` ou qualquer objeto sem um dos campos
obrigatórios é recusado. Metadados desconhecidos/incompatíveis também são recusados
na rota estrita. Metadados presentes continuam sendo declarações, não assinatura,
autenticidade ou autorização.

Na geração local, `IntegrationReport.verify_outputs` constrói o envelope com TODOS
os valores explícitos. `audit=None` ou a ausência TOTAL de `audit` continuam permitindo
recomputar o corpo e gerar uma NOVA auditoria local. Isso não restaura nem comprova
a política original de um arquivo. Não substituir um envelope recebido por None
para apresentar o resultado como o mesmo registro histórico.

Os bytes dos relatórios atuais completos, seus hashes e as regras de comparação
permanecem os mesmos. A correção altera a aceitação de envelopes incompletos, não
os algoritmos de hash ou a estrutura das evidências.

## Dois procedimentos diferentes

1. Validação estrita de registro recebido:
   `IntegrationReport.model_validate_json(source_json)`.
   Exige todos os metadados, orçamento vigente, recomputação completa e digest
   correspondente. Se faltar uma versão, pare: não adivinhe o valor histórico.

2. Reprocessamento explícito de ENTRADA histórica:
   Preserve os bytes originais em arquivo separado, nunca sobrescrito.
   Extraia somente `input`, valide o contrato atual de entrada e chame `integrate`.
   Registre que o resultado é uma nova avaliação sob a política atual, sem afirmar
   que os outputs ou o envelope históricos foram validados. Preserve o envelope
   original exatamente como recebido, inclusive campos ausentes, nulos ou versões
   antigas. Se a política original não constava do arquivo, ela continua desconhecida.

O exemplo abaixo é um procedimento offline de aplicação, NÃO um novo parser de
transporte ou uma capacidade de persistência do domínio. O código é executado nos
testes de regressão para evitar divergência entre documentação e procedimento.
O recibo é um vínculo de rastreabilidade, não assinatura. Não deve ser confundido
com o envelope IntegrationAudit. Não há geração de horário ou identidade inventada.

```python
import hashlib
import json

from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_budget import OUTPUT_BUDGET_VERSION
from editalfinder_v2.domain.integration_models import IntegrationInput, IntegrationReport
from editalfinder_v2.domain.models import OperationalError


def reprocess_archived_report(
    source_json: str,
) -> tuple[dict[str, object], IntegrationReport | OperationalError]:
    # O chamador já preservou os bytes originais e aplicou limites de transporte.
    # Apenas inspecionamos o envelope de origem; NÃO instanciamos IntegrationAudit.
    source = json.loads(source_json)
    current_input = IntegrationInput.model_validate_json(json.dumps(source["input"]))
    result = integrate(current_input)
    receipt: dict[str, object] = {
        "operation": "reprocess_input_under_current_policy",
        "source_report_sha256": hashlib.sha256(source_json.encode("utf-8")).hexdigest(),
        "source_audit_present": "audit" in source,
        "source_audit": source.get("audit"),
        "original_policy_inferred": False,
        "historical_outputs_verified": False,
        "verification_policy": {
            "integration_version": current_input.integration_version,
            "limits_version": "m2.3-integration-limits-v1",
            "output_budget_version": OUTPUT_BUDGET_VERSION,
        },
        "verification_audit": (
            result.audit.model_dump(mode="json")
            if isinstance(result, IntegrationReport) and result.audit is not None
            else None
        ),
        "operational_error": (
            result.model_dump(mode="json") if isinstance(result, OperationalError) else None
        ),
    }
    return receipt, result
```

Arquive separadamente: (a) fonte original inalterada, (b) recibo de reprocessamento,
(c) novo resultado, inclusive OperationalError. A ausência de políticas na origem
não é reparada; o recibo registra a ausência original e a nova política em lugares
distintos. O digest da fonte vincula os bytes originais, não autentica a origem.
Nenhuma escrita é feita pelo exemplo.

## Limites preservados

O caminho de reprocessamento usa `integrate`, logo preserva a admissão de 64 MiB,
limites anteriores, evidências, isolamento, papéis, recomputação, OperationalError
e `promotable=False`. Exceder o orçamento não gera relatório parcial ou REJECTED.
Entradas de schema incompatível exigem migração futura explícita; este procedimento
não converte schemas nem assume versões ausentes de auditoria.

Reprocessar somente `input` NÃO valida decisões, diagnósticos ou hashes dos outputs
históricos. Se a finalidade for comprovar os outputs antigos, é necessário um
verificador da política histórica, que não foi implementado nesta correção.

`json.loads` e `model_validate_json` já recebem/decodificam dados na memória.
O exemplo pressupõe transporte com limites de bytes/estrutura e parser apropriado
para a origem; não é um endpoint para JSON hostil. O orçamento não é teto de RSS.
Não registrar erros com entradas completas: use `errors(include_input=False)`.

Não há restauração automática, backfill, migração, rede, banco, promoção ou M2.3b.

## M2.3d.1 — envelopes aninhados e versões do corpo auditado

A regra de presença explícita também se aplica a SnapshotAudit, ValidationAudit,
IdentityAudit, NormalizationAudit (M2.2a) e M22BAudit (M2.2b). TODOS os campos
existentes desses DTOs são obrigatórios, incluindo schema_version herdado,
representação do snapshot, identificadores, digests e inventários de evidências,
snapshots e regras. Não foi acrescentado um campo de política fictício aos envelopes:
policy_version/normalization_version continuam nos respectivos corpos auditados.

Quando um corpo com campo audit recebe um envelope não nulo, todas as suas
propriedades existentes terminadas em _version também precisam estar explícitas.
Isso inclui schema_version, policy_version, normalization_version, ruleset_version,
integration_version e country_catalog_version, conforme o tipo concreto; no snapshot,
collector_version já era obrigatório. Não se preenchem versões ausentes para fazer
um digest retido corresponder à representação reconstruída. A regra não muda os
defaults de inputs/claims que não têm um envelope de auditoria próprio.

Geração local sem audit ou com audit=None permanece permitida. Os binders fornecem
explicitamente todas as constantes de seus envelopes, sem novo algoritmo de hash,
versão de política ou versão de schema. Os relatórios completos atuais mantêm os
mesmos bytes, digests e resultados; contratos de construção que dependiam de defaults
em envelopes incompletos passam a falhar com ValidationError, intencionalmente.

O exemplo de reprocessamento acima continua válido para arquivos cujos inputs,
incluindo envelopes de snapshots fornecidos, estão completos. Se o input também
contiver um envelope de snapshot incompleto, a validação de IntegrationInput recusa.
Não há migração automática: preservar os bytes e metadados originais, criar uma cópia
separada dos inputs e tomar uma decisão EXPLÍCITA de remover o envelope de snapshot
dessa cópia antes de solicitar nova avaliação local. O recibo deve registrar essa
separação e não declarar verificado o snapshot/envelope histórico. Não regravar o
arquivo original, não atribuir a ele versões atuais, nem transformar uma rejeição
histórica em aprovação por uma tentativa silenciosa com audit=None.

Ausência/None de um envelope, inclusive aninhado, conserva o significado anterior
de avaliação local. Não é prova de completude histórica; chamadores não podem chamar
uma operação desse tipo de verificação de um envelope que não foi retido. Nenhum
DTO, digest ou reprocessamento confere autoridade de promoção ou merge.
