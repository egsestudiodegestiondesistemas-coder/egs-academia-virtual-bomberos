from pathlib import Path
import shutil, re
from datetime import datetime

ROOT = Path.cwd()
ALT = ROOT / '05 - Código Fuente' / 'egs-fire-academy'
if not (ROOT/'web').exists() and (ALT/'web').exists(): ROOT = ALT
WEB = ROOT/'web'
if not WEB.exists(): raise SystemExit('ERROR: ejecutá este archivo dentro de egs-fire-academy.')

BACKUP = ROOT/'_backup_aar_final_clean_v5'
BACKUP.mkdir(exist_ok=True)
stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
for rel in ['simulation-core-client.js','web/simulation-core-client.js','styles.css','web/styles.css','index.html','web/index.html']:
    p=ROOT/rel
    if p.exists(): shutil.copy2(p, BACKUP/f"{rel.replace('/','__')}.{stamp}.bak")

CLIENT = r'''(() => {
"use strict";
const CORE_BASE="./simulation_core";
const ACTION_MAP={recognition:"sizeup_360",observe:"read_smoke",open_access:"open_door",control_door:"control_door",open_window:"open_window",ventilate:"open_window",deploy_line:"deploy_simple_line",select_fog:"select_fog",select_straight:"select_straight",cooling:"open_nozzle",search:"search_primary",era_check:"era_check",enter:"era_entry",exit:"era_exit",isolate:"vehicle_isolate",stabilize:"vehicle_stabilize",access:"vehicle_access",extricate:"vehicle_extricate",protect:"direct_attack",rollover:"read_smoke",flashover:"read_smoke"};
const HUMAN_ACTION={sizeup_360:"Realizaste un reconocimiento 360°",read_smoke:"Interpretaste las condiciones de humo",control_door:"Controlaste una puerta",open_door:"Abriste una puerta",open_window:"Abriste una ventana",deploy_simple_line:"Desplegaste una línea simple",select_fog:"Seleccionaste patrón niebla",select_straight:"Seleccionaste chorro pleno",open_nozzle:"Abriste la lanza y aplicaste agua",direct_attack:"Realizaste un ataque directo",search_primary:"Iniciaste una búsqueda primaria",era_check:"Realizaste el chequeo del ERA",era_entry:"Ingresaste con ERA",era_exit:"Saliste del área con ERA",vehicle_isolate:"Aislaste los riesgos del vehículo",vehicle_stabilize:"Estabilizaste el vehículo",vehicle_access:"Creaste un acceso al vehículo",vehicle_extricate:"Extrajiste a la víctima"};
const HUMAN_EVENT={camera_or_scene_sizeup:"Se registró el reconocimiento de la escena.",smoke_observation:"Se registró la lectura de humo.",door_control:"La puerta quedó bajo control.",door_open:"La puerta quedó abierta.",airflow_change:"Se modificó el flujo de aire del escenario.",window_open:"La ventana quedó abierta.",hose_deploy:"La línea quedó desplegada.",nozzle_fog:"Se seleccionó patrón niebla.",nozzle_straight:"Se seleccionó chorro pleno.",water_stream_start:"Comenzó la aplicación de agua.",search_mode:"Se inició el modo de búsqueda.",era_check:"Se registró el chequeo del ERA.",crew_enter:"Se registró el ingreso del personal.",crew_exit:"Se registró la salida del personal.",hazard_isolation:"Se registró el aislamiento de riesgos.",vehicle_stabilize:"Se registró la estabilización del vehículo.",vehicle_access:"Se registró la creación de acceso.",victim_extricate:"Se registró la extricación."};
const LEARNING={
open_door:{why:"Modificar una abertura puede cambiar las condiciones de ventilación y el flujo dentro del escenario.",consequence:"Se registró apertura de puerta y cambio de flujo. La consecuencia táctica exacta depende de las condiciones del incendio y requiere una regla doctrinaria validada.",expected:"Evaluá las condiciones del incendio y la coordinación operativa antes de modificar una abertura.",topic:"Ventilación, flujo de gases y comportamiento del fuego"},
open_nozzle:{why:"Abrir la lanza inicia la aplicación de agua y modifica las condiciones del escenario.",consequence:"Se registró el inicio de la aplicación de agua. El efecto real depende de técnica, patrón, caudal, ubicación y objetivo táctico.",expected:"Aplicá la técnica correspondiente al objetivo táctico y a la doctrina validada.",topic:"Aplicación de agua, patrón, caudal y objetivo táctico"},
era_check:{why:"El chequeo previo del ERA confirma que el equipo se encuentra listo para utilizarse.",consequence:"Se registró el chequeo del equipo.",expected:"Realizá el control completo según el procedimiento del equipo y la doctrina cargada.",topic:"ERA: inspección y chequeo previo"},
era_entry:{why:"El ingreso con ERA forma parte de una secuencia de seguridad y protección respiratoria.",consequence:"Se registró el ingreso. La secuencia completa debe ajustarse al procedimiento validado.",expected:"Comprobá el ERA y cumplí la secuencia de ingreso indicada por la fuente aplicable.",topic:"ERA, ingreso y seguridad"},
era_exit:{why:"La salida forma parte del control de exposición, autonomía y seguridad del personal.",consequence:"Se registró la salida del área.",expected:"Realizá la salida de acuerdo con la secuencia y criterios de seguridad validados.",topic:"ERA: salida y control de autonomía"},
search_primary:{why:"La búsqueda primaria tiene como objetivo localizar víctimas con prioridad operativa.",consequence:"Se registró el inicio de una búsqueda.",expected:"Aplicá el procedimiento de búsqueda indicado por la doctrina y mantené orientación y seguridad.",topic:"Búsqueda primaria y rescate"}
};
let lastActionName="",lastActionAt=0;
const EGSCore={ready:false,initialState:null,pendingRules:[],currentScenario:null,timeline:[],startedAt:null,
async load(){try{const [s,p]=await Promise.all([fetch(`${CORE_BASE}/engine/initial_state.json`).then(r=>r.json()),fetch(`${CORE_BASE}/rules/pending/starter_rules.json`).then(r=>r.json())]);this.initialState=s;this.pendingRules=p;this.ready=true;console.log('EGS Simulation Core v5 conectado')}catch(e){console.warn(e)}},
reset(id){this.currentScenario=id||'structural_house_master';this.timeline=[];this.startedAt=new Date()},
findRule(a){return this.pendingRules.find(r=>r&&r.trigger&&r.trigger.user_action===a)||null},
evaluate(uiAction){const now=Date.now();if(uiAction===lastActionName&&now-lastActionAt<900)return null;lastActionName=uiAction;lastActionAt=now;const action=ACTION_MAP[uiAction]||uiAction;const rule=this.findRule(action);let visual=[];let source={source_id:'PENDING',validation_status:'pending'};if(rule){visual=(rule.effects||[]).map(x=>x.visual_event).filter(Boolean);source=rule.source||source}const fallback={sizeup_360:['camera_or_scene_sizeup'],read_smoke:['smoke_observation'],control_door:['door_control'],open_door:['door_open','airflow_change'],open_window:['window_open','airflow_change'],deploy_simple_line:['hose_deploy'],select_fog:['nozzle_fog'],select_straight:['nozzle_straight'],open_nozzle:['water_stream_start'],search_primary:['search_mode'],era_check:['era_check'],era_entry:['crew_enter'],era_exit:['crew_exit'],vehicle_isolate:['hazard_isolation'],vehicle_stabilize:['vehicle_stabilize'],vehicle_access:['vehicle_access'],vehicle_extricate:['victim_extricate']};if(!visual.length)visual=fallback[action]||[];const learning=LEARNING[action]||{why:'La acción quedó registrada dentro de la secuencia de intervención.',consequence:'La consecuencia doctrinaria específica todavía no está validada para esta acción.',expected:'Revisá el procedimiento correspondiente en el material de estudio.',topic:'Tema pendiente de vinculación doctrinaria'};const entry={t:Math.max(0,Math.round((Date.now()-(this.startedAt?this.startedAt.getTime():Date.now()))/1000)),action,visual_events:visual,source,learning};this.timeline.push(entry);return entry},
finish(){const d=this.startedAt?Math.round((new Date()-this.startedAt)/1000):0;this.showAAR({duration_seconds:d,timeline:this.timeline})},
showAAR(aar){let o=document.getElementById('egsAAROverlay');if(!o){o=document.createElement('div');o.id='egsAAROverlay';o.className='aarOverlay';document.body.appendChild(o)}const total=aar.timeline.length;const validated=aar.timeline.filter(x=>x.source&&x.source.validation_status==='validated').length;const rows=aar.timeline.map((x,i)=>{const a=HUMAN_ACTION[x.action]||x.action;const ev=(x.visual_events||[]).map(v=>HUMAN_EVENT[v]||v).join(' ');const ok=x.source&&x.source.validation_status==='validated';return `<article class="debriefCard ${ok?'validated':'pending'}"><div class="debriefHead"><span>PASO ${String(i+1).padStart(2,'0')}</span><span>${x.t}s</span></div><h3>${this.escape(a)}</h3><p><strong>Qué ocurrió:</strong> ${this.escape(ev||'La acción quedó registrada.')}</p><p><strong>Por qué importa:</strong> ${this.escape(x.learning.why)}</p><p><strong>Consecuencia:</strong> ${this.escape(x.learning.consequence)}</p><p><strong>Qué deberías revisar:</strong> ${this.escape(x.learning.expected)}</p><p><strong>Concepto para repasar:</strong> ${this.escape(x.learning.topic)}</p><div class="debriefFooter"><span>${this.escape((x.source&&x.source.source_id)||'PENDING')}</span><span>${ok?'VALIDADO':'PENDIENTE DE VALIDACIÓN'}</span></div></article>`}).join('');o.innerHTML=`<div class="aarModal cleanAAR"><button class="aarClose" onclick="document.getElementById('egsAAROverlay').classList.remove('open')">X</button><p class="eyebrow">ANÁLISIS POSTERIOR</p><h2>Análisis de tu intervención</h2><p class="aarIntro">Revisá qué hiciste, qué produjo cada decisión y qué concepto conviene repasar antes de repetir el escenario.</p><div class="aarSummary"><div><span>Duración</span><strong>${aar.duration_seconds}s</strong></div><div><span>Decisiones</span><strong>${total}</strong></div><div><span>Validadas</span><strong>${validated}</strong></div><div><span>Pendientes</span><strong>${total-validated}</strong></div></div><div class="aarWarning">Las acciones pendientes todavía no tienen una regla doctrinaria validada y no deben interpretarse como conducta operativa definitiva.</div><div class="debriefList">${rows||'<p>No se registraron acciones.</p>'}</div><div class="heroActions"><button class="primary" onclick="document.getElementById('egsAAROverlay').classList.remove('open')">VOLVER</button></div></div>`;o.classList.add('open')},
escape(v){return String(v??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
};
window.EGSCore=EGSCore;
document.addEventListener('DOMContentLoaded',async()=>{await EGSCore.load();const L=window.launchScenario;if(typeof L==='function')window.launchScenario=async function(id){EGSCore.reset(id);return L.apply(this,arguments)};const A=window.simAction;if(typeof A==='function')window.simAction=async function(action){const e=EGSCore.evaluate(action);if(!e)return;return A.apply(this,arguments)};const F=window.finish3DSimulation;if(typeof F==='function')window.finish3DSimulation=async function(){const r=await F.apply(this,arguments);EGSCore.finish();return r};const R=window.reset3DScenario;if(typeof R==='function')window.reset3DScenario=async function(){EGSCore.reset(EGSCore.currentScenario);return R.apply(this,arguments)}});
})();'''

