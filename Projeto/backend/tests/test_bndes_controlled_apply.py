"""Testes apply controlado BNDES (Backend 10.2D)."""
from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from bndes_controlled_apply import (  # noqa: E402
    DEFAULT_MAX_APPLY_BATCH,
    apply_bndes_candidates,
    build_candidate_entry,
    classify_apply_action,
    is_bndes_record,
    load_candidates_file,
    merge_extras_for_apply,
    resolve_prazo_for_apply,
    run_bndes_deadline_dry_run,
    validate_candidates_batch,
    validate_dry_run_report_recent,
)
from bndes_detail_recrawl import (  # noqa: E402
    classify_bndes_record,
    enrich_bndes_recrawl_item,
    extract_bndes_deadline_from_text,
    extract_bndes_pdf_text,
)
from bndes_submission_deadline import (  # noqa: E402
    SUBMISSION_DEADLINE_KIND,
    collect_bndes_ignored_dates,
    extract_bndes_section,
    extract_bndes_submission_deadline,
)
from deadline_backfill import controlled_apply_enabled, deadline_backfill_enabled, extract_source_deadline_fields  # noqa: E402


def _future(days: int = 120) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _br(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d}/{m}/{y}"


def _bndes_item(**kwargs: object) -> dict:
    base = {
        "titulo": "Chamada Pública BNDES",
        "descricao": "",
        "link": "https://www.bndes.gov.br/wps/portal/site/home/test",
        "fonte": "BNDES",
        "extras": {"orgao_responsavel": "BNDES"},
    }
    base.update(kwargs)
    return enrich_bndes_recrawl_item(base, fetch_detail=False, fetch_pdf=False)


def test_inscricoes_ate_generates_candidate() -> None:
    iso = _future(200)
    item = _bndes_item(descricao=f"Inscrições até {_br(iso)} para seleção de fundos.")
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] >= 1


def test_prazo_final_dezembro_generates_candidate() -> None:
    y = date.today().year + 1
    item = _bndes_item(
        extras={"bndes_detail_text": f"Prazo final: 15 de dezembro de {y} para envio de propostas."}
    )
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] >= 1


def test_lancamento_rejects_date() -> None:
    item = _bndes_item(
        descricao="O Sistema BNDES lançou, em 29.10.2025, Edital de Chamada Pública.",
        extras={"pdf_url": "https://www.bndes.gov.br/documents/edital.pdf"},
    )
    out = extract_source_deadline_fields(item)
    assert out.get("prazo_envio") is None
    assert out.get("sem_prazo_kind") == "deadline_in_pdf_or_detail"


def test_publicado_em_rejected() -> None:
    dl = extract_bndes_deadline_from_text("Publicado em 10/05/2026. Resultado preliminar.")
    assert dl.get("iso") is None


def test_linha_permanente_kind() -> None:
    item = _bndes_item(
        titulo="Linha permanente BNDES Mais Inovação",
        descricao="Crédito disponível de forma contínua.",
    )
    cls = classify_bndes_record(item)
    assert cls["sem_prazo_kind"] == "permanent_funding_line"
    out = extract_source_deadline_fields(item)
    assert out["sem_prazo_kind"] == "permanent_funding_line"


def test_pdf_url_without_text_sem_prazo_kind() -> None:
    item = _bndes_item(
        descricao="Consulte o edital em PDF.",
        extras={
            "pdf_url": "https://www.bndes.gov.br/documents/edital.pdf",
            "bndes_detail_links": {
                "pdf_urls": ["https://www.bndes.gov.br/documents/edital.pdf"],
            },
        },
    )
    assert item["extras"].get("sem_prazo_kind") == "deadline_in_pdf_or_detail"


def test_pdf_text_with_deadline_candidate() -> None:
    iso = _future(300)
    item = _bndes_item(
        extras={"pdf_texto_extraido": f"Chamada Pública. Propostas até {_br(iso)}."}
    )
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] >= 1


