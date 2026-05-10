"""Testes sintéticos para official_link_only / is_official_link_only_candidate."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from official_link_only import is_official_link_only_candidate  # noqa: E402


def _base_nato(link: str, **kwargs):
    return {
        "titulo": kwargs.get("titulo", "NATO DIANA challenge call"),
        "descricao": kwargs.get("descricao", "x" * 30),
        "link": link,
        "fonte": "NATO DIANA",
        "programa": kwargs.get("programa", "DIANA"),
        "data_publicacao": kwargs.get("data_publicacao"),
        "fim_inscricao": kwargs.get("fim_inscricao"),
        "extras": {
            "metodo_extracao": kwargs.get("metodo_extracao", "curated_official_public_brief"),
            "orgao_contratante": "NATO DIANA",
            **kwargs.get("extras_extra", {}),
        },
    }


class TestOfficialLinkOnly(unittest.TestCase):
    def test_challenge_official_domain_curated_accepted(self):
        item = _base_nato("https://www.diana.nato.int/challenges/warfighters.html")
        r = is_official_link_only_candidate(item, "nato_diana")
        self.assertTrue(r["accepted"])
        self.assertIn(r["access_reason"], ("html_insuficiente", "cloudflare_or_403"))

    def test_homepage_rejected(self):
        item = _base_nato("https://www.diana.nato.int/")
        r = is_official_link_only_candidate(item, "nato_diana")
        self.assertFalse(r["accepted"])
        self.assertIn("homepage", r["reason"])

    def test_contact_path_rejected(self):
        item = _base_nato("https://www.diana.nato.int/en/contact/")
        item["titulo"] = "Institutional"
        r = is_official_link_only_candidate(item, "nato_diana")
        self.assertFalse(r["accepted"])

    def test_news_generic_rejected(self):
        item = _base_nato("https://www.diana.nato.int/news/press-release/")
        item["titulo"] = "Press release"
        r = is_official_link_only_candidate(item, "nato_diana")
        self.assertFalse(r["accepted"])

    def test_external_non_official_rejected(self):
        item = _base_nato("https://example.com/funding/call-123")
        item["extras"]["metodo_extracao"] = "curated_official_public_brief"
        r = is_official_link_only_candidate(item, "nato_diana")
        self.assertFalse(r["accepted"])

    def test_no_opportunity_slug_rejected(self):
        item = _base_nato("https://www.diana.nato.int/some/deep/page.html")
        item["titulo"] = "Page"
        r = is_official_link_only_candidate(item, "nato_diana")
        self.assertFalse(r["accepted"])

    def test_no_metadata_rejected(self):
        item = _base_nato("https://www.diana.nato.int/challenges/foo")
        item["programa"] = ""
        item["extras"] = {"metodo_extracao": "curated_official_public_brief"}
        r = is_official_link_only_candidate(item, "nato_diana")
        self.assertFalse(r["accepted"])

    def test_http_403_signal_accepted(self):
        item = _base_nato(
            "https://www.diana.nato.int/challenges/open-call",
            descricao="y" * 40,
            programa="P",
            metodo_extracao="live_scrape",
        )
        item["extras"]["http_status_detail"] = 403
        r = is_official_link_only_candidate(item, "nato_diana")
        self.assertTrue(r["accepted"])
        self.assertEqual(r["access_reason"], "cloudflare_or_403")

    def test_iarpa_allowlist(self):
        item = {
            "titulo": "IARPA research BAA",
            "descricao": "x" * 50,
            "link": "https://www.iarpa.gov/research-programs/foo",
            "programa": "IARPA",
            "extras": {"metodo_extracao": "curated_official_public_brief", "codigo_oportunidade": "X1"},
        }
        r = is_official_link_only_candidate(item, "iarpa")
        self.assertTrue(r["accepted"])


if __name__ == "__main__":
    unittest.main()
