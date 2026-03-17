import re
from datetime import datetime
from urllib.parse import urljoin
from utils_embrapii import get_soup
from models_embrapii import Chamada

BASE_URL = "https://embrapii.org.br"
URL = "https://embrapii.org.br/transparencia/#chamadas"

ANO_ALVO = "2026"

def extrair_ano(titulo):
    match = re.search(r"/(\d{4})", titulo)
    return match.group(1) if match else None

def extrair_detalhes_chamada(url):
    """Extrai data de abertura e deadline da página do edital."""
    try:
        soup = get_soup(url)
        data_publicacao = "Não informada"
        deadline = "Não informada"

        # Procura por tabelas de prazos
        tabelas = soup.find_all("table")
        for tabela in tabelas:
            rows = tabela.find_all("tr")
            for row in rows:
                cols = row.find_all(["td", "th"])
                if len(cols) >= 2:
                    texto_atividade = cols[0].get_text(strip=True).lower()
                    data_valor = cols[1].get_text(strip=True)

                    if "abertura" in texto_atividade:
                        data_publicacao = data_valor
                    elif "submissão" in texto_atividade or "prazo limite" in texto_atividade:
                        deadline = data_valor

        return data_publicacao, deadline
    except Exception as e:
        print(f"Erro ao extrair detalhes de {url}: {e}")
        return "Não informada", "Não informada"

def coletar_chamadas():
    soup = get_soup(URL)

    chamadas = []
    links = soup.find_all("a")

    for a in links:
        titulo = a.get_text(strip=True)

        if "Chamada Pública" not in titulo:
            continue

        ano = extrair_ano(titulo)

        if ano != ANO_ALVO:
            continue

        link = urljoin(BASE_URL, a.get("href", ""))
        print(f"Extraindo detalhes de: {titulo}")
        
        data_pub, deadline_str = extrair_detalhes_chamada(link)

        # Filtragem por deadline (apenas se a data for válida)
        hoje = datetime.now().date()
        try:
            deadline_dt = datetime.strptime(deadline_str, "%d/%m/%Y").date()
            if deadline_dt < hoje:
                print(f"Edital descartado: deadline {deadline_str} já passou.")
                continue
        except ValueError:
            # Se não houver data válida ou for "A definir*", mantemos o edital por precaução
            pass

        chamadas.append(
            Chamada(
                titulo=titulo,
                link=link,
                ano=ano,
                data_publicacao=data_pub,
                deadline=deadline_str
            )
        )

    return chamadas
