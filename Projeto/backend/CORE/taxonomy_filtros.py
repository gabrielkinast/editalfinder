"""
Classificação central (fase 1) para filtros do EditalFinder.
Usa evidência textual (título, descrição, programa, tipo_recurso, extras).
Não inventa rótulos sem match mínimo — confiança baixa e listas vazias quando aplicável.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, Sequence, Tuple

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from keyword_taxonomy import classify_thematic_tags, _normalize

# (rótulo_canônico, padrões normalizados como substring)
AREA_NEGOCIO: List[Tuple[str, Tuple[str, ...]]] = [
    ("Agro", ("agro", "agronegocio", "agricultura", "pecuaria", "rural")),
    ("Bioeconomia", ("bioeconomia", "biorefinaria", "biomassa")),
    ("Biotecnologia", ("biotecnologia", "bioengenharia", "genomica")),
    ("Energia", ("energia", "eletricidade", "geracao distribuida", "matriz energetica")),
    ("Energia renovável", ("renovavel", "eolica", "solar", "hidreletrica", "biogas")),
    ("Tecnologia e inovação", ("inovacao", "tecnologia", "pesquisa e desenvolvimento", "p&d", "pd&i")),
    ("Inteligência artificial", ("inteligencia artificial", "machine learning", "deep learning")),
    ("Big data", ("big data", "ciencia de dados", "analytics")),
    ("Saúde", ("saude", "hospital", "medicina", "epidemiologia")),
    ("Saneamento", ("saneamento", "esgoto", "tratamento de agua")),
    ("Meio ambiente", ("meio ambiente", "conservacao", "biodiversidade", "clima")),
    ("Startups", ("startup", "scale-up", "venture")),
    ("Indústria", ("industria", "manufatura", "fabric")),
    ("Defesa nacional", ("defesa nacional", "forcas armadas", "militar")),
    ("Petróleo e gás", ("petroleo", "gas natural", "biocombustivel", "anp")),
    ("Educação e pesquisa", ("educacao", "universidade", "ensino superior", "pesquisa cientifica")),
    ("Bolsas", ("bolsa", "bolsista", "capes", "cnpq")),
]

TIPO_OPORTUNIDADE_RULES: List[Tuple[str, Tuple[str, ...]]] = [
    ("licitação", ("licitacao", "pregao", "dispensa de licitacao", "compras publicas")),
    ("chamada_publica", ("chamada publica", "chamamento publico", "selecao publica")),
    ("edital", ("edital", "publicacao do edital", "normativo do edital")),
    ("bolsa", (" bolsa ", "auxilio financeiro a pesquisador")),
    ("fomento", (" fomento", "subvencao economica", "repasse")),
    ("financiamento", ("financiamento", "linha de credito", "credito rotativo")),
    ("grant", ("grant ", " research grant")),
    ("aceleração", ("aceleracao", "accelerator")),
    ("programa", (" programa ", "programa nacional")),
]

PUBLICO_ALVO_RULES: List[Tuple[str, Tuple[str, ...]]] = [
    ("startups", ("startup", "spin-off")),
    ("empresas", ("empresas", "empresarial", "mei e epp", "micro e pequena")),
    ("universidades", ("universidade", "instituicao de ensino superior")),
    ("ICTs", ("ict", "instituto de ciencia e tecnologia", "instituicao cientifica")),
    ("pesquisadores", ("pesquisador", "docente", "pos-doutor")),
    ("estudantes", ("estudante", "graduacao", "mestrado", "doutorado")),
    ("governo", ("orgao publico", "administracao publica", "governo federal")),
    ("fornecedores", ("fornecedor", "supplier", "credenciamento de fornecedores")),
]

SETOR_ECONOMICO_FROM_TAGS: Dict[str, str] = {
    "defesa": "defesa",
    "nuclear": "nuclear",
    "energia": "energia",
    "aeroespacial": "aeroespacial",
    "industria": "indústria",
    "ciencia_tecnologia": "tecnologia",
}

SCIENCE_STRONG_MARKERS = (
    "fisica",
    "quimica",
    "biologia",
    "matematica",
    "engenharia",
    "ciencia dos materiais",
    "materiais avancados",
    "nuclear",
    "computacao",
    "medicina",
    "farmacia",
    "biotecnologia",
    "radioquimica",
    "geociencia",
    "astrofisica",
)

TECH_STRONG_MARKERS = (
    "inteligencia artificial",
    "big data",
    "semicondutor",
    "sensor",
    "radar",
    "robot",
    "drone",
    "embarcad",
    "energia nuclear",
    "energia renovavel",
    "bateria",
    "hidrogenio",
    "material avancad",
    "manufatura avancada",
    "cibersegur",
    "aeroespacial",
    "satelite",
)

PROCUREMENT_MARKERS = (
    "licitacao",
    "pregao",
    "contratacao",
    "compra",
    "pncp",
    "termo de referencia",
    "objeto da contratacao",
    "procurement",
    "tender",
    "bid",
)

PROFILE_MARKERS: Dict[str, Tuple[str, ...]] = {
    "empresa": ("empresa", "cnpj", "industrial", "setor produtivo", "capital de giro", "financiamento empresarial"),
    "startups": ("startup", "aceleracao", "aceleração", "incubacao", "incubação", "open innovation", "empresa nascente"),
    "pesquisador": ("pesquisador", "docente", "professor", "pesquisa", "bolsa"),
    "pesquisadores": ("pesquisador", "docente", "professor", "pesquisa", "bolsa"),
    "universidades": ("universidade", "instituicao de ensino", "instituição de ensino"),
    "icts": ("ict", "instituto de ciencia e tecnologia", "instituto de ciência e tecnologia"),
    "fornecedor": ("fornecedor", "licitacao", "pregao", "contratacao", "compra publica", "procurement"),
    "fornecedores": ("fornecedor", "licitacao", "pregao", "contratacao", "compra publica", "procurement"),
    "municipio": ("municipio", "município", "prefeitura"),
    "prefeitura": ("prefeitura", "municipio", "município"),
}


def _unique_preserve(seq: Sequence[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in seq:
        k = x.strip()
        if not k or k.lower() in seen:
            continue
        seen.add(k.lower())
        out.append(k)
    return out


def _match_rules(norm: str, rules: List[Tuple[str, Tuple[str, ...]]]) -> Tuple[List[str], List[str]]:
    """Retorna (rótulos, palavras-chave que dispararam)."""
    hits: List[str] = []
    kws: List[str] = []
    for label, patterns in rules:
        for p in patterns:
            if p.strip() and p in norm:
                hits.append(label)
                kws.append(p.strip())
                break
    return _unique_preserve(hits), kws


def _thematic_to_setor_estrategico(tags: List[str]) -> List[str]:
    out: List[str] = []
    for t in tags:
        if t == "defesa":
            out.append("defesa")
        elif t == "nuclear":
            out.append("nuclear")
        elif t == "seguranca_publica":
            out.append("seguranca_publica")
        elif t in ("aeroespacial", "veiculos"):
            out.append("aeroespacial")
        elif t == "energia":
            out.append("energia")
        elif t == "ciencia_tecnologia":
            out.append("ciencia_tecnologia")
        elif t == "dual_use":
            out.append("dual_use")
        elif t == "materiais":
            out.append("materiais_avancados")
        else:
            out.append(t)
    return _unique_preserve(out)


def _has_any(norm: str, patterns: Tuple[str, ...]) -> bool:
    return any(p in norm for p in patterns if p)


def _prune_area(area: List[str], norm: str) -> List[str]:
    if not area:
        return []
    # Evita explosão de áreas amplas quando há baixa evidência.
    generic = {"Tecnologia e inovação", "Educação e pesquisa", "Indústria"}
    scored: List[Tuple[int, str]] = []
    for a in area:
        an = _normalize(a)
        score = 1
        if an and an in norm:
            score += 2
        if "nuclear" in an and "nuclear" in norm:
            score += 2
        if "inteligencia artificial" in an and _has_any(norm, TECH_STRONG_MARKERS):
            score += 2
        if a in generic:
            score -= 1
        scored.append((score, a))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return _unique_preserve([a for s, a in scored if s > 0][:6])


def _prune_profile(perfil: List[str], norm: str) -> List[str]:
    out: List[str] = []
    for p in perfil:
        pk = _normalize(p)
        pats = PROFILE_MARKERS.get(pk)
        if pats and not _has_any(norm, pats):
            continue
        out.append(p)
    return _unique_preserve(out)[:4]


def _infer_tipo_recurso(norm: str, declarado: Optional[str]) -> str:
    if declarado and str(declarado).strip() and declarado != "Não Especificado":
        return str(declarado).strip()
    if "topic-details/horizon-" in norm:
        return "fomento"
    if "erc.europa.eu/apply-grant/" in norm:
        return "fomento"
    if _has_any(norm, PROCUREMENT_MARKERS):
        return "licitação"
    if "bolsa" in norm:
        return "bolsa"
    if "financiamento" in norm or "credito" in norm:
        return "financiamento"
    if "subvencao" in norm or "fomento" in norm or "repasse" in norm:
        return "fomento"
    return declarado or ""


def _confidence(areas: List[str], tipos: List[str], kws: int) -> str:
    score = len(areas) + len(tipos) + min(3, kws // 2)
    if score >= 4:
        return "alta"
    if score >= 2:
        return "media"
    return "baixa"


def enrich_opportunity_classification(item: Dict[str, Any]) -> None:
    """
    Enriquece item['extras'] in-place com áreas, tipos, público, setores e metadados de classificação.

    `setor_estrategico`: por defeito **substitui** o valor anterior pelo resultado taxonómico do pipeline
    (sem união com listas antigas contaminadas). Quando `extras["setor_estrategico_crawler_locked"]` é
    verdadeiro, a lista existente não é alterada aqui (curadoria do crawler). Alterações anteriores podem
    ficar em `extras["setor_estrategico_historico_merge"]` (últimas 5 listas).
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        item["extras"] = extras

    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    prog = str(item.get("programa") or "")
    acao = str(item.get("acao") or "")
    link = str(item.get("link") or "")
    tipo_decl = item.get("tipo_recurso")
    corpus = " ".join(
        [
            titulo,
            desc,
            prog,
            acao,
            link,
            str(extras.get("objetivo") or ""),
            str(extras.get("elegibilidade") or ""),
            str(tipo_decl or ""),
        ]
    )
    norm = _normalize(corpus)

    areas_kw, k1 = _match_rules(norm, AREA_NEGOCIO)
    tipo_opp, k2 = _match_rules(norm, TIPO_OPORTUNIDADE_RULES)
    pub_alvo, k3 = _match_rules(norm, PUBLICO_ALVO_RULES)

    thematic_tags = classify_thematic_tags(corpus)
    setor_estr = _thematic_to_setor_estrategico(thematic_tags)
    if len(setor_estr) > 4:
        setor_estr = setor_estr[:4]
    setor_econ = [SETOR_ECONOMICO_FROM_TAGS.get(t, t.replace("_", " ")) for t in thematic_tags if t in SETOR_ECONOMICO_FROM_TAGS]

    palavras = _unique_preserve(list(extras.get("palavras_chave_detectadas") or []) + k1 + k2 + k3)[:80]

    # Merge não destrutivo: listas do crawler prevalecem se já existirem
    def _merge_list(key: str, computed: List[str]) -> None:
        cur = extras.get(key)
        if isinstance(cur, str) and cur.strip():
            cur = [cur.strip()]
        if isinstance(cur, list) and len(cur) > 0:
            extras[key] = _unique_preserve(list(cur) + computed)
        elif cur is None or cur == [] or cur == "":
            extras[key] = computed

    _merge_list("area", _prune_area(areas_kw, norm))
    _merge_list("publico_alvo", _prune_profile(pub_alvo, norm))
    _merge_list("setor_economico", _unique_preserve(setor_econ + areas_kw[:3]))
    _apply_taxonomy_setor_estrategico(extras, setor_estr)
    extras["setor_economico"] = _unique_preserve(extras.get("setor_economico") or [])
    extras["area"] = _prune_area(_unique_preserve(extras.get("area") or []), norm)
    extras["publico_alvo"] = _prune_profile(_unique_preserve(extras.get("publico_alvo") or []), norm)
    extras["setor_estrategico"] = _unique_preserve(extras.get("setor_estrategico") or [])[:4]

    area_c = extras.get("area_cientifica")
    if isinstance(area_c, list) and area_c and not _has_any(norm, SCIENCE_STRONG_MARKERS):
        extras["area_cientifica"] = []
    area_t = extras.get("area_tecnologica")
    if isinstance(area_t, list) and area_t and not _has_any(norm, TECH_STRONG_MARKERS):
        extras["area_tecnologica"] = []

    perfil_ideal = extras.get("perfil_ideal")
    if isinstance(perfil_ideal, str) and perfil_ideal.strip():
        pclean = _prune_profile([perfil_ideal.strip()], norm)
        extras["perfil_ideal"] = pclean[0] if pclean else ""
    elif isinstance(perfil_ideal, list):
        extras["perfil_ideal"] = _prune_profile(perfil_ideal, norm)

    if not extras.get("tipo_oportunidade") and tipo_opp:
        extras["tipo_oportunidade"] = tipo_opp[0]

    tipo_rec = _infer_tipo_recurso(norm, tipo_decl if isinstance(tipo_decl, str) else None)
    if item.get("tipo_recurso") in (None, "", "Não Especificado") and tipo_rec and tipo_rec != "Não Especificado":
        item["tipo_recurso"] = tipo_rec

    extras["palavras_chave_detectadas"] = palavras
    extras["classificacao_confianca"] = _confidence(
        list(extras.get("area") or []),
        [extras.get("tipo_oportunidade") or ""] + tipo_opp,
        len(palavras),
    )
    extras["metodo_classificacao"] = extras.get("metodo_classificacao") or "transformer_keyword"


def calibrate_pncp_extras(item: Dict[str, Any]) -> None:
    """
    Calibração local só para itens PNCP já normalizados (pós-enriquecimento).
    Não altera opportunity_gate global; ajusta coerência semântica e metadados de exibição.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return

    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    acao = str(item.get("acao") or "")
    prog = str(item.get("programa") or "")
    modal = str(extras.get("modalidade_nome") or extras.get("modalidade") or "").lower()
    corp = " ".join(
        [
            titulo,
            desc,
            acao,
            prog,
            modal,
            str(extras.get("numero_processo") or ""),
            str(extras.get("codigo_oportunidade") or ""),
        ]
    )
    norm = _normalize(corp)

    ctrl = str(
        extras.get("codigo_oportunidade") or extras.get("numero_edital") or extras.get("pncp_id") or ""
    ).strip()
    orgao = str(extras.get("orgao_responsavel") or extras.get("orgao_nome") or "").strip()

    # tipo_oportunidade: alinhar a licitação explícita quando a modalidade indicar.
    if any(x in modal for x in ("pregão", "pregao", "concorrência", "concorrencia", "leilão", "leilao", "credenciamento")):
        extras["tipo_oportunidade"] = "licitacao"
    elif not str(extras.get("tipo_oportunidade") or "").strip():
        extras["tipo_oportunidade"] = "compra_publica"

    tr_raw = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "").strip()
    tr = _normalize(tr_raw)
    if not tr_raw or tr in ("nao especificado", "licitacao"):
        extras["tipo_recurso"] = "contratacao_publica"
        item["tipo_recurso"] = "contratacao_publica"
    else:
        extras.setdefault("tipo_recurso", tr_raw)

    # perfil_ideal: fornecedor/empresa quando há objeto + órgão + controle.
    perfil_atual = extras.get("perfil_ideal")
    if (not perfil_atual or perfil_atual == [] or perfil_atual == "") and ctrl and orgao and titulo.strip():
        extras["perfil_ideal"] = ["fornecedor", "empresa"]

    # setor_economico: manter só entradas sustentadas pelo texto (evita arrastar só tags temáticas).
    se_raw = extras.get("setor_economico")
    if isinstance(se_raw, list) and se_raw:
        filtrados = [s for s in se_raw if isinstance(s, str) and s.strip() and _normalize(s) in norm]
        extras["setor_economico"] = _unique_preserve(filtrados)[:4]
    elif isinstance(se_raw, str) and se_raw.strip():
        if _normalize(se_raw) not in norm:
            extras["setor_economico"] = []

    # setor_estrategico: teto mais contido para PNCP.
    ss = extras.get("setor_estrategico")
    if isinstance(ss, list) and len(ss) > 3:
        extras["setor_estrategico"] = _unique_preserve(ss)[:3]

    # Confiança: metadados oficiais PNCP elevam o sinal (reduz falso "baixa" na auditoria semântica).
    if ctrl and orgao and titulo.strip():
        extras["classificacao_confianca"] = "media"
    if ctrl and orgao and titulo.strip() and (extras.get("numero_processo") or modal):
        extras["classificacao_confianca"] = "alta"

    extras.setdefault("metodo_classificacao", "pncp_local_calibration")

    # links_oficiais: espelho leve para auditoria (PDF continua só em pdf_url quando for .pdf).
    links_of: List[Dict[str, str]] = []
    main_link = str(item.get("link") or "").strip()
    if main_link and "pncp.gov.br/app/editais" in main_link:
        links_of.append({"tipo": "detalhe_pncp", "url": main_link[:2000]})
    for d in extras.get("documentos") if isinstance(extras.get("documentos"), list) else []:
        if not isinstance(d, dict):
            continue
        u = str(d.get("url") or "").strip()
        t = str(d.get("tipo") or "").strip()
        if u and t in ("sistema_origem", "processo_eletronico", "edital_pncp", "detalhe_pncp"):
            links_of.append({"tipo": t, "url": u[:2000]})
    if links_of:
        extras["links_oficiais"] = links_of[:12]


def calibrate_portal_plataforma_inovacao_extras(item: Dict[str, Any], pipeline_source: str = "") -> None:
    """
    Calibração local para páginas /categoria/ do Portal da Indústria (Plataforma Inovação).
    Usada por SENAI e plataforma_industria — agregado de linhas, não licitação/fornecedor.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    link = (item.get("link") or "").lower()
    if "portaldaindustria.com.br" not in link or "/categoria/" not in link:
        return
    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([titulo, desc, link]))
    extras["tipo_oportunidade"] = "programa_agregado"
    src = (pipeline_source or "").strip().lower()
    if src == "plataforma_industria":
        extras["tipo_conteudo_plataforma_industria"] = "categoria_plataforma_inovacao"
        extras["metodo_classificacao"] = "plataforma_industria_local_calibration"
    else:
        extras["tipo_conteudo_senai"] = "categoria_plataforma_inovacao"
        extras["metodo_classificacao"] = "senai_local_calibration"
    item["tipo_recurso"] = "Fomento e apoio à inovação industrial"
    extras["tipo_recurso"] = item["tipo_recurso"]
    perfil_labels: List[str] = []
    for label, pats in PROFILE_MARKERS.items():
        if label in ("fornecedor", "fornecedores"):
            continue
        if _has_any(norm, pats):
            perfil_labels.append(label)
    perfil_labels = _unique_preserve(perfil_labels)[:6]
    if perfil_labels:
        pruned = _prune_profile(perfil_labels, norm)
        extras["perfil_ideal"] = pruned if pruned else perfil_labels[:4]
    elif _has_any(norm, ("industria", "industrial", "empresa", "startup", "tecnologia", "instituto senai")):
        extras["perfil_ideal"] = _prune_profile(["empresa", "startups"], norm) or ["empresa"]


def calibrate_senai_extras(item: Dict[str, Any]) -> None:
    """Compat: delega para calibração comum do portal."""
    calibrate_portal_plataforma_inovacao_extras(item, "senai")


