import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Optional, Set, Tuple

from utils_apex import get_soup, normalize_text, extract_date, is_deadline_valid
from models_apex import EditalApex

BASE_URL = "https://apexbrasil.com.br"

# Páginas-semente com HTML estático e links para programas de exportação / transparência.
# (URLs antigas de /licitacoes-e-contratos/editais.html retornam 404 no /content/ atual.)
SEED_URLS: List[str] = [
    "https://apexbrasil.com.br/content/apexbrasil/br/pt/nossos-servicos/internacionalizacao-de-empresas.html",
    "https://apexbrasil.com.br/br/pt/nossos-servicos/internacionalizacao-de-empresas.html",
    "https://apexbrasil.com.br/exporta-mais-brasil",
    "https://apexbrasil.com.br/content/apexbrasil/br/pt/transparencia-e-prestacao-de-contas.html",
]

# Fragmentos de URL a não seguir (menu, eventos genéricos, notícia, institucional, externos de agenda).
URL_DENY_FRAGMENTS: Tuple[str, ...] = (
    "/eventos",
    "/noticias",
    "/noticia/",
    "/solucoes.html",
    "/institucional",
    "/fale-conosco",
    "/contato",
    "/acesso-a-informacao/transparencia",
    "facebook.com",
    "twitter.com",
    "linkedin.com",
    "instagram.com",
    "whatsapp",
    "brasilexportacao.com.br",
    "youtube.com",
    "/politica-de-cookies",
    "/termos-e-condicoes",
    "/mapa-do-site",
    "/busca",
    "/search",
    "/conteudo/noticias/",
)

# Títulos de navegação / página vazia (nunca persistir).
TITLE_DENY_EXACT: Set[str] = {
    "menu",
    "home",
    "início",
    "inicio",
    "buscar",
    "login",
    "entrar",
    "saiba mais",
    "aceitar cookies",
    "aceite os cookies",
    "calendário de eventos",
    "calendario de eventos",
    "eventos",
    "nossos serviços",
    "nossos servicos",
    "ver todos",
    "voltar",
    "acesse aqui",
}


def _path_parts(url: str) -> List[str]:
    try:
        return [p for p in urlparse(url).path.strip("/").split("/") if p]
    except Exception:
        return []


def _title_is_nav_noise(t: str) -> bool:
    s = normalize_text(t).lower()
    if not s or len(s) < 4:
        return True
    if s in TITLE_DENY_EXACT:
        return True
    if len(s) <= 12 and s in ("eventos", "notícias", "noticias", "serviços", "servicos"):
        return True
    return False


