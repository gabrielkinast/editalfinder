"""validate_asia.py

Validador local da expansao Asia. Roda 4 fases:

  1. Smoke test offline de asia_intel (deteccao de idioma, setor, subtemas,
     exclusoes sensiveis, build_asia_extras).
  2. Smoke test offline de asia_source_common (parse_loose_date, is_relevant).
  3. Sanity check do patch no transformer:
     - Importa CORE/transformer.py
     - Cria item sintetico de uma fonte asiatica
     - Confirma que extras.regiao == "asia" e nenhuma sobrescrita por defesa.
     - Cria item sintetico de uma fonte nao asiatica e confirma que continua
       indo pelo fluxo build_defense_extras (compatibilidade).
  4. Teste ao vivo OPCIONAL de 1 crawler asiatico leve (--live).
     Default: japan_jetro_procurement (em ingles, paginas estaveis).

Uso:
  python scripts/validate_asia.py            # so offline
  python scripts/validate_asia.py --live     # offline + crawler ao vivo
  python scripts/validate_asia.py --live japan_jst   # crawler especifico

Sai com codigo 0 se tudo OK, 1 se qualquer assert falhar.
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Helpers de teste
# ---------------------------------------------------------------------------

PASS = "[OK]"
FAIL = "[FAIL]"

_failures = []


def _check(label, condition, detail=""):
    if condition:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label} {detail}")
        _failures.append(label)


# ---------------------------------------------------------------------------
# Fase 1: asia_intel
# ---------------------------------------------------------------------------

def phase_1_asia_intel():
    print("\n[Fase 1] asia_intel - smoke test offline")
    from asia_intel import (
        build_asia_extras, classify_strategic_sector, classify_subthemes,
        detect_keywords, detect_language, detect_sensitive_context, has_sensitive_content,
    )

    t_ja = "半導体材料および量子センサーに関する公募研究"
    t_zh = "关于核物理与先进材料的项目申报通知"
    t_en = "Call for proposals: nuclear engineering and accelerators"

    _check("detect_language(ja)", detect_language(t_ja) == "ja")
    _check("detect_language(zh)", detect_language(t_zh) == "zh")
    _check("detect_language(en)", detect_language(t_en) == "en")
    _check("detect_language(empty)", detect_language("") == "en")

    s_ja = classify_strategic_sector(t_ja)
    s_zh = classify_strategic_sector(t_zh)
    s_en = classify_strategic_sector(t_en)
    _check(
        "classify_strategic_sector(ja semicondutor+quantico)",
        s_ja in ("semicondutores", "tecnologias_quanticas"),
        f"got={s_ja}",
    )
    _check(
        "classify_strategic_sector(zh nuclear+materiais)",
        s_zh in ("nuclear", "materiais_avancados"),
        f"got={s_zh}",
    )
    _check(
        "classify_strategic_sector(en nuclear+accelerator)",
        s_en == "nuclear",
        f"got={s_en}",
    )

    sub_zh = classify_subthemes(t_zh)
    _check(
        "classify_subthemes(zh) contem fisica_nuclear",
        "fisica_nuclear" in sub_zh,
        f"got={sub_zh}",
    )

    kw_ja = detect_keywords(t_ja)
    _check(
        "detect_keywords(ja) detecta '半導体' e '量子センサー'",
        "半導体" in kw_ja and any("量子" in k for k in kw_ja),
        f"got={kw_ja}",
    )

    _check(
        "has_sensitive_content('weapon manufacturing manual')",
        has_sensitive_content("weapon manufacturing manual") is True,
    )
    _check(
        "detect_sensitive_context('weapon manufacturing manual') marca sem filtrar",
        "weapon manufacturing" in detect_sensitive_context("weapon manufacturing manual"),
    )
    _check(
        "has_sensitive_content('量子計算研究公募')",
        has_sensitive_content("量子計算研究公募") is False,
    )
    _check(
        "has_sensitive_content('武器制造工艺')",
        has_sensitive_content("武器制造工艺") is True,
    )

    extras = build_asia_extras(
        titulo_original=t_ja,
        descricao_original=t_ja,
        text_for_classification=t_ja,
        source_name="JST",
        origem="https://jst.go.jp/x",
        pais="japao",
        instituicao="Japan Science and Technology Agency",
    )
    _check("extras.regiao == 'asia'", extras["regiao"] == "asia")
    _check("extras.pais == 'japao'", extras["pais"] == "japao")
    _check("extras.idioma_original == 'ja'", extras["idioma_original"] == "ja")
    _check("extras.titulo_original preservado", extras["titulo_original"] == t_ja)
    _check("extras.necessita_traducao True", extras["necessita_traducao"] is True)
    _check(
        "extras.nivel_sensibilidade == 'publico_institucional'",
        extras["nivel_sensibilidade"] == "publico_institucional",
    )
    _check(
        "extras.palavras_chave_detectadas nao vazia",
        len(extras["palavras_chave_detectadas"]) > 0,
    )

    extras_clean = build_asia_extras(
        titulo_original="Some weapon manufacturing manual",
        descricao_original="Some weapon manufacturing manual",
        text_for_classification="Some weapon manufacturing manual",
        source_name="X",
        origem="x",
        pais="japao",
    )
    _check(
        "conteudo sensivel preserva extras do registro",
        extras_clean["titulo_original"] == "Some weapon manufacturing manual"
        and extras_clean["tipo_oportunidade"],
        f"got={extras_clean}",
    )
    _check(
        "conteudo sensivel marcado nos extras",
        extras_clean["contexto_sensivel_detectado"] is True,
        f"got={extras_clean.get('marcadores_contexto_sensivel')}",
    )


# ---------------------------------------------------------------------------
# Fase 2: asia_source_common
# ---------------------------------------------------------------------------

def phase_2_asia_source_common():
    print("\n[Fase 2] asia_source_common - smoke test offline")
    from asia_source_common import is_relevant, parse_loose_date

    _check("parse_loose_date('2025-10-15')", parse_loose_date("2025-10-15") == "2025-10-15")
    _check("parse_loose_date('2025/10/15')", parse_loose_date("2025/10/15") == "2025-10-15")
    _check("parse_loose_date('2025年10月15日')",
           parse_loose_date("2025年10月15日") == "2025-10-15")
    _check("parse_loose_date('lixo')", parse_loose_date("lixo") is None)

    _check(
        "is_relevant(ja keyword)",
        is_relevant("量子コンピュータ研究公募") is True,
    )
    _check(
        "is_relevant(zh keyword)",
        is_relevant("核物理项目申报") is True,
    )
    _check(
        "is_relevant(off-topic)",
        is_relevant("blog post sobre culinaria japonesa") is False,
    )
    _check(
        "is_relevant(sensivel preservado se relevante)",
        is_relevant("weapon manufacturing manual nuclear engineering") is True,
    )


# ---------------------------------------------------------------------------
# Fase 3: patch transformer
# ---------------------------------------------------------------------------

def phase_3_transformer_patch():
    print("\n[Fase 3] CORE/transformer.py - patch de roteamento Asia/Defesa")
    # Importa o transformer adicionando CORE/ ao path.
    core_dir = ROOT / "CORE"
    if str(core_dir) not in sys.path:
        sys.path.insert(0, str(core_dir))
    transformer = importlib.import_module("transformer")

    # Caso 1: fonte asiatica.
    item_asia = {
        "titulo": "量子センサーに関する公募研究",
        "descricao": "本公募では量子センサー技術および加速器を対象とする",
        "link": "https://www.jst.go.jp/announce/example",
        "fonte": "JST",
        "extras": {
            "regiao": "asia",
            "pais": "japao",
            "idioma_original": "ja",
            "titulo_original": "量子センサーに関する公募研究",
            "descricao_original": "本公募では量子センサー技術および加速器を対象とする",
            "instituicao": "Japan Science and Technology Agency",
            "orgao_responsavel": "JST",
        },
    }
    out_asia = transformer._transform_single_item(item_asia, "japan_jst")
    if out_asia is None:
        _check("transform asia produziu output", False, "out_asia is None")
        return
    ex = out_asia["extras"]
    _check("[asia] extras.regiao == 'asia'", ex.get("regiao") == "asia")
    _check("[asia] extras.pais == 'japao'", ex.get("pais") == "japao")
    _check(
        "[asia] extras.setor_estrategico nao 'defesa_industrial'",
        ex.get("setor_estrategico") != "defesa_industrial",
        f"got={ex.get('setor_estrategico')}",
    )
    _check(
        "[asia] extras.titulo_original preservado",
        ex.get("titulo_original") == item_asia["extras"]["titulo_original"],
    )
    _check(
        "[asia] extras.nivel_sensibilidade == 'publico_institucional'",
        ex.get("nivel_sensibilidade") == "publico_institucional",
    )
    _check(
        "[asia] palavras_chave_detectadas nao vazias",
        len(ex.get("palavras_chave_detectadas") or []) > 0,
    )

    # Caso 2: fonte nao-asiatica - confirma compatibilidade.
    item_def = {
        "titulo": "Edital de defesa industrial",
        "descricao": "Programa de financiamento dual-use",
        "link": "https://example.gov/edital123",
        "fonte": "PNCP",
        "extras": {},
    }
    out_def = transformer._transform_single_item(item_def, "pncp_defesa")
    if out_def is None:
        _check("transform defesa produziu output", False, "out_def is None")
        return
    ex_def = out_def["extras"]
    _check(
        "[defesa] extras.setor_estrategico == 'defesa_industrial'",
        ex_def.get("setor_estrategico") == "defesa_industrial",
        f"got={ex_def.get('setor_estrategico')}",
    )
    _check(
        "[defesa] extras NAO contem 'regiao'='asia'",
        ex_def.get("regiao") != "asia",
        f"got={ex_def.get('regiao')}",
    )


# ---------------------------------------------------------------------------
# Fase 4: live crawler (opcional)
# ---------------------------------------------------------------------------

def phase_4_live_crawler(crawler_name: str):
    print(f"\n[Fase 4] Crawler ao vivo: {crawler_name}")
    crawler_dir = ROOT / crawler_name
    if not crawler_dir.is_dir():
        _check(f"pasta {crawler_name} existe", False)
        return
    main_py = crawler_dir / f"main_{crawler_name}.py"
    if not main_py.exists():
        _check(f"{main_py.name} existe", False)
        return

    # Roda como subprocess para isolar.
    import subprocess
    print(f"  -> Executando {main_py} ...")
    result = subprocess.run(
        [sys.executable, main_py.name],
        cwd=str(crawler_dir),
        capture_output=True,
        text=True,
        timeout=180,
    )
    print(f"  stdout: {result.stdout.strip()[:500]}")
    if result.stderr.strip():
        print(f"  stderr: {result.stderr.strip()[:500]}")
    _check(f"crawler {crawler_name} returncode == 0", result.returncode == 0)

    out_path = crawler_dir / "outputs" / f"{crawler_name}_editais.json"
    _check(f"output JSON gerado: {out_path.name}", out_path.exists())
    if not out_path.exists():
        return

    raw = out_path.read_text(encoding="utf-8")
    _check("JSON nao-vazio (pode ser '[]' se site mudou - aceito)", len(raw) > 0)
    # ensure_ascii=False -> nao deve ter sequencias \uXXXX para CJK
    _check(
        "JSON UTF-8 sem escape \\u (ensure_ascii=False)",
        "\\u" not in raw or any(ord(c) > 127 for c in raw),
    )

    try:
        data = json.loads(raw)
        _check("JSON parseavel", isinstance(data, list))
        if data:
            it = data[0]
            ex = it.get("extras", {})
            _check("[live] item tem regiao=='asia'", ex.get("regiao") == "asia")
            _check("[live] item tem nivel_sensibilidade", bool(ex.get("nivel_sensibilidade")))
        else:
            print("  (lista vazia - normal se o site nao expos itens hoje)")
    except Exception as exc:
        _check(f"JSON parse OK", False, f"{exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Validador da expansao Asia.")
    parser.add_argument(
        "--live",
        nargs="?",
        const="japan_jetro_procurement",
        default=None,
        help="Roda 1 crawler asiatico ao vivo (default: japan_jetro_procurement).",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("VALIDADOR EditalFinder - Expansao Asia")
    print("=" * 60)

    phase_1_asia_intel()
    phase_2_asia_source_common()
    phase_3_transformer_patch()
    if args.live:
        phase_4_live_crawler(args.live)

    print("\n" + "=" * 60)
    if _failures:
        print(f"{FAIL} {len(_failures)} verificacao(oes) falharam:")
        for f in _failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"{PASS} TODAS as verificacoes passaram.")
        sys.exit(0)


if __name__ == "__main__":
    main()
