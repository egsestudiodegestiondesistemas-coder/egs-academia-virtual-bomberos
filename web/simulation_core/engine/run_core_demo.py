import json, copy
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