for rel in ['simulation-core-client.js','web/simulation-core-client.js']:
    (ROOT/rel).write_text(CLIENT,encoding='utf-8')

CSS = r'''
/* ===== EGS CLEAN AAR v5 ===== */
.aarOverlay{position:fixed;inset:0;background:rgba(0,0,0,.82);z-index:9999;display:none;align-items:center;justify-content:center;padding:18px}
.aarOverlay.open{display:flex}
.cleanAAR{position:relative;width:min(920px,100%);max-height:92vh;overflow:auto;background:#101419;border:1px solid #343c45;border-radius:14px;padding:28px}
.aarClose{position:absolute;right:16px;top:12px;background:none;border:0;color:#fff;font-size:22px;cursor:pointer}
.cleanAAR h2{font-size:34px;margin:8px 0 10px}
.aarIntro{color:#aab2ba;line-height:1.6;margin-bottom:18px}
.aarSummary{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:18px 0}
.aarSummary div{background:#171d23;border:1px solid #2f3740;padding:14px;border-radius:8px}
.aarSummary span{display:block;color:#7f8993;font-size:9px;text-transform:uppercase;letter-spacing:1px}
.aarSummary strong{display:block;font-size:24px;margin-top:5px}
.aarWarning{padding:12px 14px;background:#1b1711;border:1px solid #59462c;color:#d9b77c;border-radius:8px;font-size:12px;margin-bottom:16px;line-height:1.5}
.debriefList{display:grid;gap:12px}
.debriefCard{background:#151a20;border:1px solid #303740;border-radius:10px;padding:18px}
.debriefCard.validated{border-left:4px solid #72d6a1}
.debriefCard.pending{border-left:4px solid #d9a45c}
.debriefHead{display:flex;justify-content:space-between;color:#8f99a3;font-size:10px;letter-spacing:1px}
.debriefCard h3{margin:10px 0 12px;font-size:21px}
.debriefCard p{color:#b6bec6;line-height:1.55;margin:8px 0}
.debriefCard strong{color:#eef1f3}
.debriefFooter{display:flex;justify-content:space-between;gap:10px;border-top:1px solid #2b3239;margin-top:14px;padding-top:10px;color:#8f99a3;font-size:10px}
@media(max-width:680px){.cleanAAR{padding:22px 14px}.aarSummary{grid-template-columns:1fr 1fr}.debriefFooter{flex-direction:column}}
'''

