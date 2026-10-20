"""Baseline seed codes, not a classifier or source-readiness authorization.

Source: docs/v2/MIGRATION_000002_VALIDATION.md and migration 000002.
Taxonomies remain strings, not rigid domain enums; a future catalog port may
supply updated active codes after versioning/governance is approved.
"""

from typing import Final

CATALOG_VERSION = "seeds-000002"
VALIDATION_LIMITS_VERSION: Final = "m1.1a-limits-1"
MAX_ASSERTIONS = 1200
MAX_CANDIDATE_EVIDENCE = 2400
MAX_FIELD_EVIDENCE = 64
SOURCES = frozenset(
    {
        "fapergs",
        "fapesp",
        "cnpq",
        "finep",
        "bndes",
        "grants_gov",
        "nsf",
        "arpa_e",
        "horizon_europe",
        "erc",
    }
)
OPPORTUNITY_TYPES = frozenset(
    {
        "chamada_publica",
        "edital",
        "bolsa",
        "premio",
        "concurso",
        "credenciamento",
        "encomenda_tecnologica",
        "outra",
    }
)
RESOURCE_TYPES = frozenset(
    {
        "financiamento_nao_reembolsavel",
        "financiamento_reembolsavel",
        "bolsa",
        "premio_financeiro",
        "credito",
        "apoio_nao_financeiro",
        "contratacao",
        "misto",
        "nao_identificado",
    }
)
AREAS = frozenset(
    {
        "multidisciplinar",
        "ciencias_exatas_e_da_terra",
        "engenharias",
        "ciencias_biologicas",
        "ciencias_da_saude",
        "ciencias_agrarias",
        "ciencias_sociais_aplicadas",
        "ciencias_humanas",
        "linguistica_letras_e_artes",
        "tecnologia_e_inovacao",
        "energia",
        "meio_ambiente",
        "defesa_e_aeroespacial",
        "materiais",
        "computacao_e_dados",
    }
)
DOMAINS = {
    "content_kind": frozenset(
        {
            "instrument",
            "news",
            "aggregator",
            "result",
            "menu",
            "institutional",
            "auxiliary",
        }
    ),
    "opportunity_type": OPPORTUNITY_TYPES,
    "resource_type": RESOURCE_TYPES,
    "area": AREAS,
    "geographic_scope": frozenset({"brasil", "internacional", "misto", "nao_identificado"}),
    "no_deadline_reason": frozenset(
        {
            "nao_informado",
            "a_definir",
            "fluxo_continuo",
            "nao_aplicavel",
        }
    ),
}
DATE_FIELDS = frozenset({"submission_deadline", "publication_date", "opening_date", "result_date"})
BOOL_FIELDS = frozenset({"actionable", "specific_instrument"})
TEXT_FIELDS = frozenset({"title", "official_url", "reported_status"})
SUPPORTED_FIELDS = frozenset(DOMAINS) | DATE_FIELDS | BOOL_FIELDS | TEXT_FIELDS