def calibrate_softex_extras(item: Dict[str, Any]) -> None:
    """
    Calibração local Softex: posts de programa/inscrição (ex.: Amazônia Geek) não são notícia institucional genérica.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    link = (item.get("link") or "").lower()
    if "softex.br" not in link:
        return
    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([titulo, desc, link]))
    if not _has_any(norm, ("inscri", "programa", "geek", "formacao", "formação", "capacita", "talento", "games")):
        return
    extras["tipo_oportunidade"] = "programa"
    if _has_any(norm, ("formacao", "formação", "capacita", "talento", "curso", "jovem", "educacao", "educação")):
        item["tipo_recurso"] = "Capacitação"
    else:
        item["tipo_recurso"] = "Fomento"
    extras["tipo_recurso"] = item["tipo_recurso"]
    perfil_labels: List[str] = []
    for label, pats in PROFILE_MARKERS.items():
        if label in ("fornecedor", "fornecedores"):
            continue
        if _has_any(norm, pats):
            perfil_labels.append(label)
    perfil_labels = _unique_preserve(perfil_labels)[:6]
    if perfil_labels:
        pruned = _prune_profile(perfil_labels, norm)
        extras["perfil_ideal"] = pruned if pruned else perfil_labels[:4]
    elif _has_any(
        norm,
        (
            "startup",
            "empresa",
            "tecnologia",
            "software",
            "jovem",
            "mulher",
            "talento",
            "formacao",
            "formação",
            "games",
            "geek",
            "amazonia",
            "vulnerabilidade",
        ),
    ):
        extras["perfil_ideal"] = _prune_profile(["startups", "empresa"], norm) or ["startups", "empresa"]
    extras["metodo_classificacao"] = "softex_local_calibration"


def calibrate_faperg_extras(item: Dict[str, Any]) -> None:
    """
    Calibração local para itens da pasta/fonte `faperg` (portal FAPERGS-RS).
    Preenche UF/origem e refina tipo quando há evidência no texto (sem inventar código).
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "fapergs.rs.gov.br" not in lk:
        return
    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([titulo, desc, lk]))

    extras.setdefault("origem_portal", "FAPERGS")
    extras.setdefault("uf", "RS")
    extras.setdefault("estado", "RS")
    if not str(extras.get("regiao") or "").strip() or str(extras.get("regiao")).lower() in ("brasil", "nacional"):
        extras["regiao"] = "Sul"
    extras.setdefault("pais", "Brasil")

    cur_to = str(extras.get("tipo_oportunidade") or "").strip().lower()
    if _has_any(norm, ("bolsa", "bolsista", "auxilio recem", "auxilio recem-doutor", "bolsa de")):
        if not cur_to or cur_to in ("desconhecido", "oportunidade"):
            extras["tipo_oportunidade"] = "bolsa"
        if item.get("tipo_recurso") in (None, "", "Não Especificado"):
            item["tipo_recurso"] = "Bolsa / Auxílio"
    elif _has_any(norm, ("processo seletivo", "selecao publica")):
        if not cur_to or cur_to in ("desconhecido", "oportunidade"):
            extras["tipo_oportunidade"] = "processo_seletivo"
    elif _has_any(norm, ("edital", "chamada", "fomento", "programa", "centelha")):
        if not cur_to or cur_to in ("desconhecido", "oportunidade"):
            extras["tipo_oportunidade"] = "edital"

    if item.get("tipo_recurso") in (None, "", "Não Especificado"):
        if _has_any(norm, ("bolsa", "auxilio", "auxílio")):
            item["tipo_recurso"] = "Bolsa / Auxílio"
        elif _has_any(norm, ("pesquisa", "fomento", "tecnologia", "inovacao", "inovação", "ciencia", "ciência")):
            item["tipo_recurso"] = "Subvenção (Não Reembolsável)"
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    perfil: List[str] = []
    if _has_any(norm, ("empresa", "startup", "setor produtivo", "sict", "industria", "indústria")):
        perfil.append("empresa")
    if _has_any(norm, ("pesquisador", "docente", "doutor", "pesquisa cientifica", "pesquisa científica")):
        perfil.append("pesquisador")
    if _has_any(norm, ("estudante", "graduacao", "graduação", "mestrado")):
        perfil.append("estudante")
    if _has_any(norm, ("universidade", "instituto de ciencia", "instituto federal", "comite cientifico", "comitê científico")):
        perfil.extend(["universidades", "pesquisadores"])
    perfil = _prune_profile(_unique_preserve(perfil), norm)
    if perfil:
        extras["perfil_ideal"] = perfil
    extras["metodo_classificacao"] = extras.get("metodo_classificacao") or "faperg_local_calibration"


# Marcadores estritos para licitação/contratação Apex (evitar "compra" isolado — casa com "compradores").
APEX_LICITACAO_EVIDENCIA: Tuple[str, ...] = (
    "licitacao",
    "licitação",
    "pregao",
    "pregão",
    "pregao eletronico",
    "pregão eletrônico",
    "compra publica",
    "compra pública",
    "compras publicas",
    "compras públicas",
    "contratacao direta",
    "contratação direta",
    "dispensa de licitacao",
    "dispensa de licitação",
    "edital de contratacao",
    "edital de contratação",
    "contratacao de servicos",
    "contratação de serviços",
    "portal de aquisicoes",
    "portal de aquisições",
    "compras.apexbrasil",
    "fornecedor",
    "fornecedores",
    "pncp",
    "procurement",
    "termo de referencia",
    "termo de referência",
    "objeto da contratacao",
    "objeto da contratação",
)

# Programa / inscrição / internacionalização (Exporta Mais, CRM, etc.) — não usar PROCUREMENT_MARKERS genérico.
APEX_PROGRAMA_EXPORTACAO: Tuple[str, ...] = (
    "exporta mais",
    "crm-apps.apexbrasil",
    "inscricao-eventos",
    "inscrição-eventos",
    "programa da apexbrasil",
    "internacionaliz",
    "exportacao",
    "exportação",
    "comercio exterior",
    "comércio exterior",
    "compradores internacionais",
    "rodada de negocios",
    "rodada de negócios",
    "missao de negocios",
    "missão de negócios",
    "missao-negocios",
    "promocao de exportacoes",
    "promoção de exportações",
)


def calibrate_apex_extras(item: Dict[str, Any]) -> None:
    """
    Calibração local ApexBrasil: Exporta Mais / inscrições / CRM ≠ licitação.
    Licitação só com APEX_LICITACAO_EVIDENCIA (sem substring genérico \"compra\").
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "apexbrasil.com.br" not in lk:
        return
    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([titulo, desc, lk]))

    extras.setdefault("origem_portal", "ApexBrasil")

    es_programa_export = _has_any(norm, APEX_PROGRAMA_EXPORTACAO)
    es_licitacao = _has_any(norm, APEX_LICITACAO_EVIDENCIA)

    # Corrige classificação errada herdada (ex.: \"compradores\" + \"compra\" em heurísticas antigas).
    tr_atual = _normalize(str(item.get("tipo_recurso") or extras.get("tipo_recurso") or ""))
    parece_licitacao_errada = (
        es_programa_export
        and not es_licitacao
        and (
            "licit" in tr_atual
            or "contratacao_publica" in tr_atual
            or "contratação" in tr_atual
        )
    )

    if es_licitacao:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "licitacao"
        item["tipo_recurso"] = "contratacao_publica"
    elif es_programa_export or parece_licitacao_errada:
        if _has_any(norm, ("selecao de empresas", "seleção de empresas", "selecao baseada", "seleção baseada", "credenciamento de empresas")):
            extras["tipo_oportunidade"] = "selecao_empresas"
        elif _has_any(norm, ("inscricao", "inscrição", "inscricao-eventos", "inscricoes", "inscrições", "propostas", "submissao", "submissão")):
            extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "chamada_publica"
        else:
            extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "programa"
        if "crm-apps.apexbrasil" in lk or _has_any(norm, ("internacionaliz", "exporta mais", "inscricao-eventos")):
            item["tipo_recurso"] = "apoio_internacionalizacao"
        elif _has_any(norm, ("exportacao", "exportação", "comercio exterior", "comércio exterior", "promocao", "promoção")):
            item["tipo_recurso"] = "promocao_exportacao"
        else:
            item["tipo_recurso"] = "apoio"
    elif _has_any(norm, ("selecao de empresas", "seleção de empresas", "credenciamento de empresas")):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "selecao_empresas"
    elif _has_any(norm, ("chamada", "inscricao", "inscrição", "propostas", "submissao", "submissão")):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "chamada_publica"
    elif _has_any(norm, ("programa", "projeto", "internacionaliz", "exportacao", "exportação", "missao", "missão")):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "programa"

    if item.get("tipo_recurso") in (None, "", "Não Especificado"):
        if es_licitacao:
            item["tipo_recurso"] = "contratacao_publica"
        elif _has_any(norm, ("exportacao", "exportação", "comercio exterior", "comércio exterior", "internacionaliz")):
            item["tipo_recurso"] = "promocao_exportacao"
        else:
            item["tipo_recurso"] = item.get("tipo_recurso") or "apoio"

    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    se_in = extras.get("setor_economico")
    se_list: List[str] = [str(x) for x in se_in] if isinstance(se_in, list) else ([] if not se_in else [str(se_in)])
    if _has_any(norm, ("exportacao", "exportação", "comercio exterior", "comércio exterior")):
        se_list = _unique_preserve(se_list + ["exportação", "comércio exterior"])
    if _has_any(norm, ("inovacao", "inovação", "tecnologia")):
        se_list = _unique_preserve(se_list + ["inovação"])
    if se_list:
        extras["setor_economico"] = se_list[:6]

    pl: List[str] = []
    if _has_any(norm, ("mei", "pequena empresa", "pme", "microempresa", "micro e pequena")):
        pl.append("pequena empresa")
    if _has_any(norm, ("exportador", "exportação", "exportacao", "internacionaliz")):
        pl.append("exportador")
    if _has_any(norm, ("startup", "startups")):
        pl.append("startup")
    if _has_any(norm, ("empresa", "empresas", "setor privado", "companhia")):
        pl.append("empresa")
    if _has_any(norm, ("industria", "indústria", "manufatura")):
        pl.append("indústria")
    pl = _prune_profile(_unique_preserve(pl), norm)
    if pl:
        extras["perfil_ideal"] = pl
    extras["metodo_classificacao"] = "apex_local_calibration"


def calibrate_ambev_extras(item: Dict[str, Any]) -> None:
    """
    Ambev / 100+ Accelerator: desafios temáticos de open innovation (não notícia institucional genérica).
    Suprime tags ML espúrias (ex.: aeroespacial em texto EN de sustentabilidade).
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "100accelerator.com" not in lk and "ambev.com.br" not in lk:
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([tit, desc, lk]))

    accelerator_detail = "100accelerator.com/challenges/" in lk
    try:
        parts = [p for p in lk.split("/") if p]
        ix = parts.index("challenges") if "challenges" in parts else -1
        slug = parts[ix + 1] if ix >= 0 and ix + 1 < len(parts) else ""
    except (ValueError, IndexError):
        slug = ""
    accelerator_detail = accelerator_detail and slug not in ("", "challenges", "challenge")

    if accelerator_detail or _has_any(
        norm,
        (
            "100 accelerator",
            "100+",
            "challenge",
            "startup",
            "scale pilot",
            "solutions",
            "open innovation",
            "pilot",
            "partnership",
        ),
    ):
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_ambev"] = "open_innovation_aceleracao"
        item["tipo_recurso"] = "apoio_inovacao"
        extras["publico_alvo"] = ["empresas", "startups", "scaleups"]
        extras["perfil_ideal"] = _prune_profile(["startup", "empresa", "empreendedor"], norm) or [
            "startup",
            "empresa",
        ]
        extras.setdefault("origem_portal", "100+ Accelerator (AB InBev)")
        extras["idioma_original"] = (str(extras.get("idioma_original") or "").strip() or "en")
    elif "ambev.com.br" in lk and _has_any(
        norm, ("startup", "programa", "inova", "edital", "chamada", "desafio", "oportunidade")
    ):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "programa"
        extras["tipo_conteudo_ambev"] = "hub_startups_ambev"
        item["tipo_recurso"] = item.get("tipo_recurso") or "apoio_inovacao"
        extras["perfil_ideal"] = extras.get("perfil_ideal") or ["startup", "empresa"]

    if accelerator_detail or "100accelerator.com" in lk:
        extras["setor_estrategico"] = []
        extras["thematic_tags"] = []
        extras["thematic_confidence"] = 0.0
        if not _has_any(norm, ("defesa", "militar", "armamento", "dual use", "dual-use")):
            extras["area_tecnologica"] = []
        item["regiao"] = "Internacional"

    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")
    extras["metodo_classificacao"] = "ambev_local_calibration"


_SUPPLIER_CALIBRATION_SOURCES = frozenset(
    {
        "bae_systems_suppliers",
        "rheinmetall_suppliers",
        "thales_suppliers",
        "general_dynamics_suppliers",
        "lockheed_martin_suppliers",
        "japan_kawasaki_heavy",
    }
)

# Recovery D — taxonomia alinhada à secção produto «Fornecedores & Investimentos» / portais estratégicos.
# Valores canónicos (tipo_oportunidade / tipo_recurso) usados nesta onda; outros ficam reservados para expansão.
TIPO_OPORTUNIDADE_FORNECEDORES_INVESTIMENTOS: Tuple[str, ...] = (
    "oportunidade_fornecedor",
    "supplier_registration",
    "supplier_portal",
    "procurement_portal",
    "programa_agregado",
    "documentacao_fornecedor",
    "recurso_fornecedor",
    "investment_portal",
    "corporate_venture",
    "startup_program",
    "internationalization_portal",
)

# Títulos exatos do standardized Recovery D.1 (UTF-8).
_RECOVERY_D_FORNECEDORES_DOC_TITLES: frozenset = frozenset(
    {
        "Small Business Innovation Research",
        "Cybersecurity",
        "Supplier Ethics",
        "Sustainable Supply Chain Management",
        "Supplier Documentation",
        "Webinars & Programs",
        "Supplier News and Events",
        "LM eInvoicing 2026 Training",
        "Maintaining Cybersecurity Maturity Model Certification",
        "Shared Commitment to Equal Employment Opportunity",
        "Power Of A Shared Focus",
        "Document CMMC status in Exostar",
        "Discontinuation of Phone-Based OTP for Supplier Access",
        "Upcoming CMMC Requirements",
    }
)

_RECOVERY_D_FORNECEDORES_DESTAQUE_TITLES: frozenset = frozenset(
    {
        "New supplier registration (HICX)",
        "Responsible supply chain | BAE Systems UK suppliers",
        "Mentor-Protégé Program",
        "General Dynamics Land Systems — Suppliers (hub)",
        "CYBERSECURITY",
        "iSUPPLIER",
        "QUALITY",
        "TRANSPORTATION AND TRADE COMPLIANCE",
        "Lockheed Martin — Supplier portal (hub)",
        "Doing Business",
        "Business Area Procurement",
        "Small Business Programs",
    }
)


def _recovery_d_append_validacao_warning(extras: Dict[str, Any], code: str) -> None:
    wl = extras.get("validacao_warnings")
    if not isinstance(wl, list):
        wl = []
    wl.append(code)
    extras["validacao_warnings"] = _unique_preserve([str(x) for x in wl])


def _recovery_d_supplier_portal_validacao(
    item: Dict[str, Any],
    extras: Dict[str, Any],
    *,
    lk: str,
    norm: str,
    desc_plain: str,
    metodo: str,
    source_key: str,
) -> None:
    warns = _as_str_list(extras.get("validacao_warnings"))
    if "supplier_login_isolado" in warns:
        return

    if source_key == "bae_systems_suppliers":
        if "hicx.net" in lk and "discovery-login" in lk:
            item["validacao_status"] = "incompleto" if len(desc_plain) >= 200 else "acesso_limitado"
        elif "hicx.net" in lk:
            item["validacao_status"] = "acesso_limitado"
        elif metodo == "bae_baesystems_waf_stub":
            item["validacao_status"] = "acesso_limitado"
        elif metodo == "bae_corporate_supplier_html":
            vs0 = str(item.get("validacao_status") or "").strip().lower()
            if vs0 in ("", "suspeito"):
                item["validacao_status"] = "incompleto" if len(desc_plain) >= 200 else "acesso_limitado"
        else:
            vs0 = str(item.get("validacao_status") or "").strip().lower()
            if vs0 in ("", "suspeito"):
                item["validacao_status"] = "incompleto" if len(desc_plain) >= 160 else "acesso_limitado"
        return

    if ".pdf" in lk:
        item["validacao_status"] = "incompleto" if len(desc_plain) >= 160 else "acesso_limitado"
    elif (
        "oracle" in lk
        or "isupplier" in lk
        or "ivalua.app" in lk
        or "e-acquisition" in lk
        or "eacquisition" in lk
    ):
        item["validacao_status"] = "acesso_limitado"
    else:
        vs0 = str(item.get("validacao_status") or "").strip().lower()
        if vs0 in ("", "suspeito"):
            item["validacao_status"] = "incompleto" if len(desc_plain) >= 200 else "acesso_limitado"


def _calibrate_supplier_portal_recovery_d_core(
    item: Dict[str, Any],
    *,
    source_key: str,
    origem_portal: str,
    curadoria_referencia: str,
) -> None:
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    lk = (item.get("link") or "").lower()
    norm = _normalize(" ".join([tit, desc, lk]))
    desc_plain = desc.strip()
    metodo = str(extras.get("metodo_extracao") or "")
    tit_lower = tit.lower()

    extras["origem_portal"] = origem_portal
    item["regiao"] = "Internacional"
    extras["idioma_original"] = (str(extras.get("idioma_original") or "").strip() or "en")
    extras["curadoria_referencia"] = curadoria_referencia
    extras["thematic_tags"] = []
    extras["thematic_confidence"] = 0.0
    if not _has_any(
        norm,
        (
            "defence",
            "defense",
            "military",
            "militar",
            "weapon",
            "armament",
            "missile",
            "tank",
            "combat ",
            "warship",
            "aerospace and defence",
            "aerospace and defense",
        ),
    ):
        extras["setor_economico"] = []

    extras["recovery_d1_hub_supplier"] = False
    if (
        source_key == "lockheed_martin_suppliers"
        and tit_lower.strip() == "suppliers"
        and "suppliers.html" in lk
    ):
        item["titulo"] = "Lockheed Martin — Supplier portal (hub)"
        tit = str(item.get("titulo") or "")
        tit_lower = tit.lower()
        norm = _normalize(" ".join([tit, desc, lk]))
        extras["tipo_oportunidade"] = "programa_agregado"
        extras["recovery_d1_hub_supplier"] = True
    elif (
        source_key == "general_dynamics_suppliers"
        and tit.strip().upper() == "SUPPLIERS"
        and "gdls.com" in lk
        and "/suppliers" in lk
    ):
        item["titulo"] = "General Dynamics Land Systems — Suppliers (hub)"
        tit = str(item.get("titulo") or "")
        tit_lower = tit.lower()
        norm = _normalize(" ".join([tit, desc, lk]))
        extras["tipo_oportunidade"] = "programa_agregado"
        extras["recovery_d1_hub_supplier"] = True
    else:
        extras["tipo_oportunidade"] = "oportunidade_fornecedor"
    item["tipo_recurso"] = "oportunidade_fornecedor"
    extras["tipo_recurso"] = "oportunidade_fornecedor"
    extras["perfil_ideal"] = _unique_preserve(_as_str_list(extras.get("perfil_ideal")) + ["fornecedor", "empresa"]) or [
        "fornecedor",
        "empresa",
    ]
    extras["publico_alvo"] = _as_str_list(extras.get("publico_alvo")) or ["fornecedores", "empresas"]

    cur_set = _as_str_list(extras.get("setor_estrategico"))
    if len(cur_set) > 3:
        overflow = cur_set[3:]
        extras["setores_detectados"] = _unique_preserve(_as_str_list(extras.get("setores_detectados")) + cur_set)
        extras["tags_secundarias"] = _unique_preserve(_as_str_list(extras.get("tags_secundarias")) + overflow)
        extras["setor_estrategico"] = cur_set[:3]

    faq_hit = (
        "/faq" in lk
        or "/faqs" in lk
        or "faq" in tit_lower
        or "help center" in norm
        or "supplier faq" in norm
        or "/help" in lk
        or "/support" in lk
    )
    if faq_hit:
        _recovery_d_append_validacao_warning(extras, "recovery_d_supplier_faq_ruido")
        extras["recovery_d_recomendar_ativo_false"] = True

    login_isolated = False
    if not faq_hit:
        if "/login" in lk or lk.rstrip("/").endswith("/login"):
            if not _has_any(
                norm,
                (
                    "register",
                    "registration",
                    "supplier",
                    "vendor",
                    "sign up",
                    "sign-up",
                    "cadastro",
                    "self-registr",
                ),
            ):
                login_isolated = True
        tl = tit_lower.strip()
        if "login to" in tl and "account" in tl and not _has_any(norm, ("supplier", "vendor", "registration", "portal")):
            login_isolated = True
        if tl in ("log in", "sign in", "login", "sign-in"):
            login_isolated = True

    if login_isolated and not faq_hit:
        item["validacao_status"] = "suspeito"
        _recovery_d_append_validacao_warning(extras, "supplier_login_isolado")
        extras["recovery_d_login_isolado"] = True
        extras["recovery_d_recomendar_ativo_false"] = True

    if not faq_hit and not login_isolated:
        instit = _has_any(norm, ("supplier code of conduct", "code of ethics", "sustainability supply", "about supply chain")) and not _has_any(
            norm,
            (
                "become a supplier",
                "supplier registration",
                "vendor registration",
                "register ",
                "registration",
                "apply",
                "application",
                "procurement",
                "discovery-login",
                "hicx",
            ),
        )
        if instit:
            _recovery_d_append_validacao_warning(extras, "recovery_d_institucional_generico")
            extras["recovery_d_needs_manual_review"] = True

    if faq_hit:
        vs0 = str(item.get("validacao_status") or "").strip().lower()
        if vs0 not in ("suspeito",):
            item["validacao_status"] = "incompleto"
    elif not login_isolated:
        _recovery_d_supplier_portal_validacao(item, extras, lk=lk, norm=norm, desc_plain=desc_plain, metodo=metodo, source_key=source_key)

    extras["validacao_status"] = str(item.get("validacao_status") or extras.get("validacao_status") or "")
    _apply_recovery_d_fornecedores_investimentos_routing(item, source_key)
    _apply_recovery_d1_supplier_qa_metadata(item, source_key)


