const API_URL="https://egs-academia-bomberos-api.onrender.com";
let cache={academy:null,sources:null};let activeModule=null,activeTraining=[],activeMeta=null,current=0,correctCount=0,reviewed=0,log=[],timer=null,seconds=0,answered=false,selectedScenario=null;
const SIM_SCENARIOS=[
{id:"house",category:"structural",icon:"⌂",name:"Incendio en vivienda",difficulty:"Inicial–Intermedio",description:"Vivienda con fuego interior, humo, aberturas y víctima.",dispatch:"22:14 h. Humo visible en una vivienda. Posible persona en el interior.",facts:[["Tipo","Vivienda"],["Condición","Noche"],["Dotación","6 bomberos"],["Riesgo","Víctima posible"]],objectives:["Reconocer","Interpretar condiciones","Controlar aberturas","Aplicar agua","Buscar víctima"]},
{id:"apartment",category:"structural",icon:"▦",name:"Incendio en departamento",difficulty:"Intermedio",description:"Compartimentación, ventilación limitada y víctima.",dispatch:"03:38 h. Humo en departamento. Una persona sin localizar.",facts:[["Tipo","Departamento"],["Acceso","Pasillo"],["Ventilación","Limitada"],["Riesgo","Propagación"]],objectives:["Evaluar acceso","Controlar puerta","Enfriar","Ventilar con criterio","Buscar"]},
{id:"warehouse",category:"structural",icon:"▤",name:"Incendio en depósito",difficulty:"Avanzado",description:"Gran volumen, carga combustible y exposiciones.",dispatch:"17:26 h. Columna de humo desde depósito. Personal evacuando.",facts:[["Tipo","Depósito"],["Volumen","Grande"],["Carga","Combustible"],["Riesgo","Propagación"]],objectives:["Reconocer volumen","Proteger exposición","Seleccionar ataque","Controlar propagación"]},
{id:"vehicle_fire",category:"vehicle",icon:"▰",name:"Incendio vehicular",difficulty:"Intermedio",description:"Vehículo liviano con foco en sector motor.",dispatch:"19:02 h. Vehículo en vía pública con fuego visible.",facts:[["Tipo","Vehículo"],["Entorno","Vía pública"],["Foco","Motor"],["Tránsito","Presente"]],objectives:["Asegurar escena","Aislar","Desplegar línea","Enfriar"]},
{id:"vehicle_rescue",category:"vehicle",icon:"✚",name:"Rescate vehicular",difficulty:"Intermedio–Avanzado",description:"Colisión con víctima atrapada y vehículo inestable.",dispatch:"06:41 h. Colisión. Una persona atrapada, consciente.",facts:[["Evento","Colisión"],["Víctima","1"],["Vehículo","Inestable"],["Riesgo","Movimiento"]],objectives:["Evaluar","Aislar riesgos","Estabilizar","Crear acceso","Extricar"]},
{id:"fire_behavior",category:"behavior",icon:"≈",name:"Laboratorio de comportamiento del fuego",difficulty:"Formativo",description:"Cambios de humo, ventilación y transición térmica.",dispatch:"Laboratorio didáctico. Observá indicadores y modificá condiciones.",facts:[["Entorno","Compartimiento"],["Objetivo","Observación"],["Variables","Fuego / humo / aire"],["Modo","Didáctico"]],objectives:["Reconocer indicadores","Comparar ventilación","Visualizar rollover","Visualizar transición"]},
{id:"lines",category:"operations",icon:"↝",name:"Líneas y aplicación de agua",difficulty:"Formativo",description:"Despliegue y uso de línea de ataque con respuesta visual.",dispatch:"Práctica operacional. Prepará una línea y aplicá agua.",facts:[["Recurso","Línea"],["Objetivo","Despliegue"],["Agente","Agua"],["Modo","Práctica"]],objectives:["Desplegar","Seleccionar patrón","Abrir agua","Aplicar sobre foco"]},
{id:"era",category:"operations",icon:"◉",name:"Ingreso con ERA y búsqueda",difficulty:"Intermedio",description:"Ingreso con humo, control de equipo y búsqueda.",dispatch:"Ambiente con humo y visibilidad reducida. Posible víctima.",facts:[["EPP","ERA"],["Visibilidad","Reducida"],["Víctima","Posible"],["Riesgo","Consumo de aire"]],objectives:["Comprobar ERA","Ingresar","Mantener orientación","Buscar","Salir"]}
];
function showScreen(id){document.querySelectorAll(".screen").forEach(x=>x.classList.remove("active"));document.getElementById(id)?.classList.add("active");window.scrollTo(0,0)}
function goHome(){stopTimer();showScreen("home")}async function api(p){const r=await fetch(API_URL+p);if(!r.ok)throw new Error("HTTP "+r.status);return r.json()}function txt(v){return String(v??"")}
async function boot(){try{const s=await api("/");document.getElementById("apiStatus").textContent=txt(s.status||"EN LÍNEA").toUpperCase();[cache.academy,cache.sources]=await Promise.all([api("/academy/modules"),api("/sources")])}catch(e){document.getElementById("apiStatus").textContent="SERVICIO INICIANDO";console.warn(e)}renderSimCatalog()}
async function openAcademy(){if(!cache.academy)cache.academy=await api("/academy/modules");document.getElementById("academyGrid").innerHTML=cache.academy.modules.map((m,i)=>`<article class="tile clickable" onclick="openModule('${m.id}')"><span class="moduleStatus">MÓDULO ${String(i+1).padStart(2,"0")} · ${txt(m.area)}</span><h2>${txt(m.name)}</h2><p>${txt(m.description)}</p><strong>Explorar módulo →</strong></article>`).join("");showScreen("academy")}
async function openModule(id){activeModule=await api(`/academy/module/${id}`);activeModule._id=id;document.getElementById("moduleTitle").textContent=activeModule.metadata?.module_name||id;document.getElementById("moduleStatus").textContent=(activeModule.metadata?.status||"módulo").toUpperCase();document.getElementById("moduleSourceCount").textContent=`${(activeModule.metadata?.source_ids||[]).length} fuentes`;document.getElementById("moduleQuestionCount").textContent=`${(activeModule.training||[]).length} preguntas disponibles`;document.getElementById("moduleSections").innerHTML=(activeModule.sections||[]).map((s,i)=>`<article class="tile clickable" onclick="openSection(${i})"><span class="moduleStatus">FICHA</span><h2>${txt(s.title)}</h2><p>${txt(s.summary||s.concepts?.join(" · ")||"")}</p><strong>Abrir ficha →</strong></article>`).join("");const b=document.getElementById("moduleTrainingButton");b.style.display=(activeModule.training||[]).length?"inline-block":"none";b.onclick=()=>startTraining(id);showScreen("module")}
function openSection(i){const s=activeModule?.sections?.[i];if(!s)return;document.getElementById("moduleSections").innerHTML=`<article class="tile section-detail"><span class="moduleStatus">FICHA DE ESTUDIO</span><h2>${txt(s.title)}</h2><p style="font-size:1.08rem">${txt(s.summary||s.concepts?.join(" · ")||"Contenido en desarrollo.")}</p>${s.concepts?.length?`<h3>Conceptos clave</h3><ul>${s.concepts.map(c=>`<li>${txt(c)}</li>`).join("")}</ul>`:""}<h3>Fuente doctrinaria</h3><p>${txt(s.source_id||"Material académico")}</p><div class="heroActions"><button class="secondary" onclick="openModule('${activeModule._id}')">← Volver</button>${(activeModule.training||[]).length?`<button class="primary" onclick="startTraining('${activeModule._id}')">Practicar</button>`:""}</div></article>`}
async function showSources(){if(!cache.sources)cache.sources=await api("/sources");document.getElementById("sourceList").innerHTML=cache.sources.sources.map(s=>`<article class="sourceCard"><span class="moduleStatus">${txt(s.status||"FUENTE").toUpperCase()}</span><h3>${txt(s.title)}</h3><p>${txt(s.organization)}</p><p><strong>Rol:</strong> ${txt(s.role)}</p></article>`).join("");showScreen("sources")}
async function searchContent(q){const box=document.getElementById("searchResults");q=q.trim().toLowerCase();if(q.length<2){box.innerHTML="";return}if(!cache.academy)cache.academy=await api("/academy/modules");let rs=[];for(const m of cache.academy.modules){if((m.name+" "+m.description+" "+m.area).toLowerCase().includes(q))rs.push({type:"Módulo",title:m.name,id:m.id,desc:m.description});try{const d=await api(`/academy/module/${m.id}`);for(const s of d.sections||[]){if((s.title+" "+(s.summary||"")).toLowerCase().includes(q))rs.push({type:"Tema",title:s.title,id:m.id,desc:m.name})}}catch(e){}}box.innerHTML=rs.slice(0,10).map(r=>`<article class="tile clickable" onclick="openModule('${r.id}')"><span class="moduleStatus">${r.type}</span><h3>${txt(r.title)}</h3><p>${txt(r.desc)}</p></article>`).join("")}
function renderSimCatalog(f="all"){const g=document.getElementById("simCatalogGrid");if(!g)return;g.innerHTML=SIM_SCENARIOS.filter(s=>f==="all"||s.category===f).map(s=>`<article class="simCard" onclick="selectScenario('${s.id}')"><div class="simIcon">${s.icon}</div><span class="simDifficulty">${s.difficulty}</span><h3>${s.name}</h3><p>${s.description}</p><strong>Ver despacho →</strong></article>`).join("")}
function filterSimCatalog(f,b){document.querySelectorAll(".chip").forEach(x=>x.classList.remove("active"));b.classList.add("active");renderSimCatalog(f)}function openSimulatorCatalog(){renderSimCatalog();showScreen("simCatalog")}
function selectScenario(id){selectedScenario=SIM_SCENARIOS.find(s=>s.id===id);document.getElementById("briefTitle").textContent=selectedScenario.name;document.getElementById("briefDescription").textContent=selectedScenario.dispatch;document.getElementById("briefFacts").innerHTML=selectedScenario.facts.map(x=>`<div class="briefFact"><span>${x[0]}</span><strong>${x[1]}</strong></div>`).join("");document.getElementById("briefObjectives").innerHTML=`<ul>${selectedScenario.objectives.map(x=>`<li>${x}</li>`).join("")}</ul>`;document.getElementById("launchScenarioBtn").onclick=()=>launchScenario(id);showScreen("simBrief")}
async function launchScenario(id){
selectedScenario=SIM_SCENARIOS.find(s=>s.id===id)||selectedScenario;
showScreen("simulator");
document.getElementById("simScenarioTitle").textContent=selectedScenario?.name||"SIMULADOR EGS";
startDidacticSimulator(id);
}

