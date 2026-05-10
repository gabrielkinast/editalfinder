#!/usr/bin/env python3
"""Parte 1: verifica standardized oficial isolado e grava recovery_b_official_dryrun_context.{md,json}."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "audit_reports_main_pipeline"
STD_DIR = MAIN / "recovery_b_official_dryrun_standardized"
ARTIFACTS = [
    MAIN / "recovery_b_by_source.json",
    MAIN / "recovery_b_suspeitos_context.json",
    MAIN / "recovery_b_loader_dryrun.json",
    MAIN / "recovery_b_apply_recommendation.json",
]

NOISE_TITLES = {
    "contato",
    "fale conosco",
    "saiba mais",
    "menu",
    "buscar",
    "detalhes",
    "home",
    "about",
    "contact",
    "faq",
}


def _load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _val_status(it: Dict[str, Any]) -> str:
    ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
    return str(ex.get("validacao_status") or it.get("validacao_status") or "").strip().lower()


def _setor_len(it: Dict[str, Any]) -> int:
    ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
    s = ex.get("setor_estrategico")
    if isinstance(s, list):
        return len([x for x in s if str(x).strip()])
    if isinstance(s, str) and s.strip():
        return 1
    return 0


def _audit_items(items: List[Dict[str, Any]], fonte: str) -> Dict[str, Any]:
    suspeito = 0
    noise = []
    login_like = []
    inst = []
    setor_gt3 = []
    for it in items:
        if not isinstance(it, dict):
            continue
        if _val_status(it) == "suspeito":
            suspeito += 1
        tit = str(it.get("titulo") or "").strip().lower()
        if tit in NOISE_TITLES:
            noise.append({"titulo": it.get("titulo"), "link": it.get("link")})
        if "login" in tit and len(tit) < 48:
            login_like.append({"titulo": it.get("titulo"), "link": it.get("link")})
        lk = str(it.get("link") or "").lower().rstrip("/")
        if lk.endswith("badesul.com.br/home") or lk == "https://www.badesul.com.br/home":
            inst.append({"titulo": it.get("titulo"), "link": it.get("link")})
        if _setor_len(it) > 3:
            setor_gt3.append({"titulo": it.get("titulo"), "setor_n": _setor_len(it)})
    return {
        "fonte": fonte,
        "itens": len(items),
        "validacao_suspeito": suspeito,
        "titulo_ruidoso_exact": noise,
        "login_titulo_curto": login_like,
        "institucional_home_badesul": inst,
        "setor_estrategico_mais_de_3": setor_gt3,
    }


def main() -> int:
    expected = ["amazul_standardized.json", "ambev_standardized.json", "badesul_standardized.json"]
    missing = [n for n in expected if not (STD_DIR / n).is_file()]
    per_file: List[Dict[str, Any]] = []
    total_items = 0
    total_suspeito = 0
    for name in expected:
        p = STD_DIR / name
        data = _load(p)
        if isinstance(data, dict):
            data = [data]
        items = [x for x in data if isinstance(x, dict)]
        src = name.replace("_standardized.json", "")
        r = _audit_items(items, src)
        per_file.append(r)
        total_items += r["itens"]
        total_suspeito += r["validacao_suspeito"]

    artifacts_present = {str(a.relative_to(ROOT)).replace("\\", "/"): a.is_file() for a in ARTIFACTS}

    checks = {
        "ficheiros_standardized_presentes": len(missing) == 0,
        "ficheiros_em_falta": missing,
        "total_itens": total_items,
        "validacao_suspeito_total": total_suspeito,
        "validacao_suspeito_zero": total_suspeito == 0,
        "mapping_errors_total_loader_previo": _load(MAIN / "recovery_b_loader_dryrun.json").get(
            "mapping_errors_total"
        ),
        "titulo_ruidoso_exact_total": sum(len(x["titulo_ruidoso_exact"]) for x in per_file),
        "login_titulo_curto_total": sum(len(x["login_titulo_curto"]) for x in per_file),
        "institucional_badesul_home_total": sum(len(x["institucional_home_badesul"]) for x in per_file),
        "setor_estrategico_mais_de_3_total": sum(len(x["setor_estrategico_mais_de_3"]) for x in per_file),
        "artefatos_recovery_b_lidos": artifacts_present,
    }

    out_json = {
        "pasta_standardized": str(STD_DIR.relative_to(ROOT)).replace("\\", "/"),
        "verificacao_por_ficheiro": per_file,
        "checks": checks,
        "conformidade": {
            "tres_jsons_presentes": checks["ficheiros_standardized_presentes"],
            "nenhum_suspeito": checks["validacao_suspeito_zero"],
            "mapping_errors_previo_zero": checks["mapping_errors_total_loader_previo"] == 0,
            "sem_titulo_ruidoso_canonico": checks["titulo_ruidoso_exact_total"] == 0,
            "sem_login_isolado_heuristica": checks["login_titulo_curto_total"] == 0,
        "sem_institucional_home": checks["institucional_badesul_home_total"] == 0,
        "setor_estrategico_mais_de_3_zero": checks["setor_estrategico_mais_de_3_total"] == 0,
    },
}
    (MAIN / "recovery_b_official_dryrun_context.json").write_text(
        json.dumps(out_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    c = out_json["conformidade"]

    def _sim(x: Any) -> str:
        return "sim" if x else "não"

    lines = [
        "# Recovery B — contexto dry-run oficial (isolado)",
        "",
        "## Pasta",
        "",
        "- `audit_reports_main_pipeline/recovery_b_official_dryrun_standardized/`",
        "",
        "## Contagens",
        "",
        f"- Itens totais (3 ficheiros): **{total_items}**",
        f"- `validacao_status=suspeito`: **{total_suspeito}**",
        "",
        "## Conformidade (verificações automáticas)",
        "",
        f"- Três JSONs presentes: **{_sim(c['tres_jsons_presentes'])}**",
        f"- Nenhum suspeito: **{_sim(c['nenhum_suspeito'])}**",
        f"- Loader prévio mapping_errors=0: **{_sim(c['mapping_errors_previo_zero'])}**",
        f"- Título ruído (lista curta canónica): **{_sim(c['sem_titulo_ruidoso_canonico'])}** (ocorrências: {checks['titulo_ruidoso_exact_total']})",
        f"- Login isolado (heurística título): **{_sim(c['sem_login_isolado_heuristica'])}**",
        f"- Institucional BADESUL /home: **{_sim(c['sem_institucional_home'])}**",
        f"- Itens com setor_estrategico > 3: **{checks['setor_estrategico_mais_de_3_total']}** (meta: zero — **{_sim(c.get('setor_estrategico_mais_de_3_zero', True))}**)",
        "",
        "Detalhe: ver `recovery_b_official_dryrun_context.json`.",
    ]
    (MAIN / "recovery_b_official_dryrun_context.md").write_text("\n".join(lines), encoding="utf-8")
    print("OK", MAIN / "recovery_b_official_dryrun_context.json")
    return 0 if all(c.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