def _apply_recovery_d_fornecedores_investimentos_routing(item: Dict[str, Any], source_key: str) -> None:
    """
    Marcações backend para secção «Fornecedores & Investimentos» — não altera opportunity_gate global.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    tit_raw = str(item.get("titulo") or "").strip()
    lk = (item.get("link") or "").lower()

    extras["frontend_section"] = "fornecedores"
    extras["mostrar_no_radar"] = False
    extras["mostrar_em_fornecedores"] = True
    extras["mostrar_em_investimentos"] = False
    extras["supplier_portal"] = True
    extras["recovery_d_fornecedores_wave"] = "recovery_d_fornecedores_final"

    if tit_raw in _RECOVERY_D_FORNECEDORES_DOC_TITLES:
        extras["recovery_d_doc_supplier"] = True
        extras["tipo_oportunidade"] = "documentacao_fornecedor"
        item["tipo_recurso"] = "recurso_fornecedor"
        extras["tipo_recurso"] = "recurso_fornecedor"
        if any(x in lk for x in ("/training", "webinar", "einvoice", "invoic", "otp")):
            extras["portal_tipo"] = "supplier_resource"
        else:
            extras["portal_tipo"] = "documentation"
        return

    if tit_raw not in _RECOVERY_D_FORNECEDORES_DESTAQUE_TITLES:
        extras["portal_tipo"] = "supplier_resource"
        return

    if tit_raw == "New supplier registration (HICX)":
        extras["tipo_oportunidade"] = "supplier_registration"
        extras["portal_tipo"] = "registration"
    elif tit_raw == "Responsible supply chain | BAE Systems UK suppliers":
        extras["tipo_oportunidade"] = "supplier_portal"
        extras["portal_tipo"] = "access_limited"
    elif tit_raw == "Mentor-Protégé Program":
        extras["tipo_oportunidade"] = "oportunidade_fornecedor"
        extras["portal_tipo"] = "procurement"
    elif tit_raw == "General Dynamics Land Systems — Suppliers (hub)":
        extras["tipo_oportunidade"] = "programa_agregado"
        extras["portal_tipo"] = "hub"
    elif tit_raw == "Lockheed Martin — Supplier portal (hub)":
        extras["tipo_oportunidade"] = "programa_agregado"
        extras["portal_tipo"] = "hub"
    elif tit_raw == "iSUPPLIER":
        extras["tipo_oportunidade"] = "supplier_registration"
        extras["portal_tipo"] = "registration"
    elif tit_raw in ("CYBERSECURITY", "QUALITY", "TRANSPORTATION AND TRADE COMPLIANCE"):
        extras["tipo_oportunidade"] = "oportunidade_fornecedor"
        extras["portal_tipo"] = "supplier_resource"
    elif tit_raw == "Doing Business":
        extras["tipo_oportunidade"] = "procurement_portal"
        extras["portal_tipo"] = "procurement"
    elif tit_raw == "Business Area Procurement":
        extras["tipo_oportunidade"] = "procurement_portal"
        extras["portal_tipo"] = "procurement"
    elif tit_raw == "Small Business Programs":
        extras["tipo_oportunidade"] = "oportunidade_fornecedor"
        extras["portal_tipo"] = "supplier_resource"
    else:
        extras["portal_tipo"] = "supplier_resource"


def _apply_recovery_d1_supplier_qa_metadata(item: Dict[str, Any], source_key: str) -> None:
    """Campos apenas para relatório/traceability Recovery D.1 — não altera readiness nem gate global."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    tit_raw = str(item.get("titulo") or "")
    tit = tit_raw.lower()
    tit_norm = _normalize(tit_raw)
    to = str(extras.get("tipo_oportunidade") or "")
    vs = str(item.get("validacao_status") or "").lower()
    warns = _as_str_list(extras.get("validacao_warnings"))

    def _set(d: str, m: str, a: str) -> None:
        extras["recovery_d1_decisao_qa"] = d
        extras["recovery_d1_motivo_qa"] = m
        extras["recovery_d1_acao_recomendada"] = a

    if tit_raw in _RECOVERY_D_FORNECEDORES_DOC_TITLES:
        _set(
            "documentacao_fornecedor",
            "Conteúdo de apoio, documentação, notícias, CMMC ou formação — não oportunidade acionável principal.",
            "Secção Fornecedores (recurso/documentação); mostrar_no_radar=false; não misturar com Radar de Fomento.",
        )
        return

    if "supplier_login_isolado" in warns or extras.get("recovery_d_login_isolado"):
        _set(
            "candidato_ativo_false",
            "Login isolado sem texto útil público suficiente para cadastro.",
            "marcar ativo=false após apply; não classificar como oportunidade forte.",
        )
        return
    if "recovery_d_supplier_faq_ruido" in warns:
        _set("candidato_ativo_false", "FAQ/help/support detectado.", "ativo=false; excluir de destaques de edital.")
        return

    if extras.get("recovery_d1_hub_supplier") or to == "programa_agregado":
        _set(
            "hub_programa_agregado",
            "Hub oficial de fornecedores com múltiplos recursos; não é formulário único.",
            "Manter programa_agregado + incompleto; badge supplier hub no frontend.",
        )
        return

    if "hicx.net" in lk and "discovery-login" in lk:
        _set(
            "manter_oportunidade_fornecedor",
            "Self-registration HICX com contexto público mínimo.",
            f"Manter tipo_recurso oportunidade_fornecedor; validação {vs}; portal credential.",
        )
        return

    if "isupplier" in lk or "supplieronboarding" in lk:
        _set(
            "manter_oportunidade_fornecedor",
            "Portal Oracle / onboarding com camada autenticada.",
            "validacao_status=acesso_limitado; não promover como edital aberto.",
        )
        return

    if source_key == "bae_systems_suppliers" and "responsible-supply-chain" in lk:
        _set(
            "acesso_limitado_institucional",
            "Página institucional supply chain / stub WAF.",
            "acesso_limitado; uso informativo, não cadastro direto aqui.",
        )
        return

    if "mentor-protege" in lk or ("mentor" in tit_norm and "protege" in tit_norm):
        _set(
            "manter_oportunidade_fornecedor",
            "Programa Mentor-Protégé com texto operacional público.",
            "Manter oportunidade_fornecedor; incompleto até haver objeto/prazo estruturado.",
        )
        return

    if source_key == "lockheed_martin_suppliers" and "/suppliers" in lk:
        _set(
            "manter_oportunidade_fornecedor",
            "Leaf sob /suppliers (docs, SMBR, cybersecurity, formação, notícias).",
            "incompleto; não destacar como licitação; útil como referência fornecedor.",
        )
        return

    if source_key == "general_dynamics_suppliers" and "/suppliers" in lk:
        _set(
            "manter_oportunidade_fornecedor",
            "Secções supplier GDLS/GD com requisitos (quality, cybersecurity, trade).",
            "incompleto; manter índice navegável.",
        )
        return

    _set(
        "manter_oportunidade_fornecedor",
            "Default Recovery D.1: URL alinhado a tema fornecedor após filtros crawl.",
            f"Seguir validacao_status={vs}.",
        )


def calibrate_general_dynamics_suppliers_extras(item: Dict[str, Any]) -> None:
    """Recovery D — General Dynamics supplier portal: tipo e validação alinhados ao contexto público."""
    _calibrate_supplier_portal_recovery_d_core(
        item,
        source_key="general_dynamics_suppliers",
        origem_portal="General Dynamics",
        curadoria_referencia="recovery_d_general_dynamics_suppliers",
    )


def calibrate_lockheed_martin_suppliers_extras(item: Dict[str, Any]) -> None:
    """Recovery D — Lockheed Martin supplier portal."""
    _calibrate_supplier_portal_recovery_d_core(
        item,
        source_key="lockheed_martin_suppliers",
        origem_portal="Lockheed Martin",
        curadoria_referencia="recovery_d_lockheed_martin_suppliers",
    )


def calibrate_bae_systems_suppliers_extras(item: Dict[str, Any]) -> None:
    """Recovery D — BAE Systems supplier / HICX discovery (sem index de login isolado no crawl)."""
    _calibrate_supplier_portal_recovery_d_core(
        item,
        source_key="bae_systems_suppliers",
        origem_portal="BAE Systems",
        curadoria_referencia="recovery_d_bae_systems_suppliers",
    )


def calibrate_corporate_supplier_sources_extras(item: Dict[str, Any], source_name: str) -> None:
    """
    Portais corporativos de fornecedores / procurement: não classificar como licitação pública
    ou fomento; setor de defesa só com evidência no texto (não pelo nome da empresa).
    """
    src = (source_name or "").strip().lower()
    if src not in _SUPPLIER_CALIBRATION_SOURCES and not src.endswith("_suppliers"):
        return
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    lk = (item.get("link") or "").lower()
    norm = _normalize(" ".join([tit, desc, lk]))

    if any(
        h in lk
        for h in (
            "ivalua.app",
            "hicx.net",
            "procurementportal.",
            "supplierportal",
            "/sourcing",
            "e-acquisition",
            "eacquisition",
        )
    ):
        extras["tipo_oportunidade"] = "supplier_portal"
    elif _has_any(
        norm,
        (
            "become a supplier",
            "new supplier",
            "self-registr",
            "supplier application",
            "vendor registration",
            "cadastro de fornecedor",
            "cadastro fornecedor",
            "supplier onboarding",
        ),
    ):
        extras["tipo_oportunidade"] = "cadastro_fornecedor"
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "procurement_corporativo"

    item["tipo_recurso"] = "oportunidade_fornecedor"
    extras["tipo_recurso"] = "oportunidade_fornecedor"
    extras["perfil_ideal"] = ["fornecedor", "empresa"]
    extras["publico_alvo"] = ["fornecedores", "empresas"]

    if not _has_any(
        norm,
        (
            "defence",
            "defense",
            "military",
            "militar",
            "weapon",
            "armament",
            "missile",
            "tank",
            "combat ",
            "warship",
            "aerospace and defence",
            "aerospace and defense",
        ),
    ):
        extras["setor_estrategico"] = []
        extras["subtema"] = []
        extras["area_tecnologica"] = []

    if src == "rheinmetall_suppliers":
        extras["origem_portal"] = "Rheinmetall"
        extras["idioma_original"] = (str(extras.get("idioma_original") or "").strip() or "en")
        extras["curadoria_referencia"] = "lote5_rheinmetall_suppliers"
        extras["thematic_tags"] = []
        extras["thematic_confidence"] = 0.0
        if not _has_any(
            norm,
            (
                "defence",
                "defense",
                "military",
                "militar",
                "weapon",
                "armament",
                "missile",
                "tank",
                "combat ",
                "warship",
            ),
        ):
            extras["setor_economico"] = []
        desc_plain = str(item.get("descricao") or "").strip()
        if "ivalua.app" in lk and len(desc_plain) < 100:
            item["validacao_status"] = "acesso_limitado"
        else:
            vs0 = str(item.get("validacao_status") or "").strip().lower()
            if vs0 in ("", "suspeito"):
                item["validacao_status"] = "incompleto"
        extras["validacao_status"] = str(item.get("validacao_status") or extras.get("validacao_status") or "")

    if src == "thales_suppliers":
        extras["origem_portal"] = "Thales"
        item["regiao"] = "Internacional"
        extras["idioma_original"] = (str(extras.get("idioma_original") or "").strip() or "en")
        extras["curadoria_referencia"] = "lote5_thales_fix"
        extras["thematic_tags"] = []
        extras["thematic_confidence"] = 0.0
        if not _has_any(
            norm,
            (
                "defence",
                "defense",
                "military",
                "militar",
                "weapon",
                "armament",
                "missile",
                "tank",
                "combat ",
                "warship",
            ),
        ):
            extras["setor_economico"] = []
        desc_plain = str(item.get("descricao") or "").strip()
        metodo = str(extras.get("metodo_extracao") or "")
        if ".pdf" in lk or metodo == "curated_official_manifest":
            item["validacao_status"] = "incompleto" if len(desc_plain) >= 160 else "acesso_limitado"
        elif "ivalua.app" in lk or "e-acquisition" in lk or "eacquisition" in lk:
            item["validacao_status"] = "acesso_limitado"
        else:
            vs0 = str(item.get("validacao_status") or "").strip().lower()
            if vs0 in ("", "suspeito"):
                item["validacao_status"] = "incompleto" if len(desc_plain) >= 200 else "acesso_limitado"
        extras["validacao_status"] = str(item.get("validacao_status") or extras.get("validacao_status") or "")

    if src == "general_dynamics_suppliers":
        calibrate_general_dynamics_suppliers_extras(item)

    if src == "lockheed_martin_suppliers":
        calibrate_lockheed_martin_suppliers_extras(item)

    if src == "bae_systems_suppliers":
        calibrate_bae_systems_suppliers_extras(item)

    extras["metodo_classificacao"] = "corporate_supplier_local_calibration"


def calibrate_petrobras_extras(item: Dict[str, Any]) -> None:
    """
    Calibração local Petrobras: seleções de patrocínio (Bússola Social) e regulamentos em PDF
    na petrobras.com.br — não classificar como licitação/fornecedor sem marcadores explícitos.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "petrobras.com.br" not in lk and "bussolasocial.com.br/petrobras/editais" not in lk:
        return
    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([titulo, desc, lk]))

    procurement = (
        "pregao",
        "pregão",
        "licitacao",
        "licitação",
        "dispensa de licitacao",
        "compra publica",
        "compra pública",
        "contratacao direta",
        "contratação direta",
    )
    if not _has_any(norm, procurement):
        cur = str(extras.get("tipo_oportunidade") or "").strip().lower()
        if cur in ("licitacao", "licitação", "compra_publica", "supplier_portal") or "fornec" in cur:
            extras.pop("tipo_oportunidade", None)

    if "bussolasocial.com.br/petrobras/editais" in lk:
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_petrobras"] = "selecao_patrocinio_projeto_social"
        if item.get("tipo_recurso") in (None, "", "Não Especificado"):
            item["tipo_recurso"] = "Patrocínio e projetos sociais e culturais"
        extras["tipo_recurso"] = str(item.get("tipo_recurso") or "")
        extras.setdefault("orgao_responsavel", "Petrobras")
    elif "petrobras.com.br" in lk and "/documents/" in lk and ".pdf" in lk:
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_petrobras"] = "regulamento_pdf_selecao"
        if item.get("tipo_recurso") in (None, "", "Não Especificado"):
            item["tipo_recurso"] = "Patrocínio e projetos sociais e culturais"
        extras["tipo_recurso"] = str(item.get("tipo_recurso") or "")
        extras.setdefault("orgao_responsavel", "Petrobras")

    extras["metodo_classificacao"] = "petrobras_local_calibration"
    if not extras.get("publico_alvo"):
        if _has_any(norm, ("osc", "ong", "cultural", "projeto social", "proponente", "lei de incentivo", "incentivo fiscal")):
            extras["publico_alvo"] = ["OSC", "proponentes culturais"]
        elif _has_any(norm, ("empresa", "patrocin", "patrocínio", "incentiv", "investidor")):
            extras["publico_alvo"] = ["empresas incentivadoras", "OSC"]


def calibrate_marinha_extras(item: Dict[str, Any]) -> None:
    """
    Marinha: licitação/compra só com evidência textual; concurso/processos seletivos separados;
    setor defesa/nuclear só com contexto compatível.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "marinha.mil.br" not in lk:
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm_body = _normalize(" ".join([tit, desc]))
    norm = _normalize(" ".join([tit, desc, lk]))

    procurement = (
        "pregao",
        "pregão",
        "licit",
        "dispensa",
        "compra publica",
        "compra pública",
        "contratacao",
        "contratação",
        "aquisicao",
        "aquisição",
        "uasg",
        "modalidade licit",
        "edital de licit",
        "processo licit",
        "termo de referencia",
        "termo de referência",
        "pncp",
    )
    concurso = (
        "concurso publico",
        "concurso público",
        "processo seletivo",
        "cadastro de reserva",
        "prova objetiva",
        "edital de abertura de concurso",
    )

    if _has_any(norm, concurso) and not _has_any(norm, procurement):
        extras["tipo_oportunidade"] = "processo_seletivo"
        extras["tipo_conteudo_marinha"] = "concurso_ou_seletivo"
        extras["publico_alvo"] = ["candidatos", "profissionais"]
        extras["perfil_ideal"] = "candidatos"
        item["tipo_recurso"] = item.get("tipo_recurso") or "Seleção / emprego público"
    elif _has_any(norm, procurement):
        extras["tipo_oportunidade"] = "licitacao"
        extras["tipo_conteudo_marinha"] = "compra_licitacao"
        extras.setdefault("publico_alvo", ["empresas", "fornecedores"])
        extras["perfil_ideal"] = _prune_profile(["fornecedores", "empresa"], norm) or ["fornecedores"]
        item["tipo_recurso"] = item.get("tipo_recurso") or "Contrato público / aquisição"
    elif _has_any(norm, ("chamada publica", "chamada pública", "chamamento")):
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_marinha"] = "chamada"
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "chamada_publica"

    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    nuclear_ctx = ("nuclear", "propulsao", "propulsão", "reator", "radioativid", "usina naval")
    naval_defesa = ("naval", "marinha", "defesa", "arsenal", "armamento")
    if _has_any(norm_body, nuclear_ctx):
        extras["setor_estrategico"] = ["nuclear", "defesa"]
    elif _has_any(norm_body, naval_defesa):
        extras["setor_estrategico"] = ["defesa"]
    else:
        extras["setor_estrategico"] = []

    extras["metodo_classificacao"] = "marinha_local_calibration"


def calibrate_amazul_extras(item: Dict[str, Any]) -> None:
    """
    AMAZUL: idem Marinha; nuclear/defesa só com evidência forte (evita rotular compra genérica como nuclear).
    Força tipo_recurso de contratação/licitação quando há compra pública — texto/PDF DOU agregado não deve
    deixar Prêmio/Subvenção/Reembolsável herdados do transformer.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "amazul.mar.mil.br" not in lk:
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm_body = _normalize(" ".join([tit, desc]))
    norm = _normalize(" ".join([tit, desc, lk]))

    lk_licit_hub = "/acesso-a-informacao/licitacoes-e-contratos/" in lk
    lk_procurement_slug = any(
        x in lk
        for x in (
            "dispensa-de-licitacao",
            "dispensa-de-licitação",
            "pregao",
            "pregão",
            "edital",
            "contrato",
            "uasg",
            "nup",
        )
    )

    procurement = (
        "pregao",
        "pregão",
        "licit",
        "dispensa",
        "compra publica",
        "compra pública",
        "contratacao",
        "contratação",
        "aquisicao",
        "aquisição",
        "uasg",
        "modalidade licit",
        "edital de licit",
        "processo licit",
        "termo de referencia",
        "termo de referência",
        "pncp",
        "fornecedor",
        "fornecedora",
        "contratada",
        "contratante",
        "objeto",
        "ratificada",
        "inexigibilidade",
        "processo administrativo",
        "numero unico de protocolo",
        "número único de protocolo",
        "edital",
    )
    procurement_hit = _has_any(norm, procurement) or (lk_licit_hub and lk_procurement_slug)
    concurso = (
        "concurso publico",
        "concurso público",
        "edital de abertura de concurso",
        "prova objetiva",
        "processo seletivo",
        "cadastro de reserva",
    )
    nuclear_strong = (
        "propulsao nuclear",
        "propulsão nuclear",
        "combustivel nuclear",
        "combustível nuclear",
        "laboratorio nuclear",
        "laboratório nuclear",
        "reatores navais",
        "fonte neutronica",
        "fonte neutrônica",
    )

    if _has_any(norm, concurso) and not procurement_hit:
        extras["tipo_oportunidade"] = "processo_seletivo"
        extras["tipo_conteudo_amazul"] = "concurso_ou_seletivo"
        extras["publico_alvo"] = ["candidatos", "profissionais"]
        extras["perfil_ideal"] = "candidatos"
        item["tipo_recurso"] = "Seleção / emprego público"
        item["reembolsavel"] = False
        extras["reembolsavel"] = False
    elif procurement_hit:
        extras["tipo_oportunidade"] = "licitacao"
        extras["tipo_conteudo_amazul"] = "compra_licitacao"
        extras.setdefault("publico_alvo", ["empresas", "fornecedores"])
        extras["perfil_ideal"] = _prune_profile(["fornecedores", "empresa"], norm) or ["fornecedores"]
        item["tipo_recurso"] = "licitação"
        # Compra pública não é produto de crédito bancário; evita falso positivo
        # credito_tipo_recurso_incoerente quando o PDF menciona "crédito" no objeto (ex.: vale-transporte).
        item["reembolsavel"] = False
        extras["reembolsavel"] = False
    elif _has_any(norm, ("chamada publica", "chamada pública", "subven", "fomento")) and not lk_licit_hub:
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_amazul"] = "chamada_ou_fomento"
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or (
            "licitacao" if lk_licit_hub else "chamada_publica"
        )
        if lk_licit_hub:
            extras["tipo_conteudo_amazul"] = extras.get("tipo_conteudo_amazul") or "compra_licitacao"
            item["tipo_recurso"] = "licitação"
            extras.setdefault("publico_alvo", ["empresas", "fornecedores"])
            extras["perfil_ideal"] = extras.get("perfil_ideal") or (
                _prune_profile(["fornecedores", "empresa"], norm) or ["fornecedores"]
            )
            item["reembolsavel"] = False
            extras["reembolsavel"] = False

    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    if _has_any(norm_body, nuclear_strong) or (
        _has_any(norm_body, ("nuclear", "submarino", "propulsao", "propulsão")) and procurement_hit
    ):
        extras["setor_estrategico"] = ["nuclear", "defesa"]
    elif _has_any(
        norm_body,
        (
            "ministerio da defesa",
            "ministério da defesa",
            "comando da marinha",
            "defesa nacional",
            "tecnologias de defesa",
            "tecnologia de defesa",
        ),
    ):
        extras["setor_estrategico"] = ["defesa"]
    else:
        extras["setor_estrategico"] = []

    se_list = extras.get("setor_estrategico")
    if isinstance(se_list, list) and len(se_list) > 3:
        extras["setor_estrategico"] = se_list[:3]

    extras["metodo_classificacao"] = "amazul_local_calibration"


def calibrate_badesul_extras(item: Dict[str, Any]) -> None:
    """
    BADESUL: PDFs/listagens oficiais não devem herdar noticia_institucional do classificador global;
    setores de defesa/aero só com evidência no texto ou URL (evita setor_estrategico_muito_amplo indevido).
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "badesul.com.br" not in lk:
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([tit, desc, lk]))
    low_tit = tit.lower()

    oportunidade_markers = (
        "edital",
        "subven",
        "seleção pública",
        "selecao publica",
        "chamada",
        "programa",
        "linha de crédito",
        "linha de credito",
        "financiamento",
        "credito",
        "crédito",
        "capital de giro",
        "microcredito",
        "microcrédito",
    )
    cur_to = str(extras.get("tipo_oportunidade") or item.get("tipo_oportunidade") or "").strip().lower()
    looks_oportunidade = any(m in low_tit for m in oportunidade_markers) or _has_any(norm, oportunidade_markers)
    if looks_oportunidade and cur_to in ("noticia_institucional", "noticia", "pagina_institucional", "pesquisa", ""):
        tr = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "").lower()
        if "subven" in low_tit or tr == "subvencao":
            extras["tipo_oportunidade"] = "programa"
        elif any(k in low_tit for k in ("crédito", "credito", "financiamento", "linha")):
            extras["tipo_oportunidade"] = "linha_de_credito"
        else:
            extras["tipo_oportunidade"] = "programa"
        item["tipo_oportunidade"] = extras["tipo_oportunidade"]

    defesa_ctx = (
        "defesa",
        "aeroespacial",
        "militar",
        "exercito",
        "exército",
        "marinha",
        "aeronautica",
        "aeronáutica",
        "forças armadas",
        "forcas armadas",
        "dual use",
        "dual-use",
    )
    se = extras.get("setor_estrategico")
    if isinstance(se, str):
        se_list = [se] if se.strip() else []
    elif isinstance(se, list):
        se_list = [str(x).strip() for x in se if str(x).strip()]
    else:
        se_list = []
    noisy_sectors = {"aeroespacial", "defesa_industrial", "defesa", "dual_use"}
    if se_list and noisy_sectors.intersection({s.lower() for s in se_list}) and not _has_any(norm, defesa_ctx):
        extras["setor_estrategico"] = ["desenvolvimento_regional"]

    extras["metodo_classificacao"] = "badesul_local_calibration"


