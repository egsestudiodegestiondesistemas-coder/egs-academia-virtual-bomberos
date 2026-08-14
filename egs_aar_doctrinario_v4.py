from pathlib import Path
import json, shutil, re
from datetime import datetime

ROOT = Path.cwd()
ALT = ROOT / '05 - Código Fuente' / 'egs-fire-academy'
if not (ROOT/'web').exists() and (ALT/'web').exists(): ROOT = ALT
WEB = ROOT/'web'
CORE = ROOT/'simulation_core'
if not WEB.exists(): raise SystemExit('ERROR: ejecutá este archivo dentro de egs-fire-academy.')
if not CORE.exists(): raise SystemExit('ERROR: no existe simulation_core.')

BACKUP = ROOT/'_backup_aar_doctrinario_v4'
BACKUP.mkdir(exist_ok=True)
stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
for rel in ['simulation-core-client.js','web/simulation-core-client.js','simulation_core/rules/pending/starter_rules.json','web/simulation_core/rules/pending/starter_rules.json','index.html','web/index.html','styles.css','web/styles.css']:
    p=ROOT/rel
    if p.exists(): shutil.copy2(p, BACKUP/f"{rel.replace('/','__')}.{stamp}.bak")

rules_path = CORE/'rules'/'pending'/'starter_rules.json'
rules = json.loads(rules_path.read_text(encoding='utf-8'))
defaults = {
 'open_door': {'why':'La apertura modifica el estado de una abertura y puede alterar la ventilación del compartimiento.','consequence':'El simulador registra cambio de abertura y cambio de flujo como evento técnico. La consecuencia táctica específica permanece pendiente de validación doctrinaria.','expected_action':'Evaluar condiciones del incendio y la coordinación operativa antes de modificar una abertura.','review_topic':'Ventilación, flujo de gases y comportamiento del fuego','severity':'review','corrective_message':'Revisá la lectura de condiciones y el fundamento doctrinario antes de repetir la maniobra.'},
 'open_nozzle': {'why':'La apertura de la lanza inicia la aplicación de agua.','consequence':'El simulador registra inicio de chorro. El efecto térmico y táctico exacto depende de la técnica, patrón, caudal, ubicación y condiciones del incendio.','expected_action':'Aplicar la técnica correspondiente al objetivo táctico y a la doctrina validada.','review_topic':'Aplicación de agua, patrón, caudal y objetivo táctico','severity':'review','corrective_message':'Revisá la técnica de aplicación de agua asociada al escenario.'},
 'era_entry': {'why':'El ingreso a una atmósfera potencialmente peligrosa requiere la condición previa de protección respiratoria correspondiente.','consequence':'El simulador registra el ingreso. Los criterios completos de seguridad y secuencia quedan sujetos a la doctrina validada.','expected_action':'Comprobar el ERA y cumplir la secuencia de ingreso definida por la fuente doctrinaria aplicable.','review_topic':'ERA, chequeo previo, ingreso y seguridad','severity':'review','corrective_message':'Revisá el procedimiento de chequeo e ingreso con ERA antes de repetir.'}
}
for r in rules:
    action=(r.get('trigger') or {}).get('user_action')
    r.setdefault('learning',{})
    for k,v in defaults.get(action,{}).items(): r['learning'].setdefault(k,v)
    r['learning'].setdefault('doctrine_note','Contenido pedagógico de integración. La corrección operativa definitiva requiere fuente validada.')
rules_path.write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding='utf-8')
web_rules=WEB/'simulation_core'/'rules'/'pending'/'starter_rules.json'
web_rules.parent.mkdir(parents=True,exist_ok=True)
web_rules.write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding='utf-8')