def test_pdf_text_without_deadline_no_candidate() -> None:
    item = _bndes_item(
        extras={"pdf_texto_extraido": "Documento informativo sem datas de submissão."}
    )
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] == 0


def test_non_bndes_rejected() -> None:
    report = run_bndes_deadline_dry_run([{"fonte": "Grants.gov", "link": "https://grants.gov/x"}])
    assert report["stats"]["rejected"] == 1


def test_apply_aborts_without_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", raising=False)
    monkeypatch.setenv("EDITALFINDER_ENABLE_DEADLINE_BACKFILL", "1")
    with pytest.raises(RuntimeError, match="ALLOW_CONTROLLED_APPLY"):
        apply_bndes_candidates([{"payload_after": _bndes_item(descricao=f"Inscrições até {_br(_future())}")}])


def test_apply_aborts_wrong_source() -> None:
    with pytest.raises(RuntimeError, match="BNDES"):
        validate_candidates_batch([{"fonte": "Grants.gov", "payload_after": {"fonte": "Grants.gov"}}])


def test_merge_extras_preserves_existing() -> None:
    merged = merge_extras_for_apply(
        {"legacy": "keep"},
        {"bndes_deadline_iso": _future()},
    )
    assert merged["legacy"] == "keep"


def test_resolve_prazo_preserves_valid_existing() -> None:
    existing_iso = _future(400)
    new_iso = _future(200)
    existing = {"prazo_envio": existing_iso, "fonte_recurso": "BNDES"}
    mapped = {"prazo_envio": new_iso, "fonte_recurso": "BNDES"}
    assert resolve_prazo_for_apply(existing, mapped, {}) == existing_iso


def test_large_batch_requires_confirmation() -> None:
    cand = build_candidate_entry(
        _bndes_item(descricao=f"Inscrições até {_br(_future())}"),
        action="update",
        meta={},
    )
    big = [cand] * (DEFAULT_MAX_APPLY_BATCH + 1)
    with pytest.raises(RuntimeError, match="confirm-large"):
        validate_candidates_batch(big, confirm_large=False)


def test_dry_run_generates_pdf_candidates_json() -> None:
    item = _bndes_item(
        extras={
            "pdf_url": "https://www.bndes.gov.br/documents/edital.pdf",
            "bndes_detail_links": {"pdf_urls": ["https://www.bndes.gov.br/documents/edital.pdf"]},
        }
    )
    report = run_bndes_deadline_dry_run([item])
    assert report.get("pdf_candidates")


def test_classify_preserve_different_valid_prazo() -> None:
    existing_iso = _future(400)
    new_iso = _future(200)
    item = _bndes_item(descricao=f"Inscrições até {_br(new_iso)}")
    db = {"prazo_envio": existing_iso, "fonte_recurso": "BNDES", "link": item["link"]}
    action, _ = classify_apply_action(item, db_record=db)
    assert action == "preserve"


def test_extract_pdf_respects_size_limit() -> None:
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Length": str(10_000_000)}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        out = extract_bndes_pdf_text("https://www.bndes.gov.br/documents/x.pdf", max_bytes=5_000_000)
    assert out["ok"] is False
    assert out["error"] == "pdf_too_large"


