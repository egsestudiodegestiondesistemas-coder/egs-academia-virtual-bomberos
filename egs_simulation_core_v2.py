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
if not CORE.exists():
    raise SystemExit("ERROR: primero debe existir simulation_core v1.")

for sub in ["engine","events","aar","rules/pending","rules/validated"]:
    (CORE / sub).mkdir(parents=True, exist_ok=True)

engine = {
    "metadata":{"name":"EGS Simulation Core Engine","version":"2.0.0-dev","created":datetime.now().isoformat(timespec="seconds"),"graphics_independent":True},
    "lifecycle":["dispatch","arrival","sizeup","decision","operation","reassessment","control","termination","aar"],
    "state_domains":["environment","fire","smoke","structure","ventilation","water","resources","crew","era","victims","hazards","objectives","decisions","events"]
}
actions = [
    {"id":"sizeup_360","label":"Reconocimiento 360°","domain":"sizeup"},
    {"id":"read_smoke","label":"Interpretar humo","domain":"fire_behavior"},
    {"id":"control_door","label":"Controlar puerta","domain":"ventilation"},
    {"id":"open_door","label":"Abrir puerta","domain":"ventilation"},
    {"id":"open_window","label":"Abrir ventana","domain":"ventilation"},
    {"id":"deploy_simple_line","label":"Desplegar línea simple","domain":"water_lines"},
    {"id":"deploy_combined_line","label":"Desplegar línea combinada","domain":"water_lines"},
    {"id":"deploy_mixed_line","label":"Desplegar línea mixta","domain":"water_lines"},
    {"id":"select_fog","label":"Seleccionar patrón niebla","domain":"water_lines"},
    {"id":"select_straight","label":"Seleccionar chorro pleno","domain":"water_lines"},
    {"id":"open_nozzle","label":"Abrir lanza","domain":"water_lines"},
    {"id":"gas_cooling","label":"Enfriamiento de gases","domain":"fire_attack"},
    {"id":"direct_attack","label":"Ataque directo","domain":"fire_attack"},
    {"id":"search_primary","label":"Búsqueda primaria","domain":"search"},
    {"id":"locate_victim","label":"Localizar víctima","domain":"search"},
    {"id":"remove_victim","label":"Retirar víctima","domain":"rescue"},
    {"id":"era_check","label":"Chequeo ERA","domain":"era"},
    {"id":"era_entry","label":"Ingreso con ERA","domain":"era"},
    {"id":"era_exit","label":"Salida con ERA","domain":"era"},
    {"id":"vehicle_isolate","label":"Aislar riesgos vehiculares","domain":"vehicle"},
    {"id":"vehicle_stabilize","label":"Estabilizar vehículo","domain":"vehicle"},
    {"id":"vehicle_access","label":"Crear acceso vehicular","domain":"vehicle"},
    {"id":"vehicle_extricate","label":"Extricar víctima","domain":"vehicle"}
]
initial_state = {
    "scenario_id":"structural_house_master","phase":"dispatch","clock_seconds":0,
    "environment":{"time_of_day":"night","weather":"pending","wind":"pending"},
    "fire":{"development_stage":"pending","heat_level":None,"smoke_density":None,"visibility":None,"oxygen_level":None,"ventilation_state":"closed","flow_path":{"status":"unknown"},"fire_locations":[]},
    "structure":{"type":"single_family_house","doors":{"front":{"state":"closed"}},"windows":{"front":{"state":"closed"}},"compartments":[],"exposures":[]},
    "resources":{"crew":[],"apparatus":[],"hoselines":[],"tools":[],"era":[]},
    "victims":[],"hazards":[],"objectives":[{"id":"recognition","status":"active"},{"id":"fire_control","status":"pending"},{"id":"search","status":"pending"}],
    "decisions":[],"events":[],"doctrine_links":[]
}
pending_rules = [
    {
        "rule_id":"R-PENDING-VENT-001","concept":"Apertura y ventilación",
        "trigger":{"conditions":["estructura cerrada"],"user_action":"open_door"},
        "effects":[
            {"target":"structure.doors.front.state","operation":"set","value":"open","visual_event":"door_open"},
            {"target":"fire.ventilation_state","operation":"transition","value":"modified","visual_event":"airflow_change"}
        ],
        "evaluation":{"classification":"review","feedback":"La consecuencia táctica final debe validarse contra la fuente doctrinaria aplicable al escenario."},
        "source":{"source_id":"PENDING","document":"","section":"","page":"","validation_status":"pending"}
    },
    {
        "rule_id":"R-PENDING-WATER-001","concept":"Aplicación de agua",
        "trigger":{"conditions":["línea desplegada","lanza disponible"],"user_action":"open_nozzle"},
        "effects":[{"target":"water.flow","operation":"transition","value":"open","visual_event":"water_stream_start"}],
        "evaluation":{"classification":"review","feedback":"El efecto térmico y operativo debe parametrizarse con fuente validada."},
        "source":{"source_id":"PENDING","document":"","section":"","page":"","validation_status":"pending"}
    },
    {
        "rule_id":"R-PENDING-ERA-001","concept":"Ingreso con ERA",
        "trigger":{"conditions":["ERA comprobado"],"user_action":"era_entry"},
        "effects":[{"target":"crew.entry_state","operation":"transition","value":"interior","visual_event":"crew_enter"}],
        "evaluation":{"classification":"review","feedback":"Secuencia y criterios de ingreso pendientes de validación doctrinaria."},
        "source":{"source_id":"PENDING","document":"","section":"","page":"","validation_status":"pending"}
    }
]
bridge = {
    "description":"Contrato entre Simulation Core y cualquier motor gráfico",
    "input_from_ui":{"scenario_id":"string","action_id":"string","parameters":"object"},
    "output_to_graphics":{"state_patch":"object","visual_events":"array","audio_events":"array","hud_patch":"object"},
    "output_to_learning":{"classification":"string","feedback":"string","source":"object","review_topic":"string"}
}
aar_schema = {
    "scenario_id":"string","started_at":"datetime","finished_at":"datetime","duration_seconds":"number",
    "objectives":[{"id":"string","status":"completed|partial|not_completed"}],
    "timeline":[{"t":"number","phase":"string","action":"string","state_before":"object","state_after":"object","visual_events":"array","classification":"adequate|review|critical|unscored","feedback":"string","source":"object"}],
    "review_topics":"array","sources_used":"array"
}

