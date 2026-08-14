
from pathlib import Path
import json
from datetime import datetime

ROOT = Path.cwd()
ALT = ROOT / "05 - Código Fuente" / "egs-fire-academy"
if not (ROOT / "web").exists() and (ALT / "web").exists():
    ROOT = ALT

if not (ROOT / "web").exists():
    raise SystemExit("ERROR: ejecutá este archivo dentro de egs-fire-academy.")

CORE = ROOT / "simulation_core"
(CORE / "rules").mkdir(parents=True, exist_ok=True)
(CORE / "scenarios").mkdir(parents=True, exist_ok=True)
(CORE / "schemas").mkdir(parents=True, exist_ok=True)

catalog = {
    "metadata": {
        "name": "EGS Simulation Core",
        "version": "1.0.0-dev",
        "created": datetime.now().isoformat(timespec="seconds"),
        "principle": "Teoría -> observación -> decisión -> consecuencia -> análisis -> fuente"
    },
    "families": [
        {"id":"structural","name":"Incendios estructurales","status":"priority","scenarios":[
            "vivienda_unifamiliar","departamento","edificio_altura","comercio","deposito",
            "industria","sotano","garage","escuela","hospital","hotel"
        ]},
        {"id":"vehicle","name":"Incendios vehiculares","status":"priority","scenarios":[
            "vehiculo_convencional","vehiculo_hibrido","vehiculo_electrico","camion","colectivo","maquinaria_agricola"
        ]},
        {"id":"wildland_interface","name":"Incendios forestales y de interfaz","status":"planned","scenarios":[
            "pastizal","monte","bosque","interfaz_urbano_rural","propagacion_por_viento","proteccion_de_viviendas"
        ]},
        {"id":"flammable_liquids_gases","name":"Líquidos inflamables y gases","status":"planned","scenarios":[
            "derrame_combustible","deposito_combustibles","fuga_gas_con_incendio","cilindro_gas_expuesto","estacion_servicio"
        ]},
        {"id":"electrical","name":"Riesgo e incendio eléctrico","status":"planned","scenarios":[
            "tablero_electrico","instalacion_energizada","transformador","sala_electrica"
        ]},
        {"id":"metals_special","name":"Metales combustibles y riesgos especiales","status":"planned","scenarios":[
            "metal_combustible","taller_industrial","almacenamiento_especial"
        ]},
        {"id":"cooking_oils","name":"Aceites y grasas de cocina","status":"planned","scenarios":[
            "cocina_domestica","cocina_comercial","freidora"
        ]},
        {"id":"fire_behavior","name":"Comportamiento del fuego","status":"priority","scenarios":[
            "crecimiento_incendio","transferencia_calor","plano_neutro","flujo_gases","ventilacion",
            "rollover","flashover","incendio_limitado_combustible","incendio_limitado_ventilacion"
        ]},
        {"id":"water_lines","name":"Líneas, abastecimiento y aplicación de agua","status":"priority","scenarios":[
            "linea_simple","linea_combinada","linea_mixta","despliegue_cleveland","despliegue_estiba",
            "seleccion_lanza","patrones_chorro","abastecimiento","perdidas_y_presion"
        ]},
        {"id":"era_search","name":"ERA, ingreso, búsqueda y rescate","status":"priority","scenarios":[
            "chequeo_era","ingreso_atmosfera","orientacion","busqueda_primaria","victima_inconsciente",
            "consumo_aire","emergencia_era","salida"
        ]},
        {"id":"vehicle_rescue","name":"Rescate vehicular","status":"priority","scenarios":[
            "reconocimiento","aislamiento_riesgos","estabilizacion","acceso","manejo_herramientas","extricacion"
        ]},
        {"id":"integrated","name":"Escenarios integrales","status":"future","scenarios":[
            "incendio_estructural_completo","incendio_con_multiples_victimas","incendio_y_rescate",
            "mando_y_toma_decisiones","operacion_multi_dotacion"
        ]}
    ]
}

