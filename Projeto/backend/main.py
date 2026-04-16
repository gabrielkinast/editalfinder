import subprocess
import os
from pathlib import Path
import sys

# Configuração de diretórios
BASE_DIR = Path(__file__).parent
CORE_DIR = BASE_DIR / "CORE"

# Lista de scrapers para rodar (diretório, script)
SCRAPERS = [
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
]

def run_script(script_path, cwd):
    """Executa um script python usando subprocess."""
    print(f"\n" + "="*50)
    print(f"EXECUTANDO: {script_path} em {cwd}")
    print("="*50)
    
    try:
        # Usamos sys.executable para garantir que use o mesmo interpretador python
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=cwd,
            capture_output=False, # Mostra o output no terminal em tempo real
            text=True
        )
        if result.returncode == 0:
            print(f"\n[SUCESSO] {script_path} finalizado com êxito.")
        else:
            print(f"\n[ERRO] {script_path} falhou com código {result.returncode}.")
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha ao executar {script_path}: {e}")

def main():
    print("INICIANDO PIPELINE DE EXTRAÇÃO E CARREGAMENTO DE EDITAIS\n")

    # 1. Rodar todos os scrapers
    print("--- PASSO 1: RODANDO SCRAPERS ---")
    for folder, script in SCRAPERS:
        folder_path = BASE_DIR / folder
        script_path = folder_path / script
        if script_path.exists():
            run_script(script, folder_path)
        else:
            print(f"\n[AVISO] Script não encontrado: {script_path}")

    # 2. Rodar o transformer
    print("\n--- PASSO 2: PADRONIZANDO JSONS (TRANSFORMER) ---")
    transformer_path = CORE_DIR / "transformer.py"
    if transformer_path.exists():
        run_script("transformer.py", CORE_DIR)
    else:
        print(f"\n[ERRO] Transformer não encontrado em: {transformer_path}")

    # 3. Rodar o loader
    print("\n--- PASSO 3: CARREGANDO NO BANCO DE DADOS (LOADER) ---")
    loader_path = CORE_DIR / "loader.py"
    if loader_path.exists():
        run_script("loader.py", CORE_DIR)
    else:
        print(f"\n[ERRO] Loader não encontrado em: {loader_path}")

    print("\n" + "="*50)
    print("PIPELINE FINALIZADO!")
    print("="*50)

if __name__ == "__main__":
    main()
