"""Safe crawler for ESA tender/procurement — apenas URLs públicas (sem SSO/login)."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from international_onda_c_common import run_source


SOURCE_KEY = "esa_star"
LABEL = "ESA STAR"


CONFIG = {
    "origem_portal": "ESA esa-star Publication",
    "listing_urls": [
        "https://www.esa.int/About_Us/Business_with_ESA/How_to_do/Open_Invitations_to_Tender",
        "https://www.esa.int/About_Us/Business_with_ESA/How_to_do/Intended_Invitations_To_Tender",
    ],
    # Apenas hosts públicos; nunca coletar esastar-publication-ext.sso.esa.int como oportunidade.
    "allowed_domains": ["esa.int", "procurement.esa.int", "esamultimedia.esa.int"],
    "listing_text_must_contain_any": ["Tender", "esa-star", "Invitation", "ITT", "procurement"],
    "url_must_contain_any": [
        "Tender",
        "tender",
        "esa-star",
        "ESATenderActions",
        "invitation",
        "itt",
        "procurement",
    ],
    "url_exclude_contains": [
        "sso.esa.int",
        "esastar-publication-ext",
        "/login",
        "/signin",
    ],
    "extra_action_markers": ("esa-star", "invitation to tender", "itt", "tender", "procurement", "bid"),
    "default_tipo_oportunidade": "procurement",
    "default_tipo_recurso": "oportunidade_fornecedor",
    "programa": "ESA tender opportunities",
    "pais": "Internacional",
    "regiao": "europa",
    "max_items": 12,
    "max_links": 40,
    # Sem fallback para portal SSO: se não houver ITT público listado, output vazio (Onda Recovery A).
    "fallback_items": [],
    "allow_empty": True,
}


if __name__ == "__main__":
    run_source(SOURCE_KEY, LABEL, CONFIG)
