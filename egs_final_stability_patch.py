from pathlib import Path
import shutil, re
from datetime import datetime

ROOT = Path.cwd()
ALT = ROOT / "05 - Código Fuente" / "egs-fire-academy"
if not (ROOT / "web").exists() and (ALT / "web").exists():
    ROOT = ALT

WEB = ROOT / "web"
if not WEB.exists():
    raise SystemExit("ERROR: ejecutá este archivo dentro de egs-fire-academy.")

BACKUP = ROOT / "_backup_final_stability"
BACKUP.mkdir(exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for rel in ["simulation-core-client.js","web/simulation-core-client.js","index.html","web/index.html"]:
    p = ROOT / rel
    if p.exists():
        shutil.copy2(p, BACKUP / f"{rel.replace('/','__')}.{stamp}.bak")

HUMAN_BLOCK = '''
const HUMAN_ACTION = {
  sizeup_360:"Reconocimiento 360°",
  read_smoke:"Interpretar humo",
  control_door:"Controlar puerta",
  open_door:"Abrir puerta",
  open_window:"Abrir ventana",
  deploy_simple_line:"Desplegar línea simple",
  deploy_combined_line:"Desplegar línea combinada",
  deploy_mixed_line:"Desplegar línea mixta",
  select_fog:"Seleccionar patrón niebla",
  select_straight:"Seleccionar chorro pleno",
  open_nozzle:"Abrir lanza / aplicar agua",
  gas_cooling:"Enfriamiento de gases",
  direct_attack:"Ataque directo",
  search_primary:"Búsqueda primaria",
  locate_victim:"Localizar víctima",
  remove_victim:"Retirar víctima",
  era_check:"Chequeo ERA",
  era_entry:"Ingreso con ERA",
  era_exit:"Salida con ERA",
  vehicle_isolate:"Aislar riesgos",
  vehicle_stabilize:"Estabilizar vehículo",
  vehicle_access:"Crear acceso",
  vehicle_extricate:"Extricar víctima"
};

const HUMAN_EVENT = {
  camera_or_scene_sizeup:"Reconocimiento de escena",
  smoke_observation:"Lectura de humo",
  door_control:"Control de puerta",
  door_open:"Puerta abierta",
  airflow_change:"Cambio de flujo de aire",
  window_open:"Ventana abierta",
  hose_deploy:"Línea desplegada",
  nozzle_fog:"Patrón niebla seleccionado",
  nozzle_straight:"Chorro pleno seleccionado",
  water_stream_start:"Aplicación de agua",
  search_mode:"Búsqueda iniciada",
  victim_highlight:"Víctima localizada",
  victim_remove:"Víctima retirada",
  era_check:"ERA comprobado",
  crew_enter:"Ingreso realizado",
  crew_exit:"Salida realizada",
  hazard_isolation:"Riesgos aislados",
  vehicle_stabilize:"Vehículo estabilizado",
  vehicle_access:"Acceso creado",
  victim_extricate:"Víctima extricada"
};

let lastCoreActionAt = 0;
let lastCoreActionName = "";
'''

for rel in ["simulation-core-client.js","web/simulation-core-client.js"]:
    p = ROOT / rel
    if not p.exists():
        continue

    t = p.read_text(encoding="utf-8")

    if "const HUMAN_ACTION" not in t:
        t = t.replace("const VISUAL_FROM_ACTION = {", HUMAN_BLOCK + "\nconst VISUAL_FROM_ACTION = {")

    old_eval = 'evaluate(uiAction){\n    if(!this.currentState) this.reset(this.currentScenario);'
    new_eval = '''evaluate(uiAction){
    const now=Date.now();
    if(uiAction===lastCoreActionName && (now-lastCoreActionAt)<900){
      console.debug("ACCIÓN IGNORADA POR REBOTE", uiAction);
      return null;
    }
    lastCoreActionAt=now;
    lastCoreActionName=uiAction;
    if(!this.currentState) this.reset(this.currentScenario);'''
    if old_eval in t:
        t = t.replace(old_eval, new_eval)

    old_log = 'row.innerHTML="<strong>CORE</strong> - "+this.escape(entry.action)+"<br><small>"+this.escape(entry.visual_events.join(" / ")||"acción registrada")+"</small>";'
    new_log = 'const actionLabel=HUMAN_ACTION[entry.action]||entry.action; const eventLabel=(entry.visual_events||[]).map(x=>HUMAN_EVENT[x]||x).join(" / "); row.innerHTML="<strong>CORE</strong> - "+this.escape(actionLabel)+"<br><small>"+this.escape(eventLabel||"Acción registrada")+"</small>";'
    t = t.replace(old_log, new_log)

    t = t.replace("this.escape(x.action)", "this.escape(HUMAN_ACTION[x.action]||x.action)")
    t = t.replace(
        'this.escape((x.visual_events||[]).join(" / ")||"Interacción registrada")',
        'this.escape((x.visual_events||[]).map(v=>HUMAN_EVENT[v]||v).join(" / ")||"Interacción registrada")'
    )

    old_wrap = '''const entry=EGSCore.evaluate(action);
      const result=await originalAction.apply(this,arguments);
      window.dispatchEvent(new CustomEvent("egs:simulation-event",{detail:entry}));'''
    new_wrap = '''const entry=EGSCore.evaluate(action);
      if(!entry) return;
      const result=await originalAction.apply(this,arguments);
      window.dispatchEvent(new CustomEvent("egs:simulation-event",{detail:entry}));'''
    t = t.replace(old_wrap, new_wrap)

    p.write_text(t, encoding="utf-8")

for rel in ["index.html","web/index.html"]:
    p = ROOT / rel
    if p.exists():
        t = p.read_text(encoding="utf-8")
        t = re.sub(r'simulation-core-client\.js\?v=\d+', 'simulation-core-client.js?v=41', t)
        p.write_text(t, encoding="utf-8")

print("="*74)
print("EGS FINAL STABILITY PATCH APLICADO")
print("="*74)
print("[OK] Anti-doble-click / anti-rebote en acciones")
print("[OK] AAR con nombres humanos")
print("[OK] Eventos con nombres humanos")
print("[OK] Cache actualizado a v41")
print("[OK] Backup automático creado")
print()
print("Backup:", BACKUP)
print("NO hace git push.")
