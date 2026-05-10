import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "CORE"))

from content_routing import destination_table_for_item


def test_news_routes_to_noticia():
    assert (
        destination_table_for_item(
            {
                "titulo": "Defense spokesperson comments on meeting",
                "descricao": "Press release published today.",
                "link": "https://example.gov/news/1",
                "extras": {},
            }
        )
        == "noticia"
    )


def test_research_routes_to_pesquisa():
    assert (
        destination_table_for_item(
            {
                "titulo": "Research paper on plasma physics",
                "descricao": "Published in journal. DOI: 10.123/test",
                "link": "https://example.gov/publications/paper",
                "extras": {},
            }
        )
        == "pesquisa"
    )


def test_research_grant_routes_to_edital():
    assert (
        destination_table_for_item(
            {
                "titulo": "The Research Fund For International Scientists",
                "tipo_oportunidade": "grant",
                "tipo_recurso": "Grant para pesquisa competitiva",
                "link": "https://example.gov/funding/program",
                "extras": {},
            }
        )
        == "edital"
    )


def test_opportunity_routes_to_edital():
    assert (
        destination_table_for_item(
            {
                "titulo": "Edital de chamada publica 01/2026",
                "descricao": "Inscricoes abertas e prazo de submissao definido.",
                "link": "https://example.gov/editais/1",
                "extras": {},
            }
        )
        == "edital"
    )


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