const EGS_DIDACTIC_SCENARIOS={
fire_behavior:{title:"Laboratorio del fuego",intro:"Observá, predecí, decidí y explicá. Las experiencias son conceptuales y no requieren reproducir prácticas peligrosas.",steps:[
{type:"EXPERIENCIA 01 · ENCENDEDOR",situation:"El instructor acciona un encendedor y aparece una llama estable.",question:"¿Qué componentes permiten que exista esta combustión?",options:[
["Combustible + comburente + calor",1,"Correcto. Los tres componentes están presentes.","El combustible aporta materia capaz de arder, el aire aporta comburente y la ignición suministra energía."],
["Humo + llama + combustible",0,"No corresponde al triángulo del fuego.","Humo y llama son manifestaciones o productos; no sustituyen al comburente y al calor."],
["Solamente combustible + oxígeno",0,"La respuesta está incompleta.","También se necesita energía suficiente para iniciar la combustión."]]},
{type:"EXPERIENCIA 02 · RETIRAR UN COMPONENTE",situation:"La llama continúa estable. Se interrumpe el suministro de combustible.",question:"¿Qué esperás que ocurra?",options:[
["La llama se extingue",1,"La combustión deja de sostenerse.","Eliminar uno de los componentes necesarios interrumpe el proceso."],
["La llama aumenta",0,"No ocurre eso.","Sin aporte de combustible la combustión no puede continuar."],
["No cambia nada",0,"La llama no puede mantenerse indefinidamente.","Relacioná la experiencia con el triángulo del fuego."]]},
{type:"EXPERIENCIA 03 · RECIPIENTE",situation:"Una pequeña llama controlada queda cubierta por un recipiente que limita el intercambio con el ambiente.",question:"¿Sobre qué componente actuamos principalmente?",options:[
["Comburente",1,"La disponibilidad de oxígeno queda limitada.","La experiencia representa conceptualmente la sofocación."],
["Combustible",0,"El combustible continúa presente.","La variable modificada principalmente es el intercambio de aire."],
["Temperatura solamente",0,"Puede variar después, pero no es la modificación principal.","Observá qué deja de renovarse al cubrir la llama."]]},
{type:"EXPERIENCIA 04 · CARTÓN",situation:"Analizamos cartón como combustible sólido expuesto a una fuente de calor.",question:"¿Qué proceso ayuda a explicar su participación en la combustión?",options:[
["Calentamiento y pirólisis/descomposición térmica",1,"El material recibe energía y libera productos combustibles.","En muchos sólidos, el calentamiento genera productos capaces de arder."],
["Debe convertirse siempre en líquido",0,"No es una condición general.","Los sólidos pueden descomponerse térmicamente sin fundirse completamente."],
["El color determina la ignición",0,"El color no explica el fenómeno.","Importan el material, la exposición térmica y las condiciones de combustión."]]},
{type:"EXPERIENCIA 05 · CALEFACTOR",situation:"Hay un calefactor funcionando y una cortina demasiado próxima. Todavía no existe incendio.",question:"¿Qué condición peligrosa identificás?",options:[
["Fuente de calor próxima a combustible",1,"Reconociste una condición previa a la ignición.","La prevención empieza antes de la llama: fuente térmica, combustible, distancia y exposición importan."],
["No existe riesgo porque no hay llama",0,"La ausencia de llama no elimina el peligro.","Una fuente de calor puede transferir energía suficiente para producir ignición."],
["El problema es solamente la ventilación",0,"No es la variable central.","La proximidad entre fuente térmica y combustible es el dato crítico."]]},
{type:"EXPERIENCIA 06 · ALCOHOL Y NAFTA",situation:"Comparamos conceptualmente líquidos combustibles. No realizamos una experiencia física con nafta.",question:"¿Qué aspecto debemos considerar especialmente?",options:[
["Formación y comportamiento de vapores",1,"Pasaste de observar el líquido a considerar la fase vapor.","Volatilidad, temperatura y mezcla vapor-aire son claves para comprender el riesgo."],
["Solamente el color",0,"No caracteriza adecuadamente el peligro.","Hay que analizar propiedades relacionadas con vaporización y combustión."],
["Solamente el peso del recipiente",0,"No explica la combustión.","Debemos comprender primero el combustible y sus vapores."]]},
{type:"TRANSFERENCIA DE CALOR",situation:"Un material todavía no toca la llama, pero recibe energía térmica desde una fuente cercana.",question:"¿Qué debemos analizar?",options:[
["Cómo se transfiere el calor hacia el combustible",1,"Identificaste el mecanismo que puede preparar el material para la ignición.","Conducción, convección y radiación explican distintas formas de transferencia térmica."],
["Solamente si aparece humo",0,"Puede existir calentamiento antes del humo.","La transferencia térmica puede comenzar antes de manifestaciones visibles."],
["Nada hasta que aparezca llama",0,"Eso impediría anticipar la evolución.","El análisis bomberil debe reconocer condiciones previas a la ignición."]]}
]},
house:{title:"Incendio en vivienda",intro:"Caso operativo progresivo. Cada decisión modifica la lectura del incidente.",steps:[
{type:"RECONOCIMIENTO",situation:"22:14 h. Arribás a una vivienda con humo visible y posible persona en el interior. Todavía no conocés el foco ni las condiciones internas.",question:"¿Qué hacés primero?",options:[
["Realizar reconocimiento exterior y obtener información",1,"Construís una lectura inicial antes de comprometer recursos.","El reconocimiento permite identificar riesgos, accesos, condiciones, exposiciones y posibles víctimas."],
["Ingresar inmediatamente",0,"Te comprometés en un ambiente todavía no evaluado.","La posible víctima aumenta la urgencia, pero no elimina la evaluación inicial y el control de riesgos."],
["Abrir todas las ventanas",0,"Modificás la ventilación sin comprender el incendio.","Las aberturas pueden cambiar el aporte de aire y el comportamiento del fuego."]]},
{type:"VENTILACIÓN",situation:"La puerta permanece cerrada y hay humo por una abertura existente. Proponen abrir otra ventana.",question:"¿Qué decisión es más adecuada?",options:[
["Evaluar y coordinar antes de modificar aberturas",1,"Mantenés control sobre una variable crítica.","La ventilación debe coordinarse con la estrategia de ataque y las condiciones observadas."],
["Abrir todo para sacar humo",0,"Podés aumentar el aire disponible.","Ventilar puede modificar intensamente la combustión."],
["Romper cualquier abertura",0,"La acción carece de coordinación.","Las aberturas forman parte de la dinámica del incendio."]]},
{type:"APLICACIÓN DE AGUA",situation:"La dotación está preparada y la línea disponible.",question:"¿Qué efecto térmico buscamos principalmente al aplicar agua?",options:[
["Absorber calor y reducir la energía del incendio",1,"Reducís la energía térmica del sistema.","El enfriamiento actúa sobre el componente calor."],
["Agregar oxígeno",0,"No es el objetivo.","El agua se utiliza principalmente por su capacidad de absorción térmica y mecanismos asociados."],
["Aumentar temperatura",0,"Agravarías las condiciones.","El objetivo es controlar y reducir energía."]]},
{type:"BÚSQUEDA",situation:"Existe información de una posible persona en el interior.",question:"¿Qué enfoque corresponde?",options:[
["Integrar búsqueda, control del incendio, orientación, ERA y seguridad",1,"Tratás el rescate como parte de una operación coordinada.","La búsqueda depende de condiciones, protección, orientación, comunicaciones y control del incendio."],
["Entrar sin ERA para avanzar rápido",0,"Exponés al personal.","Humo y atmósferas comprometidas requieren protección respiratoria adecuada."],
["Ignorar el incendio hasta terminar la búsqueda",0,"Separás problemas que se influyen mutuamente.","El incendio condiciona la supervivencia y la seguridad."]]}
]},
lines:{title:"Líneas y aplicación de agua",intro:"Resolvé el armado según la necesidad operativa.",steps:[
{type:"LÍNEA SIMPLE",situation:"Una única lanza será alimentada por mangas del mismo diámetro, sin derivaciones.",question:"¿Qué sistema corresponde?",options:[
["Simple",1,"Correcto.","Una línea simple mantiene un único diámetro y alimenta una única lanza."],["Mixta",0,"No corresponde.","La mixta utiliza una línea principal que alimenta secundarias mediante bifurcador."],["Combinada",0,"No corresponde.","La combinada cambia de diámetro mediante reductor."]]},
{type:"LÍNEA COMBINADA",situation:"Necesitás conducir por diámetro mayor y luego pasar a uno menor mediante reductor.",question:"¿Qué sistema corresponde?",options:[
["Combinada",1,"Correcto.","Combina dos diámetros mediante un reductor."],["Simple",0,"Mantendría el mismo diámetro.","Acá existe cambio de diámetro."],["Mixta",0,"La mixta implica derivación.","Acá la clave es el reductor."]]},
{type:"LÍNEA MIXTA",situation:"Una línea principal debe alimentar dos líneas secundarias.",question:"¿Qué sistema y elemento corresponden?",options:[
["Mixta + bifurcador",1,"Correcto.","La línea principal alimenta dos o más secundarias mediante bifurcador."],["Combinada + reductor",0,"No resuelve la derivación.","Necesitás distribuir el caudal."],["Simple + una lanza",0,"No satisface el ataque simultáneo.","La necesidad es ramificar."]]}
]},
era:{title:"Ingreso con ERA y búsqueda",intro:"Tomá decisiones sobre protección respiratoria y control del equipo.",steps:[
{type:"ATMÓSFERA",situation:"Debés ingresar a un ambiente con humo y visibilidad reducida.",question:"¿Qué riesgo asumís inicialmente?",options:[
["Atmósfera potencialmente peligrosa; corresponde protección respiratoria",1,"Priorizás protección antes del ingreso.","Humo, gases, temperatura y posible deficiencia de oxígeno comprometen la atmósfera."],["El humo solo molesta la visión",0,"Subestimás el riesgo.","También puede contener productos tóxicos y afectar el oxígeno."],["No hay riesgo si todavía se ve",0,"La visibilidad no determina seguridad atmosférica.","Una atmósfera puede ser peligrosa aun con cierta visibilidad."]]},
{type:"CONTROL PREVIO",situation:"Tenés el ERA colocado y la dotación lista.",question:"¿Qué corresponde antes del ingreso?",options:[
["Comprobar equipo, aire disponible y funcionamiento",1,"Reducís la posibilidad de descubrir una falla dentro.","Los controles esenciales se realizan antes de comprometerse."],["Revisarlo después de ingresar",0,"Trasladás un control crítico a una zona peligrosa.","Debe comprobarse previamente."],["Cerrar el cilindro para ahorrar aire",0,"Inutilizarías el suministro.","El sistema debe estar operativo."]]}
]}
};