@patch.dict(os.environ, {"EDITALFINDER_ALLOW_CONTROLLED_APPLY": "1", "EDITALFINDER_ENABLE_DEADLINE_BACKFILL": "1"})
def test_apply_bndes_with_mocks(tmp_path: Path) -> None:
    assert controlled_apply_enabled()
    assert deadline_backfill_enabled()

    summary = tmp_path / "outputs" / "bndes_deadline_apply" / "summary.md"
    summary.parent.mkdir(parents=True)
    summary.write_text("# dry-run ok", encoding="utf-8")

    iso = _future()
    item = _bndes_item(descricao=f"Inscrições até {_br(iso)}")
    cand = build_candidate_entry(item, action="update", meta={"deadline_backfill_status": "new_deadline_found"})

    mock_loader = MagicMock()
    mock_loader.fetch_edital_by_link.return_value = {
        "fonte_recurso": "BNDES",
        "prazo_envio": None,
        "extras": {"legacy_key": "preserved"},
    }
    mock_loader.map_to_db_schema.return_value = (
        {"link": item["link"], "prazo_envio": iso, "fonte_recurso": "BNDES"},
        {"bndes_deadline_iso": iso},
    )
    mock_loader._merge_db_row.return_value = {
        "link": item["link"],
        "prazo_envio": iso,
        "fonte_recurso": "BNDES",
        "extras": {"legacy_key": "preserved"},
    }
    mock_loader.inserir_ou_atualizar_edital.return_value = ("ok", 55)

    with patch.dict(sys.modules, {"loader": mock_loader}):
        result = apply_bndes_candidates([cand], root=tmp_path, skip_dry_run_check=False)

    assert result["ok"] == 1


def test_is_bndes_record() -> None:
    assert is_bndes_record({"fonte": "BNDES"})
    assert not is_bndes_record({"fonte": "Grants.gov"})


def test_validate_dry_run_report_missing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="dry-run ausente"):
        validate_dry_run_report_recent(tmp_path)


def test_load_candidates_file(tmp_path: Path) -> None:
    cand = build_candidate_entry(_bndes_item(descricao=f"Inscrições até {_br(_future())}"), action="update", meta={})
    path = tmp_path / "candidates.json"
    path.write_text(json.dumps([cand]), encoding="utf-8")
    assert len(load_candidates_file(path)) == 1


# --- Backend 10.2D-HOTFIX: submission deadline priority ---


@pytest.mark.parametrize(
    ("text", "expected_iso"),
    [
        ("a partir de 09.04.2026 até as 18h do dia 28.05.2026", "2026-05-28"),
        (
            "Como participar. a partir de 29.10.2025 até às 18h do dia 05.12.2025. "
            "prazo para encaminhamento de dúvidas encerra-se em 21.11.2025. "
            "dúvidas serão respondidas até 28.11.2025",
            "2025-12-05",
        ),
        (
            "Prazo para recebimento das propostas: De 01.07.2025 até às 18h de 31.07.2025",
            "2025-07-31",
        ),
    ],
)
def test_bndes_submission_range_patterns(text: str, expected_iso: str) -> None:
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] == expected_iso
    assert result["deadline_kind"] == SUBMISSION_DEADLINE_KIND


@pytest.mark.parametrize(
    "text",
    [
        "prazo para encaminhamento de dúvidas encerra-se em 21.11.2025",
        "dúvidas serão respondidas até 28.11.2025",
        "convocadas em prazo máximo para due diligence até 26 de janeiro de 2027",
        "aprovação da Diretoria até 26 de janeiro de 2028",
        "O Sistema BNDES lançou, em 29.10.2025, Edital de Chamada Pública.",
    ],
)
def test_bndes_administrative_dates_rejected(text: str) -> None:
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] is None
    assert result["deadline_kind"] is None
    assert result["ignored_dates"]


def test_bndes_resultado_final_does_not_use_post_result_date() -> None:
    text = (
        "Como participar. Propostas até 21.10.2025. "
        "Resultado Final divulgado. "
        "convocadas em prazo máximo para due diligence até 26 de janeiro de 2027"
    )
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] == "2025-10-21"
    ignored_isos = {d["iso"] for d in result["ignored_dates"]}
    assert "2027-01-26" in ignored_isos
    assert result["iso"] != "2027-01-26"


