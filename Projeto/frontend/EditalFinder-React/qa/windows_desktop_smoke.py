#!/usr/bin/env python3
"""DESKTOP QA 1.0 — Camada D (fallback Windows).

Smoke test semiautomatizado do EXE Tauri usando UI Automation (pywinauto).

Importante / limitações:
- O EditalFinder roda dentro de um WebView2 (Edge/Chromium embarcado). O conteúdo
  HTML normalmente NÃO é exposto à UI Automation nativa do Windows. Portanto este
  script verifica o que é viável (janela, título, captura de tela) e documenta a
  limitação quando não consegue inspecionar textos internos.
- Não usa coordenadas fixas como mecanismo principal.
- Não usa OCR.
- Não é obrigatório no `npm test`.

Uso:
    python qa/windows_desktop_smoke.py --exe "src-tauri/target/release/editalfinder.exe"

Saídas:
    qa/artifacts/windows/screenshots/*.png
    qa/artifacts/windows/desktop_smoke_report.json
    qa/artifacts/windows/desktop_smoke_report.md
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent / "artifacts" / "windows"
SHOTS = ARTIFACTS / "screenshots"
WINDOW_TITLE_RE = ".*EditalFinder.*"
EXPECTED_TEXTS = ["EditalFinder", "Dashboard", "Reportar problema"]
CLICK_TARGETS = ["Atualizar dados", "Editais", "Reportar problema"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)


def save_screenshot(window, name: str, steps: list) -> None:
    try:
        path = SHOTS / f"{name}.png"
        img = window.capture_as_image()
        img.save(str(path))
        steps.append({"step": f"screenshot:{name}", "ok": True, "path": str(path)})
    except Exception as exc:  # noqa: BLE001
        steps.append({"step": f"screenshot:{name}", "ok": False, "error": str(exc)})


def run(exe_path: str, timeout: float) -> dict:
    result = {
        "exe": exe_path,
        "started_at": now_iso(),
        "steps": [],
        "expected_texts": {t: None for t in EXPECTED_TEXTS},
        "clicks": {t: None for t in CLICK_TARGETS},
        "limitations": [],
        "ok": False,
    }
    steps = result["steps"]

    try:
        from pywinauto.application import Application  # type: ignore
    except Exception as exc:  # noqa: BLE001
        result["limitations"].append(
            "pywinauto não disponível — rode: pip install -r qa/requirements.txt"
        )
        steps.append({"step": "import_pywinauto", "ok": False, "error": str(exc)})
        return result

    exe = Path(exe_path)
    if not exe.exists():
        steps.append({"step": "exe_exists", "ok": False, "error": f"não encontrado: {exe}"})
        result["limitations"].append("Compile o EXE antes: npm run desktop:build")
        return result
    steps.append({"step": "exe_exists", "ok": True})

    app = None
    window = None
    try:
        app = Application(backend="uia").start(str(exe))
        steps.append({"step": "start_app", "ok": True})
    except Exception as exc:  # noqa: BLE001
        steps.append({"step": "start_app", "ok": False, "error": str(exc)})
        return result

    # Aguarda janela do EditalFinder.
    deadline = time.time() + timeout
    while time.time() < deadline and window is None:
        try:
            window = app.window(title_re=WINDOW_TITLE_RE)
            window.wait("exists ready", timeout=3)
        except Exception:  # noqa: BLE001
            window = None
            time.sleep(1)

    if window is None:
        steps.append({"step": "wait_window", "ok": False, "error": "janela EditalFinder não encontrada"})
        _safe_kill(app)
        return result
    steps.append({"step": "wait_window", "ok": True})
    time.sleep(2)
    save_screenshot(window, "01_window_ready", steps)

    # Coleta de textos via UIA (provável vazio em WebView2 → limitação).
    found_texts = _collect_texts(window)
    for t in EXPECTED_TEXTS:
        present = any(t.lower() in ft.lower() for ft in found_texts)
        result["expected_texts"][t] = present
    if not any(result["expected_texts"].values()):
        result["limitations"].append(
            "UI Automation não expôs textos do WebView2 (esperado). "
            "Verificação textual inconclusiva no desktop — use os logs dev e o Playwright web."
        )

    # Tentativa de cliques por nome de controle (best-effort, sem coordenadas).
    for target in CLICK_TARGETS:
        ok = _try_click(window, target)
        result["clicks"][target] = ok
        time.sleep(0.8)
        save_screenshot(window, f"click_{_slug(target)}", steps)

    save_screenshot(window, "99_final", steps)
    _safe_close(window, app, steps)

    result["ok"] = True
    result["finished_at"] = now_iso()
    return result


def _collect_texts(window) -> list[str]:
    texts: list[str] = []
    try:
        for ctrl in window.descendants():
            try:
                txt = ctrl.window_text()
                if txt:
                    texts.append(txt)
            except Exception:  # noqa: BLE001
                continue
    except Exception:  # noqa: BLE001
        pass
    return texts


def _try_click(window, name: str) -> bool:
    try:
        ctrl = window.child_window(title=name, control_type="Button")
        ctrl.wait("exists ready", timeout=3)
        ctrl.click_input()
        return True
    except Exception:  # noqa: BLE001
        return False


def _safe_close(window, app, steps) -> None:
    try:
        window.close()
        steps.append({"step": "close_window", "ok": True})
    except Exception:  # noqa: BLE001
        _safe_kill(app)
        steps.append({"step": "close_window", "ok": False})


def _safe_kill(app) -> None:
    try:
        app.kill()
    except Exception:  # noqa: BLE001
        pass


def _slug(s: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in s.lower())


def write_reports(result: dict) -> None:
    ensure_dirs()
    (ARTIFACTS / "desktop_smoke_report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Desktop Smoke Report (DESKTOP QA 1.0 — Windows fallback)",
        "",
        f"- EXE: `{result.get('exe')}`",
        f"- Início: {result.get('started_at')}",
        f"- Fim: {result.get('finished_at', '—')}",
        f"- Status geral: {'OK' if result.get('ok') else 'FALHOU/INCONCLUSIVO'}",
        "",
        "## Textos esperados (UIA)",
    ]
    for t, v in result.get("expected_texts", {}).items():
        mark = "✅" if v else ("❓" if v is None else "❌")
        lines.append(f"- {mark} {t}")
    lines += ["", "## Cliques tentados"]
    for t, v in result.get("clicks", {}).items():
        mark = "✅" if v else "❌"
        lines.append(f"- {mark} {t}")
    lines += ["", "## Passos"]
    for s in result.get("steps", []):
        mark = "✅" if s.get("ok") else "❌"
        extra = s.get("error") or s.get("path") or ""
        lines.append(f"- {mark} {s.get('step')} {extra}".rstrip())
    if result.get("limitations"):
        lines += ["", "## Limitações"]
        lines += [f"- {l}" for l in result["limitations"]]

    (ARTIFACTS / "desktop_smoke_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="EditalFinder desktop smoke test (Windows).")
    parser.add_argument("--exe", required=True, help="Caminho do EXE Tauri.")
    parser.add_argument("--timeout", type=float, default=40.0, help="Timeout para abrir a janela (s).")
    args = parser.parse_args()

    result = run(args.exe, args.timeout)
    write_reports(result)

    print(f"Relatório: {ARTIFACTS / 'desktop_smoke_report.md'}")
    # Não falha o pipeline por limitação do WebView2; falha só se nem abriu a janela.
    started = any(s["step"] == "wait_window" and s["ok"] for s in result["steps"])
    return 0 if started else 1


if __name__ == "__main__":
    sys.exit(main())