let EGS_SIM={scenario:null,step:0,score:0,errors:0,decisions:[]};

function startDidacticSimulator(id){
let sc=EGS_DIDACTIC_SCENARIOS[id];
if(!sc){
sc={title:selectedScenario?.name||"Caso operativo",intro:selectedScenario?.dispatch||"Analizá el despacho.",steps:[
{type:"RECONOCIMIENTO",situation:selectedScenario?.dispatch||"Arribás a la escena.",question:"¿Cuál es el primer enfoque?",options:[
["Evaluar escena, riesgos, recursos y prioridades",1,"Comenzás con una lectura organizada.","Antes de una maniobra específica necesitás comprender condiciones, amenazas, recursos y objetivos."],
["Actuar sin evaluación",0,"Omitís información crítica.","La evaluación inicial orienta las prioridades."],
["Elegir una maniobra al azar",0,"No responde a una estrategia.","Las tácticas deben derivarse de las condiciones y objetivos."]]},
{type:"REEVALUACIÓN",situation:"La situación evoluciona después de tu primera decisión.",question:"¿Qué principio debe mantenerse?",options:[
["Reevaluar continuamente y adaptar el plan",1,"Mantenés conciencia situacional.","El incidente es dinámico y las decisiones deben actualizarse."],
["Mantener el plan aunque cambien las condiciones",0,"Un plan rígido puede quedar desactualizado.","La estrategia debe responder a la evolución."],
["Dejar de comunicar para trabajar rápido",0,"Perdés coordinación.","La comunicación es parte del control operacional."]]}
]};
}
EGS_SIM={scenario:sc,step:0,score:0,errors:0,decisions:[]};
renderDidacticStep();
}