def test_bndes_etf_dry_run_prefers_submission_over_duvidas() -> None:
    text = (
        "Como participar. a partir de 29.10.2025 até às 18h do dia 05.12.2025. "
        "prazo para encaminhamento de dúvidas encerra-se em 21.11.2025. "
        "dúvidas serão respondidas até 28.11.2025"
    )
    item = _bndes_item(extras={"bndes_detail_text": text, "pdf_texto_extraido": text})
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] == 1
    cand = report["candidates_to_update"][0]
    assert cand["after"]["prazo_envio"] == "2025-12-05"
    assert cand["after"]["prazo_envio"] != "2025-11-28"
    ignored = cand["meta"].get("bndes_ignored_dates") or cand["payload_after"]["extras"].get("bndes_ignored_dates") or []
    ignored_isos = {d["iso"] for d in ignored}
    assert "2025-11-28" in ignored_isos


def test_bndes_fip_ia_range_becomes_candidate() -> None:
    text = "Como participar. a partir de 09.04.2026 até as 18h do dia 28.05.2026"
    item = _bndes_item(extras={"bndes_detail_text": text})
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] == 1
    assert report["candidates_to_update"][0]["after"]["prazo_envio"] == "2026-05-28"


def test_candidates_to_update_only_submission_deadline() -> None:
    items = [
        _bndes_item(
            titulo="Chamada ETFs",
            extras={
                "bndes_detail_text": (
                    "Como participar. a partir de 29.10.2025 até às 18h do dia 05.12.2025. "
                    "dúvidas serão respondidas até 28.11.2025"
                )
            },
        ),
        _bndes_item(
            titulo="Somente dúvidas",
            extras={"bndes_detail_text": "dúvidas serão respondidas até 28.11.2025"},
        ),
        _bndes_item(
            titulo="Clima pós-resultado",
            extras={
                "bndes_detail_text": (
                    "Como participar. Propostas até 21.10.2025. Resultado Final. "
                    "convocadas até 26 de janeiro de 2027"
                )
            },
        ),
    ]
    report = run_bndes_deadline_dry_run(items)
    assert report["stats"]["candidates_to_update"] == 2
    for cand in report["candidates_to_update"]:
        assert cand["payload_after"]["extras"].get("deadline_kind") == SUBMISSION_DEADLINE_KIND
        assert cand["meta"].get("deadline_kind") == SUBMISSION_DEADLINE_KIND


def test_collect_bndes_ignored_dates_duvidas() -> None:
    ignored = collect_bndes_ignored_dates("dúvidas serão respondidas até 28.11.2025")
    assert any(d["iso"] == "2025-11-28" and d["reason"] == "duvidas_resposta" for d in ignored)


# --- Backend 10.2D-HOTFIX.2: Como participar block recovery ---


def test_extract_bndes_section_como_participar() -> None:
    text = (
        "Resultado Final divulgado. convocadas até 26 de janeiro de 2027. "
        "Como participar. a partir de 01.09.2025 até as 18h do dia 21.10.2025 (prazo prorrogado). "
        "Resultado preliminar em breve."
    )
    block = extract_bndes_section(text, "Como participar")
    assert "a partir de 01.09.2025" in block
    assert "21.10.2025" in block
    assert "26 de janeiro de 2027" not in block


def test_hotfix2_etf_submission_not_rejected() -> None:
    text = (
        "Como participar. a partir de 29.10.2025 até às 18h do dia 05.12.2025. "
        "O prazo para encaminhamento de dúvidas encerra-se em 21.11.2025. "
        "As dúvidas serão respondidas até 28.11.2025"
    )
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] == "2025-12-05"
    assert result["deadline_kind"] == SUBMISSION_DEADLINE_KIND
    assert result["source_block"] == "como_participar"
    ignored_isos = {d["iso"] for d in result["ignored_dates"]}
    assert "2025-11-21" in ignored_isos
    assert "2025-11-28" in ignored_isos

    item = _bndes_item(
        titulo="Chamada ETFs",
        prazo_envio="2025-11-28",
        extras={"bndes_detail_text": text},
    )
    action, meta = classify_apply_action(item)
    assert action == "update"
    assert meta["deadline_kind"] == SUBMISSION_DEADLINE_KIND
    assert meta["after_prazo_envio"] == "2025-12-05"
    assert meta.get("reason") in ("corrected_bndes_submission_deadline", "novo_prazo_bndes")


