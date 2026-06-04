"""
Classificação central de oportunidades (Backend 1).

- tipo de registro (edital / notícia / pesquisa / concurso / …)
- modalidade normalizada
- escopo geográfico
- fonte normalizada

Somente leitura — não persiste no banco.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
MODALITY_BUCKETS: Dict[str, str] = {
    "fomento_chamada_publica": "Fomento / chamada pública",
    "subvencao_inovacao": "Subvenção / inovação",
    "pesquisa_cientifica": "Pesquisa científica",
    "bolsa_formacao": "Bolsas / formação",
    "cooperacao_internacional": "Cooperação internacional",
    "compra_licitacao": "Compras / licitação",
    "concurso_selecao": "Concurso / seleção",
    "premio_desafio": "Prêmio / desafio",
    "evento_capacitacao": "Evento / capacitação",
    "noticia_institucional": "Notícia institucional",
    "pesquisa_publicacao": "Pesquisa / publicação",
    "outro": "Outro",
    "sem_classificacao": "Sem classificação",
}

BR_ORGAOS = (
    "fapesc",
    "fapergs",
    "cnpq",
    "finep",
    "capes",
    "fapesp",
    "faperj",
    "fapemig",
    "bndes",
    "sebrae",
    "senai",
    "embrapii",
    "mcti",
    "mctic",
    "fundação araucária",
    "fundacao araucaria",
    "banco do brasil",
    "caixa",
)

MULTILATERAL = (
    "banco mundial",
    "world bank",
    "banco interamericano",
    "bid",
    "idb",
    "onu",
    "unesco",
    "oecd",
    "ocde",
    "horizon europe",
    "horizon 2020",
    "european commission",
    "união europeia",
    "european union",
    "undp",
)

INTERNATIONAL = (
    "grants.gov",
    "grants gov",
    "nsf",
    "nih",
    "nasa",
    "darpa",
    "nato",
    "ukri",
    "china international",
    "china ",
    "korea",
    "japan",
    "australia",
    "defense.gov",
    "army.mil",
    "horizon",
    "european",
    "uk research",
)


def _norm(s: Any) -> str:
    if s is None:
        return ""
    t = str(s).strip().lower()
    t = unicodedata.normalize("NFKD", t)
    return "".join(c for c in t if not unicodedata.combining(c))


def _blob(record: Dict[str, Any]) -> str:
    parts = [
        record.get("titulo"),
        record.get("descricao"),
        record.get("tipo_oportunidade"),
        record.get("tipo_recurso"),
        record.get("modalidade"),
        record.get("categoria"),
        record.get("area"),
        record.get("fonte_recurso"),
        record.get("fonte"),
        record.get("link"),
    ]
    return _norm(" ".join(str(p) for p in parts if p))


def classify_record_kind(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    edital | noticia | pesquisa | concurso | portal | desconhecido
    """
    reasons: List[str] = []
    b = _blob(record)
    link = _norm(record.get("link") or "")
    tipo_op = _norm(record.get("tipo_oportunidade") or "")

    if any(
        x in b
        for x in (
            "concurso publico",
            "concurso público",
            "processo seletivo",
            "vestibular",
            "selecao publica",
            "seleção pública",
            "vagas para",
            "cargo publico",
        )
    ) or tipo_op in ("concurso", "processo_seletivo", "vestibular"):
        return {"kind": "concurso", "confidence": "media", "reasons": ["concurso_keywords"]}

    if any(
        x in b or x in link
        for x in (
            "/news/",
            "/noticia",
            "/noticias",
            "comunicado",
            "press release",
            "publicado em",
            "ministro anuncia",
            "secretario anuncia",
        )
    ):
        reasons.append("news_hints")
        if not any(
            x in b
            for x in ("chamada pública", "chamada publica", "edital n", "fomento", "submissão de propostas")
        ):
            return {"kind": "noticia", "confidence": "media", "reasons": reasons}

    if any(
        x in b
        for x in (
            "artigo científico",
            "artigo cientifico",
            "preprint",
            "doi:",
            "journal",
            "published in",
            "dataset",
            "research article",
            "paper",
            "publicação científica",
        )
    ):
        return {"kind": "pesquisa", "confidence": "media", "reasons": ["research_publication"]}

    if any(x in b for x in ("resultado", "homologação", "homologacao", "retificação", "retificacao")):
        reasons.append("edital_auxiliar")
        return {"kind": "edital", "confidence": "baixa", "reasons": reasons + ["auxiliary_edital_doc"]}

    if any(
        x in b
        for x in (
            "chamada pública",
            "chamada publica",
            "edital de fomento",
            "funding opportunity",
            "grant program",
            "call for proposals",
            "licitação",
            "licitacao",
            "pregão",
            "fomento",
            "subvenção",
            "bolsa",
            "financiamento",
        )
    ) or tipo_op in ("edital", "chamada_publica", "chamada", "grant", "funding"):
        return {"kind": "edital", "confidence": "alta", "reasons": ["opportunity_keywords"]}

    if any(x in link for x in ("/portal", "/home", "/index")) and "edital" not in b:
        return {"kind": "portal", "confidence": "baixa", "reasons": ["portal_url"]}

    return {"kind": "desconhecido", "confidence": "baixa", "reasons": ["no_strong_signal"]}