for rel in ['simulation-core-client.js','web/simulation-core-client.js']:
    p=ROOT/rel
    if not p.exists(): continue
    t=p.read_text(encoding='utf-8')
    old='feedback,\n      source\n    };'
    new='feedback,\n      source,\n      learning: rule && rule.learning ? this.clone(rule.learning) : {why:"Acción registrada por el Simulation Core.",consequence:"La consecuencia doctrinaria específica todavía no está validada para esta acción.",expected_action:"Revisar la fuente correspondiente antes de considerar una conducta correcta.",review_topic:"Tema pendiente de vinculación",severity:"unscored",corrective_message:"Esta acción todavía no tiene devolución doctrinaria validada.",doctrine_note:"Contenido pendiente de validación."}\n    };'
    if old in t: t=t.replace(old,new)
    start=t.find('const rows=(aar.timeline||[]).map((x,i)=>')
    if start!=-1:
        end=t.find(').join(\"\");',start)
        if end!=-1:
            end += len(').join(\"\");')
            block = '''const rows=(aar.timeline||[]).map((x,i)=>{
      const actionName=HUMAN_ACTION[x.action]||x.action;
      const events=(x.visual_events||[]).map(v=>HUMAN_EVENT[v]||v).join(' / ');
      const learning=x.learning||{};
      const validated=x.source&&x.source.validation_status==='validated';
      const badge=validated ? 'VALIDADA' : 'PENDIENTE DE VALIDACIÓN';
      const cls=validated ? 'aarValidated' : 'aarPending';
      return '<div class=\"aarEntry '+cls+'\">'+
        '<div><strong>'+String(i+1).padStart(2,'0')+' - '+this.escape(actionName)+'</strong><span>'+x.t+'s</span></div>'+
        '<p><b>Qué hiciste:</b> '+this.escape(actionName)+'</p>'+
        '<p><b>Qué ocurrió en el simulador:</b> '+this.escape(events||'Interacción registrada')+'</p>'+
        '<p><b>Por qué importa:</b> '+this.escape(learning.why||x.feedback||'Sin explicación cargada.')+'</p>'+
        '<p><b>Consecuencia:</b> '+this.escape(learning.consequence||'Pendiente de validación doctrinaria.')+'</p>'+
        '<p><b>Qué deberías revisar:</b> '+this.escape(learning.expected_action||'Revisar la fuente asociada.')+'</p>'+
        '<p><b>Concepto para repasar:</b> '+this.escape(learning.review_topic||'Sin tema vinculado.')+'</p>'+
        '<p><b>Fuente:</b> '+this.escape((x.source&&x.source.source_id)||'PENDING')+'</p>'+
        '<small>'+badge+'</small>'+
      '</div>';
    }).join('');'''
            t=t[:start]+block+t[end:]
    t=t.replace('Las reglas pendientes sirven para integración técnica y no deben interpretarse como doctrina validada.','El análisis diferencia reglas validadas de reglas pendientes. Las pendientes no deben interpretarse como conducta operativa definitiva.')
    t=t.replace('<button class=\"secondary\" onclick=\"window.EGSCore.downloadAAR()\">EXPORTAR AAR</button>','')
    p.write_text(t,encoding='utf-8')

css_extra='\n/* ===== EGS AAR DOCTRINARIO v4 ===== */\n.aarEntry p{line-height:1.55}\n.aarEntry b{color:#e2e7eb}\n.aarValidated{border-left:3px solid #72d6a1;padding-left:14px}\n.aarPending{border-left:3px solid #d9a45c;padding-left:14px}\n.aarValidated small{color:#72d6a1}\n.aarPending small{color:#d9a45c}\n'
for rel in ['styles.css','web/styles.css']:
    p=ROOT/rel
    if p.exists():
        t=p.read_text(encoding='utf-8')
        if 'EGS AAR DOCTRINARIO v4' not in t: t+=css_extra
        p.write_text(t,encoding='utf-8')

for rel in ['index.html','web/index.html']:
    p=ROOT/rel
    if p.exists():
        t=p.read_text(encoding='utf-8')
        t=re.sub(r'simulation-core-client\\.js\\?v=\\d+','simulation-core-client.js?v=42',t)
        t=re.sub(r'styles\\.css\\?v=\\d+','styles.css?v=42',t)
        p.write_text(t,encoding='utf-8')

print('='*78)
print('EGS AAR DOCTRINARIO v4 APLICADO')
print('='*78)
print('[OK] Debriefing por acción')
print('[OK] Qué hiciste / qué ocurrió / por qué importa')
print('[OK] Consecuencia y forma de revisión')
print('[OK] Concepto para repasar')
print('[OK] Fuente y estado de validación')
print('[OK] Botón EXPORTAR AAR eliminado')
print('[OK] Cache actualizado a v42')
print('[OK] Backup automático creado')
print('IMPORTANTE: las reglas PENDING no se presentan como conducta definitiva.')
print('Backup:',BACKUP)
print('NO hace git push.')