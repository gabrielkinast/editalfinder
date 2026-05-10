from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    # Fonte oficial: FAPERGS (RS). Pasta do projeto mantém o id histórico `faperg` para o pipeline.
    config = {
        "source_label": "FAPERGS",
        "listing_urls": [
            "https://fapergs.rs.gov.br/chamadas-e-editais",
        ],
        "allowed_domains": ["fapergs.rs.gov.br"],
        "keywords": [
            "edital",
            "chamada",
            "fomento",
            "programa",
            "pesquisa",
            "bolsa",
            "processo seletivo",
            "inscrição",
            "inscricoes",
            "inscrições",
            "auxílio",
            "auxilio",
            "recem-doutor",
            "recém-doutor",
            "centelha",
            "seleção",
            "selecao",
        ],
        "avoid_keywords": [
            "fale conosco",
            "mapa do site",
            "acessibilidade",
            "quem somos",
            "intranet",
            "privacidade",
            "denúncia",
            "galeria de dirigentes",
            "identidade visual",
        ],
        "link_url_exclude_substrings": [
            "/noticias",
            "/quem-somos",
            "/fale-conosco",
            "/transparencia-ativa",
            "/legislacao-",
            "/resolucoes",
            "/normas-comites",
            "/valores-de-bolsas",
            "/valores-de-diarias",
            "/prestacao-de-contas",
            "/resultados-e-indicadores",
            "/links-uteis",
            "/denuncia",
            "/selecao-2025",
            "/processo-seletivo-edital-n-01-2025",
            "resultado-preliminar",
            "resultado-final",
            "publicada-a-convocacao",
            "convocacao-dos-selecionados",
            "/avisos",
        ],
        "link_path_min_depth": 1,
        "max_items": 45,
        "max_links_per_page": 200,
        "http_timeout": 20,
        "require_opportunity_signals": True,
        "enrich_meta_tags": True,
        "program_hint": "FAPERGS",
        "regiao": "Sul",
        "pais": "Brasil",
        "idioma_original": "pt",
        "tipo_oportunidade": "",
        "orgao_responsavel": "FAPERGS",
        "instituicao": "FAPERGS — Fundação de Amparo à Pesquisa do Estado do RS",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "faperg", items)
    print(f"FAPERGS (faperg): {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