files = {
    CORE/"engine"/"engine.json":engine,
    CORE/"engine"/"actions.json":actions,
    CORE/"engine"/"initial_state.json":initial_state,
    CORE/"engine"/"bridge_contract.json":bridge,
    CORE/"aar"/"aar.schema.json":aar_schema,
    CORE/"rules"/"pending"/"starter_rules.json":pending_rules
}
for p,data in files.items():
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

runner = '''import json, copy
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parents[1]
ENGINE = BASE / "engine"
RULES = BASE / "rules"

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def nested_set(obj, path, value):
    parts = path.split(".")
    cur = obj
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value

def apply_rule(state, rule):
    before = copy.deepcopy(state)
    visual = []
    for effect in rule.get("effects", []):
        if effect.get("operation") in ("set","transition"):
            nested_set(state, effect["target"], effect.get("value"))
        if effect.get("visual_event"):
            visual.append(effect["visual_event"])
    entry = {
        "t": state.get("clock_seconds",0),
        "phase": state.get("phase"),
        "action": rule.get("trigger",{}).get("user_action"),
        "state_before": before,
        "state_after": copy.deepcopy(state),
        "visual_events": visual,
        "classification": rule.get("evaluation",{}).get("classification","unscored"),
        "feedback": rule.get("evaluation",{}).get("feedback",""),
        "source": rule.get("source",{})
    }
    state.setdefault("decisions",[]).append(entry)
    state.setdefault("events",[]).extend(visual)
    return state, entry

def main():
    state = load_json(ENGINE/"initial_state.json")
    pending = load_json(RULES/"pending"/"starter_rules.json")
    print("EGS Simulation Core v2")
    print("Escenario:", state["scenario_id"])
    print("Reglas pending:", len(pending))
    for rule in pending:
        state, entry = apply_rule(state, rule)
        print("-", entry["action"], "=>", ", ".join(entry["visual_events"]) or "sin evento")
    out = BASE/"aar"/"last_test_run.json"
    out.write_text(json.dumps({"generated_at":datetime.now().isoformat(),"state":state,"timeline":state["decisions"]},ensure_ascii=False,indent=2),encoding="utf-8")
    print("AAR de prueba:", out)

if __name__ == "__main__":
    main()
'''
(CORE/"engine"/"run_core_demo.py").write_text(runner,encoding="utf-8")

(CORE/"README_V2.md").write_text(
    "# EGS Simulation Core v2\n\n"
    "Agrega motor de estados, catálogo de acciones, contrato UI/Core/Gráficos, eventos visuales, reglas pending/validated y After Action Review.\n\n"
    "Las reglas pending demuestran integración técnica, pero NO deben mostrarse como doctrina validada.\n",
    encoding="utf-8"
)

print("="*78)
print("EGS SIMULATION CORE v2 CREADO")
print("="*78)
print("[OK] Motor de estados")
print("[OK] Catálogo de acciones")
print("[OK] Contrato para motor gráfico / Unreal")
print("[OK] Eventos visuales")
print("[OK] After Action Review")
print("[OK] Reglas pending separadas de validated")
print("[OK] Demo ejecutable")
print()
print("Probá ahora:")
print(r"python .\simulation_core\engine\run_core_demo.py")
print()
print("NO modifica la web pública.")