def classify_opportunity_modality(record: Dict[str, Any]) -> Dict[str, Any]:
    """modalidade_normalizada + modalidade_label + confidence + reasons."""
    reasons: List[str] = []
    field_blob = _norm(
        " ".join(
            str(record.get(k) or "")
            for k in (
                "tipo_recurso",
                "tipo_oportunidade",
                "modalidade",
                "modalidade_financiamento",
                "categoria",
                "linha_credito",
                "natureza_recurso",
            )
        )
    )
    title = _norm(record.get("titulo") or "")
    combined = f"{field_blob} {title}"

    rules: List[Tuple[str, Tuple[str, ...]]] = [
        ("noticia_institucional", ("noticia", "notícia", "comunicado", "press release", "announcement")),
        ("pesquisa_publicacao", ("preprint", "doi", "journal", "paper", "publication", "dataset")),
        ("concurso_selecao", ("concurso", "processo seletivo", "vestibular", "seleção pública")),
        ("compra_licitacao", ("licitação", "licitacao", "pregão", "pregao", "procurement", "tender", "rfp")),
        ("bolsa_formacao", ("bolsa", "fellowship", "scholarship", "traineeship", "mestrado", "doutorado")),
        ("premio_desafio", ("prêmio", "premio", "challenge", "desafio", "award", "prize")),
        ("evento_capacitacao", ("webinar", "workshop", "evento", "capacitação", "training", "curso")),
        ("cooperacao_internacional", ("cooperação internacional", "international cooperation", "bilateral")),
        ("subvencao_inovacao", ("subvenção", "subvencao", "fundo perdido", "innovation grant", "sbir", "sttr")),
        ("pesquisa_cientifica", ("pesquisa científica", "research grant", "p&d", "r&d", "scientific research")),
        ("fomento_chamada_publica", ("chamada pública", "chamada publica", "edital", "fomento", "grant", "funding")),
    ]

    for key, phrases in rules:
        if any(p in combined for p in phrases):
            reasons.append(f"match:{key}")
            return {
                "modalidade_normalizada": key,
                "modalidade_label": MODALITY_BUCKETS[key],
                "confidence": "alta" if field_blob else "media",
                "reasons": reasons,
            }

    if field_blob and len(field_blob) < 80:
        reasons.append("short_field_fallback")
        return {
            "modalidade_normalizada": "outro",
            "modalidade_label": MODALITY_BUCKETS["outro"],
            "confidence": "baixa",
            "reasons": reasons + [f"raw:{field_blob[:60]}"],
        }

    return {
        "modalidade_normalizada": "sem_classificacao",
        "modalidade_label": MODALITY_BUCKETS["sem_classificacao"],
        "confidence": "nenhuma",
        "reasons": reasons,
    }