def calibrate_dcta_ita_iae_extras(item: Dict[str, Any]) -> None:
    """
    DCTA/ITA/IAE (gov.br): tipo_oportunidade só com evidência; defesa/aeroespacial e área
    tecnológica só com contexto; perfil fornecedor vs académico conforme o objeto.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "gov.br" not in lk or not any(x in lk for x in ("/dcta/", "/ita/", "/iae/")):
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm_body = _normalize(" ".join([tit, desc]))
    norm = _normalize(" ".join([tit, desc, lk]))

    procurement = (
        "pregao",
        "pregão",
        "licit",
        "dispensa",
        "compra publica",
        "compra pública",
        "contratacao",
        "contratação",
        "uasg",
        "modalidade licit",
        "edital de licit",
        "processo licit",
        "aquisicao",
        "aquisição",
        "termo de referencia",
        "termo de referência",
        "pncp",
    )
    concurso_publico = (
        "concurso publico",
        "concurso público",
        "lei 8112",
        "lei8112",
        "quadro de pessoal",
        "provimento efetivo",
        "cargo publico",
        "cargo público",
    )
    academico = (
        "mestrado",
        "doutorado",
        "stricto sensu",
        "lato sensu",
        "pos-graduacao",
        "pós-graduação",
        "ingresso",
        "programa de pos",
        "ppg",
        "selecao de aluno",
        "seleção de aluno",
        "bolsa",
        "pesquisador visitante",
    )
    chamada_fomento = (
        "chamada publica",
        "chamada pública",
        "chamamento",
        "fomento",
        "financiamento de pesquisa",
        "linha de pesquisa",
        "proposta de projeto",
        "subvencao",
        "subvenção",
    )

    if _has_any(norm, procurement):
        extras["tipo_oportunidade"] = "licitacao"
        extras["tipo_conteudo_dcta"] = "compra_licitacao"
        item["tipo_recurso"] = item.get("tipo_recurso") or "Contrato público / aquisição"
        extras["publico_alvo"] = _unique_preserve(
            list(extras.get("publico_alvo") or []) + ["empresas", "fornecedores"]
        )
        extras["perfil_ideal"] = _prune_profile(["fornecedores", "empresa"], norm) or ["fornecedores"]
    elif _has_any(norm, concurso_publico) and not _has_any(norm, procurement):
        extras["tipo_oportunidade"] = "processo_seletivo"
        extras["tipo_conteudo_dcta"] = "concurso_institucional"
        item["tipo_recurso"] = item.get("tipo_recurso") or "Seleção / emprego público"
        extras["publico_alvo"] = ["candidatos", "profissionais"]
        extras["perfil_ideal"] = "candidatos"
    elif _has_any(norm, academico) and not _has_any(norm, procurement):
        extras["tipo_oportunidade"] = "edital_academico"
        extras["tipo_conteudo_dcta"] = "ensino_pesquisa"
        item["tipo_recurso"] = item.get("tipo_recurso") or "Bolsa / Auxílio"
        extras["perfil_ideal"] = _prune_profile(["pesquisadores", "universidades"], norm) or [
            "pesquisadores",
            "universidades",
        ]
    elif _has_any(norm, chamada_fomento) or _has_any(norm, ("edital", "selecao", "seleção", "programa")):
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_dcta"] = "chamada_ou_fomento"
    else:
        extras.pop("tipo_oportunidade", None)
        extras["tipo_conteudo_dcta"] = "sem_rotulo_forte"

    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    aero_tech = (
        "aeroespacial",
        "foguetes",
        "satelite",
        "satélite",
        "propulsao espacial",
        "orbita",
        "órbita",
        "aviação militar",
        "aviacao militar",
        "missil",
        "míssil",
        "radar aero",
        "sistemas espaciais",
    )
    area_t = extras.get("area_tecnologica")
    if isinstance(area_t, list) and area_t and not _has_any(norm_body, aero_tech + TECH_STRONG_MARKERS):
        extras["area_tecnologica"] = []
    if _has_any(norm_body, aero_tech):
        extras["area_tecnologica"] = _unique_preserve(list(extras.get("area_tecnologica") or []) + ["aeroespacial"])[:6]

    defesa_strong = (
        "força aérea brasileira",
        "forca aérea brasileira",
        "forca aerea brasileira",
        "defesa aeroespacial",
        "comando aereo",
        "comando aéreo",
        "sistema de armas",
        "projeto estrategico de defesa",
        "projeto estratégico de defesa",
    )
    mil_aero_ctx = (
        "defesa nacional",
        "forca aerea",
        "força aérea",
        "comando aereo",
        "comando aéreo",
        "aeronautica militar",
        "aviacao militar",
        "estado maior",
    )
    if _has_any(norm_body, defesa_strong) or (
        _has_any(norm_body, mil_aero_ctx)
        and _has_any(norm, procurement + aero_tech + ("missil", "míssil", "caça", "caca ", "radar"))
    ):
        extras["setor_estrategico"] = (
            ["defesa", "aeroespacial"] if _has_any(norm_body, aero_tech) else ["defesa"]
        )
    elif _has_any(norm_body, ("aeroespacial", "satelite", "satélite", "foguete")):
        extras["setor_estrategico"] = ["aeroespacial"]
    else:
        extras["setor_estrategico"] = []

    extras["metodo_classificacao"] = "dcta_ita_iae_local_calibration"


def calibrate_horizon_europe_extras(item: Dict[str, Any]) -> None:
    """
    Calibração local Horizon Europe (sem gate global): tópicos oficiais topic-details/horizon-*;
    outras páginas europa.eu mantêm heurística por texto.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "europa.eu" not in lk and "ec.europa" not in lk:
        return
    tit = str(item.get("titulo") or "").strip()
    desc = str(item.get("descricao") or "").strip()
    norm = _normalize(" ".join([tit, desc, lk]))

    extras["idioma_original"] = extras.get("idioma_original") or "en"
    extras.setdefault("pais", "União Europeia")
    extras.setdefault("regiao", "Europa")

    topic_m = re.search(r"/topic-details/(horizon-[^/?#]+)", lk, re.IGNORECASE)
    if topic_m:
        topic_slug = topic_m.group(1).strip()
        extras["topic_id"] = topic_slug
        extras["call_code"] = topic_slug
        extras["programa"] = "Horizon Europe"
        extras["origem_portal"] = "Funding & Tenders Portal"
        extras["tipo_conteudo_horizon"] = "funding_topic"
        extras["tipo_oportunidade"] = "funding_opportunity"
        item["tipo_recurso"] = "fomento"
        extras["tipo_recurso"] = "fomento"
        extras["natureza_recurso"] = "nao_reembolsavel"
        extras["classificacao_confianca"] = "media"

        if len(desc) < 400:
            extras["area"] = []
            extras["setor_estrategico"] = []
            extras["setor_economico"] = []
            extras["thematic_tags"] = []
            extras["thematic_confidence"] = 0.0
            extras["publico_alvo"] = []

        labels: List[str] = []
        if _has_any(norm, ("university", "higher education institution", "research organisation", "universidade")):
            labels.append("universidades")
        if _has_any(norm, ("sme", "startup", "industry", "enterprise", "company")):
            labels.extend(["empresas", "startups"])
        if _has_any(norm, ("researcher", "principal investigator", "pi ", "pesquisador", "docente")):
            labels.append("pesquisadores")
        if _has_any(norm, ("ict", "research and technology organisation", "technology centre")):
            labels.append("icts")
        if _has_any(norm, ("consortium", "partners", "partner")):
            labels.append("consorcio")
        if labels:
            pr = _prune_profile(_unique_preserve(labels), norm)
            extras["perfil_ideal"] = pr if pr else labels[:4]
        else:
            extras.pop("perfil_ideal", None)

        top_url = str(item.get("link") or "").strip()
        extras["links_oficiais"] = {
            "topico_oficial": top_url,
            "portal_funding_tenders": (
                "https://ec.europa.eu/info/funding-tenders/opportunities/portal/"
            ),
        }

        if len(desc) < 200:
            fb = (
                f"{tit} — Tópico do programa Horizon Europe no portal Funding & Tenders da Comissão Europeia. "
                "Consulte o link oficial para detalhes da chamada, condições, prazos e submissão."
            )
            item["descricao"] = fb
            extras["descricao_original"] = fb

        extras["metodo_classificacao"] = "horizon_europe_local_calibration"
        return

    if _has_any(norm, ("msca", "marie sklodowska", "doctoral network", "postdoctoral fellowship")):
        extras["tipo_oportunidade"] = "grant"
        extras["tipo_conteudo_horizon"] = "msca_or_similar"
    elif _has_any(
        norm,
        (
            "research and innovation action",
            "innovation action",
            "coordination and support",
        ),
    ):
        extras["tipo_oportunidade"] = "chamada_internacional"
        extras["tipo_conteudo_horizon"] = "r_and_i_action"
    elif _has_any(norm, ("topic", "call", "grant", "work programme", "submission", "deadline", "funding & tenders")):
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_horizon"] = "topic_or_call"
    else:
        extras.pop("tipo_oportunidade", None)
        extras["tipo_conteudo_horizon"] = "sem_rotulo_forte"

    if _has_any(norm, ("grant", "funding", "european commission", "eu funding", "horizon europe")):
        if item.get("tipo_recurso") in (None, "", "Não Especificado"):
            item["tipo_recurso"] = "Subvenção (Não Reembolsável)"
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    labels = []
    if _has_any(norm, ("university", "higher education institution", "research organisation", "universidade")):
        labels.append("universidades")
    if _has_any(norm, ("sme", "startup", "industry", "enterprise", "company")):
        labels.extend(["empresas", "startups"])
    if _has_any(norm, ("researcher", "principal investigator", "pi ", "pesquisador", "docente")):
        labels.append("pesquisadores")
    if _has_any(norm, ("consortium", "partners", "partner")):
        labels.append("consorcio")
    if labels:
        extras["perfil_ideal"] = _prune_profile(_unique_preserve(labels), norm) or labels[:4]

    area_hits: List[str] = []
    if _has_any(norm, ("energy", "battery", "hydrogen", "solar", "wind power")):
        area_hits.append("Energia")
    if _has_any(norm, ("health", "medicine", "clinical", "disease")):
        area_hits.append("Saúde")
    if _has_any(norm, ("climate", "environment", "biodiversity", "circular")):
        area_hits.append("Meio ambiente")
    if _has_any(norm, ("digital", "artificial intelligence", "quantum", "cyber", "software")):
        area_hits.append("Tecnologia e inovação")
    if area_hits:
        cur = extras.get("area")
        if isinstance(cur, str) and cur.strip():
            cur = [cur.strip()]
        if not isinstance(cur, list):
            cur = []
        extras["area"] = _unique_preserve(list(cur) + area_hits)[:8]

    extras["metodo_classificacao"] = "horizon_europe_local_calibration"


def _erc_apply_grant_slug(link: str) -> str:
    try:
        path = urlparse((link or "").strip().lower()).path.rstrip("/")
    except Exception:
        return ""
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 2 and parts[0] == "apply-grant":
        return parts[1]
    return ""


def calibrate_erc_extras(item: Dict[str, Any]) -> None:
    """ERC: grants por esquema (URL apply-grant/* ou texto); UE; sem área genérica sem evidência."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk_raw = str(item.get("link") or "")
    lk = lk_raw.lower()
    if "erc.europa.eu" not in lk:
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([tit, desc, lk]))
    slug = _erc_apply_grant_slug(lk_raw)

    extras["idioma_original"] = extras.get("idioma_original") or "en"
    extras.setdefault("pais", "União Europeia")
    extras.setdefault("regiao", "Europa")
    extras["origem_portal"] = extras.get("origem_portal") or "erc.europa.eu"
    extras["links_oficiais"] = {
        "pagina_oficial": lk_raw.strip(),
        "apply_grants_hub": "https://erc.europa.eu/apply-grant",
    }
    if slug:
        extras["erc_scheme_slug"] = slug

    def _from_slug() -> tuple[str, str]:
        if slug == "starting-grant":
            return "grant", "starting_grant"
        if slug == "consolidator-grant":
            return "grant", "consolidator_grant"
        if slug == "advanced-grant":
            return "grant", "advanced_grant"
        if slug == "synergy-grant":
            return "grant", "synergy_grant"
        if slug == "proof-concept":
            return "grant", "proof_of_concept"
        if slug == "erc-plus-grant":
            return "grant", "erc_plus_grant"
        if slug in ("additional-opportunities", "erc-ukraine", "non-european-researchers"):
            return "chamada_publica", slug.replace("-", "_")
        return "", ""

    tipo_op, tcont = _from_slug()
    if not tipo_op:
        if _has_any(norm, ("starting grant", "starting grants")):
            tipo_op, tcont = "grant", "starting_grant"
        elif _has_any(norm, ("consolidator grant", "consolidator")):
            tipo_op, tcont = "grant", "consolidator_grant"
        elif _has_any(norm, ("advanced grant",)):
            tipo_op, tcont = "grant", "advanced_grant"
        elif _has_any(norm, ("synergy grant", "synergy grants")):
            tipo_op, tcont = "grant", "synergy_grant"
        elif _has_any(norm, ("proof of concept",)):
            tipo_op, tcont = "grant", "proof_of_concept"
        elif _has_any(norm, ("call", "deadline", "proposal", "applicant")):
            tipo_op, tcont = "chamada_publica", "open_call"

    if tipo_op:
        extras["tipo_oportunidade"] = tipo_op
        extras["tipo_conteudo_erc"] = tcont
    else:
        extras.pop("tipo_oportunidade", None)
        extras["tipo_conteudo_erc"] = "sem_rotulo_forte"

    item["tipo_recurso"] = "fomento"
    extras["tipo_recurso"] = "fomento"

    if extras.get("tipo_oportunidade") == "grant":
        extras["natureza_recurso"] = "nao_reembolsavel"

    labels = ["pesquisadores", "universidades", "icts"]
    if _has_any(norm, ("professor", "faculty", "docente", "lecturer")):
        labels.append("professores")
    pr = _prune_profile(_unique_preserve(labels), norm)
    if pr:
        extras["perfil_ideal"] = pr
    elif slug:
        extras["perfil_ideal"] = ["pesquisadores", "universidades", "icts"]

    if _has_any(norm, SCIENCE_STRONG_MARKERS):
        extras["area"] = ["Pesquisa científica"]
    else:
        extras.pop("area", None)

    extras["metodo_classificacao"] = "erc_local_calibration"


def calibrate_doe_arpae_extras(item: Dict[str, Any]) -> None:
    """DOE / ARPA-E: funding opportunity / programa; EUA; energia por evidência."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if not any(
        s in lk
        for s in (
            "arpa-e.energy.gov",
            "arpa-e-foa.energy.gov",
            "energy.gov",
        )
    ):
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([tit, desc, lk]))

    extras["idioma_original"] = extras.get("idioma_original") or "en"
    extras.setdefault("pais", "Estados Unidos")
    extras.setdefault("regiao", "América do Norte")
    extras.setdefault("origem_portal", "ARPA-E eXCHANGE" if "arpa-e-foa.energy.gov" in lk else "energy.gov")

    if _has_any(norm, ("rfi-",)) and _has_any(norm, ("teaming", "announcement")):
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_arpae"] = "teaming_partner_notice"
    elif "de-foa-" in norm or ("arpa-e-foa.energy.gov" in lk and "#foaid" in lk):
        extras["tipo_oportunidade"] = "funding_opportunity"
        extras["tipo_conteudo_arpae"] = "foa_or_announcement"
    elif _has_any(norm, ("foa", "funding opportunity announcement", "solicitation", "funding opportunity", "nofo")):
        extras["tipo_oportunidade"] = "funding_opportunity"
        extras["tipo_conteudo_arpae"] = "foa_or_announcement"
    elif _has_any(norm, ("program", "technical", "workshop")) and _has_any(norm, ("arpa", "energy", "eere")):
        extras["tipo_oportunidade"] = "programa"
        extras["tipo_conteudo_arpae"] = "program_or_network"
    elif _has_any(norm, ("apply", "concept paper", "full application")):
        extras["tipo_oportunidade"] = "chamada_publica"
        extras["tipo_conteudo_arpae"] = "application_window"
    else:
        extras.pop("tipo_oportunidade", None)
        extras["tipo_conteudo_arpae"] = "sem_rotulo_forte"

    item["tipo_recurso"] = "fomento"
    extras["tipo_recurso"] = "fomento"

    labels: List[str] = []
    if _has_any(norm, ("company", "industry", "startup", "firm")):
        labels.extend(["empresas", "startups"])
    if _has_any(norm, ("university", "national laboratory", "researcher", "pi ")):
        labels.extend(["universidades", "pesquisadores"])
    if labels:
        extras["perfil_ideal"] = _prune_profile(_unique_preserve(labels), norm) or labels[:4]
    elif "de-foa-" in norm or ("arpa-e-foa.energy.gov" in lk and "#foaid" in lk):
        extras["perfil_ideal"] = ["pesquisadores", "empresas", "universidades", "laboratórios"]

    tech: List[str] = []
    if _has_any(norm, ("battery", "storage", "grid", "electricity")):
        tech.append("energia")
    if _has_any(norm, ("hydrogen", "fuel cell", "carbon capture", "ccus")):
        tech.append("energia")
    if _has_any(norm, ("material", "catalyst", "semiconductor")):
        tech.append("materiais avancados")
    if tech:
        extras["area_tecnologica"] = _unique_preserve(list(extras.get("area_tecnologica") or []) + tech)[:8]

    tags = extras.get("thematic_tags")
    if isinstance(tags, list) and tags:
        keep: List[str] = []
        for t in tags:
            if t == "aeroespacial" and not _has_any(
                norm,
                ("aerospace", "aviation", "aircraft", "satellite", "spacecraft", "launch vehicle", "rocket"),
            ):
                continue
            if t == "defesa" and not _has_any(norm, ("defense", "military", "weapon", "warfighter", "dod contract")):
                continue
            if t == "seguranca_publica" and not _has_any(norm, ("law enforcement", "police", "security force")):
                continue
            keep.append(t)
        extras["thematic_tags"] = keep

    extras["metodo_classificacao"] = "doe_arpae_local_calibration"


