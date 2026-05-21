import re
import ssl
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
ctx = ssl.create_default_context()


def get(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=45, context=ctx) as r:
        return r.read().decode("utf-8", "replace")


def scan(name: str, js: str) -> None:
    print("===", name, "len", len(js))
    for pat in (r"https?://[a-zA-Z0-9./_?=&-]+", r"/[a-zA-Z0-9./_?=&-]+edital[a-zA-Z0-9./_?=&-]*"):
        hits = sorted(set(re.findall(pat, js)))
        sub = [x for x in hits if any(k in x.lower() for k in ("edital", "api", "ajax", "json", "list", "abertos"))]
        print(pat, "interesting", len(sub))
        for x in sub[:40]:
            print(" ", x[:120])


def main() -> None:
    base = "https://portal.editais.legalleconcursos.com.br"
    for path in (
        "/public/template10/arquivos/js/CONFIG.js",
        "/public/template10/arquivos/js/editais.js",
        "/public/template10/arquivos/js/script.js",
    ):
        try:
            scan(path, get(base + path))
        except Exception as e:
            print("ERR", path, e)


if __name__ == "__main__":
    main()
