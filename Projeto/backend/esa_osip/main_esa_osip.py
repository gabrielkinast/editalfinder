"""Safe crawler for ESA Open Space Innovation Platform campaigns and channels."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from international_onda_c_common import run_source


SOURCE_KEY = "esa_osip"
LABEL = "ESA OSIP"


CONFIG = {
    "origem_portal": "ESA Open Space Innovation Platform",
    "listing_urls": [
        "https://ideas.esa.int/core/servlet/hype/IMT?templateName=MenuItem&userAction=BrowseCurrentUser",
        "https://www.esa.int/Enabling_Support/Preparing_for_the_Future/Discovery_and_Preparation/The_Open_Space_Innovation_Platform_OSIP",
    ],
    "allowed_domains": ["ideas.esa.int", "esa.int"],
    "url_must_contain_any": ["documentId=", "Open_Space_Innovation_Platform", "ideas.esa.int"],
    "extra_action_markers": ("campaign", "channel", "submit ideas", "call for ideas", "open space innovation"),
    "default_tipo_oportunidade": "space_opportunity",
    "default_tipo_recurso": "apoio_inovacao",
    "programa": "ESA Open Space Innovation Platform",
    "pais": "Internacional",
    "regiao": "europa",
    "max_items": 18,
    "max_links": 75,
}


if __name__ == "__main__":
    run_source(SOURCE_KEY, LABEL, CONFIG)