def classify_geo_scope(record: Dict[str, Any]) -> Dict[str, Any]:
    fonte = _norm(record.get("fonte_recurso") or record.get("fonte") or "")
    link = _norm(record.get("link") or "")
    pais = _norm(record.get("pais") or "")
    uf = _norm(record.get("uf") or "")
    regiao = _norm(record.get("regiao") or "")
    blob = f"{fonte} {link} {pais} {uf} {regiao}"

    if any(m in blob for m in MULTILATERAL):
        return {"scope": "multilateral", "confidence": "media", "pais_origem": pais or None}
    if any(b in fonte for b in BR_ORGAOS) or ".br" in link or pais in ("brasil", "brazil") or uf:
        return {"scope": "brasil", "confidence": "alta", "pais_origem": pais or "Brasil"}
    if any(i in blob for i in INTERNATIONAL):
        return {
            "scope": "internacional",
            "confidence": "media",
            "pais_origem": pais or None,
        }
    if pais and pais not in ("brasil", "brazil", ""):
        return {"scope": "internacional", "confidence": "baixa", "pais_origem": pais}
    return {"scope": "desconhecido", "confidence": "baixa", "pais_origem": pais or None}


THEMATIC_AREA_BUCKETS: Dict[str, str] = {
    "tecnologia_inovacao": "Tecnologia e Inovação",
    "tecnologias_estrategicas": "Tecnologias estratégicas",
    "computacao_ia": "Computação e IA",
    "saude": "Saúde",
    "educacao_pesquisa": "Educação e Pesquisa",
    "energia": "Energia",
    "meio_ambiente": "Meio ambiente",
    "agronegocio": "Agronegócio",
    "industria": "Indústria",
    "defesa_seguranca": "Defesa e Segurança",
    "espaco": "Espaço / sistemas orbitais",
    "aeroespacial": "Aeroespacial",
    "nuclear": "Nuclear",
    "materiais": "Materiais",
    "biotecnologia": "Biotecnologia",
    "cidades_mobilidade": "Cidades e Mobilidade",
    "cultura_social": "Cultura e Social",
    "economia_negocios": "Economia e Negócios",
    "startups": "Startups",
    "multissetorial": "Multissetorial",
    "sem_classificacao": "Sem classificação",
}

