from pathlib import Path
import shutil, re, json
from datetime import datetime

ROOT = Path.cwd()
ALT = ROOT / "05 - Código Fuente" / "egs-fire-academy"
if not (ROOT / "web").exists() and (ALT / "web").exists():
    ROOT = ALT

WEB = ROOT / "web"
CORE = ROOT / "simulation_core"

if not WEB.exists():
    raise SystemExit("ERROR: ejecutá este archivo dentro de egs-fire-academy.")
if not CORE.exists():
    raise SystemExit("ERROR: no existe simulation_core. Ejecutá primero v1 y v2.")

BACKUP = ROOT / "_backup_integration_v3"
BACKUP.mkdir(exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for rel in ["index.html","web/index.html","app.js","web/app.js","styles.css","web/styles.css"]:
    p = ROOT / rel
    if p.exists():
        shutil.copy2(p, BACKUP / f"{rel.replace('/','__')}.{stamp}.bak")

web_core = WEB / "simulation_core"
if web_core.exists():
    shutil.rmtree(web_core)
shutil.copytree(CORE, web_core)

client = r'''(() => {
"use strict";

const CORE_BASE = "./simulation_core";
const ACTION_MAP = {
  recognition:"sizeup_360",
  observe:"read_smoke",
  open_access:"open_door",
  control_door:"control_door",
  open_window:"open_window",
  ventilate:"open_window",
  deploy_line:"deploy_simple_line",
  select_fog:"select_fog",
  select_straight:"select_straight",
  cooling:"open_nozzle",
  search:"search_primary",
  era_check:"era_check",
  enter:"era_entry",
  exit:"era_exit",
  isolate:"vehicle_isolate",
  stabilize:"vehicle_stabilize",
  access:"vehicle_access",
  extricate:"vehicle_extricate",
  protect:"direct_attack",
  rollover:"read_smoke",
  flashover:"read_smoke"
};

const VISUAL_FROM_ACTION = {
  sizeup_360:["camera_or_scene_sizeup"],
  read_smoke:["smoke_observation"],
  control_door:["door_control"],
  open_door:["door_open","airflow_change"],
  open_window:["window_open","airflow_change"],
  deploy_simple_line:["hose_deploy"],
  deploy_combined_line:["hose_deploy"],
  deploy_mixed_line:["hose_deploy"],
  select_fog:["nozzle_fog"],
  select_straight:["nozzle_straight"],
  open_nozzle:["water_stream_start"],
  gas_cooling:["water_stream_start"],
  direct_attack:["water_stream_start"],
  search_primary:["search_mode"],
  locate_victim:["victim_highlight"],
  remove_victim:["victim_remove"],
  era_check:["era_check"],
  era_entry:["crew_enter"],
  era_exit:["crew_exit"],
  vehicle_isolate:["hazard_isolation"],
  vehicle_stabilize:["vehicle_stabilize"],
  vehicle_access:["vehicle_access"],
  vehicle_extricate:["victim_extricate"]
};

const EGSCore = {
  ready:false,
  catalog:null,
  engine:null,
  actions:[],
  initialState:null,
  pendingRules:[],
  currentState:null,
  currentScenario:null,
  timeline:[],
  startedAt:null,

  async load(){
    try{
      const [catalog,engine,actions,state,pending] = await Promise.all([
        fetch(`${CORE_BASE}/catalog.json`).then(r=>r.json()),
        fetch(`${CORE_BASE}/engine/engine.json`).then(r=>r.json()),
        fetch(`${CORE_BASE}/engine/actions.json`).then(r=>r.json()),
        fetch(`${CORE_BASE}/engine/initial_state.json`).then(r=>r.json()),
        fetch(`${CORE_BASE}/rules/pending/starter_rules.json`).then(r=>r.json())
      ]);
      this.catalog=catalog;
      this.engine=engine;
      this.actions=actions;
      this.initialState=state;
      this.pendingRules=pending;
      this.ready=true;
      console.log("EGS Simulation Core v3 conectado");
    }catch(err){
      console.warn("Simulation Core no disponible:",err);
    }
  },

  clone(v){ return JSON.parse(JSON.stringify(v)); },

  reset(scenarioId){
    this.currentScenario=scenarioId || "structural_house_master";
    this.currentState=this.clone(this.initialState || {});
    this.currentState.scenario_id=this.currentScenario;
    this.currentState.phase="arrival";
    this.currentState.decisions=[];
    this.currentState.events=[];
    this.timeline=[];
    this.startedAt=new Date();
    const cond=document.getElementById("simCondition");
    if(cond) cond.textContent="CORE ACTIVO";
  },

  nestedSet(obj,path,value){
    const parts=path.split(".");
    let cur=obj;
    for(let i=0;i<parts.length-1;i++){
      const p=parts[i];
      if(!cur[p] || typeof cur[p]!=="object") cur[p]={};
      cur=cur[p];
    }
    cur[parts[parts.length-1]]=value;
  },

  findRule(coreAction){
    return this.pendingRules.find(r=>r && r.trigger && r.trigger.user_action===coreAction) || null;
  },

  evaluate(uiAction){
    if(!this.currentState) this.reset(this.currentScenario);
    const coreAction=ACTION_MAP[uiAction] || uiAction;
    const before=this.clone(this.currentState);
    const rule=this.findRule(coreAction);
    let visualEvents=[...(VISUAL_FROM_ACTION[coreAction]||[])];
    let classification="unscored";
    let feedback="Interacción registrada. Evaluación doctrinaria pendiente de una regla validada.";
    let source={validation_status:"pending"};

    if(rule){
      for(const effect of rule.effects||[]){
        if(["set","transition"].includes(effect.operation)){
          this.nestedSet(this.currentState,effect.target,effect.value);
        }
        if(effect.visual_event && !visualEvents.includes(effect.visual_event)){
          visualEvents.push(effect.visual_event);
        }
      }
      classification=(rule.evaluation&&rule.evaluation.classification)||"review";
      feedback=(rule.evaluation&&rule.evaluation.feedback)||feedback;
      source=rule.source||source;
    }

    const entry={
      t:Math.max(0,Math.round((Date.now()-(this.startedAt?this.startedAt.getTime():Date.now()))/1000)),
      scenario_id:this.currentScenario,
      ui_action:uiAction,
      action:coreAction,
      state_before:before,
      state_after:this.clone(this.currentState),
      visual_events:visualEvents,
      classification,
      feedback,
      source
    };

    this.timeline.push(entry);
    this.currentState.decisions.push(entry);
    this.currentState.events.push(...visualEvents);
    this.renderCoreEvent(entry);
    return entry;
  },

  renderCoreEvent(entry){
    const box=document.getElementById("simLog");
    if(box){
      const row=document.createElement("div");
      row.className="coreLog";
      row.innerHTML="<strong>CORE</strong> - "+this.escape(entry.action)+"<br><small>"+this.escape(entry.visual_events.join(" / ")||"acción registrada")+"</small>";
      box.prepend(row);
    }
    const cond=document.getElementById("simCondition");
    if(cond) cond.textContent="CORE - "+String(entry.classification).toUpperCase();
  },

  finish(){
    const finished=new Date();
    const aar={
      version:"EGS-AAR-1",
      scenario_id:this.currentScenario,
      started_at:this.startedAt?this.startedAt.toISOString():null,
      finished_at:finished.toISOString(),
      duration_seconds:this.startedAt?Math.round((finished-this.startedAt)/1000):0,
      timeline:this.clone(this.timeline),
      doctrine_status:{
        validated:this.timeline.filter(x=>x.source&&x.source.validation_status==="validated").length,
        pending:this.timeline.filter(x=>!x.source||x.source.validation_status!=="validated").length
      }
    };
    try{ localStorage.setItem("egs_last_simulation_aar",JSON.stringify(aar)); }catch(e){}
    this.showAAR(aar);
    return aar;
  },

  showAAR(aar){
    let overlay=document.getElementById("egsAAROverlay");
    if(!overlay){
      overlay=document.createElement("div");
      overlay.id="egsAAROverlay";
      overlay.className="aarOverlay";
      document.body.appendChild(overlay);
    }

    const rows=(aar.timeline||[]).map((x,i)=>
      '<div class="aarEntry">'+
      '<div><strong>'+String(i+1).padStart(2,"0")+' - '+this.escape(x.action)+'</strong><span>'+x.t+'s</span></div>'+
      '<p>'+this.escape((x.visual_events||[]).join(" / ")||"Interacción registrada")+'</p>'+
      '<small>'+(x.source&&x.source.validation_status==="validated"?"Regla validada":"Regla doctrinaria pendiente de validación")+'</small>'+
      '</div>'
    ).join("");

    overlay.innerHTML=
      '<div class="aarModal">'+
      '<button class="aarClose" onclick="document.getElementById(\'egsAAROverlay\').classList.remove(\'open\')">×</button>'+
      '<p class="eyebrow">AFTER ACTION REVIEW</p>'+
      '<h2>Análisis de la intervención</h2>'+
      '<div class="aarSummary">'+
      '<div><span>Duración</span><strong>'+aar.duration_seconds+'s</strong></div>'+
      '<div><span>Decisiones</span><strong>'+aar.timeline.length+'</strong></div>'+
      '<div><span>Validadas</span><strong>'+aar.doctrine_status.validated+'</strong></div>'+
      '<div><span>Pendientes</span><strong>'+aar.doctrine_status.pending+'</strong></div>'+
      '</div>'+
      '<div class="aarWarning">Las reglas pendientes sirven para integración técnica y no deben interpretarse como doctrina validada.</div>'+
      '<div class="aarTimeline">'+(rows||"<p>Sin acciones registradas.</p>")+'</div>'+
      '<div class="heroActions">'+
      '<button class="primary" onclick="document.getElementById(\'egsAAROverlay\').classList.remove(\'open\')">VOLVER</button>'+
      '<button class="secondary" onclick="window.EGSCore.downloadAAR()">EXPORTAR AAR</button>'+
      '</div></div>';

    overlay.classList.add("open");
  },

  downloadAAR(){
    const raw=localStorage.getItem("egs_last_simulation_aar");
    if(!raw)return;
    const blob=new Blob([raw],{type:"application/json"});
    const a=document.createElement("a");
    a.href=URL.createObjectURL(blob);
    a.download="egs_aar_"+Date.now()+".json";
    a.click();
    URL.revokeObjectURL(a.href);
  },

  escape(v){
    return String(v??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));
  }
};

window.EGSCore=EGSCore;

document.addEventListener("DOMContentLoaded",async()=>{
  await EGSCore.load();

  const originalLaunch=window.launchScenario;
  if(typeof originalLaunch==="function"){
    window.launchScenario=async function(id){
      EGSCore.reset(id);
      return originalLaunch.apply(this,arguments);
    };
  }

  const originalAction=window.simAction;
  if(typeof originalAction==="function"){
    window.simAction=async function(action){
      const entry=EGSCore.evaluate(action);
      const result=await originalAction.apply(this,arguments);
      window.dispatchEvent(new CustomEvent("egs:simulation-event",{detail:entry}));
      return result;
    };
  }

  const originalFinish=window.finish3DSimulation;
  if(typeof originalFinish==="function"){
    window.finish3DSimulation=async function(){
      const result=await originalFinish.apply(this,arguments);
      EGSCore.finish();
      return result;
    };
  }

  const originalReset=window.reset3DScenario;
  if(typeof originalReset==="function"){
    window.reset3DScenario=async function(){
      EGSCore.reset(EGSCore.currentScenario);
      return originalReset.apply(this,arguments);
    };
  }
});
})();'''

(WEB/"simulation-core-client.js").write_text(client,encoding="utf-8")
(ROOT/"simulation-core-client.js").write_text(client,encoding="utf-8")

extra_css = r'''
/* ===== EGS Simulation Core v3 ===== */
.coreLog{border-left:2px solid #f26b38!important;padding-left:9px!important}
.coreLog strong{color:#f26b38}.coreLog small{color:#7f8993}
.aarOverlay{position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:9999;display:none;align-items:center;justify-content:center;padding:18px}
.aarOverlay.open{display:flex}.aarModal{position:relative;width:min(900px,100%);max-height:92vh;overflow:auto;background:#101419;border:1px solid #343c45;border-radius:14px;padding:28px;box-shadow:0 30px 90px rgba(0,0,0,.55)}
.aarClose{position:absolute;right:16px;top:12px;background:none;border:0;color:white;font-size:30px;cursor:pointer}
.aarSummary{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:20px 0}.aarSummary div{background:#171d23;border:1px solid #2f3740;padding:14px;border-radius:8px}.aarSummary span{display:block;color:#7f8993;font-size:9px;text-transform:uppercase;letter-spacing:1px}.aarSummary strong{display:block;font-size:24px;margin-top:5px}
.aarWarning{padding:12px 14px;background:#1b1711;border:1px solid #59462c;color:#d9b77c;border-radius:8px;font-size:12px;margin-bottom:14px}
.aarEntry{padding:14px 0;border-bottom:1px solid #292f36}.aarEntry>div{display:flex;justify-content:space-between;gap:12px}.aarEntry p{color:#aab2ba;margin:7px 0}.aarEntry small{color:#7f8993}
@media(max-width:680px){.aarSummary{grid-template-columns:1fr 1fr}.aarModal{padding:20px 15px}}
'''

for rel in ["styles.css","web/styles.css"]:
    p=ROOT/rel
    if p.exists():
        t=p.read_text(encoding="utf-8")
        if "EGS Simulation Core v3" not in t:
            t += "\n" + extra_css
        p.write_text(t,encoding="utf-8")

for rel in ["index.html","web/index.html"]:
    p=ROOT/rel
    if not p.exists():
        continue
    t=p.read_text(encoding="utf-8")
    for a,b in {
        "ENTRAR AL SIMULADOR 3D":"IR AL SIMULADOR",
        "ENTRENAR EN 3D":"SIMULADOR",
        "Entrenar 3D":"Simulador",
        "Simulador 3D":"Simulador",
        "SIMULADOR OPERACIONAL 3D":"SIMULADOR OPERACIONAL"
    }.items():
        t=t.replace(a,b)

    t=re.sub(r'app\.js\?v=\d+','app.js?v=30',t)
    t=re.sub(r'styles\.css\?v=\d+','styles.css?v=30',t)
    t=re.sub(r'simulator\.js\?v=\d+','simulator.js?v=30',t)

    if "simulation-core-client.js" not in t:
        marker='<script src="app.js?v=30"></script>'
        if marker in t:
            t=t.replace(marker,marker+'\n<script src="simulation-core-client.js?v=30"></script>')
        else:
            t=t.replace("</body>",'<script src="simulation-core-client.js?v=30"></script>\n</body>')
    p.write_text(t,encoding="utf-8")

for rel in ["app.js","web/app.js"]:
    p=ROOT/rel
    if p.exists():
        t=p.read_text(encoding="utf-8")
        t=re.sub(r'import\("\./simulator\.js\?v=\d+"\)','import("./simulator.js?v=30")',t)
        p.write_text(t,encoding="utf-8")

manifest = {
  "name":"EGS Simulation Architecture",
  "version":"3.0-dev",
  "components":{
    "academy":"Interfaz y aprendizaje web",
    "simulation_core":"Estados, acciones, reglas, eventos, trazabilidad y AAR",
    "graphics_current":"Three.js prototipo",
    "graphics_target":"Unreal Engine / Pixel Streaming cuando exista GPU remota"
  },
  "flow":[
    "Usuario selecciona escenario",
    "Core inicializa estado",
    "Usuario ejecuta acción",
    "Core registra/evalúa y emite eventos",
    "Motor gráfico representa la acción",
    "AAR registra timeline",
    "Motor gráfico puede cambiar sin cambiar el Core"
  ],
  "doctrine_policy":{
    "validated_rules":"Pueden alimentar evaluación doctrinaria",
    "pending_rules":"Solo integración técnica; no presentarlas como doctrina definitiva"
  }
}
(CORE/"ARCHITECTURE_V3.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
shutil.copy2(CORE/"ARCHITECTURE_V3.json",WEB/"simulation_core"/"ARCHITECTURE_V3.json")

print("="*78)
print("EGS SIMULATION INTEGRATION v3 APLICADA")
print("="*78)
print("[OK] Simulation Core disponible para el navegador")
print("[OK] Acciones del simulador pasan por el Core")
print("[OK] Timeline de decisiones")
print("[OK] After Action Review visual + exportable")
print("[OK] Estado doctrinario validated/pending visible")
print("[OK] Nombre simplificado a SIMULADOR")
print("[OK] Preparado para reemplazar Three.js por Unreal")
print("[OK] Backup automático creado")
print()
print("Backup:", BACKUP)
print("NO hace git push.")
print()
print("Siguiente prueba local:")
print("python -m http.server 8000 -d web")