def calibrate_nato_diana_extras(item: Dict[str, Any]) -> None:
    """NATO DIANA: challenges/programa; OTAN; cibersegurança só com marcadores fortes (não usar 'security' isolado)."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "diana.nato.int" not in lk:
        return
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([tit, desc, lk]))

    extras["idioma_original"] = extras.get("idioma_original") or "en"
    extras.setdefault("regiao", "Internacional")
    extras.setdefault("origem_portal", "NATO DIANA (diana.nato.int)")

    cyber_strong = (
        "cybersecurity",
        "cyber security",
        "cyber defence",
        "cyber defense",
        "network security",
        "information security",
        "encryption",
        "cryptography",
        "cryptographic",
        "malware",
        "ransomware",
        "zero trust",
        "incident response",
        "secure systems",
    )

    raw_top = str(extras.get("tipo_oportunidade") or "").strip().lower()
    if raw_top in ("challenge", "programa", "chamada_publica", "accelerator"):
        extras["tipo_oportunidade"] = raw_top
    elif _has_any(norm, ("accelerator", "acceleration programme", "acceleration program")):
        extras["tipo_oportunidade"] = "accelerator"
    elif _has_any(norm, ("challenge", "challenge call", "challenge portal", "warfighter")):
        extras["tipo_oportunidade"] = "challenge"
    elif _has_any(norm, ("faq", "programme overview", "program overview", "eligibility")):
        extras["tipo_oportunidade"] = "programa"
    else:
        extras["tipo_oportunidade"] = "chamada_publica"

    tr = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "").strip().lower()
    if "invest" in tr:
        item["tipo_recurso"] = "fomento_investimento"
    elif _has_any(norm, ("challenge", "contractual funding", "trl", "accelerator", "sme", "startup")):
        item["tipo_recurso"] = "fomento_pdi"
    else:
        item["tipo_recurso"] = item.get("tipo_recurso") or "fomento_pdi"
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or "fomento_pdi")

    # Contexto institucional OTAN/DIANA: inovação em defesa / dual-use explícito no texto ou marca diana.
    se_in = extras.get("setor_estrategico")
    se: List[str] = [str(x) for x in se_in] if isinstance(se_in, list) else ([] if not se_in else [str(se_in)])
    if _has_any(norm, ("diana", "nato", "defence", "defense", "allied", "dual-use", "dual use")):
        se = _unique_preserve(se + ["inovacao_defesa", "dual_use"])[:8]
    extras["setor_estrategico"] = se

    labels: List[str] = []
    if _has_any(norm, ("startup", "sme", "small and medium", "enterprise")):
        labels.extend(["startups", "pequenas empresas"])
    if _has_any(norm, ("company", "industry", "firm")):
        labels.append("empresas")
    if _has_any(norm, ("university", "researcher", "laboratory", "laboratories")):
        labels.extend(["pesquisadores", "universidades"])
    if _has_any(norm, ("ict", "software", "digital solution", "data")):
        labels.append("icts")
    if labels:
        extras["perfil_ideal"] = _prune_profile(_unique_preserve(labels), norm) or labels[:6]
    else:
        extras["perfil_ideal"] = ["startups", "pequenas empresas", "empresas", "pesquisadores"]

    at_in = extras.get("area_tecnologica")
    at: List[str] = [str(x) for x in at_in] if isinstance(at_in, list) else ([] if not at_in else [str(at_in)])
    if not _has_any(norm, cyber_strong):
        at = [
            x
            for x in at
            if "ciber" not in str(x).lower() and "cyber" not in str(x).lower() and "crypt" not in str(x).lower()
        ]
    if _has_any(norm, cyber_strong):
        if not any("ciber" in str(x).lower() or "cyber" in str(x).lower() for x in at):
            at.append("ciberseguranca")
    extras["area_tecnologica"] = _unique_preserve(at)[:8]

    tags = extras.get("thematic_tags")
    if isinstance(tags, list) and tags:
        keep: List[str] = []
        for t in tags:
            if str(t).lower() in ("seguranca_publica",) and not _has_any(
                norm, ("law enforcement", "police", "cybersecurity", "cyber security")
            ):
                continue
            keep.append(t)
        extras["thematic_tags"] = keep

    extras["metodo_classificacao"] = "nato_diana_local_calibration"


def calibrate_iarpa_extras(item: Dict[str, Any]) -> None:
    """IARPA: programas / funding via Grants.gov ou páginas iarpa.gov; ciber só com marcadores fortes."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([tit, desc, lk]))
    if "iarpa.gov" not in lk and "grants.gov" not in lk:
        return
    prog_l = str(item.get("programa") or "").strip().lower()
    if "grants.gov" in lk and prog_l != "iarpa" and not _has_any(
        norm,
        (
            "iarpa",
            "intelligence advanced research",
            "intelligence advanced research projects",
            "odni",
            "national intelligence",
        ),
    ):
        return

    extras["pais"] = extras.get("pais") or "Estados Unidos"
    extras["idioma_original"] = extras.get("idioma_original") or "en"
    extras.setdefault("origem_portal", extras.get("origem_portal") or "IARPA")

    cyber_strong = (
        "cybersecurity",
        "cyber security",
        "cyber defence",
        "cyber defense",
        "network security",
        "information security",
        "encryption",
        "cryptography",
        "cryptographic",
        "malware",
        "ransomware",
        "zero trust",
        "incident response",
        "secure systems",
    )

    if _has_any(norm, ("broad agency announcement", "baa", "solicitation", "funding opportunity", "grants.gov", "foa", "rfp")):
        extras["tipo_oportunidade"] = "funding_opportunity"
        item["tipo_recurso"] = item.get("tipo_recurso") or "fomento_pdi"
        if _has_any(norm, ("contract", "performance work", "procurement")):
            item["tipo_recurso"] = "contrato_pesquisa"
    elif _has_any(norm, ("research program", "/research-programs/", "program overview")) or (
        "iarpa.gov" in lk and "/research-programs/" in lk
    ):
        extras["tipo_oportunidade"] = "programa_pesquisa"
        item["tipo_recurso"] = item.get("tipo_recurso") or "pesquisa_aplicada"
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "programa_pesquisa"
        item["tipo_recurso"] = item.get("tipo_recurso") or "fomento_pdi"
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or "fomento_pdi")

    se_in = extras.get("setor_estrategico")
    se: List[str] = [str(x) for x in se_in] if isinstance(se_in, list) else ([] if not se_in else [str(se_in)])
    if prog_l == "iarpa" or _has_any(
        norm,
        (
            "iarpa",
            "intelligence advanced research",
            "intelligence community",
            "odni",
            "office of the director of national intelligence",
            "national security research",
        ),
    ):
        se = _unique_preserve(se + ["inteligencia", "pesquisa_avancada"])[:8]
    extras["setor_estrategico"] = se

    labels: List[str] = []
    if _has_any(norm, ("university", "academia", "faculty", "graduate student")):
        labels.extend(["universidades", "pesquisadores"])
    if _has_any(norm, ("industry", "company", "firm", "contractor")):
        labels.append("empresas")
    if _has_any(norm, ("laboratory", "laboratories", "lab ")):
        labels.append("laboratórios")
    if _has_any(norm, ("ict", "software", "information technology")):
        labels.append("icts")
    if labels:
        extras["perfil_ideal"] = _prune_profile(_unique_preserve(labels), norm) or labels[:6]
    else:
        extras["perfil_ideal"] = ["universidades", "pesquisadores", "empresas", "laboratórios"]

    at_in = extras.get("area_tecnologica")
    at: List[str] = [str(x) for x in at_in] if isinstance(at_in, list) else ([] if not at_in else [str(at_in)])
    if not _has_any(norm, cyber_strong):
        at = [
            x
            for x in at
            if "ciber" not in str(x).lower() and "cyber" not in str(x).lower() and "crypt" not in str(x).lower()
        ]
    if _has_any(norm, cyber_strong):
        if not any("ciber" in str(x).lower() or "cyber" in str(x).lower() for x in at):
            at.append("ciberseguranca")
    extras["area_tecnologica"] = _unique_preserve(at)[:8]

    extras["metodo_classificacao"] = "iarpa_local_calibration"


def calibrate_sam_gov_extras(item: Dict[str, Any]) -> None:
    """SAM.gov: notice federal via API ou páginas sam.gov; tipos BAA/RFI/SBIR/solicitation; ciber só com marcadores fortes."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "sam.gov" not in lk and str(extras.get("origem_portal") or "").lower() != "sam.gov":
        return

    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    nid = str(extras.get("sam_gov_notice_id") or "").strip()
    if not nid and "/opp/" not in lk:
        extras["sam_gov_listagem_ou_hub"] = True
        extras["tipo_oportunidade"] = "generic_page"
        item["tipo_recurso"] = "nao_classificado"
        extras["tipo_recurso"] = "nao_classificado"
        extras.setdefault("classificacao_confianca", "baixa")
        extras["metodo_classificacao"] = "sam_gov_local_calibration"
        return

    dept = str(extras.get("sam_gov_department") or "")
    sub = str(extras.get("sam_gov_subtier") or "")
    office = str(extras.get("sam_gov_office") or "")
    nt_raw = str(extras.get("sam_gov_notice_type") or "").strip()
    bt_raw = str(extras.get("sam_gov_base_type") or "").strip()
    norm = _normalize(" ".join([tit, desc, lk, nt_raw, bt_raw, dept, sub, office]))

    cyber_strong = (
        "cybersecurity",
        "cyber security",
        "cyber defence",
        "cyber defense",
        "network security",
        "information security",
        "encryption",
        "cryptography",
        "cryptographic",
        "malware",
        "ransomware",
        "zero trust",
        "incident response",
        "secure systems",
    )

    extras["pais"] = extras.get("pais") or "Estados Unidos"
    extras["idioma_original"] = extras.get("idioma_original") or "en"
    extras.setdefault("origem_portal", extras.get("origem_portal") or "SAM.gov")

    noise_buy = _has_any(
        norm,
        (
            "janitorial",
            "custodial",
            "food service",
            "catering",
            "office supplies",
            "landscaping",
            "pest control",
            "toner",
            "copier",
            "vehicle rental",
            "shredding",
        ),
    )
    tech_signal = _has_any(
        norm,
        (
            "research",
            "r&d",
            "development",
            "sbir",
            "sttr",
            "baa",
            "solicitation",
            "laboratory",
            "engineering",
            "technology",
            "science",
            "nuclear",
            "energy",
            "defense",
            "defence",
            "darpa",
            "nasa",
            "doe",
            "sensor",
            "aerospace",
            "prototype",
            "innovation",
        ),
    )
    if noise_buy and not tech_signal:
        extras["sam_gov_ruido_compra_generica"] = True
        extras.setdefault("classificacao_confianca", "baixa")

    # Tipo de oportunidade / recurso (ordem: SBIR/STTR, BAA, RFI, sources sought, solicitation/RFP)
    if _has_any(norm, ("sbir", "sttr")):
        extras["tipo_oportunidade"] = "chamada_publica"
        item["tipo_recurso"] = "fomento_pdi"
        extras["sam_gov_small_business_program"] = True
    elif _has_any(norm, ("broad agency announcement", " baa ", "baa-", "type:baa")) or "baa" in nt_raw.lower():
        extras["tipo_oportunidade"] = "funding_opportunity"
        item["tipo_recurso"] = "fomento_pdi"
        if _has_any(norm, ("contract", "performance work statement", "statement of work")):
            item["tipo_recurso"] = "contrato_pesquisa"
    elif _has_any(norm, ("request for information", " rfi ", "rfi:", "type:rfi")) or "rfi" in nt_raw.lower():
        extras["tipo_oportunidade"] = "consulta_publica"
        extras["sam_gov_request_for_information"] = True
        item["tipo_recurso"] = "pesquisa_aplicada"
    elif "sources sought" in nt_raw.lower() or "source sought" in norm:
        extras["tipo_oportunidade"] = "sources_sought"
        item["tipo_recurso"] = "compra_publica"
    elif _has_any(
        norm,
        ("solicitation", " rfp ", "rfp:", "presolicitation", "combined synopsis", "special notice"),
    ) or any(x in nt_raw.lower() for x in ("solicitation", "presolicitation", "combined", "special notice")):
        extras["tipo_oportunidade"] = "compra_publica"
        item["tipo_recurso"] = "contrato_publico"
        if _has_any(norm, ("research", "development", "science", "technology", "laboratory")):
            item["tipo_recurso"] = "contrato_pesquisa"
    elif _has_any(norm, ("prototype", "prototyping", "pilot", "demonstration")):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "chamada_publica"
        item["tipo_recurso"] = "prototipo"
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "nao_classificado"

    extras["tipo_recurso"] = str(item.get("tipo_recurso") or "nao_classificado")

    se_in = extras.get("setor_estrategico")
    se: List[str] = [str(x) for x in se_in] if isinstance(se_in, list) else ([] if not se_in else [str(se_in)])
    if _has_any(norm, ("department of defense", "dod", "darpa", "navy", "air force", "army", "marine", "defense logistics", "pentagon")):
        se = _unique_preserve(se + ["defesa"])[:8]
    if _has_any(norm, ("department of energy", "doe", "arpa-e", "arpa e", "nnsa", "national laboratory", "national lab", "nuclear", "reactor", "radiation")):
        se = _unique_preserve(se + ["energia", "nuclear"])[:8]
    if _has_any(norm, ("nasa", "aerospace", "space ", "satellite", "propulsion")):
        se = _unique_preserve(se + ["aeroespacial"])[:8]
    if _has_any(norm, ("materials", "material science", "semiconductor", "photonics")):
        se = _unique_preserve(se + ["materiais"])[:8]
    if _has_any(norm, ("national science foundation", "scientific", "university", "laboratory", "research")):
        se = _unique_preserve(se + ["ciencia_tecnologia", "pesquisa_avancada"])[:8]
    extras["setor_estrategico"] = se

    labels: List[str] = []
    if _has_any(norm, ("small business", "sbir", "sttr", "sme ", "8(a)")):
        labels.extend(["pequena_empresa", "startup"])
    if _has_any(norm, ("university", "academic", "education", "college")):
        labels.extend(["universidade", "pesquisador"])
    if _has_any(norm, ("industry", "contractor", "vendor", "supplier", "offeror")):
        labels.extend(["empresa", "fornecedor"])
    if _has_any(norm, ("laboratory", "national lab", "national laboratory")):
        labels.append("laboratório")
    if _has_any(norm, ("ict", "information technology", "software")):
        labels.append("ICT")
    if labels:
        extras["perfil_ideal"] = _prune_profile(_unique_preserve(labels), norm) or labels[:8]
    else:
        extras["perfil_ideal"] = ["empresa", "fornecedor", "universidade", "pesquisador"]

    at_in = extras.get("area_tecnologica")
    at: List[str] = [str(x) for x in at_in] if isinstance(at_in, list) else ([] if not at_in else [str(at_in)])
    if not _has_any(norm, cyber_strong):
        at = [
            x
            for x in at
            if "ciber" not in str(x).lower() and "cyber" not in str(x).lower() and "crypt" not in str(x).lower()
        ]
    if _has_any(norm, cyber_strong):
        if not any("ciber" in str(x).lower() or "cyber" in str(x).lower() for x in at):
            at.append("ciberseguranca")
    extras["area_tecnologica"] = _unique_preserve(at)[:8]

    extras["metodo_classificacao"] = "sam_gov_local_calibration"


# --- Calibração local: fontes japonesas (lote 3A) ---------------------------------

_JA_SCRIPT_RE = re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF]")

_NUCLEAR_EVIDENCE: Tuple[str, ...] = (
    "原子力",
    "核融合",
    "核分裂",
    "核燃料",
    "放射線",
    "放射性",
    "nuclear",
    "radiation",
    "radioactive",
    "reactor",
    "nuclear fuel",
    "nuclear waste",
    "nuclear energy",
    "radiological",
)
_AERO_EVIDENCE: Tuple[str, ...] = (
    "航空宇宙",
    "宇宙開発",
    "衛星",
    "ロケット",
    "打ち上げ",
    "aerospace",
    "spacecraft",
    "satellite",
    "launch vehicle",
    "space mission",
)
_JA_PROCUREMENT: Tuple[str, ...] = (
    "調達",
    "入札",
    "見積",
    "競争入札",
    "随意契約",
)
_GRANT_OR_CALL_EVIDENCE: Tuple[str, ...] = (
    "grant",
    "funding opportunity",
    "公募",
    "助成",
    "補助金",
    "委託研究",
    "研究開発",
    "共同研究",
    "cr-est",
    "solicitation",
    "call for proposals",
)


def _japan_item_corpus(item: Dict[str, Any]) -> str:
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
    parts = [
        str(item.get("titulo") or ""),
        str(item.get("descricao") or ""),
        str(item.get("programa") or ""),
        str(item.get("acao") or ""),
        str(item.get("link") or ""),
        str(extras.get("titulo_original") or ""),
        str(extras.get("descricao_original") or ""),
        str(extras.get("objetivo") or ""),
    ]
    return " ".join(parts)


def _japan_norm(item: Dict[str, Any]) -> str:
    return _normalize(_japan_item_corpus(item))


def _japan_setor_as_list(extras: Dict[str, Any]) -> List[str]:
    v = extras.get("setor_estrategico")
    if isinstance(v, list):
        return _unique_preserve([str(x).strip() for x in v if str(x).strip()])
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def _japan_write_setor(extras: Dict[str, Any], sectors: List[str]) -> None:
    u = _unique_preserve(sectors)[:8]
    if not u:
        extras["setor_estrategico"] = "ciencia_tecnologia"
    elif len(u) == 1:
        extras["setor_estrategico"] = u[0]
    else:
        extras["setor_estrategico"] = u


def _japan_strip_sectors(sectors: List[str], drop: Tuple[str, ...]) -> List[str]:
    d = {x.lower() for x in drop}
    return [s for s in sectors if str(s).lower() not in d]


def _japan_text_has_script(text: str) -> bool:
    return bool(_JA_SCRIPT_RE.search(text or ""))


def _japan_apply_portal_metadata(
    item: Dict[str, Any],
    extras: Dict[str, Any],
    *,
    origem_portal: str,
) -> None:
    extras["pais"] = (extras.get("pais") or "").strip() or "Japão"
    if not str(extras.get("origem_portal") or "").strip():
        extras["origem_portal"] = origem_portal

    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    if not str(extras.get("titulo_original") or "").strip():
        extras["titulo_original"] = tit
    if not str(extras.get("descricao_original") or "").strip():
        extras["descricao_original"] = desc

    io = str(extras.get("idioma_original") or "").strip().lower()
    blob = tit + " " + desc
    if not io or io == "auto":
        if _japan_text_has_script(blob):
            extras["idioma_original"] = "ja"
        elif re.search(r"[a-zA-Z]{4,}", blob):
            extras["idioma_original"] = "en"
        else:
            extras["idioma_original"] = io or "ja"

    if str(extras.get("idioma_original") or "").lower() == "en" and tit:
        extras.setdefault("titulo_en", tit)
    desc_en = str(extras.get("descricao_en") or "").strip()
    if str(extras.get("idioma_original") or "").lower() == "en" and desc and not desc_en:
        extras.setdefault("descricao_en", desc[:8000])

    if str(extras.get("titulo_traduzido") or "").strip() or str(extras.get("descricao_traduzida") or "").strip():
        extras["traducao_automatica"] = True
    elif extras.get("traducao_automatica") is None:
        extras["traducao_automatica"] = False


def _japan_procurement_signal(norm: str, raw: str) -> bool:
    return _has_any(norm, PROCUREMENT_MARKERS) or any(p in (raw or "") for p in _JA_PROCUREMENT)


def _japan_grant_signal(norm: str, raw: str) -> bool:
    return _has_any(norm, _GRANT_OR_CALL_EVIDENCE) or any(p in (raw or "") for p in _GRANT_OR_CALL_EVIDENCE)


def calibrate_japan_jst_extras(item: Dict[str, Any]) -> None:
    """JST: fomento/pesquisa; sem nuclear/aero só por instituição; extras de idioma e portal."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    raw = _japan_item_corpus(item)
    norm = _japan_norm(item)
    _japan_apply_portal_metadata(item, extras, origem_portal="JST (jst.go.jp)")

    se = _japan_setor_as_list(extras)
    if not _has_any(norm, _NUCLEAR_EVIDENCE):
        se = _japan_strip_sectors(se, ("nuclear",))
    if not _has_any(norm, _AERO_EVIDENCE):
        se = _japan_strip_sectors(se, ("aeroespacial", "veiculos"))
    if not _has_any(norm, ("defesa", "defense", "defence", "防衛", "軍事")):
        se = _japan_strip_sectors(se, ("defesa", "defesa_industrial"))
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    if _japan_procurement_signal(norm, raw):
        extras["tipo_oportunidade"] = "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
        extras["perfil_ideal"] = _prune_profile(["fornecedor", "empresa", "pesquisador"], norm) or ["empresa", "fornecedor"]
    elif _japan_grant_signal(norm, raw):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "funding_opportunity"
        item["tipo_recurso"] = item.get("tipo_recurso") or "fomento_pdi"
        labs = ["pesquisador", "universidades", "icts", "empresas"]
        extras["perfil_ideal"] = _prune_profile(labs, norm) or ["pesquisador", "universidades"]
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "programa_pesquisa"
        item["tipo_recurso"] = item.get("tipo_recurso") or "pesquisa_aplicada"
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    extras["metodo_classificacao"] = "japan_jst_local_calibration"


def calibrate_japan_jaea_extras(item: Dict[str, Any]) -> None:
    """JAEA: nuclear e procurement só com evidência textual; instituição não basta para setor."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    raw = _japan_item_corpus(item)
    norm = _japan_norm(item)
    _japan_apply_portal_metadata(item, extras, origem_portal="JAEA (jaea.go.jp)")

    se = _japan_setor_as_list(extras)
    proc = _japan_procurement_signal(norm, raw)
    nuclear_ok = _has_any(norm, _NUCLEAR_EVIDENCE)
    if not nuclear_ok:
        se = _japan_strip_sectors(se, ("nuclear", "energia"))
    if proc and not _has_any(norm, _NUCLEAR_EVIDENCE):
        se = _japan_strip_sectors(se, ("nuclear",))
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    if proc:
        extras["tipo_oportunidade"] = "licitacao" if _has_any(norm, ("入札", "pregao", "pregão", "licitacao", "tender")) else "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
        extras["perfil_ideal"] = _prune_profile(["fornecedor", "empresa"], norm) or ["empresa", "fornecedor"]
    elif _japan_grant_signal(norm, raw) or _has_any(norm, ("研究", "research", "cooperation", "協力")):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "chamada_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "pesquisa_aplicada"
        extras["perfil_ideal"] = _prune_profile(["pesquisador", "universidades", "icts"], norm) or ["pesquisador", "universidades"]
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    extras["metodo_classificacao"] = "japan_jaea_local_calibration"


def calibrate_japan_jaxa_extras(item: Dict[str, Any]) -> None:
    """JAXA: aeroespacial só com evidência; procurement separado de grant/chamada."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    raw = _japan_item_corpus(item)
    norm = _japan_norm(item)
    _japan_apply_portal_metadata(item, extras, origem_portal="JAXA (jaxa.jp)")

    se = _japan_setor_as_list(extras)
    if not _has_any(norm, _AERO_EVIDENCE):
        se = _japan_strip_sectors(se, ("aeroespacial", "veiculos"))
    if not _has_any(norm, _NUCLEAR_EVIDENCE):
        se = _japan_strip_sectors(se, ("nuclear",))
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    if _japan_procurement_signal(norm, raw):
        extras["tipo_oportunidade"] = "procurement" if "procurement" in norm or "調達" in raw else "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
        extras["perfil_ideal"] = _prune_profile(["fornecedor", "empresa"], norm) or ["empresa", "fornecedor"]
    elif _japan_grant_signal(norm, raw):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "chamada_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "fomento_pdi"
        extras["perfil_ideal"] = _prune_profile(["pesquisador", "universidades", "icts", "empresas"], norm) or ["pesquisador", "universidades"]
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    extras["metodo_classificacao"] = "japan_jaxa_local_calibration"