state_schema = {
    "scenario_id":"string",
    "phase":"dispatch|sizeup|operations|control|termination|aar",
    "environment":{"time_of_day":"string","weather":"object","wind":"object"},
    "fire":{"development_stage":"string","heat_level":"number","smoke_density":"number","visibility":"number",
            "oxygen_level":"number","ventilation_state":"string","flow_path":"object","fire_locations":"array"},
    "structure":{"type":"string","doors":"array","windows":"array","compartments":"array","exposures":"array"},
    "resources":{"crew":"array","apparatus":"array","hoselines":"array","tools":"array","era":"array"},
    "victims":"array","decisions":"array","objectives":"array","doctrine_links":"array"
}

rule_schema = {
    "rule_id":"string",
    "concept":"string",
    "trigger":{"conditions":"array","user_action":"string"},
    "effects":[{"target":"state.path","operation":"set|add|subtract|multiply|transition",
                "value":"number|string|object","visual_event":"string"}],
    "evaluation":{"classification":"adequate|review|critical","feedback":"string"},
    "source":{"source_id":"string","document":"string","section":"string","page":"string",
              "validation_status":"pending|validated"}
}

master = {
    "id":"structural_house_master",
    "family":"structural",
    "name":"Escenario Maestro | Incendio estructural en vivienda",
    "status":"design",
    "briefing":{"dispatch":"Pendiente de redacción doctrinaria validada","known_information":[],"unknown_information":[]},
    "learning_objectives":[
        "Reconocimiento y lectura de escena","Interpretación de humo y condiciones",
        "Control de accesos y ventilación","Selección y despliegue de línea","Aplicación de agua",
        "Búsqueda y rescate","Reevaluación continua","Análisis posterior"
    ],
    "phases":["despacho","arribo","reconocimiento","seleccion_tactica","despliegue","ingreso",
              "control","busqueda","reevaluacion","finalizacion","after_action_review"],
    "doctrine_policy":{
        "allow_unvalidated_rules":False,
        "rule_behavior":"Una acción sin regla validada no debe producir una consecuencia doctrinaria definitiva.",
        "source_priority":[
            "Material de formación aportado por el usuario",
            "Federación de Bomberos Voluntarios de Córdoba",
            "Academia Nacional / fuentes institucionales pertinentes",
            "Referencias internacionales complementarias identificadas"
        ]
    }
}

readme = """# EGS Simulation Core

## Principio
Teoría -> observación -> decisión -> consecuencia -> análisis -> fuente.

## Archivos
- catalog.json: familias y escenarios.
- schemas/state.schema.json: estado de simulación.
- schemas/rule.schema.json: regla doctrinaria.
- scenarios/structural_house_master.json: primer escenario maestro.
- rules/: reglas validadas.

## Regla doctrinaria
No se incorporan consecuencias tácticas definitivas sin una fuente identificable y validada.

## Arquitectura
El motor gráfico (web, Unreal u otro) consume estos estados y reglas.
Así podemos cambiar de tecnología visual sin perder conocimiento, trazabilidad ni diseño pedagógico.
"""

(CORE/"catalog.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding="utf-8")
(CORE/"schemas"/"state.schema.json").write_text(json.dumps(state_schema,ensure_ascii=False,indent=2),encoding="utf-8")
(CORE/"schemas"/"rule.schema.json").write_text(json.dumps(rule_schema,ensure_ascii=False,indent=2),encoding="utf-8")
(CORE/"scenarios"/"structural_house_master.json").write_text(json.dumps(master,ensure_ascii=False,indent=2),encoding="utf-8")
(CORE/"README.md").write_text(readme,encoding="utf-8")
(CORE/"rules"/"README.md").write_text("# Reglas doctrinarias\n\nSolo reglas con fuente identificada y estado de validación.\n",encoding="utf-8")

print("="*76)
print("EGS SIMULATION CORE v1 CREADO")
print("="*76)
print("[OK] Catálogo general de familias de simulación")
print("[OK] Esquema de estados")
print("[OK] Esquema de reglas doctrinarias")
print("[OK] Escenario maestro de vivienda")
print("[OK] Política de no inventar consecuencias sin fuente")
print("Directorio:", CORE)
print("NO modifica la web pública.")
