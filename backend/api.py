from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import random


app = FastAPI(
    title="EGS | ACADEMIA VIRTUAL DE BOMBEROS API",
    version="1.1.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE = BASE_DIR / "knowledge"
MODULES = KNOWLEDGE / "modules"
SCENARIOS = BASE_DIR / "scenarios"


def load_json(path: Path):
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No existe: {path.name}"
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


# =========================================================
# ESTADO GENERAL
# =========================================================

@app.get("/")
def root():
    return {
        "system": "EGS | ACADEMIA VIRTUAL DE BOMBEROS",
        "status": "en línea",
        "version": "1.1.1",
        "developer": "Téc. Sup. en Gestión Ambiental Yamila Vocos",
        "location": "San Francisco, Córdoba, Argentina"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "api": "online"
    }


# =========================================================
# ACADEMIA
# =========================================================

@app.get("/academy/modules")
def academy_modules():
    return load_json(
        KNOWLEDGE / "academy_modules.json"
    )


@app.get("/academy/module/{module_id}")
def academy_module(module_id: str):
    return load_json(
        MODULES / f"{module_id}.json"
    )


@app.get("/academy/module/{module_id}/training")
def academy_training(
    module_id: str,
    shuffle: bool = True
):

    data = academy_module(module_id)

    questions = data.get(
        "training",
        []
    )[:]

    if shuffle:
        random.shuffle(questions)

    return {
        "metadata": data.get(
            "metadata",
            {}
        ),
        "training": questions
    }


@app.get("/academy/integral")
def integral(limit: int = 20):

    catalog = load_json(
        KNOWLEDGE / "academy_modules.json"
    )

    questions = []

    for module in catalog.get("modules", []):

        path = MODULES / f"{module['id']}.json"

        if not path.exists():
            continue

        data = load_json(path)

        for question in data.get(
            "training",
            []
        ):

            item = dict(question)

            item["module_id"] = module["id"]
            item["module_name"] = module["name"]

            questions.append(item)

    random.shuffle(questions)

    limit = max(
        1,
        min(
            limit,
            len(questions)
        )
    )

    return {
        "metadata": {
            "module_name": "Evaluación Integral BN1",
            "version": "1.1.1"
        },
        "training": questions[:limit]
    }


# =========================================================
# BIBLIOTECA DOCTRINARIA
# =========================================================

@app.get("/sources")
def sources():

    return load_json(
        KNOWLEDGE / "source_registry.json"
    )


# =========================================================
# ESCENARIOS
# ESTA ERA LA RUTA QUE FALTABA
# =========================================================

@app.get("/scenarios")
def scenarios():

    registry = SCENARIOS / "scenario_registry.json"

    if registry.exists():
        return load_json(registry)

    # Fallback para que la plataforma no se caiga
    # aunque el registro de escenarios todavía no exista.

    return {
        "version": "1.1.1",
        "scenarios": [
            {
                "id": "HOUSE_3D_001",
                "name": "Incendio en vivienda unifamiliar",
                "module_id": "estructurales",
                "status": "activo",
                "description": "Entrenamiento inicial de incendio estructural."
            },
            {
                "id": "VEHICLE_3D_001",
                "name": "Incendio vehicular",
                "module_id": "estructurales",
                "status": "desarrollo",
                "description": "Escenario de incendio vehicular."
            },
            {
                "id": "RESCUE_3D_001",
                "name": "Rescate vehicular",
                "module_id": "rescate",
                "status": "desarrollo",
                "description": "Colisión vehicular con persona atrapada."
            }
        ]
    }


# =========================================================
# CONFIGURACIÓN DEL SIMULADOR 3D
# =========================================================

@app.get("/simulator/config")
def simulator_config():

    config = SCENARIOS / "simulator_3d.json"

    if config.exists():
        return load_json(config)

    return {
        "status": "active",
        "version": "1.1.1",
        "engine": "Three.js / WebGL",
        "quality": "medium"
    }