def calibrate_japan_e_rad_extras(item: Dict[str, Any]) -> None:
    """e-Rad: grants/chamadas; sem setores forçados; portal e idioma."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    raw = _japan_item_corpus(item)
    norm = _japan_norm(item)
    lk = str(item.get("link") or "").lower()
    _japan_apply_portal_metadata(item, extras, origem_portal="e-Rad (e-rad.go.jp)")

    se = _japan_setor_as_list(extras)
    if not _has_any(norm, _NUCLEAR_EVIDENCE):
        se = _japan_strip_sectors(se, ("nuclear",))
    if not _has_any(norm, _AERO_EVIDENCE):
        se = _japan_strip_sectors(se, ("aeroespacial", "veiculos"))
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    if "/news/" in lk or "/topics/" in lk:
        extras.setdefault("e_rad_listing_or_hub", True)

    if _japan_procurement_signal(norm, raw):
        extras["tipo_oportunidade"] = "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "funding_opportunity"
        item["tipo_recurso"] = item.get("tipo_recurso") or "fomento_pdi"
    extras["perfil_ideal"] = _prune_profile(["pesquisador", "universidades", "icts"], norm) or ["pesquisador", "universidades"]
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    extras["metodo_classificacao"] = "japan_e_rad_local_calibration"


# --- Calibração local: fontes chinesas (lote 3B) ---------------------------------

_ZH_SCRIPT_RE = re.compile(r"[\u4E00-\u9FFF]")
_ZH_PROCUREMENT_RAW: Tuple[str, ...] = (
    "招标",
    "采购",
    "中标",
    "投标",
    "公示",
    "供应商",
    "合同",
    "竞价",
)
_CHINA_DEFENSE_STRONG: Tuple[str, ...] = (
    "国防",
    "军工",
    "防务",
    "武器装备",
    "武器系统",
    "military",
    "defense",
    "defence",
    "armament",
    "munition",
)


def _china_item_corpus(item: Dict[str, Any]) -> str:
    return _japan_item_corpus(item)


def _china_norm(item: Dict[str, Any]) -> str:
    return _japan_norm(item)


def _china_apply_portal_metadata(
    item: Dict[str, Any],
    extras: Dict[str, Any],
    *,
    origem_portal: str,
) -> None:
    extras["pais"] = (extras.get("pais") or "").strip() or "China"
    if not str(extras.get("origem_portal") or "").strip():
        extras["origem_portal"] = origem_portal

    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    lk = str(item.get("link") or "")
    if not str(extras.get("titulo_original") or "").strip():
        extras["titulo_original"] = tit
    if not str(extras.get("descricao_original") or "").strip():
        extras["descricao_original"] = desc

    io = str(extras.get("idioma_original") or "").strip().lower()
    blob = tit + " " + desc
    if not io or io == "auto":
        if _ZH_SCRIPT_RE.search(blob):
            extras["idioma_original"] = "zh"
        elif re.search(r"[a-zA-Z]{5,}", blob) and not _ZH_SCRIPT_RE.search(blob):
            extras["idioma_original"] = "en"
        else:
            extras["idioma_original"] = io or "zh"

    low = lk.lower()
    if ("/english/" in low or "en." in low) and tit and not _ZH_SCRIPT_RE.search(tit):
        extras.setdefault("titulo_en", tit)
    if str(extras.get("idioma_original") or "").lower() == "en" and desc and not str(extras.get("descricao_en") or "").strip():
        extras.setdefault("descricao_en", desc[:8000])

    if str(extras.get("titulo_traduzido") or "").strip() or str(extras.get("descricao_traduzida") or "").strip():
        extras["traducao_automatica"] = True
    elif extras.get("traducao_automatica") is None:
        extras["traducao_automatica"] = False


def _china_procurement_signal(norm: str, raw: str) -> bool:
    return _japan_procurement_signal(norm, raw) or any(p in (raw or "") for p in _ZH_PROCUREMENT_RAW)


def _china_grant_signal(norm: str, raw: str) -> bool:
    return _japan_grant_signal(norm, raw) or any(
        p in (raw or "") for p in ("基金", "课题", "项目申报", "资助", "自然科学", "博士后", "青年基金")
    )


def calibrate_china_nsfc_extras(item: Dict[str, Any]) -> None:
    """NSFC: fomento/grant; nuclear só com evidência lexical; China/zh."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "nsfc.gov.cn" not in lk:
        return
    raw = _china_item_corpus(item)
    norm = _china_norm(item)
    _china_apply_portal_metadata(item, extras, origem_portal="NSFC (nsfc.gov.cn)")

    se = _japan_setor_as_list(extras)
    if not _has_any(norm, _NUCLEAR_EVIDENCE):
        se = _japan_strip_sectors(se, ("nuclear",))
    if not _has_any(norm, _AERO_EVIDENCE):
        se = _japan_strip_sectors(se, ("aeroespacial", "veiculos"))
    if not _has_any(norm, _CHINA_DEFENSE_STRONG):
        se = _japan_strip_sectors(se, ("defesa", "defesa_industrial"))
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    if _china_procurement_signal(norm, raw):
        extras["tipo_oportunidade"] = "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
        extras["perfil_ideal"] = _prune_profile(["fornecedor", "empresa"], norm) or ["empresa", "fornecedor"]
    else:
        # grant / guia NSFC: evitar "chamada_publica" (substring "chamada" dispara auditoria sem
        # tokens PT no blob) e "fomento_pdi" (substring "fomento") sem garantia lexical em EN.
        top = str(extras.get("tipo_oportunidade") or "").strip().lower()
        if top == "funding_opportunity":
            extras["tipo_oportunidade"] = "funding_opportunity"
        elif top == "grant":
            extras["tipo_oportunidade"] = "grant"
        else:
            extras["tipo_oportunidade"] = "grant" if top in ("chamada_publica", "") else top
        item["tipo_recurso"] = "Grant para pesquisa competitiva"
        extras["perfil_ideal"] = _prune_profile(["pesquisador", "universidades", "icts"], norm) or [
            "pesquisador",
            "universidades",
        ]
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")
    extras["metodo_classificacao"] = "china_nsfc_local_calibration"


def calibrate_china_cnnc_extras(item: Dict[str, Any]) -> None:
    """CNNC: nuclear e procurement só com evidência; separar de notícia institucional."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "cnnc.com.cn" not in lk:
        return
    raw = _china_item_corpus(item)
    norm = _china_norm(item)
    _china_apply_portal_metadata(item, extras, origem_portal="CNNC (cnnc.com.cn)")

    se = _japan_setor_as_list(extras)
    nuclear_ok = _has_any(norm, _NUCLEAR_EVIDENCE) or any(p in raw for p in ("核电", "核燃料", "核能", "反应堆"))
    if not nuclear_ok:
        se = _japan_strip_sectors(se, ("nuclear", "energia"))
    if not _has_any(norm, _AERO_EVIDENCE):
        se = _japan_strip_sectors(se, ("aeroespacial", "veiculos"))
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    if _china_procurement_signal(norm, raw):
        extras["tipo_oportunidade"] = "licitacao" if _has_any(norm, ("招标", "投标", "tender", "bid")) else "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
        extras["perfil_ideal"] = _prune_profile(["fornecedor", "empresa"], norm) or ["empresa", "fornecedor"]
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "noticia_institucional"
        item["tipo_recurso"] = item.get("tipo_recurso") or "pesquisa_aplicada"
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")
    extras["metodo_classificacao"] = "china_cnnc_local_calibration"


def calibrate_china_avic_extras(item: Dict[str, Any]) -> None:
    """AVIC: aeroespacial/defesa só com evidência; procurement separado."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "avic.com" not in lk:
        return
    raw = _china_item_corpus(item)
    norm = _china_norm(item)
    _china_apply_portal_metadata(item, extras, origem_portal="AVIC (avic.com)")

    se = _japan_setor_as_list(extras)
    if not _has_any(norm, _AERO_EVIDENCE) and not any(p in raw for p in ("航空", "航天", "飞机", "发动机")):
        se = _japan_strip_sectors(se, ("aeroespacial", "veiculos"))
    if not _has_any(norm, _CHINA_DEFENSE_STRONG):
        se = _japan_strip_sectors(se, ("defesa", "defesa_industrial"))
    if not _has_any(norm, _NUCLEAR_EVIDENCE):
        se = _japan_strip_sectors(se, ("nuclear",))
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    # Recrutamento campus (evidência no texto; não compra nem fomento; menu do site não é defesa.)
    if _ZH_SCRIPT_RE.search(raw) and "招聘" in raw and any(p in raw for p in ("校园招聘", "纪检监察")):
        se = _japan_setor_as_list(extras)
        se = _japan_strip_sectors(se, ("defesa", "defesa_industrial", "aeroespacial", "veiculos", "nuclear"))
        if not se:
            se = ["ciencia_tecnologia"]
        _japan_write_setor(extras, se)
        extras["tipo_oportunidade"] = "processo_seletivo"
        item["tipo_recurso"] = item.get("tipo_recurso") or "Seleção / emprego público"
        extras["perfil_ideal"] = _prune_profile(["pesquisador", "universidades"], norm) or ["pesquisador"]
        extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")
        extras["metodo_classificacao"] = "china_avic_local_calibration"
        return

    if _china_procurement_signal(norm, raw):
        extras["tipo_oportunidade"] = "procurement" if "procurement" in norm or "供应商" in raw else "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
        extras["perfil_ideal"] = _prune_profile(["fornecedor", "empresa"], norm) or ["empresa", "fornecedor"]
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "noticia_institucional"
        item["tipo_recurso"] = item.get("tipo_recurso") or "pesquisa_aplicada"
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")
    extras["metodo_classificacao"] = "china_avic_local_calibration"


def calibrate_china_norinco_extras(item: Dict[str, Any]) -> None:
    """NORINCO: defesa/procurement só com evidência; evitar rotular tudo como defesa."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if "norincogroup.com.cn" not in lk:
        return
    raw = _china_item_corpus(item)
    norm = _china_norm(item)
    _china_apply_portal_metadata(item, extras, origem_portal="NORINCO Group (norincogroup.com.cn)")

    se = _japan_setor_as_list(extras)
    if not _has_any(norm, _CHINA_DEFENSE_STRONG) and not any(p in raw for p in ("军工", "防务", "装备")):
        se = _japan_strip_sectors(se, ("defesa", "defesa_industrial"))
    if not _has_any(norm, _NUCLEAR_EVIDENCE):
        se = _japan_strip_sectors(se, ("nuclear",))
    if not _has_any(norm, _AERO_EVIDENCE):
        se = _japan_strip_sectors(se, ("aeroespacial", "veiculos"))
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    if _china_procurement_signal(norm, raw):
        extras["tipo_oportunidade"] = "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
        extras["perfil_ideal"] = _prune_profile(["fornecedor", "empresa"], norm) or ["empresa", "fornecedor"]
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "noticia_institucional"
        item["tipo_recurso"] = item.get("tipo_recurso") or "pesquisa_aplicada"
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")
    extras["metodo_classificacao"] = "china_norinco_local_calibration"


def calibrate_china_university_procurement_extras(item: Dict[str, Any]) -> None:
    """Universidades CN: licitação explícita vs avisos de fundos (NSFC/MOST) replicados no portal."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if not any(h in lk for h in ("tsinghua.edu.cn", "pku.edu.cn", "ustc.edu.cn")):
        return
    raw = _china_item_corpus(item)
    norm = _china_norm(item)
    portal = "USTC (ustc.edu.cn)" if "ustc.edu.cn" in lk else "China university procurement (Tsinghua/PKU/USTC)"
    _china_apply_portal_metadata(item, extras, origem_portal=portal)

    se = _japan_setor_as_list(extras)
    se = _japan_strip_sectors(se, ("nuclear",)) if not _has_any(norm, _NUCLEAR_EVIDENCE) else se
    if not se:
        se = ["ciencia_tecnologia"]
    _japan_write_setor(extras, se)

    # "采购" etc. aparecem em textos longos de ciência sem ser compra pública — exigir padrão de licitação.
    procurement_strict = _has_any(norm, ("招标", "投标", "tender", "bid", "竞价")) or (
        "采购" in (raw or "") and any(p in (raw or "") for p in ("公开招标", "采购公告", "中标", "政府采购"))
    )
    if procurement_strict:
        extras["tipo_oportunidade"] = "licitacao" if _has_any(norm, ("招标", "投标", "tender", "bid")) else "compra_publica"
        item["tipo_recurso"] = item.get("tipo_recurso") or "contrato_publico"
        extras["perfil_ideal"] = _prune_profile(["fornecedor", "empresa"], norm) or ["empresa", "fornecedor"]
    else:
        top = str(extras.get("tipo_oportunidade") or "").strip().lower()
        if top == "funding_opportunity":
            extras["tipo_oportunidade"] = "funding_opportunity"
        elif top in ("chamada_publica", "procurement", "compra_publica"):
            extras["tipo_oportunidade"] = "grant"
        elif top == "grant":
            extras["tipo_oportunidade"] = "grant"
        else:
            extras["tipo_oportunidade"] = top or "grant"
        item["tipo_recurso"] = "Grant para pesquisa competitiva"
        extras["perfil_ideal"] = _prune_profile(["pesquisador", "universidades", "icts"], norm) or [
            "pesquisador",
            "universidades",
        ]
    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")
    extras["metodo_classificacao"] = "china_university_procurement_local_calibration"


def _credito_br_innovacao_evidence(norm: str) -> bool:
    """Inovação/P&D: exige termos explícitos (não basta 'banco de desenvolvimento')."""
    if _has_any(
        norm,
        (
            "inovacao",
            "inovação",
            "pd&i",
            "p&d",
            "pesquisa e desenvolvimento",
            "pesquisa tecnologica",
            "pesquisa tecnológica",
            "desenvolvimento tecnologico",
            "desenvolvimento tecnológico",
            "laboratorio",
            "laboratório",
        ),
    ):
        return True
    if _has_any(norm, ("tecnologia", "pesquisa")) and _has_any(
        norm,
        ("inova", "desenvolvimento", "pd", "laboratorio", "laboratório", "prototipo", "protótipo"),
    ):
        return True
    return False


def _credito_br_setores_estrito(norm: str, *, max_tags: int = 3) -> List[str]:
    """
    Setores para agências de crédito BR: só com evidência no corpus; máx. 3 tags.
    Não inclui 'desenvolvimento_regional' por defeito (evita lista genérica).
    """
    sect: List[str] = []

    agro_hit = _has_any(
        norm,
        (
            "agropecuario",
            "agropecuário",
            "agronegocio",
            "agronegócio",
            "agricultura",
            "pecuaria",
            "pecuária",
            "produtor rural",
            "cooperativa",
            "pronaf",
            "plano safra",
            "horticultura",
            "caficultura",
            " silvicultura",
            "/rural/",
            "credito rural",
            "crédito rural",
            "giro produtor",
            "produtor ",
        ),
    ) or ("/rural/" in norm or " agro" in norm or "agro " in norm)
    if agro_hit:
        sect.append("agro")

    energia_hit = _has_any(
        norm,
        (
            "energia renovavel",
            "energia renovável",
            "eficiencia energetica",
            "eficiência energética",
            "geracao distribuida",
            "geração distribuída",
            "solar",
            "eolica",
            "eólica",
            "biomassa",
            "hidreletrica",
            "hidrelétrica",
            "energia verde",
            "matriz energetica",
            "matriz energética",
        ),
    )
    if energia_hit:
        sect.append("energia")

    sust_hit = _has_any(
        norm,
        (
            "sustentabil",
            "baixo carbono",
            "mudanca climatica",
            "mudança climática",
            "aquecimento global",
            "ambiental ",
            " meio ambiente",
            "esg",
            "credito verde",
            "crédito verde",
            "economia verde",
        ),
    )
    if sust_hit:
        sect.append("sustentabilidade")

    if _credito_br_innovacao_evidence(norm):
        sect.append("inovacao")

    if _has_any(norm, ("industria", "indústria", "manufatura", "fabrica", "fábrica")):
        sect.append("industria")

    if _has_any(norm, ("desenvolvimento regional", "desenvolvimento economico regional")):
        sect.append("desenvolvimento_regional")

    out = _unique_preserve(sect)
    cap = max_tags if max_tags > 0 else 3
    return out[:cap]


def _calibrate_multilateral_innovation_core(
    item: Dict[str, Any],
    *,
    host_fragments: Sequence[str],
    origem_portal: str,
    default_country: str = "Internacional",
    default_region: str = "multilateral",
    default_lang: str = "en",
) -> bool:
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return False
    lk = str(item.get("link") or "").lower()
    if not any(h in lk for h in host_fragments):
        return False
    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([titulo, desc, lk]))

    extras.setdefault("origem_portal", origem_portal)
    extras.setdefault("pais", default_country)
    extras.setdefault("regiao", default_region)
    extras.setdefault("idioma_original", default_lang)

    actionable = _has_any(
        norm,
        (
            "open call",
            "call for proposals",
            "call",
            "deadline",
            "apply",
            "application",
            "submission",
            "challenge",
            "grant",
            "funding",
            "venture",
            "accelerator",
            "procurement",
            "tender",
            "convocatoria",
            "propuesta",
            "financiamiento",
            "cooperacion tecnica",
            "cooperação técnica",
        ),
    )
    if not actionable:
        extras["tipo_oportunidade"] = "programa_agregado"
        extras["metodo_classificacao"] = "multilateral_innovation_program_page"
        return True

    if _has_any(norm, ("procurement", "tender", "licitacion", "licitação", "supplier")):
        extras["tipo_oportunidade"] = "procurement"
        item["tipo_recurso"] = "oportunidade_fornecedor"
        extras["tipo_recurso"] = "oportunidade_fornecedor"
    elif _has_any(norm, ("venture", "equity", "startup", "accelerator")):
        extras["tipo_oportunidade"] = "startup_programme"
        item["tipo_recurso"] = "venture"
        extras["tipo_recurso"] = "venture"
        extras["natureza_recurso"] = "equity"
    elif _has_any(norm, ("grant", "fomento", "subsid", "nao reembols", "não reembols")):
        extras["tipo_oportunidade"] = "call_for_proposals"
        item["tipo_recurso"] = "grant"
        extras["tipo_recurso"] = "grant"
        extras["natureza_recurso"] = "nao_reembolsavel"
    elif _has_any(norm, ("financing", "financiamiento", "project financing", "loan", "credito", "crédito")):
        extras["tipo_oportunidade"] = "project_financing"
        item["tipo_recurso"] = "financiamento"
        extras["tipo_recurso"] = "financiamento"
    elif _has_any(norm, ("cooperacion tecnica", "cooperação técnica", "technical cooperation")):
        extras["tipo_oportunidade"] = "technical_cooperation"
        item["tipo_recurso"] = "cooperacao_tecnica"
        extras["tipo_recurso"] = "cooperacao_tecnica"
    else:
        extras["tipo_oportunidade"] = "funding_opportunity"
        item["tipo_recurso"] = item.get("tipo_recurso") or "apoio_inovacao"
        extras["tipo_recurso"] = item.get("tipo_recurso")

    profiles: List[str] = []
    if _has_any(norm, ("startup", "scaleup", "entrepreneur")):
        profiles.append("startup")
    if _has_any(norm, ("sme", "empresa", "small and medium")):
        profiles.extend(["empresa", "pequena_empresa", "media_empresa"])
    if _has_any(norm, ("university", "universidad", "universidade", "research organisation")):
        profiles.extend(["universidade", "ICT"])
    if _has_any(norm, ("consortium", "consorcio")):
        profiles.append("consorcio")
    if _has_any(norm, ("government", "municipality", "public institution")):
        profiles.extend(["governo", "instituicao_publica"])
    if _has_any(norm, ("supplier", "fornecedor")):
        profiles.append("fornecedor")
    if profiles:
        extras["perfil_ideal"] = _prune_profile(_unique_preserve(profiles), norm)[:6]

    sectors: List[str] = []
    if _has_any(norm, ("innovation", "inovacion", "inovação", "p&d", "research")):
        sectors.extend(["inovacao", "ciencia_tecnologia"])
    if _has_any(norm, ("energy", "energia")):
        sectors.append("energia")
    if _has_any(norm, ("sustainability", "sostenibilidad", "sustentabilidade", "climate", "clima")):
        sectors.extend(["sustentabilidade", "clima"])
    if _has_any(norm, ("infrastructure", "infraestructura", "infraestrutura")):
        sectors.append("infraestrutura")
    if _has_any(norm, ("city", "cities", "ciudades", "cidades")):
        sectors.append("cidades")
    if _has_any(norm, ("industry", "industria", "indústria", "manufactur")):
        sectors.append("industria")
    if _has_any(norm, ("digital", "software", "ai", "artificial intelligence")):
        sectors.append("digital")
    if _has_any(norm, ("agri", "agro", "agriculture", "agricultura")):
        sectors.append("agricultura")
    if _has_any(norm, ("health", "saude", "salud", "medical")):
        sectors.append("saude")
    if _has_any(norm, ("education", "educacion", "educação")):
        sectors.append("educacao")
    if sectors:
        extras["setor_estrategico"] = _unique_preserve(sectors)[:4]
        extras["setor_economico"] = _unique_preserve(sectors)[:4]

    extras["metodo_classificacao"] = "multilateral_innovation_local_calibration"
    return True