for rel in ['styles.css','web/styles.css']:
    p=ROOT/rel
    if p.exists():
        t=p.read_text(encoding='utf-8',errors='ignore')
        t=re.sub(r'/\* ===== EGS CLEAN AAR v5 ===== \*/.*','',t,flags=re.S)
        p.write_text(t+'\n'+CSS,encoding='utf-8')

for rel in ['index.html','web/index.html']:
    p=ROOT/rel
    if p.exists():
        t=p.read_text(encoding='utf-8',errors='ignore')
        if '<meta charset="UTF-8">' not in t and '<head>' in t: t=t.replace('<head>','<head>\n<meta charset="UTF-8">',1)
        t=re.sub(r'simulation-core-client\.js\?v=\d+','simulation-core-client.js?v=50',t)
        t=re.sub(r'styles\.css\?v=\d+','styles.css?v=50',t)
        p.write_text(t,encoding='utf-8')

print('='*78)
print('EGS AAR FINAL CLEAN v5 APLICADO')
print('='*78)
print('[OK] UTF-8 reforzado')
print('[OK] Vista AAR reemplazada completa')
print('[OK] Sin nombres técnicos en pantalla')
print('[OK] Debriefing claro por decisión')
print('[OK] Botón EXPORTAR eliminado')
print('[OK] Un solo botón VOLVER')
print('[OK] Cache actualizado a v50')
print('[OK] Backup automático creado')
print('Backup:',BACKUP)
print('NO hace git push.')