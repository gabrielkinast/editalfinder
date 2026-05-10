"""Safe crawler for Eurostars calls through the official Eureka Network site."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from international_onda_c_common import run_source


SOURCE_KEY = "eurostars"
LABEL = "Eurostars"


CONFIG = {
    "origem_portal": "Eurostars / Eureka Network",
    "listing_urls": [
        "https://www.eurekanetwork.org/programmes/eurostars/",
        "https://www.eurekanetwork.org/programmes-and-calls/?programme=eurostars&status=open",
        "https://www.eurekanetwork.org/programmes-and-calls/?status=upcoming",
    ],
    "allowed_domains": ["eurekanetwork.org"],
    "listing_text_must_contain_any": ["Eurostars", "call", "deadline"],
    "url_must_contain_any": ["/programmes-and-calls/eurostars/"],
    "url_exclude_contains": ["/programme-resources/", "status=closed", "paged=1", "/programmes/?"],
    "extra_action_markers": ("eurostars", "sme", "collaborative r&d"),
    "default_tipo_oportunidade": "call_for_proposals",
    "default_tipo_recurso": "grant",
    "programa": "Eurostars",
    "pais": "Internacional",
    "regiao": "europa",
    "max_items": 12,
    "max_links": 50,
}


if __name__ == "__main__":
    run_source(SOURCE_KEY, LABEL, CONFIG)