_EU_INNOVATION_SECTOR_MARKERS: Dict[str, Tuple[str, ...]] = {
    "energia": ("energy", "energia", "battery", "batteries", "storage", "fusion", "hydrogen", "solar", "wind"),
    "sustentabilidade": (
        "sustainability",
        "sustainable",
        "circular",
        "green",
        "resource efficiency",
        "recycl",
        "low carbon",
        "net zero",
    ),
    "clima": ("climate", "clima", "climate-neutral", "emission", "carbon", "decarbon"),
    "infraestrutura": ("infrastructure", "infraestrutura", "infraestructura"),
    "cidades": ("city", "cities", "urban", "municipal", "capital of innovation"),
    "industria": ("industry", "industrial", "manufactur", "production", "factory", "lightweighting"),
    "digital": (
        "digital",
        "software",
        "artificial intelligence",
        " ai ",
        "semiconductor",
        "quantum",
        "photonics",
        "telecommunications",
        "5g",
        "6g",
    ),
    "agricultura": ("agri", "agriculture", "soil", "food", "feed", "biomass", "farming"),
    "saude": ("health", "medical", "biotech", "biotechnology", "life science", "diagnostic", "therapy"),
    "educacao": ("education", "training", "university", "universities"),
    "ciencia_tecnologia": (
        "research and development",
        "r&d",
        "deep tech",
        "science",
        "scientific",
        "technology",
        "technologies",
        "advanced materials",
    ),
    "inovacao": (
        "innovation challenge",
        "innovative product",
        "innovative products",
        "breakthrough innovation",
        "game changing",
        "high-risk innovation",
        "market uptake",
    ),
}


def _as_str_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return _unique_preserve([str(x).strip() for x in value if x is not None and str(x).strip()])
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _setor_estrategico_crawler_locked(extras: Dict[str, Any]) -> bool:
    v = extras.get("setor_estrategico_crawler_locked")
    if v is True:
        return True
    if isinstance(v, (int, float)) and v == 1:
        return True
    if isinstance(v, str) and v.strip().lower() in ("true", "yes", "1", "on"):
        return True
    return False


def _apply_taxonomy_setor_estrategico(extras: Dict[str, Any], computed: List[str]) -> None:
    """Substitui `setor_estrategico` pelo resultado do classificador global, salvo lock de crawler."""
    new_list = _unique_preserve(computed)[:4]
    if _setor_estrategico_crawler_locked(extras):
        return
    old = _as_str_list(extras.get("setor_estrategico"))
    if old and sorted(old) != sorted(new_list):
        hist = extras.get("setor_estrategico_historico_merge")
        if not isinstance(hist, list):
            hist = []
        hist = [old] + hist
        extras["setor_estrategico_historico_merge"] = hist[:5]
    extras["setor_estrategico"] = new_list


def _trim_eu_innovation_setors_by_evidence(item: Dict[str, Any], *, max_items: int = 3) -> None:
    """Keep only sectors with title/description evidence; preserve the full detected list in extras."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return

    current = _as_str_list(extras.get("setor_estrategico"))
    if not current:
        return

    title = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    text_norm = _normalize(" ".join([title, desc]))
    title_norm = _normalize(title)

    detected = _unique_preserve(_as_str_list(extras.get("setores_detectados")) + current)
    if detected:
        extras["setores_detectados"] = detected

    scored: List[Tuple[int, int, str, List[str]]] = []
    generic = {"inovacao", "ciencia_tecnologia"}
    for idx, sector in enumerate(current):
        sector_norm = _normalize(sector)
        markers = _EU_INNOVATION_SECTOR_MARKERS.get(sector_norm, ())
        hits = [m for m in markers if m and m in text_norm]
        if not hits:
            continue

        score = 10 + len(hits)
        if sector_norm not in generic:
            score += 8
        if any(m in title_norm for m in hits):
            score += 5
        if sector_norm in generic and len(current) > 1:
            score -= 6
        scored.append((score, idx, sector, hits[:3]))

    scored.sort(key=lambda x: (-x[0], x[1]))
    selected = _unique_preserve([sector for _, _, sector, _ in scored])[:max_items]
    dropped = [s for s in current if s not in selected]

    extras["setor_estrategico"] = selected
    if isinstance(extras.get("setor_economico"), list):
        extras["setor_economico"] = [s for s in _as_str_list(extras.get("setor_economico")) if s in selected][:max_items]

    if dropped:
        extras["tags_secundarias"] = _unique_preserve(_as_str_list(extras.get("tags_secundarias")) + dropped)
    extras["calibracao_setor_estrategico"] = "max3_evidencia_titulo_descricao_eic_eureka"


_INTERNATIONAL_TARGET_MARKERS: Dict[str, Tuple[str, ...]] = {
    "empresa": ("empresa", "business", "company", "companies", "industry", "industrial", "commercial"),
    "empresas": ("empresas", "businesses", "companies", "industry", "industrial", "commercial"),
    "pequena_empresa": ("sme", "small business", "small businesses", "small and medium"),
    "media_empresa": ("sme", "medium-sized", "small and medium"),
    "startup": ("startup", "start-up", "scaleup", "scale-up", "venture"),
    "startups": ("startup", "start-up", "scaleup", "scale-up", "venture"),
    "universidade": ("university", "universities", "higher education"),
    "universidades": ("university", "universities", "higher education"),
    "ict": ("research organisation", "research organization", "institute", "laboratory", "lab"),
    "icts": ("research organisation", "research organization", "institute", "laboratory", "lab"),
    "pesquisador": ("researcher", "researchers", "scientist", "scientists", "investigator", "fellowship"),
    "pesquisadores": ("researcher", "researchers", "scientist", "scientists", "investigator", "fellowship"),
    "consorcio": ("consortium", "consortia", "collaborative", "partners", "partnership"),
    "fornecedor": ("supplier", "bidder", "procurement", "tender", "contractor"),
    "fornecedores": ("supplier", "bidder", "procurement", "tender", "contractor"),
    "governo": ("government", "public sector", "municipality", "city authority"),
    "organizacao_internacional": ("organisation", "organization", "organisations", "organizations"),
}


def _prune_international_targets_by_evidence(item: Dict[str, Any], *, max_items: int = 4) -> None:
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    blob = _normalize(" ".join([str(item.get("titulo") or ""), str(item.get("descricao") or "")]))
    for key in ("publico_alvo", "perfil_ideal"):
        current = _as_str_list(extras.get(key))
        kept: List[str] = []
        removed: List[str] = []
        for label in current:
            markers = _INTERNATIONAL_TARGET_MARKERS.get(_normalize(label), ())
            if markers and _has_any(blob, markers):
                kept.append(label)
            else:
                removed.append(label)
        extras[key] = _unique_preserve(kept)[:max_items]
        if removed:
            extras["tags_secundarias"] = _unique_preserve(_as_str_list(extras.get("tags_secundarias")) + removed)
    audit_visible_markers = (
        "empresa",
        "business",
        "company",
        "supplier",
        "fornecedor",
        "researcher",
        "pesquisador",
        "university",
        "univers",
        "ict",
        "startup",
        "start-up",
        "student",
        "estudante",
    )
    if extras.get("publico_alvo") and not _has_any(blob, audit_visible_markers):
        extras["tags_secundarias"] = _unique_preserve(
            _as_str_list(extras.get("tags_secundarias")) + _as_str_list(extras.get("publico_alvo"))
        )
        extras["publico_alvo"] = []
    if not extras.get("publico_alvo") and not extras.get("perfil_ideal"):
        warnings_l = extras.get("validacao_warnings")
        if not isinstance(warnings_l, list):
            warnings_l = []
        warnings_l.append("publico_alvo_sem_evidencia_textual")
        extras["validacao_warnings"] = _unique_preserve([str(x) for x in warnings_l])
        extras.setdefault("classificacao_confianca", "media")


def _compact_international_classification(item: Dict[str, Any], *, max_area: int = 3) -> None:
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    setores = _as_str_list(extras.get("setor_estrategico"))[:3]
    extras["setor_estrategico"] = setores
    if isinstance(extras.get("setor_economico"), list):
        extras["setor_economico"] = _as_str_list(extras.get("setor_economico"))[:3]
    area = _as_str_list(extras.get("area"))
    if len(area) > max_area:
        extras["tags_secundarias"] = _unique_preserve(_as_str_list(extras.get("tags_secundarias")) + area[max_area:])
        extras["area"] = area[:max_area]


def calibrate_bid_lab_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_multilateral_innovation_core(
        item,
        host_fragments=("bidlab.org", "iadb.org", "idbinvest.org"),
        origem_portal="BID Lab (bidlab.org)",
        default_country="Internacional",
        default_region="multilateral",
        default_lang="en",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    norm = _normalize(" ".join([str(item.get("titulo") or ""), str(item.get("descricao") or ""), str(item.get("link") or "")]))
    if _has_any(norm, ("startup", "venture", "accelerator", "entrepreneur")):
        extras["tipo_oportunidade"] = "startup_programme"
        item["tipo_recurso"] = "venture"
        extras["tipo_recurso"] = "venture"
    extras["metodo_classificacao"] = "bid_lab_local_calibration"


def calibrate_caf_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_multilateral_innovation_core(
        item,
        host_fragments=("caf.com",),
        origem_portal="CAF (caf.com)",
        default_country="Internacional",
        default_region="multilateral",
        default_lang="es",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    norm = _normalize(" ".join([str(item.get("titulo") or ""), str(item.get("descricao") or ""), str(item.get("link") or "")]))
    if _has_any(norm, ("cooperacion tecnica", "cooperación técnica", "technical cooperation")):
        extras["tipo_oportunidade"] = "technical_cooperation"
        item["tipo_recurso"] = "cooperacao_tecnica"
        extras["tipo_recurso"] = "cooperacao_tecnica"
    extras["metodo_classificacao"] = "caf_local_calibration"


def calibrate_fonplata_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_multilateral_innovation_core(
        item,
        host_fragments=("fonplata.org",),
        origem_portal="FONPLATA (fonplata.org)",
        default_country="Internacional",
        default_region="multilateral",
        default_lang="es",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras["metodo_classificacao"] = "fonplata_local_calibration"


def calibrate_eureka_network_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_multilateral_innovation_core(
        item,
        host_fragments=("eurekanetwork.org",),
        origem_portal="Eureka Network (eurekanetwork.org)",
        default_country="Internacional",
        default_region="europa",
        default_lang="en",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras["tipo_oportunidade"] = "call_for_proposals"
    item["tipo_recurso"] = "grant"
    extras["tipo_recurso"] = "grant"
    extras["natureza_recurso"] = "nao_reembolsavel"
    _trim_eu_innovation_setors_by_evidence(item, max_items=3)
    extras["metodo_classificacao"] = "eureka_network_local_calibration"


def calibrate_eic_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_multilateral_innovation_core(
        item,
        host_fragments=("eic.ec.europa.eu", "ec.europa.eu"),
        origem_portal="EIC (eic.ec.europa.eu)",
        default_country="União Europeia",
        default_region="Europa",
        default_lang="en",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    norm = _normalize(" ".join([str(item.get("titulo") or ""), str(item.get("descricao") or ""), str(item.get("link") or "")]))
    if _has_any(norm, ("accelerator", "pathfinder", "transition", "open call", "deadline", "submission")):
        extras["tipo_oportunidade"] = "funding_opportunity"
        item["tipo_recurso"] = "grant"
        extras["tipo_recurso"] = "grant"
        extras["natureza_recurso"] = "nao_reembolsavel"
    _trim_eu_innovation_setors_by_evidence(item, max_items=3)
    extras["metodo_classificacao"] = "eic_local_calibration"


def _calibrate_international_innovation_core(
    item: Dict[str, Any],
    *,
    host_fragments: Sequence[str],
    origem_portal: str,
    default_country: str = "Internacional",
    default_region: str = "internacional",
    default_lang: str = "en",
) -> bool:
    if not _calibrate_multilateral_innovation_core(
        item,
        host_fragments=host_fragments,
        origem_portal=origem_portal,
        default_country=default_country,
        default_region=default_region,
        default_lang=default_lang,
    ):
        return False
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    _trim_eu_innovation_setors_by_evidence(item, max_items=3)
    if "setores_detectados" not in extras:
        extras["setores_detectados"] = _as_str_list(extras.get("setor_estrategico"))
    _prune_international_targets_by_evidence(item)
    _compact_international_classification(item)
    return True


def calibrate_innovate_uk_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_international_innovation_core(
        item,
        host_fragments=("ukri.org", "gov.uk", "apply-for-innovation-funding.service.gov.uk"),
        origem_portal="Innovate UK / UKRI Funding Finder",
        default_country="Reino Unido",
        default_region="europa",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    norm = _normalize(" ".join([str(item.get("titulo") or ""), str(item.get("descricao") or ""), str(item.get("link") or "")]))
    extras["tipo_oportunidade"] = "funding_opportunity"
    item["tipo_recurso"] = "grant" if "loan" not in norm else "financiamento"
    extras["tipo_recurso"] = item["tipo_recurso"]
    extras["natureza_recurso"] = "nao_reembolsavel" if item["tipo_recurso"] == "grant" else "reembolsavel"
    extras["metodo_classificacao"] = "innovate_uk_local_calibration"


def calibrate_ukri_funding_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_international_innovation_core(
        item,
        host_fragments=("ukri.org",),
        origem_portal="UKRI Funding Finder",
        default_country="Reino Unido",
        default_region="europa",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    norm = _normalize(" ".join([str(item.get("titulo") or ""), str(item.get("descricao") or "")]))
    if "fellowship" in norm:
        extras["tipo_oportunidade"] = "fellowship"
    elif "research" in norm or "research organisation" in norm:
        extras["tipo_oportunidade"] = "research_grant"
    else:
        extras["tipo_oportunidade"] = "funding_opportunity"
    item["tipo_recurso"] = "grant"
    extras["tipo_recurso"] = "grant"
    extras["natureza_recurso"] = "nao_reembolsavel"
    extras["metodo_classificacao"] = "ukri_funding_local_calibration"


def calibrate_eurostars_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_international_innovation_core(
        item,
        host_fragments=("eurekanetwork.org",),
        origem_portal="Eurostars / Eureka Network",
        default_country="Internacional",
        default_region="europa",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras["tipo_oportunidade"] = "call_for_proposals"
    item["tipo_recurso"] = "grant"
    extras["tipo_recurso"] = "grant"
    extras["natureza_recurso"] = "nao_reembolsavel"
    extras["metodo_classificacao"] = "eurostars_local_calibration"


def calibrate_dod_sbir_sttr_extras(item: Dict[str, Any]) -> None:
    """DoD SBIR/STTR: setores curtos; evita classificação institucional em páginas de apoio (filtradas no crawler)."""
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if not extras:
        return
    lk = (item.get("link") or "").lower()
    tit_cur = str(item.get("titulo") or "").strip()
    if tit_cur.lower() in ("topic", "topics") and "sbir.gov" in lk:
        m_tid = re.search(r"/topics/(\d+)", lk)
        if m_tid:
            item["titulo"] = f"DoD SBIR/STTR — tópico {m_tid.group(1)}"
    # Normaliza setor_estrategico (defense_intel pode enviar string única ou lista longa).
    raw_se = extras.get("setor_estrategico")
    if isinstance(raw_se, str) and raw_se.strip():
        if "," in raw_se:
            tags = [x.strip() for x in raw_se.split(",") if x.strip()]
        else:
            tags = [raw_se.strip()]
    else:
        tags = _as_str_list(raw_se)
    if not tags:
        tags = ["defesa_industrial", "aeroespacial", "defesa"]
    extras["setor_estrategico"] = tags[:3]
    item["setor_estrategico"] = extras["setor_estrategico"]
    # Oportunidades reais SBIR/STTR (API ou topic) — não hub FAQ/API.
    if extras.get("topic_code") or extras.get("codigo_oportunidade") or "/topic" in lk or "solicitation" in lk:
        extras["tipo_oportunidade"] = "funding_opportunity"
    elif "topics" in lk and lk.rstrip("/").endswith("topics"):
        extras["tipo_oportunidade"] = "programa_agregado"
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "programa_pdi"
    extras["metodo_classificacao"] = "dod_sbir_sttr_recovery_a"


def calibrate_eit_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_international_innovation_core(
        item,
        host_fragments=("eit.europa.eu",),
        origem_portal="European Institute of Innovation and Technology",
        default_country="Uniao Europeia",
        default_region="europa",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    norm = _normalize(" ".join([str(item.get("titulo") or ""), str(item.get("descricao") or ""), str(item.get("link") or "")]))
    if _has_any(norm, ("procurement", "tender")):
        extras["tipo_oportunidade"] = "procurement"
        item["tipo_recurso"] = "oportunidade_fornecedor"
    elif _has_any(norm, ("call for proposal", "call for proposals", "open call")):
        extras["tipo_oportunidade"] = "call_for_proposals"
        item["tipo_recurso"] = "grant"
    else:
        extras["tipo_oportunidade"] = "innovation_programme"
        item["tipo_recurso"] = "apoio_inovacao"
    extras["tipo_recurso"] = item["tipo_recurso"]
    extras["natureza_recurso"] = "nao_reembolsavel" if item["tipo_recurso"] != "oportunidade_fornecedor" else ""
    extras["metodo_classificacao"] = "eit_local_calibration"


def calibrate_esa_star_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_international_innovation_core(
        item,
        host_fragments=("esa.int", "procurement.esa.int", "esamultimedia.esa.int"),
        origem_portal="ESA esa-star Publication",
        default_country="Internacional",
        default_region="europa",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras["tipo_oportunidade"] = "procurement"
    item["tipo_recurso"] = "oportunidade_fornecedor"
    extras["tipo_recurso"] = "oportunidade_fornecedor"
    extras["natureza_recurso"] = ""
    extras["metodo_classificacao"] = "esa_star_local_calibration"


def calibrate_esa_osip_extras(item: Dict[str, Any]) -> None:
    if not _calibrate_international_innovation_core(
        item,
        host_fragments=("ideas.esa.int", "esa.int"),
        origem_portal="ESA Open Space Innovation Platform",
        default_country="Internacional",
        default_region="europa",
    ):
        return
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    norm = _normalize(" ".join([str(item.get("titulo") or ""), str(item.get("descricao") or ""), str(item.get("link") or "")]))
    extras["tipo_oportunidade"] = "space_opportunity" if _has_any(norm, ("campaign", "channel", "call for ideas", "submit ideas")) else "programa_agregado"
    item["tipo_recurso"] = "apoio_inovacao"
    extras["tipo_recurso"] = "apoio_inovacao"
    extras["natureza_recurso"] = "nao_reembolsavel"
    extras["metodo_classificacao"] = "esa_osip_local_calibration"


def _calibrate_br_credito_agencia_core(
    item: Dict[str, Any],
    *,
    origem_portal: str,
    host_fragment: str,
    uf: Optional[str] = None,
    regiao: Optional[str] = None,
) -> None:
    """Crédito reembolsável por defeito; subvenção só com evidência explícita; setores só com match forte (≤3)."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        return
    lk = (item.get("link") or "").lower()
    if host_fragment not in lk:
        return
    titulo = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    norm = _normalize(" ".join([titulo, desc, lk]))

    extras.setdefault("origem_portal", origem_portal)
    if regiao and (
        not str(extras.get("regiao") or "").strip() or str(extras.get("regiao")).lower() in ("brasil", "nacional")
    ):
        extras["regiao"] = regiao
    if uf:
        extras.setdefault("estado", uf)
        extras.setdefault("uf", uf)
    extras.setdefault("pais", "Brasil")

    strong_loan = _has_any(
        norm,
        (
            "juros",
            "carencia",
            "carência",
            "taxa",
            "financiamento",
            "emprestimo",
            "empréstimo",
            "credito",
            "crédito",
            "linha de credito",
            "linha de crédito",
            "rotativo",
            "pronampe",
            "pronaf",
            "fno",
            "fungetur",
            "finame",
            "microcred",
            "capital de giro",
            "bndes",
            "fgi",
            "garantia",
            "parcelamento",
            "amortiza",
        ),
    )
    sub_explicit = _has_any(
        norm,
        (
            "subvenção",
            "subvencao",
            "subven ",
            "subvenção não reembolsável",
            "subvencao nao reembolsavel",
            "recursos não reembolsáveis",
            "recursos nao reembolsaveis",
            "doação",
            "doacao fundo",
        ),
    )
    if sub_explicit and not strong_loan:
        item["tipo_recurso"] = item.get("tipo_recurso") or "subvencao"
        extras["natureza_recurso"] = "nao_reembolsavel"
        extras["reembolsavel"] = False
        extras["tipo_recurso"] = "subvencao"
    else:
        item["tipo_recurso"] = item.get("tipo_recurso") or "financiamento_reembolsavel"
        extras["natureza_recurso"] = "reembolsavel"
        extras["reembolsavel"] = True
        extras["tipo_recurso"] = extras.get("tipo_recurso") or "credito"

    if _has_any(norm, ("chamada publica", "chamada pública", "selecao de proposta", "seleção de proposta")):
        extras["tipo_oportunidade"] = "chamada_publica"
    elif _has_any(norm, ("publicação do edital", "publicacao do edital")) and _has_any(norm, ("inscricao", "inscrição", "proposta")):
        extras["tipo_oportunidade"] = "edital"
    elif _credito_br_innovacao_evidence(norm):
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "programa_inovacao"
    else:
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "programa_credito"

    extras["tipo_recurso"] = str(item.get("tipo_recurso") or extras.get("tipo_recurso") or "")

    perfil: List[str] = []
    if _has_any(norm, ("microempresa", "mei ", "micro e pequena", "pequena empresa", "pme")):
        perfil.extend(["microempresa", "pequena_empresa"])
    if _has_any(norm, ("media empresa", "média empresa")):
        perfil.append("media_empresa")
    if _has_any(norm, ("empresa", "cnpj", "pj ", "pessoa juridica")):
        if strong_loan or _has_any(norm, ("micro", "pequena", "media empresa", "média empresa", "mei ", "rural", "agro")):
            perfil.append("empresa")
    if _has_any(norm, ("startup", "scale-up", "scale up")):
        perfil.append("startup")
    if _has_any(norm, ("cooperativa", "coop.")):
        perfil.append("cooperativa")
    if _has_any(norm, ("prefeitura", "municipio", "município")):
        perfil.append("municipio")
    if _has_any(norm, ("produtor rural", "pronaf", "plano safra", "agricultura", "pecuaria")):
        perfil.append("produtor_rural")
    perfil = _prune_profile(_unique_preserve(perfil), norm)
    if perfil:
        extras["perfil_ideal"] = perfil[:4]

    sect_final = _credito_br_setores_estrito(norm, max_tags=3)
    extras["setor_estrategico"] = sect_final

    ac_ok = _has_any(norm, ("pesquisa cientifica", "pesquisa científica", "universidade", "laborat", "ciência", "ciencia "))
    if isinstance(extras.get("area_cientifica"), list):
        if not ac_ok:
            extras["area_cientifica"] = []
    at_ok = _has_any(norm, ("tecnologia", "inova", "engenharia", "software", "sistema", "pd&i", "p&d"))
    if isinstance(extras.get("area_tecnologica"), list):
        if not at_ok:
            extras["area_tecnologica"] = []

    extras["metodo_classificacao"] = extras.get("metodo_classificacao") or "credito_br_agencia_calibration"


