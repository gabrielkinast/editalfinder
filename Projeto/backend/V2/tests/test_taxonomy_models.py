from editalfinder_v2.domain.policies import AREAS, OPPORTUNITY_TYPES, RESOURCE_TYPES


def test_approved_exact_catalog_only():
    from editalfinder_v2.domain.taxonomy_models import exact_dimensions

    catalogs = {
        "opportunity_type": OPPORTUNITY_TYPES,
        "resource_type": RESOURCE_TYPES,
        "area": AREAS,
    }
    assert tuple(map(len, catalogs.values())) == (8, 9, 15)
    for role, codes in catalogs.items():
        for code in codes:
            assert exact_dimensions(code, role) == (role,)
    assert exact_dimensions("bolsa", "unspecified") == ("opportunity_type", "resource_type")
    for text in ("Bolsa", " edital", "edital ", "notícia sobre edital", "Ciências da saúde"):
        assert exact_dimensions(text, "unspecified") == ()
    assert exact_dimensions("edital", "area") == ()
