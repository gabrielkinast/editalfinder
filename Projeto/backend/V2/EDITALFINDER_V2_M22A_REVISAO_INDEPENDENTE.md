# EditalFinder V2 — revisão independente da M2.2a

**Objeto:** `V2.tar(3).gz` recebido nesta conversa, inspecionado em ambiente isolado.  
**Escopo:** contratos e funções de normalização temporal/geográfica offline, proveniência, auditoria, testes e regressões.  
**Parecer:** **NOT READY para encerramento estrito da revisão dos DTOs da M2.2a**; normalizadores operacionais sem falha crítica reproduzida nos cenários examinados. Recomendam-se duas correções pequenas e dirigidas, sem expandir a milestone. O estado NÃO implica defeito demonstrado de promoção, banco, Legacy ou crawling (que não integram esta etapa).

## Verificação executada

- Extração segura de arquivos comuns do TAR, sem seguir links nem executar scripts do projeto.
- `PYTHONPATH=src:tests PYTHONDONTWRITEBYTECODE=1 python -B -m pytest -q -p no:cacheprovider`: **958 passed in 3.88s**.
- Ambiente independente: Python **3.13.5**, Pydantic **2.13.5**, pytest **9.0.2**. O relatório do autor documenta verificações distintas em Python 3.11.16/Pydantic 2.14.1. Não reivindicar certificação de matriz 3.11–3.14.
- O TAR contém fontes, testes, documentos e SQL, mas **não contém** `pyproject.toml`, `README.md` ou `uv.lock`; Ruff/mypy **não foram reexecutados** nesta revisão. Não há evidência de acesso a serviço externo.

## Achado 1 — DTO temporal aceita offset conhecido sem instante UTC nem diagnóstico (médio; reproduzido)

**Arquivo:** `src/editalfinder_v2/domain/temporal_models.py`, `NormalizedTemporalEvent.consistent_shape()`, linhas 70–115, principalmente 97–105.

O modelo só verifica a correspondência UTC **quando `instant_utc` existe**. Para horário com offset explícito conhecido e conversão viável, aceita a omissão silenciosa do instante.

Reprodução (modelos Pydantic normais, sem `model_construct` ou `model_copy`):

```python
from editalfinder_v2.domain.temporal_models import NormalizedTemporalEvent, TemporalClaim

e = NormalizedTemporalEvent(
    claim=TemporalClaim(role="submission_deadline"),
    local_datetime="2026-05-10T12:30:00+03:00",
    timezone="+03:00",
    precision="minute",
    calendar_interpretation="gregorian",
)
assert e.instant_utc is None
assert e.diagnostics == ()
```

A função normalizadora propriamente dita converte o mesmo horário em `2026-05-10T09:30:00+00:00`, sem diagnóstico; portanto o problema demonstrado é **no contrato público de saída**, não na conversão executada pelo normalizador.

Também foi possível colocar esse DTO incompleto dentro de um `TemporalReport` novo, que recebe digest novo. Isso **não** viola o mecanismo de integridade: reter o digest de um relatório anterior e alterar seu conteúdo gera `ValidationError`, conforme reproduzido. Hash não é prova de autoria/autorização.

**Correção sugerida:** no validador do DTO, se houver timezone explícito conhecido e `local_datetime` aware, recalcular deterministicamente a conversão UTC. Quando representável, exigir `instant_utc` presente, com offset zero e instante correspondente; quando for impossível por overflow nos anos extremos, permitir ausência **somente** com diagnóstico adequado `temporal_timezone_conversion_out_of_range`. Preserve `zone=None` e `-00:00` sem instant, com semântica de horário local não resolvido. Acrescentar regressões para construção normal, `model_validate`, `model_validate_json`, relatórios e limites de ano. Evitar uma regra que inviabilize o comportamento legítimo de overflow.

## Achado 2 — localização totalmente vazia não é diagnosticada (baixo; reproduzido)

**Arquivo:** `src/editalfinder_v2/domain/geography_normalization.py`, linhas 65–84 e 162–184; `geography_models.py`, `GeographyLocationClaim` linhas 28–33.

Um `GeographyLocationClaim(role="elegibilidade")` sem país, UF, região ou município passa como localização normalizada com todos os componentes `None` e `diagnostics=()`. Se o escopo também estiver ausente, o único diagnóstico geral é `geo_scope_missing`: **não** há `geo_location_empty` ou equivalente, apesar de `locations` conter uma entrada.

```python
from semantic_fixtures import build_context
from editalfinder_v2.domain.geography_models import GeographyInput, GeographyLocationClaim
from editalfinder_v2.domain.geography_normalization import normalize_geography

ctx, *_ = build_context()
r = normalize_geography(GeographyInput(
    context=ctx,
    locations=(GeographyLocationClaim(role="elegibilidade"),),
))
assert len(r.locations) == 1
assert r.locations[0].country_code is None
assert not r.locations[0].diagnostics
assert {d.code for d in r.diagnostics} == {"geo_scope_missing"}
```

**Impacto:** não resulta em país inventado nem em promoção, mas deixa uma entrada geográfica sem conteúdo parecer não problemática. Consumidores que contem entradas em `locations` podem presumir existência de localização substantiva. Propor diagnóstico `geo_location_empty` por claim com `claim_index`, preservando a entrada e sem inventar default. Não apagar o claim silenciosamente.

## Aspectos positivos confirmados

- A suíte integral atual funciona fora do ambiente original (**958 testes**).
- Os normalizadores são funções puras no recorte examinado e mantêm promoção desabilitada.
- Evidências são amarradas a candidato, snapshot, unidade, papel semântico e texto, com distinção entre localização da fonte/organização e elegibilidade.
- Datas civis não recebem horário automaticamente; offsets ausentes/desconhecidos não geram UTC; conflitos e retificações permanecem explícitos.
- Reportes com envelope anterior e conteúdo modificado são rejeitados em validação normal.
- Política documenta corretamente limites da verdade do conteúdo: estrutura JSON rotulada pelo adaptador não prova autenticidade do documento original nem a semântica de sua extração.

## Decisão e próximo passo

Realizar **M2.2a.1 (correção dirigida de contratos)** antes de considerar a revisão técnica encerrada. Não é necessário reimplementar normalização, geografia nem M2.1; não iniciar M2.2b até reexecutar regressões e confirmar os dois casos.

**Restrições:** manter contratos de evidências, versões e invariantes anteriores; não acessar Supabase, não alterar migrations/Legacy, não habilitar promoção e não criar commit automático. Entregar antes/depois, `pytest`, Ruff, mypy e relatório final, além de uma revisão adversarial independente se o limite de uso permitir.