def calibrate_bnb_extras(item: Dict[str, Any]) -> None:
    """Onda A BR crédito: setores só com evidência; sem desenvolvimento_regional genérico."""
    _calibrate_br_credito_agencia_core(
        item,
        origem_portal="Banco do Nordeste (bnb.gov.br)",
        host_fragment="bnb.gov.br",
        uf=None,
        regiao="nordeste",
    )


def calibrate_banco_da_amazonia_extras(item: Dict[str, Any]) -> None:
    """Onda A BASA: Norte; agro/energia só se aparecerem no texto ou URL."""
    _calibrate_br_credito_agencia_core(
        item,
        origem_portal="Banco da Amazônia (bancoamazonia.com.br)",
        host_fragment="bancoamazonia.com.br",
        uf=None,
        regiao="norte",
    )
    ex = item.get("extras")
    if not isinstance(ex, dict):
        return
    lk = (item.get("link") or "").lower()
    tit = (item.get("titulo") or "").lower()
    # Linhas oficiais de crédito/fomento BASA: tipo explícito (reduz “noticia_institucional” genérico).
    if any(
        p in lk
        for p in (
            "linhas-de-fomento",
            "fno",
            "pronaf",
            "fungetur",
            "finame",
            "capital-de-giro-produtor",
            "microcredito",
            "empreendedor",
            "credito-e-financiamento",
            "financiamento-agro",
        )
    ):
        ex["tipo_oportunidade"] = "programa_credito"
        item["tipo_oportunidade"] = "programa_credito"
    # Páginas só de relatório/transparência: tags amplas do classificador genérico geram falso “muito_ampla”.
    if "relatorio" in lk or "relatório" in tit or "relatorio" in tit:
        ex["area"] = []
        pi = ex.get("perfil_ideal")
        if isinstance(pi, list) and len(pi) > 4:
            ex["perfil_ideal"] = pi[:4]


def calibrate_desenvolve_sp_extras(item: Dict[str, Any]) -> None:
    """Seeds curados — setores mínimos até haver texto rico (WAF)."""
    _calibrate_br_credito_agencia_core(
        item,
        origem_portal="Desenvolve SP (desenvolvesp.com.br)",
        host_fragment="desenvolvesp.com.br",
        uf="SP",
        regiao="sudeste",
    )


def calibrate_bdmg_extras(item: Dict[str, Any]) -> None:
    """BDMG inclui PDFs em subdomínio bdmgorienta."""
    lk = (item.get("link") or "").lower()
    host = "bdmgorienta.bdmg.mg.gov.br" if "bdmgorienta.bdmg.mg.gov.br" in lk else "bdmg.mg.gov.br"
    _calibrate_br_credito_agencia_core(
        item,
        origem_portal="BDMG (bdmg.mg.gov.br)",
        host_fragment=host,
        uf="MG",
        regiao="sudeste",
    )


def calibrate_agerio_extras(item: Dict[str, Any]) -> None:
    """AgeRio: páginas só de educação financeira não recebem setores estratégicos."""
    _calibrate_br_credito_agencia_core(
        item,
        origem_portal="AgeRio (agerio.com.br)",
        host_fragment="agerio.com.br",
        uf="RJ",
        regiao="sudeste",
    )
    ex = item.get("extras")
    if not isinstance(ex, dict):
        return
    lk = (item.get("link") or "").lower()
    if (
        "educacaofinanceira" in lk
        or "/educacao-financeira" in lk
        or "/ouvidoria" in lk
        or "/fale-conosco" in lk
        or "/faq" in lk
        or "internet-banking" in lk
    ):
        ex["setor_estrategico"] = []
        ex["perfil_ideal"] = []


def calibrate_bndes_extras(item: Dict[str, Any]) -> None:
    """BNDES: fundos/FIP/FIDC/Criatec/venture não são crédito reembolsável comum."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        item["extras"] = extras
    norm = _normalize(
        " ".join(
            str(x or "")
            for x in (
                item.get("titulo"),
                item.get("descricao"),
                item.get("link"),
                item.get("tipo_recurso"),
                extras.get("tipo_recurso"),
                extras.get("tipo_oportunidade"),
                extras.get("linha_credito"),
            )
        )
    )
    fund_markers = (
        "fundo de investimento",
        "fundos de investimento",
        "fip",
        "fidc",
        "criatec",
        "venture capital",
        "capital semente",
        "participacoes",
        "participações",
        "cotas do fidc",
        "gestor do fundo",
        "mercado de capitais",
    )
    if _has_any(norm, fund_markers):
        if _has_any(norm, ("venture", "capital semente", "startup")):
            tipo = "venture"
        elif "equity" in norm:
            tipo = "equity"
        else:
            tipo = "fundo_investimento"
        item["tipo_recurso"] = tipo
        extras["tipo_recurso"] = tipo
        extras["tipo_oportunidade"] = extras.get("tipo_oportunidade") or "investimento"
        extras["natureza_recurso"] = "investimento_participacao"
        extras["reembolsavel"] = False
        extras["calibracao_credito"] = "bndes_fundos_investimento"
        se = extras.get("setor_estrategico")
        if isinstance(se, list) and len(se) > 3:
            extras["setor_estrategico"] = se[:3]


# Recovery C — setor estratégico (≤3) com preservação em extras / tags secundárias
_BR_SETOR_STRATEGICO_MARKERS: Dict[str, Tuple[str, ...]] = {
    "defesa_industrial": (
        "defesa industrial",
        "industria de defesa",
        "defesa nacional",
        "base industrial",
        "submarino",
        "blindado",
        "industria de base",
        "fornecedor de defesa",
    ),
    "aeroespacial": (
        "aeroespacial",
        "aeronautica",
        "aeronave",
        "satelite",
        "espacial",
        "foguete",
        "aviação",
        "aviacao",
    ),
    "defesa": (
        " defesa",
        "defesa,",
        "ministerio da defesa",
        "marinha",
        "exercito",
        "forcas armadas",
        "naval",
        "militar",
    ),
    "energia": (
        " energia",
        "eletric",
        "usina",
        "petroleo",
        "oleo e gas",
        "oleo & gas",
        "gas natural",
        "matriz energetica",
    ),
    "nuclear": (
        "nuclear",
        "angra",
        "radioativ",
        "usina nuclear",
        "nucleoelétrica",
        "radioquimica",
    ),
    "ciencia_tecnologia": (
        "ciencia",
        "tecnologia",
        "pesquisa",
        "desenvolvimento",
        "inovacao",
        "pd&i",
        "p&d",
        " ci&t",
    ),
    "industria": (
        "industria",
        "manufatura",
        "fabric",
        "producao",
        "equipamento",
    ),
    "saude": (
        "saude",
        "medic",
        "hospital",
        "diagnostico",
        "clinica",
        "dispositivo",
    ),
    "agro": (
        "agro",
        "agronegocio",
        "agrícola",
        "pecuaria",
    ),
}


def _nuclep_institutional_url(link: str) -> bool:
    """Páginas corporativas NUCLEP (não oportunidade de edital)."""
    try:
        p = urlparse(link)
        path = (p.path or "").lower().rstrip("/")
    except Exception:
        return False
    if path in ("", "/"):
        return True
    needles = (
        "/quem-somos",
        "/pagina-inicial",
        "/expertise",
        "/composicao",
        "/acesso-a-informacao/institucional",
        "/participacao-social",
        "/auditorias",
        "/convenios-e-transferencias",
        "/organograma",
        "index.php",
    )
    return any(n in path for n in needles)


def recovery_c_cap_setor_estrategico_br(item: Dict[str, Any], *, source_label: str) -> None:
    """
    Limita extras['setor_estrategico'] a 3 entradas com prioridade por evidência textual
    (título, descrição, URL, tipo_oportunidade, tipo_recurso). Excedentes para
    tags_secundarias; lista completa também em setores_detectados.
    """
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        item["extras"] = extras
    current = _as_str_list(extras.get("setor_estrategico"))
    if not current:
        return

    full_list = _unique_preserve(_as_str_list(extras.get("setores_detectados")) + current)
    if full_list:
        extras["setores_detectados"] = full_list

    if len(current) <= 3:
        extras["calibracao_setor_estrategico"] = f"recovery_c_{source_label}_max3_ok"
        return

    tit = str(item.get("titulo") or "")
    desc = str(item.get("descricao") or "")
    link = str(item.get("link") or "")
    to = str(extras.get("tipo_oportunidade") or item.get("tipo_oportunidade") or "")
    tr = str(extras.get("tipo_recurso") or item.get("tipo_recurso") or "")
    blob = _normalize(" ".join([tit, desc, link, to, tr]))
    tit_n = _normalize(tit)
    link_n = _normalize(link)

    def score_one(sector: str) -> int:
        markers = _BR_SETOR_STRATEGICO_MARKERS.get(sector, ())
        sc = 0
        for m in markers:
            if not m:
                continue
            if m in blob:
                sc += 4
            if m in tit_n:
                sc += 6
            if m in link_n:
                sc += 2
        sn = _normalize(sector.replace("_", " "))
        if len(sn) > 2 and sn in blob:
            sc += 3
        return sc

    scored: List[Tuple[int, int, str]] = []
    for idx, sector in enumerate(current):
        s = score_one(sector)
        scored.append((s, idx, sector))
    scored.sort(key=lambda x: (-x[0], x[1]))

    selected: List[str] = []
    for s, _idx, sector in scored:
        if len(selected) >= 3:
            break
        if sector not in selected:
            selected.append(sector)

    if len(selected) < 3:
        for _s, _idx, sector in scored:
            if len(selected) >= 3:
                break
            if sector not in selected:
                selected.append(sector)

    dropped = [x for x in current if x not in selected]
    extras["setor_estrategico"] = selected[:3]
    if dropped:
        extras["tags_secundarias"] = _unique_preserve(_as_str_list(extras.get("tags_secundarias")) + dropped)
    extras["calibracao_setor_estrategico"] = f"recovery_c_{source_label}_max3_evidencia"


def calibrate_embrapii_extras(item: Dict[str, Any]) -> None:
    """EMBRAPII: chamadas de cooperação/inovação/PD&I não devem parecer crédito comum."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        item["extras"] = extras
    norm = _normalize(
        " ".join(
            str(x or "")
            for x in (
                item.get("titulo"),
                item.get("descricao"),
                item.get("link"),
                item.get("tipo_recurso"),
                extras.get("tipo_recurso"),
                extras.get("tipo_oportunidade"),
            )
        )
    )
    if _has_any(
        norm,
        (
            "embrapii",
            "chamada publica",
            "chamada pública",
            "centro de competencia",
            "centro de competência",
            "rota 2030",
            "cofinanciamento",
            "cofinanc",
            "cooperacao",
            "cooperação",
            "inovacao",
            "inovação",
            "pdi",
            "pd i",
            "pd&i",
        ),
    ):
        item["tipo_recurso"] = "apoio_inovacao"
        extras["tipo_recurso"] = "apoio_inovacao"
        extras["tipo_oportunidade"] = "cooperacao_pdi"
        extras["natureza_recurso"] = "nao_reembolsavel"
        extras["reembolsavel"] = False
        extras["calibracao_credito"] = "embrapii_cooperacao_pdi"
    recovery_c_cap_setor_estrategico_br(item, source_label="embrapii")


def calibrate_nuclep_extras(item: Dict[str, Any]) -> None:
    """NUCLEP: cap de setores estratégicos; páginas institucionais sem tratar como edital ativo."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        item["extras"] = extras
    link = str(item.get("link") or "")
    if _nuclep_institutional_url(link):
        extras["tipo_oportunidade"] = "noticia_institucional"
        wl = extras.get("validacao_warnings")
        if not isinstance(wl, list):
            wl = []
        if "recovery_c_nuclep_pagina_institucional" not in wl:
            wl.append("recovery_c_nuclep_pagina_institucional")
        extras["validacao_warnings"] = wl
    recovery_c_cap_setor_estrategico_br(item, source_label="nuclep")


def extras_to_filter_columns(item: Dict[str, Any], extras: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai colunas espelho para o banco (quando schema estendido estiver ativo)."""
    def _arr(key: str) -> Optional[List[str]]:
        v = extras.get(key)
        if isinstance(v, list):
            return [str(x) for x in v if x is not None and str(x).strip()]
        if isinstance(v, str) and v.strip():
            return [v.strip()]
        return None

    out: Dict[str, Any] = {}
    area = _arr("area")
    if area:
        out["area"] = area
    pa = _arr("publico_alvo")
    if pa:
        out["publico_alvo_arr"] = pa
    se = _arr("setor_economico")
    if se:
        out["setor_economico"] = se
    ac = _arr("area_cientifica")
    if ac:
        out["area_cientifica"] = ac
    at = _arr("area_tecnologica")
    if at:
        out["area_tecnologica"] = at
    ss = _arr("setor_estrategico")
    if ss:
        out["setor_estrategico"] = ss

    if extras.get("tipo_oportunidade"):
        out["tipo_oportunidade"] = str(extras["tipo_oportunidade"])[:200]
    if item.get("tipo_recurso"):
        out["tipo_recurso"] = str(item["tipo_recurso"])[:200]
    if extras.get("natureza_recurso"):
        out["natureza_recurso"] = str(extras["natureza_recurso"])[:200]

    for col, key in (
        ("pais", "pais"),
        ("estado", "estado"),
        ("municipio", "municipio"),
        ("orgao_responsavel", "orgao_responsavel"),
        ("instituicao", "instituicao"),
        ("orgao_contratante", "orgao_contratante"),
        ("numero_edital", "numero_edital"),
        ("numero_chamada", "numero_chamada"),
        ("codigo_oportunidade", "codigo_oportunidade"),
        ("url_detalhe", "url_detalhe"),
        ("classificacao_confianca", "classificacao_confianca"),
    ):
        v = extras.get(key)
        if v is not None and str(v).strip():
            out[col] = str(v)[:2000] if col != "url_detalhe" else str(v)[:8000]

    if extras.get("pdf_url"):
        out["pdf_url"] = str(extras["pdf_url"])[:8000]
    if extras.get("valor_total") or item.get("valor"):
        out["valor_total_texto"] = str(extras.get("valor_total") or item.get("valor"))[:2000]
    if extras.get("moeda"):
        out["moeda"] = str(extras["moeda"])[:32]
    if extras.get("reembolsavel") is not None:
        out["reembolsavel"] = bool(extras["reembolsavel"])

    if item.get("programa"):
        out["programa"] = str(item["programa"])[:500]
    if item.get("acao"):
        out["acao"] = str(item["acao"])[:500]

    # Crédito / BNDES e similares
    for col, key in (
        ("taxa_juros", "taxa_juros"),
        ("carencia", "carencia"),
        ("prazo_pagamento", "prazo_pagamento"),
    ):
        v = extras.get(key)
        if v is not None and str(v).strip():
            out[col] = str(v)[:2000]

    # Licitações / PNCP / processos
    for col, key in (("numero_processo", "numero_processo"),):
        v = extras.get(key)
        if v is not None and str(v).strip():
            out[col] = str(v)[:2000]

    # Internacional / tradução / resumo PDF (espelho para filtros e listagens)
    for col, key in (
        ("titulo_original", "titulo_original"),
        ("descricao_original", "descricao_original"),
        ("titulo_traduzido", "titulo_traduzido"),
        ("descricao_traduzida", "descricao_traduzida"),
        ("idioma_original", "idioma_original"),
    ):
        v = extras.get(key)
        if v is not None and str(v).strip():
            out[col] = str(v)[:8000] if col.startswith("descricao") else str(v)[:4000]

    pr = extras.get("pdf_resumo")
    if isinstance(pr, str) and pr.strip():
        out["pdf_resumo"] = pr.strip()[:50000]

    # i18n EN / flags
    for col, key in (
        ("titulo_en", "titulo_en"),
        ("descricao_en", "descricao_en"),
    ):
        v = extras.get(key)
        if v is not None and str(v).strip():
            out[col] = str(v)[:8000] if col.startswith("descricao") else str(v)[:4000]
    if extras.get("traducao_automatica") is not None:
        out["traducao_automatica"] = bool(extras["traducao_automatica"])

    # Crédito / financiamento (espelho de extras)
    for col, key in (
        ("garantias", "garantias"),
        ("limite_financiavel", "limite_financiavel"),
        ("percentual_financiavel", "percentual_financiavel"),
        ("prazo_carencia", "prazo_carencia"),
        ("prazo_amortizacao", "prazo_amortizacao"),
        ("prazo_total", "prazo_total"),
        ("publico_beneficiario", "publico_beneficiario"),
        ("finalidade_financiamento", "finalidade_financiamento"),
        ("linha_credito", "linha_credito"),
        ("modalidade_financiamento", "modalidade_financiamento"),
    ):
        v = extras.get(key)
        if v is not None and str(v).strip():
            out[col] = str(v)[:2000]

    for col, key in (
        ("orgao", "orgao"),
        ("unidade_responsavel", "unidade_responsavel"),
        ("subprograma", "subprograma"),
        ("chamada", "chamada"),
        ("edital_numero", "edital_numero"),
        ("origem_portal", "origem_portal"),
        ("uf", "uf"),
        ("cidade", "cidade"),
        ("validacao_status", "validacao_status"),
        ("motivo_rejeicao", "motivo_rejeicao"),
        ("content_type_detectado", "content_type_detectado"),
        ("extraction_mode", "extraction_mode"),
        ("access_status", "access_status"),
        ("access_reason", "access_reason"),
    ):
        v = extras.get(key)
        if v is not None and str(v).strip():
            out[col] = str(v)[:2000]

    for col, key in (("url_listagem", "url_listagem"),):
        v = extras.get(key)
        if v is not None and str(v).strip():
            out[col] = str(v)[:8000]

    def _iso_date(col: str) -> None:
        v = extras.get(col)
        if v is None:
            return
        s = str(v).strip()
        if len(s) >= 10 and s[4:5] == "-" and s[7:8] == "-":
            out[col] = s[:10]

    for dk in ("data_abertura", "data_encerramento", "data_resultado"):
        _iso_date(dk)

    qd = extras.get("qualidade_dado")
    if isinstance(qd, int):
        out["qualidade_dado"] = qd
    elif isinstance(qd, str) and qd.strip().lstrip("-").isdigit():
        try:
            out["qualidade_dado"] = int(qd.strip())
        except ValueError:
            pass

    if extras.get("suspeito") is not None:
        out["suspeito"] = bool(extras["suspeito"])

    wa = _arr("warnings") or _arr("validacao_warnings")
    if wa:
        out["warnings"] = wa

    tg = _arr("tags")
    if tg:
        out["tags"] = tg
    perf = _arr("perfil_ideal")
    if perf:
        out["perfil_ideal"] = perf

    def _numeric_extra(col: str) -> None:
        v = extras.get(col)
        if v is None:
            return
        if isinstance(v, (int, float)):
            out[col] = float(v)
            return
        if isinstance(v, str) and v.strip():
            try:
                s = v.strip().replace(",", ".")
                out[col] = float(s)
            except ValueError:
                pass

    for nk in ("valor_estimado", "valor_total"):
        _numeric_extra(nk)

    for jk in ("documentos", "anexos"):
        v = extras.get(jk)
        if isinstance(v, (dict, list)):
            out[jk] = v

    # Deduplicação: o transformer grava content_hash em extras
    raw_hash = extras.get("content_hash") or extras.get("hash_deduplicacao")
    if isinstance(raw_hash, str):
        h = raw_hash.strip()
        if len(h) >= 16:
            out["hash_deduplicacao"] = h[:128]

    return out
