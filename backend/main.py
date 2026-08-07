from pathlib import Path
import json

PROJECT_NAME = "EGS FIRE ACADEMY"
PROJECT_VERSION = "0.1.0-alpha"

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
SCENARIOS_DIR = BASE_DIR / "scenarios"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_system_status() -> dict:
    return {
        "project": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "active_modules": [
            "Química del Fuego",
            "Operaciones en Incendios Estructurales",
        ],
        "knowledge_directory": str(KNOWLEDGE_DIR),
        "scenarios_directory": str(SCENARIOS_DIR),
        "status": "Núcleo doctrinario inicializado",
    }


if __name__ == "__main__":
    status = get_system_status()

    print("=" * 60)
    print(PROJECT_NAME)
    print("=" * 60)

    for key, value in status.items():
        print(f"{key}: {value}")