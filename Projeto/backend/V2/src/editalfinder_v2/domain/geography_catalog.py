"""Closed offline code sets; never loaded from the filesystem at runtime.

ISO alpha-2: iso-codes 4.20.1 (Debian 4.20.1-1), 249 assigned entries.
Upstream https://salsa.debian.org/iso-codes-team/iso-codes
Development input: /usr/share/iso-codes/json/iso_3166-1.json
SHA256 f01b812b57fba9f31ff621bf33e7c7570a01964dbeb5be2167e94decf538c89f
Only factual alpha-2 identifiers are reproduced, not translated names.
UF/region membership follows migration 000001, constraints lines 311–330.
Updates require explicit catalog/policy versioning, not network lookups.
"""

from types import MappingProxyType
from typing import Final

COUNTRY_CODES: Final = frozenset(
    "AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN "
    "BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ "
    "DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL "
    "GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM "
    "JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME "
    "MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP "
    "NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD "
    "SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO "
    "TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW".split()
)
REGION_STATES: Final = MappingProxyType(
    {
        "norte": frozenset("AC AP AM PA RO RR TO".split()),
        "nordeste": frozenset("AL BA CE MA PB PE PI RN SE".split()),
        "centro_oeste": frozenset("DF GO MT MS".split()),
        "sudeste": frozenset("ES MG RJ SP".split()),
        "sul": frozenset("PR RS SC".split()),
    }
)
STATE_CODES: Final = frozenset(state for states in REGION_STATES.values() for state in states)