function renderDidacticStep(){
const host=document.getElementById("simActions");if(!host)return;
const sc=EGS_SIM.scenario;
if(EGS_SIM.step>=sc.steps.length){finishDidacticSimulator();return}
const s=sc.steps[EGS_SIM.step];
host.innerHTML=`<div style="max-width:900px;margin:20px auto;padding:28px;border:1px solid #333;background:#0b0f12;color:#fff">
<div style="display:flex;justify-content:space-between;letter-spacing:2px;font-size:12px;opacity:.65"><span>${txt(s.type)}</span><span>${EGS_SIM.step+1}/${sc.steps.length}</span></div>
<h2>${txt(sc.title)}</h2>${EGS_SIM.step===0?`<p style="opacity:.75;line-height:1.6">${txt(sc.intro)}</p>`:""}
<div style="padding:20px;border-left:3px solid #fff;background:rgba(255,255,255,.04);margin:20px 0"><b>SITUACIÓN</b><p>${txt(s.situation)}</p></div>
<h3>${txt(s.question)}</h3>
${s.options.map((o,i)=>`<button class="actionBtn" style="display:block;width:100%;text-align:left;margin:10px 0;padding:16px" onclick="answerDidactic(${i})">${String.fromCharCode(65+i)} · ${txt(o[0])}</button>`).join("")}
</div>`;
}

