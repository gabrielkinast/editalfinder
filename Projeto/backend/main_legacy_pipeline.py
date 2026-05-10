"""
LEGADO — Orquestrador monolítico: crawlers -> CORE/transformer -> CORE/loader.
Para o pipeline diário com readiness / news / validações, use `main.py` na raiz.

Exemplos:
  python main.py
  python main.py --sources cnpq,finep,pncp_defesa
  python main.py --sources finep,cnpq --scraper-workers 4 --transform-workers 8 --transform-item-workers 8 --loader-workers 2
  python main.py --from-step 2              # só transformer + loader (JSONs já existentes)
  python main.py --to-step 2                # crawlers + transformer, sem carregar no Supabase
  python main.py --from-step 2 --to-step 2  # só transformer
  python main.py --fail-fast --sources finep,cnpq

Variáveis de ambiente (opcional):
  EDITALFINDER_SOURCES=cnpq,finep       # filtro de crawlers (se não passar --sources)
  EDITALFINDER_SCRAPER_WORKERS=4       # paralelismo no passo 1 (default 2)
  EDITALFINDER_TRANSFORM_WORKERS=8    # ficheiros JSON em paralelo no transformer
  EDITALFINDER_TRANSFORM_ITEM_WORKERS=6 # itens/PDFs em paralelo dentro de cada ficheiro
  EDITALFINDER_LOADER_WORKERS=2        # ficheiros JSON em paralelo no loader (default 1)

VPN / proxy só para crawlers China e Japão (bloco no fim do passo 1):
  O Python não liga uma VPN por si: chame o CLI do teu fornecedor (WireGuard,
  rasdial no Windows, script OpenVPN, etc.) via hooks opcionais — comandos
  arbitrários na shell do sistema (confia apenas em variáveis de ambiente
  controladas por ti).

  EDITALFINDER_ASIA_VPN_HOOK_BEFORE="rasdial \"Minha VPN\""   # antes do bloco asia
  EDITALFINDER_ASIA_VPN_HOOK_AFTER="rasdial \"Minha VPN\" /disconnect"
  EDITALFINDER_ASIA_VPN_WAIT_SEC=5      # pausa após o hook BEFORE (VPN estabilizar)
  EDITALFINDER_ASIA_VPN_HOOK_STRICT=1   # código != 0 no hook aborta o passo 1
  EDITALFINDER_ASIA_SEQUENTIAL=1        # força sequencial no bloco asia (sem hooks)

  Alternativa sem “VPN de sistema”: HTTP_PROXY/HTTPS_PROXY (requests já usa;
  ver também asia_source_common e CORE/http_fetch).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# Evita UnicodeEncodeError no `python main.py --help` em consolas cp1252 (Windows).
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configuração de diretórios
BASE_DIR = Path(__file__).resolve().parent
CORE_DIR = BASE_DIR / "CORE"

# Lista de scrapers (diretório, script)
SCRAPERS: List[Tuple[str, str]] = [
    ("cnpq", "main-cnpq.py"),
    ("finep", "main.py"),
    ("fapergs", "main-fapergs.py"),
    ("embrapii", "main_embrapii.py"),
    ("bndes", "main_bndes.py"),
    ("abdi", "main_abdi.py"),
    ("mcti", "main_mcti.py"),
    ("saude", "main_saude.py"),
    ("mapa", "main_mapa.py"),
    ("defesa", "main_defesa.py"),
    ("mma", "main_mma.py"),
    ("softex", "main_softex.py"),
    ("apex", "main_apex.py"),
    ("anp", "main_anp.py"),
    ("petrobras", "main_petrobras.py"),
    ("ambev", "main_ambev.py"),
    ("fapesc", "main_fapesc.py"),
    ("fappr", "main_fappr.py"),
    ("aneel", "main_aneel.py"),
    ("capes", "main_capes.py"),
    ("fapesp", "main_fapesp.py"),
    ("faperg", "main_faperg.py"),
    ("senai", "main_senai.py"),
    ("horizon_europe", "main_horizon_europe.py"),
    ("nsf", "main_nsf.py"),
    ("doe_arpae", "main_doe_arpae.py"),
    ("erc", "main_erc.py"),
    ("wellcome", "main_wellcome.py"),
    ("cnen", "main_cnen.py"),
    ("ipen", "main_ipen.py"),
    ("eletronuclear", "main_eletronuclear.py"),
    ("impa", "main_impa.py"),
    ("cbpf", "main_cbpf.py"),
    ("science_scraper", "main_science.py"),
    ("fnde", "main_fnde.py"),
    ("caixa", "main_caixa.py"),
    ("badesul", "main_badesul.py"),
    ("brde", "main_brde.py"),
    ("plataforma_industria", "main_plataforma.py"),
    ("confap", "main_confap.py"),
    ("pncp", "main_pncp.py"),
    ("marinha", "main_marinha.py"),
    ("dcta_ita_iae", "main_dcta_ita_iae.py"),
    ("inb", "main_inb.py"),
    ("nuclep", "main_nuclep.py"),
    ("amazul", "main_amazul.py"),
    ("fapemig", "main_fapemig.py"),
    ("sam_gov", "main_sam_gov.py"),
    ("dod_sbir_sttr", "main_dod_sbir_sttr.py"),
    ("grants_gov", "main_grants_gov.py"),
    ("darpa_opportunities", "main_darpa_opportunities.py"),
    ("european_defence_fund", "main_european_defence_fund.py"),
    ("nato_diana", "main_nato_diana.py"),
    ("diu", "main_diu.py"),
    ("afwerx", "main_afwerx.py"),
    ("iarpa", "main_iarpa.py"),
    ("pncp_defesa", "main_pncp_defesa.py"),
    ("compras_defesa", "main_compras_defesa.py"),
    ("lockheed_martin_suppliers", "main_lockheed_martin_suppliers.py"),
    ("bae_systems_suppliers", "main_bae_systems_suppliers.py"),
    ("general_dynamics_suppliers", "main_general_dynamics_suppliers.py"),
    ("rheinmetall_suppliers", "main_rheinmetall_suppliers.py"),
    ("thales_suppliers", "main_thales_suppliers.py"),
    ("japan_jst", "main_japan_jst.py"),
    ("japan_jsps", "main_japan_jsps.py"),
    ("japan_kakenhi", "main_japan_kakenhi.py"),
    ("japan_e_rad", "main_japan_e_rad.py"),
    ("japan_mext", "main_japan_mext.py"),
    ("japan_qst", "main_japan_qst.py"),
    ("japan_jaea", "main_japan_jaea.py"),
    ("japan_nims", "main_japan_nims.py"),
    ("japan_riken", "main_japan_riken.py"),
    ("japan_kek", "main_japan_kek.py"),
    ("japan_jetro_procurement", "main_japan_jetro_procurement.py"),
    ("japan_atla", "main_japan_atla.py"),
    ("japan_mod", "main_japan_mod.py"),
    ("japan_jaxa", "main_japan_jaxa.py"),
    ("japan_nedo", "main_japan_nedo.py"),
    ("japan_aist", "main_japan_aist.py"),
    ("china_nsfc", "main_china_nsfc.py"),
    ("china_most", "main_china_most.py"),
    ("china_cas", "main_china_cas.py"),
    ("china_caea", "main_china_caea.py"),
    ("china_cnnc", "main_china_cnnc.py"),
    ("china_cgn", "main_china_cgn.py"),
    ("china_mofcom_tendering", "main_china_mofcom_tendering.py"),
    ("china_tendering_bidding", "main_china_tendering_bidding.py"),
    ("china_university_procurement", "main_china_university_procurement.py"),
    ("china_mod_public", "main_china_mod_public.py"),
    ("japan_mitsubishi_heavy", "main_japan_mitsubishi_heavy.py"),
    ("japan_kawasaki_heavy", "main_japan_kawasaki_heavy.py"),
    ("japan_ihi", "main_japan_ihi.py"),
    ("china_norinco", "main_china_norinco.py"),
    ("china_avic", "main_china_avic.py"),
]


def _parse_sources_arg(raw: Optional[str]) -> Optional[set[str]]:
    if not raw or not str(raw).strip():
        return None
    parts = {p.strip().lower() for p in str(raw).split(",") if p.strip()}
    return parts or None


def _filter_scrapers(
    scrapers: Sequence[Tuple[str, str]], allowed: Optional[set[str]]
) -> List[Tuple[str, str]]:
    if not allowed:
        return list(scrapers)
    known = {folder for folder, _ in scrapers}
    unknown = allowed - known
    if unknown:
        print(
            "[AVISO] Pastas em --sources/EDITALFINDER_SOURCES sem entrada em SCRAPERS:",
            ", ".join(sorted(unknown)),
        )
    return [(f, s) for f, s in scrapers if f.lower() in allowed]


def _is_asia_scraper_folder(folder: str) -> bool:
    fl = folder.lower()
    return fl.startswith("japan_") or fl.startswith("china_")


def _run_optional_vpn_hook(env_name: str) -> int:
    cmd = os.getenv(env_name, "").strip()
    if not cmd:
        return 0
    preview = cmd if len(cmd) <= 140 else cmd[:137] + "..."
    print(f"\n[main] Executando hook ({env_name}):\n  {preview}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(BASE_DIR),
            env=os.environ.copy(),
        )
        return int(result.returncode)
    except Exception as exc:
        print(f"[main] Exceção ao executar {env_name}: {exc}")
        return 1


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def _asia_vpn_wait_after_connect() -> float:
    try:
        return float(os.getenv("EDITALFINDER_ASIA_VPN_WAIT_SEC", "4") or "4")
    except ValueError:
        return 4.0


def _run_scraper_tasks(
    tasks: List[Tuple[str, str, Path]],
    *,
    fail_fast: bool,
    parallel_workers: int,
) -> tuple[int, int]:
    """Executa (folder, script, path). Devolve (falhas, sucessos)."""
    if not tasks:
        return 0, 0
    pw = max(1, min(int(parallel_workers or 1), 16))
    if fail_fast and pw > 1:
        print("[AVISO] --fail-fast: usando 1 worker (execucao sequencial).")
        pw = 1
    if pw <= 1 or len(tasks) <= 1:
        failures = 0
        ok = 0
        for folder, script, folder_path in tasks:
            code = run_script(script, folder_path)
            if code != 0:
                failures += 1
                if fail_fast:
                    print("[FAIL-FAST] Interrompendo bloco de crawlers após falha.")
                    break
            else:
                ok += 1
        return failures, ok

    print(f"[main] Crawlers em paralelo: {pw} workers, {len(tasks)} scripts (bloco atual).")
    failures = 0
    ok = 0
    with ThreadPoolExecutor(max_workers=min(pw, len(tasks))) as ex:
        futures = {
            ex.submit(run_script, script, folder_path): (folder, script)
            for folder, script, folder_path in tasks
        }
        for fut in as_completed(futures):
            folder, script = futures[fut]
            try:
                code = int(fut.result())
            except Exception as exc:
                print(f"\n[ERRO CRÍTICO] {folder}/{script}: {exc}")
                code = 1
            if code != 0:
                failures += 1
            else:
                ok += 1
    return failures, ok


def run_script(
    script_name: str,
    cwd: Path,
    *,
    env_extra: Optional[Dict[str, str]] = None,
) -> int:
    """Executa `python script_name` em cwd. Devolve código de saída (1 se exceção)."""
    print("\n" + "=" * 50)
    print(f"EXECUTANDO: {script_name}  (cwd={cwd})")
    print("=" * 50)
    try:
        env = os.environ.copy()
        if env_extra:
            env.update(env_extra)
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=str(cwd),
            capture_output=False,
            text=True,
            env=env,
        )
        code = int(result.returncode)
        if code == 0:
            print(f"\n[SUCESSO] {script_name} finalizado com êxito.")
        else:
            print(f"\n[ERRO] {script_name} falhou com código {code}.")
        return code
    except Exception as exc:
        print(f"\n[ERRO CRÍTICO] Falha ao executar {script_name}: {exc}")
        return 1


def _run_scrapers(
    scrapers: Iterable[Tuple[str, str]],
    *,
    fail_fast: bool,
    parallel_workers: int,
) -> tuple[int, int, int]:
    """Devolve (falhas, avisos_script_ausente, executados_ok)."""
    scraper_list = list(scrapers)
    tasks: List[Tuple[str, str, Path]] = []
    missing = 0
    for folder, script in scraper_list:
        folder_path = BASE_DIR / folder
        script_path = folder_path / script
        if not script_path.exists():
            print(f"\n[AVISO] Script não encontrado: {script_path}")
            missing += 1
            continue
        tasks.append((folder, script, folder_path))

    hook_before = os.getenv("EDITALFINDER_ASIA_VPN_HOOK_BEFORE", "").strip()
    hook_after = os.getenv("EDITALFINDER_ASIA_VPN_HOOK_AFTER", "").strip()
    force_asia_seq = bool(hook_before or hook_after) or _env_truthy("EDITALFINDER_ASIA_SEQUENTIAL")

    other_tasks: List[Tuple[str, str, Path]] = []
    asia_tasks: List[Tuple[str, str, Path]] = []
    for t in tasks:
        if _is_asia_scraper_folder(t[0]):
            asia_tasks.append(t)
        else:
            other_tasks.append(t)

    if other_tasks and asia_tasks:
        print(
            "\n[main] Crawlers China/Japão executados em bloco no fim do passo 1 "
            "(depois dos demais da lista SCRAPERS)."
        )

    failures, ok = _run_scraper_tasks(
        other_tasks,
        fail_fast=fail_fast,
        parallel_workers=parallel_workers,
    )
    if fail_fast and failures > 0:
        return failures, missing, ok

    if not asia_tasks:
        return failures, missing, ok

    if hook_before:
        rc = _run_optional_vpn_hook("EDITALFINDER_ASIA_VPN_HOOK_BEFORE")
        if rc != 0:
            msg = (
                f"[main] EDITALFINDER_ASIA_VPN_HOOK_BEFORE terminou com código {rc}."
            )
            if _env_truthy("EDITALFINDER_ASIA_VPN_HOOK_STRICT"):
                print(msg + " Abortando passo 1 (Asia não executado).")
                return failures + 1, missing, ok
            print(msg + " Continuando crawlers Asia (defina EDITALFINDER_ASIA_VPN_HOOK_STRICT=1 para abortar).")
        else:
            wait = max(0.0, min(_asia_vpn_wait_after_connect(), 120.0))
            if wait > 0:
                print(
                    f"[main] Pausa de {wait:g}s após VPN (EDITALFINDER_ASIA_VPN_WAIT_SEC)..."
                )
                time.sleep(wait)

    pw_asia = 1 if force_asia_seq else parallel_workers
    if force_asia_seq and len(asia_tasks) > 1 and parallel_workers > 1:
        print(
            "[main] Bloco Asia em modo sequencial (hooks VPN ou EDITALFINDER_ASIA_SEQUENTIAL=1)."
        )

    f_asia, ok_asia = _run_scraper_tasks(
        asia_tasks,
        fail_fast=fail_fast,
        parallel_workers=pw_asia,
    )
    failures += f_asia
    ok += ok_asia

    if hook_after:
        rc = _run_optional_vpn_hook("EDITALFINDER_ASIA_VPN_HOOK_AFTER")
        if rc != 0 and _env_truthy("EDITALFINDER_ASIA_VPN_HOOK_STRICT"):
            print(
                "[main] EDITALFINDER_ASIA_VPN_HOOK_AFTER falhou com STRICT=1; "
                "marcando falha no passo 1."
            )
            failures += 1

    return failures, missing, ok


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pipeline EditalFinder: crawlers -> transformer -> loader.")
    p.add_argument(
        "--from-step",
        type=int,
        choices=(1, 2, 3),
        default=1,
        help="1=crawlers, 2=transformer, 3=loader. Início da cadeia (default: 1).",
    )
    p.add_argument(
        "--to-step",
        type=int,
        choices=(1, 2, 3),
        default=3,
        help="Último passo a executar inclusive (default: 3 = até loader).",
    )
    p.add_argument(
        "--sources",
        type=str,
        default="",
        help="Lista separada por vírgulas de pastas de crawler (ex.: cnpq,finep).",
    )
    p.add_argument(
        "--fail-fast",
        action="store_true",
        help="No passo 1, parar no primeiro crawler com codigo de saida != 0.",
    )
    p.add_argument(
        "--scraper-workers",
        type=int,
        default=int(os.getenv("EDITALFINDER_SCRAPER_WORKERS", "2") or "2"),
        help="Threads para crawlers em paralelo (default: 2). Ex.: 6-8 acelera o passo 1; cuidado com rate limits.",
    )
    p.add_argument(
        "--transform-workers",
        type=int,
        default=int(os.getenv("EDITALFINDER_TRANSFORM_WORKERS", "8") or "8"),
        help="Repasse ao transformer: fontes JSON em paralelo (--workers). Default 8 (max 20 no executor).",
    )
    p.add_argument(
        "--transform-item-workers",
        type=int,
        default=int(os.getenv("EDITALFINDER_TRANSFORM_ITEM_WORKERS", "6") or "6"),
        help="Repasse ao transformer: itens por ficheiro em paralelo (PDF/rede). Default 6.",
    )
    p.add_argument(
        "--loader-workers",
        type=int,
        default=int(os.getenv("EDITALFINDER_LOADER_WORKERS", "1") or "1"),
        help="Repasse ao loader (--workers). Default 1 (evita rate limit Supabase).",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    if args.from_step > args.to_step:
        print("Erro: --from-step não pode ser maior que --to-step.", file=sys.stderr)
        return 2

    allowed = _parse_sources_arg(args.sources) or _parse_sources_arg(os.getenv("EDITALFINDER_SOURCES"))
    scraper_list = _filter_scrapers(SCRAPERS, allowed)

    print("INICIANDO PIPELINE DE EXTRAÇÃO E CARREGAMENTO DE EDITAIS")
    print(f"Passos: {args.from_step} .. {args.to_step}")
    if allowed:
        print(f"Filtro de fontes: {', '.join(sorted(allowed))} ({len(scraper_list)} crawlers)")
    print()

    pipeline_failures = 0

    # Passo 1
    if args.from_step <= 1 <= args.to_step:
        print("--- PASSO 1: RODANDO SCRAPERS ---")
        f, m, ok = _run_scrapers(
            scraper_list,
            fail_fast=args.fail_fast,
            parallel_workers=args.scraper_workers,
        )
        pipeline_failures += f
        if f:
            print(f"\n[RESUMO passo 1] falhas={f}, scripts ausentes={m}, sucessos={ok}")
        elif m:
            print(f"\n[RESUMO passo 1] scripts ausentes={m}, sucessos={ok}")

    # Passo 2
    if args.from_step <= 2 <= args.to_step:
        print("\n--- PASSO 2: PADRONIZANDO JSONS (TRANSFORMER) ---")
        transformer_path = CORE_DIR / "transformer.py"
        if transformer_path.exists():
            tx_env: Dict[str, str] = {
                "EDITALFINDER_TRANSFORM_WORKERS": str(
                    max(1, min(int(args.transform_workers or 1), 32))
                ),
                "EDITALFINDER_TRANSFORM_ITEM_WORKERS": str(
                    max(1, min(int(args.transform_item_workers or 1), 16))
                ),
            }
            if allowed:
                tx_env["EDITALFINDER_TRANSFORM_SOURCES"] = ",".join(sorted(allowed))
            pipeline_failures += (
                1
                if run_script("transformer.py", CORE_DIR, env_extra=tx_env) != 0
                else 0
            )
        else:
            print(f"\n[ERRO] Transformer não encontrado em: {transformer_path}")
            pipeline_failures += 1

    # Passo 3
    if args.from_step <= 3 <= args.to_step:
        print("\n--- PASSO 3: CARREGANDO NO BANCO DE DADOS (LOADER) ---")
        loader_path = CORE_DIR / "loader.py"
        if loader_path.exists():
            ld_env = {
                "EDITALFINDER_LOADER_WORKERS": str(
                    max(1, min(int(args.loader_workers or 1), 12))
                )
            }
            pipeline_failures += (
                1 if run_script("loader.py", CORE_DIR, env_extra=ld_env) != 0 else 0
            )
        else:
            print(f"\n[ERRO] Loader não encontrado em: {loader_path}")
            pipeline_failures += 1

    print("\n" + "=" * 50)
    if pipeline_failures == 0:
        print("PIPELINE FINALIZADO (sem erros reportados nos passos executados).")
    else:
        print(f"PIPELINE FINALIZADO COM {pipeline_failures} ERRO(S) NOS PASSOS EXECUTADOS.")
    print("=" * 50)

    return 1 if pipeline_failures else 0


if __name__ == "__main__":
    sys.exit(main())
