import os
import sys
import subprocess
from pathlib import Path

def setup_windows_task():
    """Configura o Task Scheduler do Windows para rodar o main.py todo dia às 12:00."""
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
    python_path = sys.executable
    task_name = "EditalCrawler_Daily_12PM"
    
    # Comando powershell para criar a tarefa
    # SchTasks /Create /SC DAILY /TN "EditalCrawler" /TR "python main.py" /ST 12:00
    cmd = [
        "schtasks", "/Create", "/SC", "DAILY", "/TN", task_name,
        "/TR", f'"{python_path}" "{script_path}"', "/ST", "12:00", "/F"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Sucesso! Tarefa agendada: {task_name}")
            print(f"Comando: {python_path} {script_path}")
        else:
            print(f"Erro ao agendar tarefa: {result.stderr}")
            print("Dica: Execute o VS Code/Terminal como ADMINISTRADOR.")
    except Exception as e:
        print(f"Erro crítico ao agendar tarefa: {e}")

if __name__ == "__main__":
    setup_windows_task()