# peso base por área; multiplicadores de canal aplicados depois
THEMATIC_AREA_RULES: List[Tuple[str, Tuple[str, ...], int]] = [
    ("energia", ("energia", "hidrogenio", "renovavel", "solar", "eolica", "biocombustivel", "bateria", "armazenamento energetico", "matriz energetica", "eletricidade"), 10),
    ("saude", ("saude", "sus", "medicina", "hospital", "diagnostico", "farmaco", "vacina", "epidemiologia", "clinica"), 10),
    ("agronegocio", ("agro", "agronegocio", "agricultura", "pecuaria", "rural", "embrapa", "lavoura", "safra", "aquicultura"), 10),
    (
        "defesa_seguranca",
        (
            "defesa",
            "defence",
            "defense",
            "militar",
            "military",
            "seguranca nacional",
            "nato",
            "darpa",
            "exercito",
            "marinha",
            "air force",
            "forcas armadas",
            "armamento",
            "counter-drone",
            "counter drone",
            "c-uas",
            "dual use",
            "dual-use",
        ),
        11,
    ),
    (
        "espaco",
        (
            "satelite",
            "satellite",
            "orbital",
            "orbita",
            "orbit",
            "spacecraft",
            "space debris",
            "debris orbital",
            "constellation",
            "launch vehicle",
            "space systems",
            "servicing orbital",
            "sistemas orbitais",
            "missao espacial",
            "programa espacial",
        ),
        12,
    ),
    (
        "aeroespacial",
        (
            "aeroespacial",
            "aerospace",
            "propulsao",
            "propulsion",
            "aeronautica",
            "aeronautics",
            "aviacao",
            "aircraft",
            "foguete",
            "rocket engine",
            "uav",
            "hypersonic",
        ),
        11,
    ),
    ("nuclear", ("nuclear", "radiacao", "reator", "radioisotopo", "dosimetria", "radioquimica", "cnen", "fissao"), 12),
    ("materiais", ("materiais", "polimeros", "ceramica", "metalurgia", "semicondutor", "nanomaterial", "compostos"), 9),
    ("computacao_ia", ("inteligencia artificial", "machine learning", "deep learning", "software", "big data", "cybersecurity", "ciberseguranca", "computacao", "llm", "data science"), 10),
    ("startups", ("startup", "aceleracao", "incubacao", "venture", "empreendedorismo inovador", "scale-up"), 9),
    ("educacao_pesquisa", ("universidade", "pesquisa cientifica", "bolsa", "capes", "cnpq", "mestrado", "doutorado", "pos-graduacao", "ensino superior"), 9),
    ("meio_ambiente", ("meio ambiente", "biodiversidade", "clima", "carbono", "conservacao", "saneamento"), 9),
    ("industria", ("industria", "manufatura", "fabrica", "processo produtivo", "cadeia produtiva", "industrial"), 8),
    ("biotecnologia", ("biotecnologia", "bioengenharia", "genomica", "bioeconomia", "fermentacao"), 9),
    ("cidades_mobilidade", ("mobilidade urbana", "transporte publico", "smart city", "cidade inteligente"), 8),
    ("cultura_social", ("cultura", "arte", "patrimonio", "inclusao social", "assistencia social"), 7),
    ("economia_negocios", ("comercio", "varejo", "turismo", "logistica", "exportacao", "microcredito"), 7),
    (
        "tecnologias_estrategicas",
        (
            "critical technologies",
            "strategic technology",
            "sovereign technology",
            "supply chain resilience",
            "advanced manufacturing",
            "tecnologias criticas",
            "tecnologia estrategica",
            "cadeia de suprimentos",
        ),
        7,
    ),
    (
        "tecnologia_inovacao",
        (
            "inovacao aberta",
            "open innovation",
            "p&d empresarial",
            "pd&i empresarial",
            "transferencia de tecnologia",
            "ecossistema de inovacao",
            "chamada de inovacao",
        ),
        6,
    ),
    ("multissetorial", ("multissetorial", "multi-setorial", "multiplos setores", "varios setores", "todas as areas"), 5),
]

# Tags/setores genéricos de crawler — baixo peso sem confirmação em título/descrição
GENERIC_TAG_ALIASES: Dict[str, str] = {
    "aeroespacial": "aeroespacial",
    "aeroespacial_militar": "aeroespacial",
    "veiculos": "aeroespacial",
    "dual_use": "defesa_seguranca",
    "defesa": "defesa_seguranca",
    "defesa_industrial": "defesa_seguranca",
    "nuclear": "nuclear",
    "energia": "energia",
    "ciencia_tecnologia": "tecnologias_estrategicas",
    "materiais_avancados": "materiais",
    "seguranca_publica": "defesa_seguranca",
}

TAG_ONLY_DOWNGRADE_AREAS = frozenset(
    {"aeroespacial", "espaco", "defesa_seguranca", "nuclear", "tecnologias_estrategicas"}
)

CHANNEL_WEIGHTS = {
    "title_desc": 3.0,
    "explicit_field": 2.0,
    "tags_meta": 0.35,
    "fonte_hint": 0.5,
}


def _thematic_title_desc_blob(record: Dict[str, Any]) -> str:
    parts = [record.get("titulo"), record.get("descricao"), record.get("objetivo")]
    extras = record.get("extras")
    if isinstance(extras, dict) and extras.get("objetivo"):
        parts.append(extras.get("objetivo"))
    return _norm(" ".join(str(p) for p in parts if p))


def _thematic_explicit_field_blob(record: Dict[str, Any]) -> str:
    parts = [record.get("area"), record.get("setor"), record.get("categoria"), record.get("temas")]
    return _norm(" ".join(str(p) for p in parts if p))


