"""Safe crawler for EIT calls and opportunities."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from international_onda_c_common import run_source


SOURCE_KEY = "eit"
LABEL = "EIT"


CONFIG = {
    "origem_portal": "European Institute of Innovation and Technology",
    "listing_urls": [
        "https://www.eit.europa.eu/our-activities/opportunities",
        "https://www.eit.europa.eu/opportunities",
        "https://www.eit.europa.eu/work-with-us/procurement/calls",
    ],
    "allowed_domains": ["eit.europa.eu"],
    "url_must_contain_any": ["/opportunities", "/calls", "/call", "/procurement"],
    "url_exclude_exact_paths": ["/opportunities", "/our-activities/opportunities"],
    "extra_action_markers": ("eit", "kic", "knowledge and innovation communities"),
    "default_tipo_oportunidade": "innovation_programme",
    "default_tipo_recurso": "apoio_inovacao",
    "programa": "EIT opportunities",
    "pais": "Uniao Europeia",
    "regiao": "europa",
    "max_items": 16,
    "max_links": 60,
}


if __name__ == "__main__":
    run_source(SOURCE_KEY, LABEL, CONFIG)