def test_hotfix2_clima_como_participar_wins_over_diligencia() -> None:
    text = (
        "Resultado final divulgado. "
        "convocadas em prazo máximo para due diligence até 26 de janeiro de 2027. "
        "aprovação da Diretoria até 26 de janeiro de 2028. "
        "Como participar. a partir de 01.09.2025 até as 18h do dia 21.10.2025 (prazo prorrogado)"
    )
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] == "2025-10-21"
    assert result["deadline_kind"] == SUBMISSION_DEADLINE_KIND
    ignored_isos = {d["iso"] for d in result["ignored_dates"]}
    assert "2027-01-26" in ignored_isos
    assert "2028-01-26" in ignored_isos

    item = _bndes_item(
        titulo="Chamada de Clima",
        prazo_envio="2027-01-26",
        extras={"bndes_detail_text": text},
    )
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] == 1
    cand = report["candidates_to_update"][0]
    assert cand["after"]["prazo_envio"] == "2025-10-21"
    assert cand["meta"]["deadline_kind"] == SUBMISSION_DEADLINE_KIND


def test_hotfix2_fip_ia_como_participar() -> None:
    text = "Como participar. a partir de 09.04.2026 até as 18h do dia 28.05.2026"
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] == "2026-05-28"
    assert result["source_block"] == "como_participar"


def test_hotfix2_duvidas_only_no_candidate() -> None:
    text = (
        "prazo para encaminhamento de dúvidas encerra-se em 21.11.2025. "
        "dúvidas serão respondidas até 28.11.2025"
    )
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] is None
    assert result["deadline_kind"] is None
    assert result["ignored_dates"]
    item = _bndes_item(extras={"bndes_detail_text": text})
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] == 0


def test_hotfix2_diligencia_only_no_candidate() -> None:
    text = (
        "poderão ser convocadas até 26 de janeiro de 2027. "
        "aprovação da Diretoria até 26 de janeiro de 2028"
    )
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] is None
    assert result["deadline_kind"] is None
    assert result["ignored_dates"]


def test_hotfix2_correct_invalid_existing_prazo() -> None:
    text = (
        "Como participar. a partir de 01.09.2025 até as 18h do dia 21.10.2025"
    )
    item = {
        "titulo": "Chamada de Clima",
        "fonte": "BNDES",
        "fonte_recurso": "BNDES",
        "link": "https://www.bndes.gov.br/clima",
        "prazo_envio": "2027-01-26",
        "extras": {"bndes_detail_text": text},
    }
    backfill = extract_source_deadline_fields(item)
    assert backfill["deadline_backfill_status"] == "corrected_deadline_found"
    assert backfill["prazo_envio"] == "2025-10-21"
    assert backfill["extras_patch"]["deadline_kind"] == SUBMISSION_DEADLINE_KIND


def test_hotfix2_invalid_existing_without_submission_rejected() -> None:
    item = _bndes_item(
        prazo_envio="2027-01-26",
        extras={"bndes_detail_text": "Resultado final. convocadas até 26 de janeiro de 2027"},
    )
    report = run_bndes_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] == 0
    assert report["stats"]["rejected"] == 1
    assert report["rejected"][0]["meta"].get("reason") in ("prazo_nao_e_submissao", "rejected_deadline")


def test_hotfix2_recebimento_postergado_pattern() -> None:
    text = "prazo para recebimento de propostas foi postergado para até as 18h do dia 21.10.2025"
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] == "2025-10-21"


def test_hotfix2_recebimento_ate_simple() -> None:
    text = "prazo para recebimento das propostas: até 31/07/2026"
    result = extract_bndes_submission_deadline(text)
    assert result["iso"] == "2026-07-31"
