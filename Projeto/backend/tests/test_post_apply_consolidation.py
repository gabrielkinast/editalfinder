"""Testes consolidação pós-apply (Backend 10.3)."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from post_apply_consolidation import (  # noqa: E402
    analyze_source_records,
    build_next_actions,
    read_apply_log,
    run_post_apply_consolidation,
    supabase_configured,
)


def _grants_record(**kwargs: object) -> dict:
    base = {
        "titulo": "NSF Research Grant Opportunity",
        "descricao": "Full proposal deadline listed in closeDate.",
        "fonte_recurso": "Grants.gov",
        "link": "https://grants.gov/opportunity/1",
        "prazo_envio": (date.today() + timedelta(days=45)).isoformat(),
        "extras": {"closeDate": (date.today() + timedelta(days=45)).isoformat()},
    }
    base.update(kwargs)
    return base


def _bndes_sem_prazo(**kwargs: object) -> dict:
    base = {
        "titulo": "Chamada BNDES sem prazo no loader",
        "descricao": "Chamada pública para seleção.",
        "fonte_recurso": "BNDES",
        "link": "https://www.bndes.gov.br/chamada-x",
    }
    base.update(kwargs)
    return base


def _bndes_resultado_final(**kwargs: object) -> dict:
    base = {
        "titulo": "Chamada BNDES — Resultado Final",
        "descricao": "Resultado Final divulgado. Convocação pós-seleção.",
        "fonte_recurso": "BNDES",
        "link": "https://www.bndes.gov.br/chamada-resultado",
        "prazo_envio": (date.today() + timedelta(days=10)).isoformat(),
    }
    base.update(kwargs)
    return base


def _doe_record(**kwargs: object) -> dict:
    base = {
        "titulo": "DOE ARPA-E FOA",
        "descricao": "Notice Of Funding Opportunity",
        "fonte_recurso": "DOE ARPA-E",
        "link": "https://arpa-e-foa.energy.gov/test",
        "extras": {"sem_prazo_kind": "deadline_in_pdf_or_detail", "pdf_url": "https://example.com/x.pdf"},
    }
    base.update(kwargs)
    return base


def test_consolidates_multiple_source_metrics() -> None:
    grants = analyze_source_records([_grants_record()], source_key="grants_gov", with_backfill=False)
    doe = analyze_source_records([_doe_record()], source_key="doe_arpae", with_backfill=False)
    assert grants["total"] == 1
    assert doe["total"] == 1
    assert grants["source_key"] == "grants_gov"
    assert doe["source_key"] == "doe_arpae"


def test_reads_apply_log_when_present(tmp_path: Path) -> None:
    log_dir = tmp_path / "outputs" / "grants_deadline_apply"
    log_dir.mkdir(parents=True)
    log_path = log_dir / "apply_log.json"
    log_path.write_text(
        json.dumps({"ok": 151, "errors": 0, "total_candidates": 151, "applied_at": "2026-06-05T00:00:00+00:00"}),
        encoding="utf-8",
    )
    result = read_apply_log(tmp_path, "grants_gov")
    assert result["ok"] == 151
    assert result["errors"] == 0
    assert result["status"] == "ok"


def test_missing_apply_log_does_not_fail(tmp_path: Path) -> None:
    result = read_apply_log(tmp_path, "grants_gov")
    assert result["status"] == "unknown"
    assert result["ok"] is None


def test_sem_prazo_separate_from_noise() -> None:
    metrics = analyze_source_records(
        [_bndes_sem_prazo()],
        source_key="bndes",
        with_backfill=True,
    )
    assert metrics["sem_prazo"] >= 0
    assert metrics["sem_prazo"] != metrics["noise_probable"] or metrics["noise_probable"] == 0


def test_encerrado_separate_from_noise() -> None:
    past = (date.today() - timedelta(days=30)).isoformat()
    metrics = analyze_source_records(
        [_grants_record(prazo_envio=past, extras={"closeDate": past})],
        source_key="grants_gov",
        with_backfill=False,
    )
    assert metrics["encerrado"] >= 1
    assert metrics["encerrado"] != metrics["noise_probable"]


def test_bndes_resultado_final_needs_source_semantics() -> None:
    metrics = analyze_source_records(
        [_bndes_resultado_final()],
        source_key="bndes",
        with_backfill=False,
    )
    md = build_next_actions([metrics], [{"label": "BNDES", "status": "ok", "ok": 1, "errors": 0, "path": "x"}])
    assert "NEEDS_SOURCE_SEMANTICS" in md
    assert len(metrics.get("bndes_resultado_final_detected") or []) >= 1


def test_deadline_in_pdf_generates_needs_detail_fetch() -> None:
    metrics = analyze_source_records([_doe_record()], source_key="doe_arpae", with_backfill=False)
    md = build_next_actions([metrics], [])
    assert "NEEDS_DETAIL_FETCH" in md
    assert len(metrics["reviews"]["pdf_detail_candidates"]) >= 1


def test_run_generates_all_outputs(tmp_path: Path) -> None:
    recrawl = tmp_path / "outputs" / "recrawl" / "grants_gov"
    recrawl.mkdir(parents=True)
    (recrawl / "grants_gov_recrawl.json").write_text(json.dumps([_grants_record()]), encoding="utf-8")

    apply_dir = tmp_path / "outputs" / "grants_deadline_apply"
    apply_dir.mkdir(parents=True)
    (apply_dir / "apply_log.json").write_text(
        json.dumps({"ok": 2, "errors": 0, "total_candidates": 2}),
        encoding="utf-8",
    )

    out = tmp_path / "outputs" / "post_apply_consolidation"
    with patch("post_apply_consolidation.supabase_configured", return_value=False):
        run_post_apply_consolidation(
            tmp_path,
            sources=["grants_gov"],
            from_db=False,
            with_backfill=False,
            limit=100,
            output_dir=out,
        )

    for name in (
        "summary.md",
        "consolidated_metrics.json",
        "source_breakdown.json",
        "deadline_status_by_source.json",
        "actionability_by_source.json",
        "no_deadline_review.json",
        "rejected_or_blocked_review.json",
        "pdf_detail_candidates_review.json",
        "applied_updates_summary.json",
        "next_actions.md",
    ):
        assert (out / name).exists(), f"missing {name}"


def test_no_database_writes(tmp_path: Path) -> None:
    recrawl = tmp_path / "outputs" / "recrawl" / "bndes"
    recrawl.mkdir(parents=True)
    (recrawl / "bndes_recrawl.json").write_text(json.dumps([_bndes_sem_prazo()]), encoding="utf-8")
    with patch("post_apply_consolidation.supabase_configured", return_value=False):
        result = run_post_apply_consolidation(tmp_path, sources=["bndes"], from_db=False, output_dir=tmp_path / "out")
    assert result["consolidated"]["totals"]["records"] >= 0


def test_sources_filtered_by_cli(tmp_path: Path) -> None:
    for sk, fname in (
        ("grants_gov", "grants_gov_recrawl.json"),
        ("bndes", "bndes_recrawl.json"),
    ):
        d = tmp_path / "outputs" / "recrawl" / sk.split("_")[0] if sk == "bndes" else tmp_path / "outputs" / "recrawl" / "grants_gov"
        if sk == "bndes":
            d = tmp_path / "outputs" / "recrawl" / "bndes"
        else:
            d = tmp_path / "outputs" / "recrawl" / "grants_gov"
        d.mkdir(parents=True, exist_ok=True)
        rec = _grants_record() if sk == "grants_gov" else _bndes_sem_prazo()
        (d / fname).write_text(json.dumps([rec]), encoding="utf-8")

    with patch("post_apply_consolidation.supabase_configured", return_value=False):
        result = run_post_apply_consolidation(
            tmp_path,
            sources=["grants_gov"],
            from_db=False,
            output_dir=tmp_path / "out2",
        )
    assert result["consolidated"]["sources_analyzed"] == ["grants_gov"]
    assert "grants_gov" in result["consolidated"]["data_origins"]


def test_summary_md_contains_semantic_notes(tmp_path: Path) -> None:
    recrawl = tmp_path / "outputs" / "recrawl" / "grants_gov"
    recrawl.mkdir(parents=True)
    (recrawl / "grants_gov_recrawl.json").write_text(json.dumps([_grants_record()]), encoding="utf-8")
    out = tmp_path / "out3"
    with patch("post_apply_consolidation.supabase_configured", return_value=False):
        run_post_apply_consolidation(tmp_path, sources=["grants_gov"], from_db=False, output_dir=out)
    text = (out / "summary.md").read_text(encoding="utf-8")
    assert "sem_prazo" in text
    assert "encerrado" in text
    assert "Aplicações executadas" in text