function answerDidactic(i){
const s=EGS_SIM.scenario.steps[EGS_SIM.step],o=s.options[i],ok=!!o[1];
if(ok)EGS_SIM.score++;else EGS_SIM.errors++;
EGS_SIM.decisions.push({type:s.type,question:s.question,answer:o[0],correct:ok});
document.getElementById("simActions").innerHTML=`<div style="max-width:900px;margin:20px auto;padding:28px;border:1px solid #333;background:#0b0f12;color:#fff">
<div style="letter-spacing:2px;font-size:12px;opacity:.65">CONSECUENCIA</div>
<h2>${ok?"DECISIÓN ADECUADA":"DECISIÓN A REVISAR"}</h2>
<div style="padding:20px;background:rgba(255,255,255,.04);margin:20px 0"><p>${txt(o[2])}</p></div>
<h3>¿POR QUÉ?</h3><p style="line-height:1.7">${txt(o[3])}</p>
<button class="actionBtn" style="width:100%;margin-top:20px" onclick="nextDidacticStep()">${EGS_SIM.step+1>=EGS_SIM.scenario.steps.length?"VER AAR":"CONTINUAR →"}</button>
</div>`;
}

function nextDidacticStep(){EGS_SIM.step++;renderDidacticStep()}

function finishDidacticSimulator(){
const total=EGS_SIM.scenario.steps.length,pct=Math.round(EGS_SIM.score/Math.max(1,total)*100);
document.getElementById("simActions").innerHTML=`<div style="max-width:900px;margin:20px auto;padding:28px;border:1px solid #333;background:#0b0f12;color:#fff">
<div style="letter-spacing:3px;font-size:12px;opacity:.65">AFTER ACTION REVIEW · AAR</div>
<h2>${txt(EGS_SIM.scenario.title)}</h2><div style="font-size:56px;font-weight:800;margin:20px 0">${pct}%</div>
<p>Adecuadas: <b>${EGS_SIM.score}/${total}</b> · A revisar: <b>${EGS_SIM.errors}</b></p>
${EGS_SIM.decisions.map((d,i)=>`<div style="padding:14px 0;border-bottom:1px solid #333"><b>${i+1}. ${d.correct?"ADECUADA":"REVISAR"} · ${txt(d.type)}</b><p>${txt(d.question)}</p><small>Tu decisión: ${txt(d.answer)}</small></div>`).join("")}
<button class="actionBtn" style="width:100%;margin-top:20px" onclick="startDidacticSimulator('${selectedScenario?.id||"fire_behavior"}')">REPETIR CASO</button>
<button class="actionBtn" style="width:100%;margin-top:10px" onclick="openSimulatorCatalog()">VOLVER A ESCENARIOS</button></div>`;
}
function exitSimulation(){openSimulatorCatalog()}
function renderScenarioActions(id){const A={house:[["recognition","Reconocimiento 360°"],["open_access","Abrir acceso"],["open_window","Abrir ventana"],["cooling","Aplicar agua"],["search","Buscar víctima"]],apartment:[["recognition","Reconocimiento"],["control_door","Controlar puerta"],["cooling","Enfriar"],["open_window","Ventilar"],["search","Buscar"]],warehouse:[["recognition","Reconocimiento"],["protect","Proteger exposición"],["cooling","Ataque con agua"],["ventilate","Ventilar"]],vehicle_fire:[["recognition","Asegurar escena"],["isolate","Aislar"],["deploy_line","Desplegar línea"],["cooling","Aplicar agua"]],vehicle_rescue:[["recognition","Evaluar"],["isolate","Aislar riesgos"],["stabilize","Estabilizar"],["access","Crear acceso"],["extricate","Extricar"]],fire_behavior:[["observe","Observar"],["rollover","Rollover"],["ventilate","Aumentar ventilación"],["flashover","Transición térmica"]],lines:[["deploy_line","Desplegar línea"],["select_fog","Patrón niebla"],["select_straight","Chorro pleno"],["cooling","Abrir agua"]],era:[["era_check","Comprobar ERA"],["enter","Ingresar"],["search","Buscar"],["exit","Salir"]]};document.getElementById("simActions").innerHTML=(A[id]||A.house).map(a=>`<button class="actionBtn" onclick="simAction('${a[0]}')">${a[1]}</button>`).join("")}
async function startTraining(id){runTraining(await api(`/academy/module/${id}/training?shuffle=true`),id)}async function startIntegral(){runTraining(await api("/academy/integral?limit=20"),"integral")}
function runTraining(d,id){activeTraining=d.training||[];activeMeta=d.metadata||{};activeMeta._id=id;current=0;correctCount=0;reviewed=0;log=[];seconds=0;answered=false;document.getElementById("trainingTitle").textContent=activeMeta.module_name||"Evaluación integral";showScreen("training");renderStep();startTimer()}
function renderStep(){const q=activeTraining[current];if(!q){finishTraining();return}answered=false;document.getElementById("nextQuestionBtn").classList.add("hidden");document.getElementById("feedback").innerHTML="";document.getElementById("question").textContent=q.question;document.getElementById("stepCounter").textContent=`${current+1}/${activeTraining.length}`;document.getElementById("sourceBadge").textContent=q.source_id||"—";document.getElementById("reviewedCount").textContent=reviewed;const opts=(q.options||[]).slice().sort(()=>Math.random()-.5);document.getElementById("options").innerHTML=opts.map((o,i)=>`<button class="optionBtn" data-i="${i}">${txt(o.text)}</button>`).join("");document.querySelectorAll(".optionBtn").forEach(b=>b.onclick=()=>chooseAnswer(opts[Number(b.dataset.i)],b,opts))}
function chooseAnswer(o,b,opts){if(answered)return;answered=true;reviewed++;const ok=o.status==="correct";if(ok)correctCount++;document.querySelectorAll(".optionBtn").forEach(x=>x.disabled=true);b.classList.add(ok?"selectedCorrect":"selectedWrong");const expected=opts.find(x=>x.status==="correct"),q=activeTraining[current];log.push({n:current+1,question:q.question,answer:o.text,correct:ok,expected:expected?.text||"",source:q.source_id||"—"});document.getElementById("reviewedCount").textContent=reviewed;document.getElementById("feedback").innerHTML=`<div class="feedbackBox ${ok?"correct":""}"><strong>${ok?"Respuesta adecuada":"Respuesta a revisar"}</strong><div>${ok?"Coincide con la respuesta marcada como correcta en el material cargado.":`Respuesta esperada: ${txt(expected?.text||"—")}`}</div><div><b>Fuente:</b> ${txt(q.source_id||"—")}</div></div>`;document.getElementById("nextQuestionBtn").classList.remove("hidden")}
function nextQuestion(){current++;renderStep()}function startTimer(){stopTimer();timer=setInterval(()=>{seconds++;document.getElementById("time").textContent=`${String(Math.floor(seconds/60)).padStart(2,"0")}:${String(seconds%60).padStart(2,"0")}`},1000)}function stopTimer(){if(timer){clearInterval(timer);timer=null}}
function finishTraining(){stopTimer();const pct=Math.round(correctCount/Math.max(1,reviewed)*100);document.getElementById("finalScore").textContent=pct;document.getElementById("analysisSummary").innerHTML=`<p>Respuestas revisadas: <strong>${reviewed}</strong></p><p>Adecuadas: <strong>${correctCount}</strong></p><p>Este resultado no crea un perfil personal: sirve para decidir qué repasar.</p>`;document.getElementById("decisionLog").innerHTML=log.map(x=>`<div class="entry"><strong>${x.n}. ${x.correct?"Adecuada":"Revisar"}</strong><p>${txt(x.question)}</p><p>Tu respuesta: ${txt(x.answer)}</p>${x.correct?"":`<p>Esperada: ${txt(x.expected)}</p>`}<p>Fuente: ${txt(x.source)}</p></div>`).join("");showScreen("analysis")}
let egs3dModulePromise=null;async function loadEGS3D(){if(window.EGS3D)return window.EGS3D;if(egs3dModulePromise)return egs3dModulePromise;egs3dModulePromise=import("./simulator.js?v=30").then(()=>window.EGS3D);return egs3dModulePromise}async function setSimulatorQuality(v){(await loadEGS3D()).setQuality(v)}async function reset3DScenario(){(await loadEGS3D()).reset()}async function simAction(a){(await loadEGS3D()).action(a)}async function finish3DSimulation(){(await loadEGS3D()).finish()}
document.addEventListener("DOMContentLoaded",boot);