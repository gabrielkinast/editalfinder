import importlib.util, pathlib, sys

# load module from filename since it contains accented characters
spec = importlib.util.spec_from_file_location(
    "extrair", pathlib.Path(__file__).parent / "extrair_informações-fapergs.py"
)
extrair = importlib.util.module_from_spec(spec)
loader = spec.loader
assert loader is not None
loader.exec_module(extrair)  # type: ignore

scr = extrair.FapergsScraper()
# hit main page first to ensure any cookies/session data
scr.get_html("https://fapergs.rs.gov.br/abertos")

url = "https://fapergs.rs.gov.br/_service/conteudo/pagedlistfilho?id=2042&templatename=pagina.listapagina.padrao"
headers = {"Referer": "https://fapergs.rs.gov.br/abertos"}
params = {"currentPage": 1, "pageSize": 20}

try:
    r = scr.session.get(url, timeout=20, headers=headers, params=params)
    print('status', r.status_code)
    print(r.text[:2000])
except Exception as e:
    print('error', e)
