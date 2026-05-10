"""
Curadoria local lote 3B China (NSFC, AVIC, USTC university).
Edita apenas os JSON brutos indicados; nao toca readiness, Supabase, gate global.
Executar a partir da raiz do repositorio: python scripts/apply_lote3b_china_curadoria.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _dump(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def curate_nsfc(items: list) -> tuple[list, dict]:
    """Remove noticias politicas, reunioes internas, forums, ciencia popular, paginas genericas."""
    remove_idx = {
        0,
        1,
        2,
        3,
        4,
        5,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        22,
        25,
        26,
        27,
    }
    tipo_by_old_index = {
        6: "chamada_publica",
        7: "grant",
        8: "grant",
        9: "chamada_publica",
        10: "chamada_publica",
        20: "funding_opportunity",
        21: "funding_opportunity",
        23: "chamada_publica",
        24: "grant",
    }
    report = {"removidos": [], "mantidos": []}
    new_list = []
    for i, it in enumerate(items):
        if i in remove_idx:
            ex = it.get("extras") or {}
            report["removidos"].append(
                {
                    "indice_original": i,
                    "titulo_original": ex.get("titulo_original") or it.get("titulo"),
                    "link": it.get("link"),
                    "motivo": _nsfc_remove_reason(i),
                }
            )
            continue
        ex = it.setdefault("extras", {})
        if i in tipo_by_old_index:
            ex["tipo_oportunidade"] = tipo_by_old_index[i]
        ex.setdefault("origem_portal", "NSFC (nsfc.gov.cn)")
        new_list.append(it)
        report["mantidos"].append(
            {
                "titulo_original": ex.get("titulo_original") or it.get("titulo"),
                "link": it.get("link"),
                "tipo_oportunidade": ex.get("tipo_oportunidade"),
            }
        )
    return new_list, report


def _nsfc_remove_reason(i: int) -> str:
    return {
        0: "indicacao politica / discurso institucional, sem edital",
        1: "reuniao interna de avaliacao, sem oportunidade de candidatura",
        2: "supervisao de fundos / evento administrativo",
        3: "duplicata noticia politica",
        4: "reuniao de revisao de projetos",
        5: "relatorio de inspecao de sites institucionais",
        11: "portal de sistema (grants.nsfc), nao e registro de oportunidade",
        12: "pagina de referencia generica (prazos)",
        13: "noticia de resultado cientifico",
        14: "relatorio de forum (Shuangqing)",
        15: "relatorio de forum",
        16: "relatorio de forum",
        17: "relatorio de forum",
        18: "ferramenta de denuncia, nao edital",
        19: "pagina de divulgacao de resultados",
        22: "indice institucional Funding & Support",
        25: "noticia institucional generica (titulo repetido)",
        26: "noticia institucional generica (titulo repetido)",
        27: "noticia institucional generica (titulo repetido)",
    }.get(i, "filtrado na curadoria")


def curate_avic(items: list) -> tuple[list, dict]:
    """Mantem uma unica entrada util (recrutamento publico); remove duplicatas e paginas genericas."""
    keep_link = "http://www.avic.com/c/2026-04-22/642825.shtml"
    report = {"removidos": [], "mantidos": []}
    chosen = None
    for it in items:
        if it.get("link") == keep_link:
            chosen = it
            break
    if chosen is None:
        return [], {"erro": "item de recrutamento AVIC esperado nao encontrado", "removidos": [], "mantidos": []}
    for i, it in enumerate(items):
        if it is chosen:
            continue
        ex = it.get("extras") or {}
        report["removidos"].append(
            {
                "indice_original": i,
                "titulo_original": ex.get("titulo_original") or it.get("titulo"),
                "link": it.get("link"),
                "motivo": _avic_remove_reason(it),
            }
        )
    ex = chosen.setdefault("extras", {})
    ex["tipo_oportunidade"] = "chamada_publica"
    ex.setdefault("origem_portal", "AVIC (avic.com)")
    ex["setor_estrategico"] = "ciencia_tecnologia"
    ex["subtema"] = []
    ex["area_cientifica"] = []
    ex["area_tecnologica"] = []
    report["mantidos"] = [
        {
            "titulo_original": ex.get("titulo_original") or chosen.get("titulo"),
            "link": chosen.get("link"),
            "classificacao_curadoria": "oportunidade_rh_publica (nao procurement de defesa)",
            "tipo_oportunidade": ex.get("tipo_oportunidade"),
        }
    ]
    return [chosen], report


def _avic_remove_reason(it: dict) -> str:
    link = str(it.get("link") or "")
    tit = str((it.get("extras") or {}).get("titulo_original") or it.get("titulo") or "")
    if "avic.com.cn" in link and "avic.com/c/2026-04-22/642825" not in link:
        return "espelho .com.cn duplicado ou pagina generica"
    if "en.avic.com" in link:
        return "secao military aviation generica (sem edital)"
    if "中储粮" in tit or "中储粮" in str(it.get("descricao", "")):
        return "noticia de outro grupo (SASAC/alimentos), fora do escopo AVIC"
    if tit in ("新闻中心", "新闻发言人", "基础科研", "管理创新"):
        return "pagina institucional / hub de navegacao"
    if link.rstrip("/") in ("http://www.avic.com/sycd/xwzx", "http://www.avic.com.cn/sycd/xwzx"):
        return "hub noticias"
    if "642825.shtml" in link and "avic.com.cn" in link:
        return "duplicata do anuncio de recrutamento no espelho .com.cn"
    return "conteudo misto ou nao edital"


def curate_university(items: list) -> tuple[list, dict]:
    """Remove pagina-agregadora e aviso de seguranca; corrige tipos e metadados sem evidencia nuclear."""
    remove_idx = {0, 5}
    report = {"removidos": [], "mantidos": []}
    new_list = []
    for i, it in enumerate(items):
        if i in remove_idx:
            ex = it.get("extras") or {}
            report["removidos"].append(
                {
                    "indice_original": i,
                    "titulo_original": ex.get("titulo_original") or it.get("titulo"),
                    "link": it.get("link"),
                    "motivo": "pagina indice de listagens"
                    if i == 0
                    else "aviso interno de seguranca de laboratorio, sem licitacao ou fundos",
                }
            )
            continue
        ex = it.setdefault("extras", {})
        ex.setdefault("origem_portal", "USTC (ustc.edu.cn)")
        ex["tipo_oportunidade"] = "grant"
        ex["setor_estrategico"] = "ciencia_tecnologia"
        ex["subtema"] = []
        ex["area_cientifica"] = []
        ex["area_tecnologica"] = []
        tit = ex.get("titulo_original") or it.get("titulo") or ""
        if "国家重点研发计划" in tit or "政府间国际科技创新合作" in tit:
            ex["tipo_oportunidade"] = "funding_opportunity"
        if "霍英东" in tit or "基金委通知" in tit:
            ex["tipo_oportunidade"] = "grant"
        dp = it.get("data_publicacao")
        if dp in ("1966-01-01", "1991-01-01"):
            it["data_publicacao"] = None
        new_list.append(it)
        report["mantidos"].append(
            {
                "titulo_original": ex.get("titulo_original") or it.get("titulo"),
                "link": it.get("link"),
                "tipo_oportunidade": ex.get("tipo_oportunidade"),
            }
        )
    return new_list, report


def main() -> dict:
    out: dict = {"fontes": {}}
    for name, curate_fn in (
        ("china_nsfc", curate_nsfc),
        ("china_avic", curate_avic),
        ("china_university_procurement", curate_university),
    ):
        path = ROOT / name / "outputs" / f"{name}_editais.json"
        items = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise SystemExit(f"{path}: esperado lista")
        new_items, rep = curate_fn(items)
        if not new_items:
            raise SystemExit(f"{name}: lista vazia apos curadoria — abortar para nao gravar [] por engano")
        _dump(path, new_items)
        out["fontes"][name] = {
            "antes": len(items),
            "depois": len(new_items),
            "detalhe": rep,
        }
    return out


if __name__ == "__main__":
    summary = main()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