def _thematic_tags_meta_blob(record: Dict[str, Any]) -> str:
    parts: List[str] = []
    extras = record.get("extras")
    if isinstance(extras, dict):
        for k in ("thematic_tags", "setor_estrategico", "area_cientifica", "area_tecnologica", "subtema"):
            v = extras.get(k)
            if isinstance(v, list):
                parts.extend(str(x) for x in v)
            elif v:
                parts.append(str(v))
    return _norm(" ".join(parts))


def _thematic_fonte_blob(record: Dict[str, Any]) -> str:
    return _norm(" ".join(str(record.get(k) or "") for k in ("fonte_recurso", "fonte")))


def _channel_hits(blob: str, patterns: Tuple[str, ...]) -> List[str]:
    if not blob:
        return []
    return [p for p in patterns if p in blob]


def _score_channel(blob: str, weight: int, channel_mult: float) -> Tuple[int, List[str]]:
    if not blob:
        return 0, []
    matched: List[str] = []
    score = 0
    for key, patterns, base in THEMATIC_AREA_RULES:
        hits = _channel_hits(blob, patterns)
        if hits:
            matched.extend(hits)
            score += int(len(hits) * base * channel_mult)
    return score, matched


def _score_thematic_by_channel(record: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, Dict[str, int]], Dict[str, Any]]:
    """Retorna scores totais, scores por canal e metadados para auditoria."""
    title_blob = _thematic_title_desc_blob(record)
    field_blob = _thematic_explicit_field_blob(record)
    tags_blob = _thematic_tags_meta_blob(record)
    fonte_blob = _thematic_fonte_blob(record)

    per_channel: Dict[str, Dict[str, int]] = {
        "title_desc": {},
        "explicit_field": {},
        "tags_meta": {},
        "fonte_hint": {},
    }
    totals: Dict[str, int] = {k: 0 for k, _, _ in THEMATIC_AREA_RULES}

    for area_key, patterns, base in THEMATIC_AREA_RULES:
        for ch, blob, mult in (
            ("title_desc", title_blob, CHANNEL_WEIGHTS["title_desc"]),
            ("explicit_field", field_blob, CHANNEL_WEIGHTS["explicit_field"]),
            ("tags_meta", tags_blob, CHANNEL_WEIGHTS["tags_meta"]),
            ("fonte_hint", fonte_blob, CHANNEL_WEIGHTS["fonte_hint"]),
        ):
            hits = _channel_hits(blob, patterns)
            if hits:
                pts = int(len(hits) * base * mult)
                per_channel[ch][area_key] = per_channel[ch].get(area_key, 0) + pts
                totals[area_key] = totals.get(area_key, 0) + pts

    # Alias genéricos em tags → área mapeada (peso baixo, só canal tags)
    extras = record.get("extras")
    if isinstance(extras, dict):
        raw_tags: List[str] = []
        for k in ("thematic_tags", "setor_estrategico"):
            v = extras.get(k)
            if isinstance(v, list):
                raw_tags.extend(str(x) for x in v)
            elif v:
                raw_tags.append(str(v))
        for tag in raw_tags:
            tn = _norm(tag).replace(" ", "_")
            mapped = GENERIC_TAG_ALIASES.get(tn) or GENERIC_TAG_ALIASES.get(_norm(tag))
            if mapped:
                per_channel["tags_meta"][mapped] = per_channel["tags_meta"].get(mapped, 0) + 4
                totals[mapped] = totals.get(mapped, 0) + 4

    # espaco > aeroespacial quando termos orbitais explícitos no título
    if totals.get("espaco", 0) > 0 and totals.get("aeroespacial", 0) > 0:
        if any(p in title_blob for p in ("orbital", "orbita", "satellite", "satelite", "spacecraft", "constellation")):
            totals["aeroespacial"] = max(0, totals["aeroespacial"] - 5)

    # Sinais fracos de tecnologia/inovacao isolados
    if totals.get("tecnologia_inovacao", 0) <= 6:
        if "tecnologia" in title_blob or "inovacao" in title_blob:
            if not any(totals.get(k, 0) > 8 for k in totals if k not in ("tecnologia_inovacao", "multissetorial", "sem_classificacao", "tecnologias_estrategicas")):
                totals.pop("tecnologia_inovacao", None)

    meta = {
        "title_desc_blob_len": len(title_blob),
        "tags_blob": tags_blob[:200],
        "title_has_space_terms": any(
            p in title_blob for p in ("satellite", "satelite", "orbital", "orbita", "spacecraft", "espaco", "espacial")
        ),
        "per_channel": per_channel,
    }
    totals = {k: v for k, v in totals.items() if v > 0}
    return totals, per_channel, meta


