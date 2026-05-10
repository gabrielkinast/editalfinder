"""Safe crawler for Innovate UK funding competitions."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from international_onda_c_common import run_source


SOURCE_KEY = "innovate_uk"
LABEL = "Innovate UK"


CONFIG = {
    "origem_portal": "Innovate UK / UKRI Funding Finder",
    "listing_urls": [
        "https://www.ukri.org/opportunity/?lang=en-gb",
        "https://www.gov.uk/apply-funding-innovation",
    ],
    "allowed_domains": ["ukri.org", "gov.uk", "apply-for-innovation-funding.service.gov.uk"],
    "url_must_contain_any": ["/opportunity/", "apply-for-innovation-funding.service.gov.uk"],
    "url_exclude_contains": ["filter_order=", "?lang=", "/opportunity/?"],
    "url_exclude_exact_paths": ["/opportunity", "/competition/search"],
    "detail_text_must_contain_any": ["Innovate UK"],
    "extra_action_markers": ("innovate uk", "competition", "business innovation"),
    "default_tipo_oportunidade": "funding_opportunity",
    "default_tipo_recurso": "grant",
    "programa": "Innovate UK innovation funding",
    "pais": "Reino Unido",
    "regiao": "europa",
    "max_items": 16,
    "max_links": 45,
}


if __name__ == "__main__":
    run_source(SOURCE_KEY, LABEL, CONFIG)
