"""Safe crawler for UKRI funding opportunities."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from international_onda_c_common import run_source


SOURCE_KEY = "ukri_funding"
LABEL = "UKRI Funding"


CONFIG = {
    "origem_portal": "UKRI Funding Finder",
    "listing_urls": [
        "https://www.ukri.org/opportunity/?lang=en-gb",
        "https://www.ukri.org/opportunity/?sort_by=closing_date",
    ],
    "allowed_domains": ["ukri.org"],
    "url_must_contain_any": ["/opportunity/"],
    "url_exclude_contains": ["filter_order=", "?lang=", "/opportunity/?", "/opportunity/feed", "/opportunity/page/"],
    "url_exclude_exact_paths": ["/opportunity"],
    "extra_action_markers": ("research grant", "fellowship", "funding opportunity"),
    "default_tipo_oportunidade": "research_grant",
    "default_tipo_recurso": "grant",
    "programa": "UKRI funding opportunities",
    "pais": "Reino Unido",
    "regiao": "europa",
    "max_items": 20,
    "max_links": 55,
}


if __name__ == "__main__":
    run_source(SOURCE_KEY, LABEL, CONFIG)