def _apex_host_ok(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    if host.startswith("www."):
        host = host[4:]
    return host == "apexbrasil.com.br" or host.endswith(".apexbrasil.com.br")


def _url_is_blocked(url: str) -> bool:
    low = url.lower()
    if any(x in low for x in URL_DENY_FRAGMENTS):
        return True
    if not _apex_host_ok(url):
        return True
    return False


def _link_signals_opportunity(url: str, title: str) -> bool:
    """Exige sinal forte de oportunidade na URL ou no texto do link (não basta 'evento' solto)."""
    hay = f"{url.lower()} {normalize_text(title).lower()}"
    strong_markers = (
        "edital",
        "chamada",
        "chamada-publica",
        "licit",
        "pregao",
        "pregão",
        "contrato",
        "selecao",
        "seleção",
        "proposta",
        "inscricao",
        "inscrição",
        "programa",
        "internacionaliz",
        "exportacao",
        "exportação",
        "exporta-mais",
        "exporta mais",
        "missao-negocios",
        "missão-negócios",
        "rodada",
        "credenciamento",
        "cadastro",
        "oportunidade",
        "jornada-export",
        "elas-export",
        "qualifica",
        "capacitacao",
        "capacitação",
    )
    if any(m in hay for m in strong_markers):
        return True
    # PDF só no domínio Apex com nome sugestivo
    if url.lower().endswith(".pdf") and _apex_host_ok(url):
        return any(m in hay for m in ("edital", "chamada", "licit", "pregao", "pregão", "contrato", "selecao"))
    return False


def _link_path_min_ok(url: str) -> bool:
    """Evita páginas rasas de menu; PDFs e paths /content/.../pt/... passam com profundidade suficiente."""
    low = url.lower()
    if low.endswith(".pdf"):
        return True
    parts = _path_parts(url)
    if len(parts) >= 5:
        return True
    # Páginas de licitações podem ser um pouco menos profundas se o slug for explícito
    if any(x in low for x in ("edital", "chamada", "licit", "pregao", "contrato", "programa")):
        return len(parts) >= 3
    return False


class ApexScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalApex]:
        all_editais: List[EditalApex] = []
        seen_links: Set[str] = set()

        for url in SEED_URLS:
            print(f"Iniciando extração Apex Brasil em: {url}")
            soup = get_soup(url)
            if not soup:
                print(f"[APEX] Sem resposta HTML: {url}")
                continue

            main_content = soup.select_one(".content") or soup.select_one("main") or soup
            links = main_content.select("a[href]")

            for a in links:
                href = a.get("href")
                titulo_link = normalize_text(a.get_text())
                if not href:
                    continue

                if not href.startswith("http"):
                    href = urljoin(self.base_url, href)

                full_url = href.split("#", 1)[0].strip()
                if full_url in seen_links:
                    continue
                if _url_is_blocked(full_url):
                    continue
                if not _link_path_min_ok(full_url):
                    continue
                if _title_is_nav_noise(titulo_link):
                    continue
                if not _link_signals_opportunity(full_url, titulo_link):
                    continue

                seen_links.add(full_url)
                print(f"Verificando potencial Apex Brasil: {titulo_link[:70]}...")
                edital = self.process_detail_page(full_url, titulo_link)
                if edital:
                    if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                        continue
                    if _title_is_nav_noise(edital.titulo):
                        continue
                    all_editais.append(edital)

        # Dedupe final por link
        by_link: dict = {}
        for e in all_editais:
            by_link[e.link] = e
        return list(by_link.values())

    def process_detail_page(self, url: str, titulo: str) -> Optional[EditalApex]:
        if _url_is_blocked(url):
            return None

        if url.lower().endswith(".pdf") and _apex_host_ok(url):
            base_titulo = titulo if len(titulo) > 10 else f"Documento: {url.split('/')[-1]}"
            return EditalApex(
                titulo=base_titulo,
                link=url,
                descricao=base_titulo,
                situacao="Aberto",
                extras={
                    "anexos": [{"nome": "Edital PDF", "url": url}],
                    "fonte_original": "Apex Brasil",
                    "metodo_extracao": "apex_pdf_direto",
                },
            )

        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one(".content") or soup.select_one("article") or soup
        text = content.get_text()

        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            titulo = normalize_text(h1.get_text())
        if _title_is_nav_noise(titulo):
            return None

        low_url = url.lower()
        if "/eventos" in low_url and "inscri" not in text.lower() and "chamada" not in text.lower():
            return None

        # Relevância no corpo: exige pelo menos um marcador forte (não basta 'exportação' genérica em landing).
        corp = (titulo + " " + text).lower()
        strong_body = (
            "edital",
            "chamada",
            "chamada pública",
            "licitação",
            "licitacao",
            "pregão",
            "pregao",
            "seleção",
            "selecao",
            "inscrição",
            "inscricoes",
            "inscrições",
            "propostas",
            "programa",
            "fomento",
            "submissão",
            "submissao",
            "contrato",
            "credenciamento",
            "internacionalização",
            "internacionalizacao",
            "exporta mais",
            "exportação",
            "exportacao",
            "jornada export",
            "elas export",
            "qualifica",
            "capacitação",
            "capacitacao",
            "missão de negócios",
            "missao de negocios",
            "rodada de negócios",
            "rodada de negocios",
        )
        if not any(k in corp for k in strong_body):
            return None

        print(f"Encontrado edital/programa relevante Apex Brasil: {url}")

        paragraphs = content.select("p")
        descricao = ""
        for p in paragraphs[:8]:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 35:
                descricao += p_text + " "

        data_pub = extract_date(text)

        prazo = None
        prazo_patterns = [
            r"(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega)\s*:?\s*(\d{2}/\d{2}/\d{4})",
            r"(\d{2}/\d{2}/\d{4})",
        ]
        for pattern in prazo_patterns:
            matches = re.findall(pattern, text, re.I)
            for m in matches:
                extracted = extract_date(m)
                if extracted:
                    if not prazo or extracted > prazo:
                        prazo = extracted

        anexos = []
        for la in content.select("a[href]"):
            a_href = la.get("href")
            a_text = normalize_text(la.get_text())
            if not a_href:
                continue
            low_h = a_href.lower()
            if low_h.endswith(".pdf") or "download" in low_h:
                if not a_href.startswith("http"):
                    a_href = urljoin(url, a_href)
                if _apex_host_ok(a_href):
                    anexos.append({"nome": a_text or "Documento", "url": a_href})

        return EditalApex(
            titulo=titulo,
            link=url,
            descricao=descricao.strip() or titulo,
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": "Apex Brasil",
                "metodo_extracao": "apex_listing_detail",
                "url_detalhe": url,
            },
        )
