import json
from pathlib import Path


CORE_DIR = Path(__file__).parent
TRANSFORMER_DIR = CORE_DIR / "transformer"


def audit_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        data = [data]

    total = len(data)
    missing_valor = 0
    missing_tipo = 0
    missing_pdf = 0

    for item in data:
        extras = item.get("extras") or {}
        if not item.get("valor"):
            missing_valor += 1
        if item.get("tipo_recurso") in (None, "Não Especificado"):
            missing_tipo += 1
        if not extras.get("pdf_url"):
            missing_pdf += 1

    return {
        "arquivo": file_path.name,
        "total": total,
        "missing_valor": missing_valor,
        "missing_tipo_recurso": missing_tipo,
        "missing_pdf_url": missing_pdf,
    }


def main():
    files = sorted(TRANSFORMER_DIR.glob("*_standardized.json"))
    if not files:
        print("Nenhum arquivo padronizado encontrado.")
        return

    print("=== Auditoria de qualidade dos campos principais ===")
    for file_path in files:
        report = audit_file(file_path)
        print(
            f"{report['arquivo']}: total={report['total']}, "
            f"sem_valor={report['missing_valor']}, "
            f"sem_tipo_recurso={report['missing_tipo_recurso']}, "
            f"sem_pdf_url={report['missing_pdf_url']}"
        )


if __name__ == "__main__":
    main()