def explain_thematic_area(record: Dict[str, Any]) -> Dict[str, Any]:
    """Diagnóstico detalhado para auditoria Backend 6."""
    result = classify_thematic_area(record)
    totals, per_channel, meta = _score_thematic_by_channel(record)
    title_blob = _thematic_title_desc_blob(record)
    primary = result["area_tematica_normalizada"]
    title_pts = per_channel.get("title_desc", {}).get(primary, 0)
    tag_pts = per_channel.get("tags_meta", {}).get(primary, 0)
    return {
        **result,
        "score_total": totals.get(primary, 0),
        "scores_all": totals,
        "per_channel": per_channel,
        "primary_from_title": title_pts > 0,
        "primary_tag_only": tag_pts > 0 and title_pts == 0 and per_channel.get("explicit_field", {}).get(primary, 0) == 0,
        "title_desc_sample": title_blob[:160],
        "meta": meta,
    }


def classify_thematic_area(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classifica área temática primária + secundárias (Backend 6).
    Tags/setor_estrategico genéricos não definem primária sem confirmação em título/descrição.
    """
    totals, per_channel, _meta = _score_thematic_by_channel(record)
    reasons: List[str] = []

    if not totals:
        return {
            "area_tematica_normalizada": "sem_classificacao",
            "area_tematica_label": THEMATIC_AREA_BUCKETS["sem_classificacao"],
            "area_tematica_confidence": "baixa",
            "area_tematica_reasons": ["no_keyword_match"],
            "area_tematica_secondary": [],
            "area_tematica_secondary_keys": [],
        }

    ranked = sorted(totals.items(), key=lambda x: -x[1])
    primary_key, primary_score = ranked[0]
    title_pts = per_channel.get("title_desc", {}).get(primary_key, 0)
    field_pts = per_channel.get("explicit_field", {}).get(primary_key, 0)
    tag_pts = per_channel.get("tags_meta", {}).get(primary_key, 0)

    tag_only_primary = tag_pts > 0 and title_pts == 0 and field_pts == 0
    secondary_candidate: Optional[str] = None
    if tag_only_primary and primary_key in TAG_ONLY_DOWNGRADE_AREAS:
        reasons.append(f"tag_only_downgrade:{primary_key}")
        secondary_candidate = primary_key
        primary_key = "multissetorial"
        if primary_score < 8:
            primary_key = "sem_classificacao"
        primary_score = totals.get(primary_key, 0) or max(5, tag_pts)
        ranked_alt = [(k, v) for k, v in ranked if k != secondary_candidate and k not in ("multissetorial", "sem_classificacao")]
        if ranked_alt and ranked_alt[0][1] >= tag_pts and per_channel.get("title_desc", {}).get(ranked_alt[0][0], 0) > 0:
            primary_key = ranked_alt[0][0]
            primary_score = ranked_alt[0][1]
            reasons.append(f"promoted_from_title:{primary_key}")

    # Defesa vs espaco vs aeroespacial
    if primary_key == "aeroespacial" and totals.get("espaco", 0) >= totals.get("aeroespacial", 0) * 0.8:
        if per_channel.get("title_desc", {}).get("espaco", 0) > 0:
            primary_key = "espaco"
            reasons.append("espaco_over_aeroespacial")

    if primary_key in ("aeroespacial", "espaco") and totals.get("defesa_seguranca", 0) > totals.get(primary_key, 0):
        if per_channel.get("title_desc", {}).get("defesa_seguranca", 0) > 0 and not per_channel.get("title_desc", {}).get(primary_key, 0):
            primary_key = "defesa_seguranca"
            reasons.append("defesa_over_space_tag")

    secondary: List[str] = []
    for key, sc in ranked:
        if key == primary_key:
            continue
        if sc >= max(6, int(primary_score * 0.4)):
            secondary.append(key)

    if primary_key == "saude" and totals.get("tecnologia_inovacao", 0) >= 6:
        secondary.append("tecnologia_inovacao")
    if primary_key == "energia" and totals.get("startups", 0) >= 6:
        secondary.append("startups")
    if tag_only_primary and secondary_candidate and secondary_candidate not in secondary and secondary_candidate != primary_key:
        secondary.append(secondary_candidate)

    secondary = [k for k in secondary if k != primary_key][:4]
    secondary_labels = [THEMATIC_AREA_BUCKETS.get(k, k) for k in secondary]

    if title_pts >= 12 or field_pts >= 10:
        confidence = "alta"
    elif title_pts >= 6 or field_pts >= 6 or (title_pts + field_pts) >= 8:
        confidence = "media"
    elif tag_pts > 0 and title_pts == 0:
        confidence = "baixa"
        reasons.append("confidence_from_tags_only")
    else:
        confidence = "baixa"

    if primary_key == "tecnologia_inovacao" and primary_score < 12 and title_pts == 0:
        primary_key = "multissetorial"
        reasons.append("weak_tech_innovation_downgraded")

    reasons.insert(0, f"primary:{primary_key}:{primary_score}:title={title_pts}:tags={tag_pts}")

    return {
        "area_tematica_normalizada": primary_key,
        "area_tematica_label": THEMATIC_AREA_BUCKETS.get(primary_key, primary_key),
        "area_tematica_confidence": confidence,
        "area_tematica_reasons": reasons,
        "area_tematica_secondary": secondary_labels,
        "area_tematica_secondary_keys": secondary,
    }


def extract_current_area_labels(record: Dict[str, Any]) -> List[str]:
    """Rótulos de área já presentes no registro (coluna area, extras, etc.)."""
    out: List[str] = []
    area = record.get("area")
    if isinstance(area, list):
        out.extend(str(x).strip() for x in area if x)
    elif area:
        out.append(str(area).strip())
    area_t = record.get("area_tematica")
    if area_t:
        out.append(str(area_t).strip())
    extras = record.get("extras")
    if isinstance(extras, dict):
        for k in ("area_negocio", "thematic_tags"):
            v = extras.get(k)
            if isinstance(v, list):
                out.extend(str(x) for x in v if x)
            elif v:
                out.append(str(v))
    return _unique_area_labels(out)


def _unique_area_labels(labels: List[str]) -> List[str]:
    seen: set = set()
    out: List[str] = []
    for lb in labels:
        k = _norm(lb)
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(lb.strip())
    return out


def is_technology_innovation_label(label: str) -> bool:
    n = _norm(label)
    return "tecnologia" in n and "inovacao" in n


def classify_source_normalized(record: Dict[str, Any]) -> Dict[str, Any]:
    original = (
        str(record.get("fonte_recurso") or record.get("fonte") or record.get("orgao") or "")
        .strip()
    ) or "Fonte não informada"
    norm = original
    norm_lower = _norm(original)

    finep_hit, finep_reasons = _detect_finep_signals(record)
    fndct_hit, fndct_reasons = _detect_fndct_signals(record)
    source_notes: List[str] = []
    fundo_origem: Optional[str] = None
    programa_fundo: Optional[str] = None

    if finep_hit:
        norm = "FINEP"
        if fndct_hit:
            fundo_origem = "FNDCT"
            programa_fundo = "FNDCT"
            source_notes.append(
                "FNDCT tratado como fundo/origem do recurso, não como fonte institucional principal."
            )
        source_notes.extend(finep_reasons)
        geo = classify_geo_scope(record)
        return {
            "fonte_normalizada": norm,
            "fonte_original": original[:200],
            "pais_origem": "Brasil",
            "source_scope": "brasil",
            "fundo_origem": fundo_origem,
            "programa_fundo": programa_fundo,
            "source_notes": source_notes,
            "source_reasons": finep_reasons,
        }

    aliases = {
        "china international": "China International Technology Transfer Center",
        "grants.gov": "Grants.gov (EUA)",
        "fapesc": "FAPESC",
        "fapergs": "FAPERGS",
        "finep": "FINEP",
        "cnpq": "CNPq",
        "horizon europe": "Horizon Europe (UE)",
        "fndct": "FNDCT",
    }
    for key, label in aliases.items():
        if key in norm_lower:
            norm = label
            break

    if fndct_hit and norm_lower in ("fndct", "fundo nacional de desenvolvimento cientifico e tecnologico"):
        if not fundo_origem:
            fundo_origem = "FNDCT"
            programa_fundo = "FNDCT"
        source_notes.extend(fndct_reasons)

    geo = classify_geo_scope(record)
    return {
        "fonte_normalizada": norm[:120],
        "fonte_original": original[:200],
        "pais_origem": geo.get("pais_origem"),
        "source_scope": geo.get("scope"),
        "fundo_origem": fundo_origem,
        "programa_fundo": programa_fundo,
        "source_notes": source_notes,
        "source_reasons": fndct_reasons if fndct_reasons else [],
    }


def _detect_finep_signals(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    link = str(record.get("link") or record.get("pdf_url") or "").lower()
    if "finep.gov.br" in link:
        reasons.append("link_finep_domain")

    for field, label in (
        ("fonte_recurso", "fonte_recurso"),
        ("fonte", "fonte"),
        ("orgao", "orgao"),
    ):
        val = _norm(str(record.get(field) or ""))
        if val and ("finep" in val or "financiadora de estudos e projetos" in val):
            reasons.append(f"{label}_finep")

    titulo = _norm(str(record.get("titulo") or ""))
    if titulo and "finep" in titulo:
        reasons.append("titulo_finep")

    descricao = _norm(str(record.get("descricao") or ""))
    if descricao and "finep" in descricao:
        fonte_val = _norm(str(record.get("fonte_recurso") or record.get("fonte") or ""))
        if "fndct" in fonte_val:
            reasons.append("descricao_finep_with_fndct_fonte")
        elif any(p in descricao for p in ("operada pela finep", "operado pela finep", "chamada publica finep")):
            if "finep" in titulo or "finep.gov.br" in link:
                reasons.append("descricao_finep_confirmed")

    extras = record.get("extras")
    if isinstance(extras, dict):
        for k in ("agencia", "orgao", "operadora"):
            v = _norm(str(extras.get(k) or ""))
            if v == "finep" or v.startswith("finep "):
                reasons.append(f"extras_{k}_finep")

    return bool(reasons), reasons


def _detect_fndct_signals(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    for field, label in (
        ("fonte_recurso", "fonte_recurso"),
        ("fonte", "fonte"),
        ("titulo", "titulo"),
        ("descricao", "descricao"),
    ):
        val = _norm(str(record.get(field) or ""))
        if val and "fndct" in val:
            reasons.append(f"{label}_fndct")

    extras = record.get("extras")
    if isinstance(extras, dict):
        for k in ("programa", "programa_fundo", "fundo_origem", "fundo"):
            v = _norm(str(extras.get(k) or ""))
            if v and "fndct" in v:
                reasons.append(f"extras_{k}_fndct")

    return bool(reasons), reasons


def classify_record_full(record: Dict[str, Any]) -> Dict[str, Any]:
    """Pacote completo para auditoria / futura view."""
    from deadline_normalizer import normalize_deadline, deadline_flags

    dl = normalize_deadline(record)
    flags = deadline_flags(dl["prazo_status"])
    return {
        "kind": classify_record_kind(record),
        "modality": classify_opportunity_modality(record),
        "geo": classify_geo_scope(record),
        "source": classify_source_normalized(record),
        "thematic_area": classify_thematic_area(record),
        "deadline": dl,
        "flags": flags,
    }
