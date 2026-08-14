from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path.cwd()
if not (ROOT / "web").exists() and (ROOT / "05 - Código Fuente" / "egs-fire-academy" / "web").exists():
    ROOT = ROOT / "05 - Código Fuente" / "egs-fire-academy"

WEB = ROOT / "web"
if not WEB.exists():
    raise SystemExit("ERROR: ejecutá este archivo dentro de egs-fire-academy.")

BACKUP = ROOT / "_backup_experience_v2"
BACKUP.mkdir(exist_ok=True)

INDEX = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#090b0e">
<title>EGS | Academia Virtual de Bomberos</title>
<link rel="stylesheet" href="styles.css?v=20">
</head>
<body>
<header class="topbar">
  <button class="brandButton" onclick="goHome()">
    <span class="brand">EGS | ACADEMIA VIRTUAL DE BOMBEROS</span>
    <span class="subtitle">Formación · Evaluación · Simulación operacional</span>
  </button>
  <nav class="topnav">
    <button onclick="openAcademy()">Aprender</button>
    <button onclick="startIntegral()">Evaluarme</button>
    <button onclick="openSimulatorCatalog()">Entrenar 3D</button>
    <button onclick="showSources()">Biblioteca</button>
  </nav>
  <div class="status" id="apiStatus">CONECTANDO</div>
</header>

<main>
<section id="home" class="screen active">
  <div class="hero">
    <div>
      <p class="eyebrow">CENTRO DE ENTRENAMIENTO BOMBERIL</p>
      <h1>Formación que se estudia.<br>Decisiones que se entrenan.</h1>
      <p class="lead">Aprendé doctrina, comprobá conocimientos y entrená decisiones operativas en escenarios 3D.</p>
      <div class="heroActions">
        <button class="primary" onclick="openAcademy()">EMPEZAR A APRENDER</button>
        <button class="secondary" onclick="openSimulatorCatalog()">ENTRAR AL SIMULADOR 3D</button>
      </div>
      <p class="microcopy">No necesitás crear una cuenta. Elegí un camino y empezá.</p>
    </div>
    <div class="heroVisual">
      <div class="heroGlow"></div><div class="heroBuilding"></div>
      <div class="heroFire f1"></div><div class="heroFire f2"></div>
      <div class="heroSmoke s1"></div><div class="heroSmoke s2"></div>
      <div class="heroBadge">ENTRENAMIENTO INTERACTIVO</div>
    </div>
  </div>

  <section class="pathSection">
    <p class="eyebrow">¿QUÉ QUERÉS HACER?</p>
    <h2>Elegí tu experiencia</h2>
    <div class="pathGrid">
      <article class="pathCard" onclick="openAcademy()"><span>01 · APRENDER</span><h3>Comprender antes de actuar</h3><p>Módulos, fichas y fuentes doctrinarias.</p><strong>Explorar Academia →</strong></article>
      <article class="pathCard" onclick="startIntegral()"><span>02 · EVALUARME</span><h3>Comprobar lo que sabés</h3><p>Preguntas, revisión y respuesta esperada según la fuente cargada.</p><strong>Iniciar evaluación →</strong></article>
      <article class="pathCard featured" onclick="openSimulatorCatalog()"><span>03 · ENTRENAR EN 3D</span><h3>Decidir y ver consecuencias</h3><p>Escenarios vivos con fuego, humo, víctimas y operaciones.</p><strong>Ver escenarios →</strong></article>
      <article class="pathCard" onclick="showSources()"><span>04 · PROFUNDIZAR</span><h3>Ir a las fuentes</h3><p>Biblioteca y trazabilidad doctrinaria.</p><strong>Abrir biblioteca →</strong></article>
    </div>
  </section>

  <section class="discoverSection">
    <p class="eyebrow">DESCUBRÍ CONTENIDO</p><h2>Buscá un tema y entrá directo</h2>
    <div class="searchBox"><input id="globalSearch" placeholder="Ej.: flashover, línea simple, ERA, rescate..." oninput="searchContent(this.value)"></div>
    <div id="searchResults" class="grid compactGrid"></div>
  </section>
</section>

<section id="academy" class="screen">
  <button class="back" onclick="goHome()">← Inicio</button><p class="eyebrow">APRENDER</p><h1>Academia</h1>
  <p class="sectionLead">Elegí un módulo. Cada tema conecta conocimiento, práctica y fuente.</p>
  <div id="academyGrid" class="grid"></div>
</section>

<section id="module" class="screen">
  <button class="back" onclick="openAcademy()">← Academia</button><p class="eyebrow" id="moduleStatus">MÓDULO</p><h1 id="moduleTitle">Módulo</h1>
  <div class="moduleBar"><span id="moduleSourceCount">0 fuentes</span><span id="moduleQuestionCount">0 preguntas</span></div>
  <div id="moduleSections" class="grid"></div><div class="moduleActions"><button id="moduleTrainingButton" class="primary">PRACTICAR ESTE MÓDULO</button></div>
</section>

<section id="sources" class="screen">
  <button class="back" onclick="goHome()">← Inicio</button><p class="eyebrow">PROFUNDIZAR</p><h1>Biblioteca doctrinaria</h1>
  <p class="sectionLead">Cada contenido debe poder rastrearse hasta su fuente.</p><div id="sourceList" class="grid"></div>
</section>

<section id="simCatalog" class="screen">
  <button class="back" onclick="goHome()">← Inicio</button><p class="eyebrow">ENTRENAR EN 3D</p><h1>Simulador operacional</h1>
  <p class="sectionLead">Elegí un escenario. Primero recibís el despacho y los objetivos.</p>
  <div class="simCategoryBar">
    <button class="chip active" onclick="filterSimCatalog('all',this)">Todos</button>
    <button class="chip" onclick="filterSimCatalog('structural',this)">Estructural</button>
    <button class="chip" onclick="filterSimCatalog('vehicle',this)">Vehicular</button>
    <button class="chip" onclick="filterSimCatalog('operations',this)">Operaciones</button>
    <button class="chip" onclick="filterSimCatalog('behavior',this)">Comportamiento</button>
  </div>
  <div id="simCatalogGrid" class="simCatalogGrid"></div>
</section>

<section id="simBrief" class="screen">
  <button class="back" onclick="openSimulatorCatalog()">← Escenarios</button>
  <div class="briefLayout">
    <div><p class="eyebrow">DESPACHO OPERACIONAL</p><h1 id="briefTitle">Escenario</h1><p id="briefDescription" class="briefText"></p><div id="briefFacts" class="briefFacts"></div></div>
    <aside class="briefCard"><span class="panelLabel">OBJETIVOS</span><div id="briefObjectives"></div><button class="primary full" id="launchScenarioBtn">COMENZAR INTERVENCIÓN</button></aside>
  </div>
</section>

<section id="simulator" class="screen simulatorScreen">
  <div class="simTop">
    <div><button class="back" onclick="exitSimulation()">← Salir</button><p class="eyebrow">SIMULACIÓN EN VIVO</p><h1 id="simScenarioTitle">Escenario</h1></div>
    <div class="simTopActions"><select id="qualitySelect" onchange="setSimulatorQuality(this.value)"><option value="baja">Baja</option><option value="media" selected>Media</option><option value="alta">Alta</option></select><button class="secondary" onclick="reset3DScenario()">REINICIAR</button></div>
  </div>
  <div class="simShell">
    <div class="simViewportWrap">
      <div id="sim3d"></div>
      <div class="simHUD topLeft"><span>TIEMPO</span><strong id="simClock">00:00</strong></div>
      <div class="simHUD topRight"><span>OBJETIVO</span><strong id="simObjective">Evaluar escena</strong></div>
      <div class="simHUD bottomLeft"><span>ESTADO</span><strong id="simCondition">Activo</strong></div><div class="crosshair">+</div>
    </div>
    <aside class="simPanel">
      <div class="panelSection telemetryPanel"><span class="panelLabel">CONDICIONES</span><div class="meterRow"><span>Temperatura</span><strong id="simTemp">—</strong></div><div class="meterRow"><span>Humo</span><strong id="simSmoke">—</strong></div><div class="meterRow"><span>Visibilidad</span><strong id="simVisibility">—</strong></div><div class="meterRow"><span>Oxígeno</span><strong id="simOxygen">—</strong></div></div>
      <div class="panelSection"><span class="panelLabel">DECISIONES Y RECURSOS</span><div id="simActions"></div></div>
      <div class="panelSection"><span class="panelLabel">REGISTRO EN VIVO</span><div id="simLog" class="simLog"></div></div>
      <button class="primary full" onclick="finish3DSimulation()">FINALIZAR Y ANALIZAR</button>
    </aside>
  </div>
  <p class="simNotice">Simulación educativa basada en reglas y visualización 3D. No reemplaza entrenamiento práctico ni constituye CFD certificado.</p>
</section>

<section id="training" class="screen">
  <button class="back" onclick="goHome()">← Salir</button>
  <div class="trainingHead"><div><p class="eyebrow">EVALUACIÓN ACTIVA</p><h1 id="trainingTitle">Evaluación</h1></div><div class="questionProgress" id="stepCounter">1/1</div></div>
  <div class="trainingLayout">
    <div class="knowledgePanel"><div class="questionMeta"><span>FUENTE</span><strong id="sourceBadge">—</strong></div><h2 id="question">Cargando...</h2><div id="options"></div><div id="feedback"></div><button id="nextQuestionBtn" class="primary full hidden" onclick="nextQuestion()">SIGUIENTE PREGUNTA</button></div>
    <aside class="evaluationSide"><span class="panelLabel">CÓMO FUNCIONA</span><p>Respondé y revisá la respuesta esperada y la fuente antes de continuar.</p><div class="sessionMetric"><span>Tiempo</span><strong id="time">00:00</strong></div><div class="sessionMetric"><span>Revisadas</span><strong id="reviewedCount">0</strong></div><button class="finish" onclick="finishTraining()">Finalizar ahora</button></aside>
  </div>
</section>

<section id="analysis" class="screen">
  <p class="eyebrow">ANÁLISIS POSTERIOR</p><h1>Qué pasó y qué conviene repasar</h1>
  <div class="analysisTop"><div class="finalScore"><strong id="finalScore">0</strong><span>%</span></div><div id="analysisSummary"></div></div>
  <div id="decisionLog" class="report"></div><div class="heroActions"><button class="primary" onclick="openAcademy()">VOLVER A LA ACADEMIA</button><button class="secondary" onclick="startIntegral()">NUEVA EVALUACIÓN</button></div>
</section>
</main>

<footer><div><strong>EGS | Estudio de Gestión de Sistemas</strong><span>Academia Virtual de Bomberos</span></div><div class="credit"><span>Desarrollado por</span><strong>Téc. Sup. en Gestión Ambiental Yamila Vocos</strong><span>San Francisco, Córdoba · Argentina</span></div><div class="right"><span>Experience 2.0 · 2026</span><span>Doctrina versionada y sujeta a revisión</span></div></footer>

<script src="app.js?v=20"></script>
<script type="module" src="simulator.js?v=20"></script>
</body></html>"""

STYLES = r"""*{box-sizing:border-box}:root{--bg:#080a0d;--panel:#101419;--line:#2a3037;--text:#f4f6f8;--muted:#9ba4ad;--accent:#f26b38;--good:#72d6a1}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 70% 0,#151a20 0,#080a0d 38%);color:var(--text);font-family:Arial,Helvetica,sans-serif}.topbar{min-height:76px;padding:12px 5vw;display:flex;gap:24px;justify-content:space-between;align-items:center;border-bottom:1px solid #242a31;background:rgba(10,13,17,.94);position:sticky;top:0;z-index:50}.brandButton{background:none;border:0;color:inherit;text-align:left;cursor:pointer}.brand{display:block;font-weight:800;letter-spacing:1.6px;font-size:17px}.subtitle{display:block;color:#808a94;font-size:11px;margin-top:5px}.status,.eyebrow,.panelLabel{color:var(--accent);letter-spacing:1.7px;font-size:10px;font-weight:800}.topnav{display:flex;gap:4px}.topnav button{background:transparent;color:#aeb5bd;border:0;padding:10px 12px;cursor:pointer;border-radius:8px}.topnav button:hover{color:#fff;background:#171c22}.screen{display:none;padding:46px 7vw 80px;min-height:calc(100vh - 150px)}.screen.active{display:block}h1{font-size:clamp(42px,6vw,78px);line-height:.98;margin:12px 0 22px;letter-spacing:-2px}h2{font-size:clamp(26px,3vw,40px)}h3{font-size:22px}.lead,.sectionLead{color:#abb4bd;font-size:17px;max-width:800px;line-height:1.7}.microcopy{color:#6f7983;font-size:12px}.hero{display:grid;grid-template-columns:1.2fr .8fr;gap:48px;align-items:center;min-height:68vh}.heroActions{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0}.primary,.secondary{padding:14px 18px;font-weight:800;cursor:pointer;border-radius:7px}.primary{background:var(--accent);color:#0a0d10;border:1px solid var(--accent)}.secondary{background:#151a20;color:#fff;border:1px solid #343b44}.heroVisual{position:relative;height:430px;border:1px solid #29313a;background:linear-gradient(160deg,#141a20,#090c10);overflow:hidden;border-radius:16px}.heroGlow{position:absolute;width:300px;height:300px;border-radius:50%;background:rgba(242,107,56,.18);filter:blur(60px);right:-50px;bottom:-70px}.heroBuilding{position:absolute;width:62%;height:45%;left:18%;bottom:0;background:#242a31;clip-path:polygon(0 28%,50% 0,100% 28%,100% 100%,0 100%)}.heroFire{position:absolute;bottom:18%;width:28px;height:70px;background:linear-gradient(#ffd16b,#ff6a00,#7a1b00);border-radius:50%;animation:flicker .8s infinite alternate}.f1{left:55%}.f2{left:62%;height:48px}.heroSmoke{position:absolute;width:110px;height:110px;border-radius:50%;background:rgba(76,81,86,.3);filter:blur(16px);animation:drift 5s infinite linear}.s1{left:50%;top:20%}.s2{left:62%;top:7%}.heroBadge{position:absolute;left:18px;bottom:18px;font-size:10px;letter-spacing:1.5px;color:#c9d0d6}.pathSection,.discoverSection{margin-top:70px}.pathGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:28px}.pathCard{min-height:270px;background:#101419;border:1px solid var(--line);padding:24px;position:relative;cursor:pointer;border-radius:12px;transition:.2s}.pathCard:hover{transform:translateY(-4px);border-color:#626d78}.pathCard.featured{border-color:rgba(242,107,56,.6)}.pathCard span{color:var(--accent);font-size:10px;letter-spacing:1px}.pathCard p{color:#929ba5;line-height:1.55}.pathCard strong{position:absolute;bottom:24px}.searchBox input{width:100%;padding:17px;background:#101419;border:1px solid #303740;color:white;font-size:16px;border-radius:9px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;margin:30px 0}.compactGrid{margin-top:16px}.tile,.sourceCard{background:#101419;border:1px solid var(--line);padding:24px;border-radius:10px}.tile.clickable{cursor:pointer;transition:.2s}.tile.clickable:hover{border-color:#66717d;transform:translateY(-2px)}.tile p,.sourceCard p{color:#9ca5ae;line-height:1.6}.moduleStatus{display:inline-block;color:var(--accent);font-size:10px;letter-spacing:1px}.moduleBar{display:flex;gap:18px;color:#8d959e;font-size:12px;margin:10px 0 25px}.moduleActions{margin-top:26px}.section-detail{grid-column:1/-1;max-width:900px}.back,.finish{background:transparent;color:#aeb5bd;border:0;padding:10px 0;cursor:pointer}.simCategoryBar{display:flex;gap:8px;flex-wrap:wrap;margin:25px 0}.chip{background:#14191f;color:#9da6af;border:1px solid #303740;padding:9px 13px;border-radius:999px;cursor:pointer}.chip.active,.chip:hover{border-color:var(--accent);color:white}.simCatalogGrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}.simCard{background:#101419;border:1px solid #2d343c;padding:23px;border-radius:12px;cursor:pointer;min-height:250px;position:relative}.simCard:hover{border-color:#6b7580}.simCard .simIcon{font-size:34px;margin-bottom:18px}.simCard p{color:#99a2ac;line-height:1.55}.simCard strong{position:absolute;bottom:22px}.simDifficulty{font-size:9px;color:#f5c16b;border:1px solid #4d4534;padding:5px 7px;border-radius:5px}.briefLayout{display:grid;grid-template-columns:1.5fr .7fr;gap:25px}.briefText{color:#abb4bd;font-size:18px;line-height:1.7}.briefFacts{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.briefFact{background:#11161b;border:1px solid #2c333b;padding:15px;border-radius:8px}.briefFact span{display:block;color:#7f8993;font-size:10px}.briefFact strong{display:block;margin-top:5px}.briefCard{background:#101419;border:1px solid #303740;padding:24px;border-radius:12px;position:sticky;top:96px}.briefCard ul{padding-left:18px;color:#b7bec5;line-height:1.7}.full{width:100%}.simTop{display:flex;justify-content:space-between;gap:20px;align-items:end}.simTop h1{font-size:40px}.simTopActions{display:flex;gap:8px}.simTopActions select{background:#151a20;color:white;border:1px solid #303740;padding:11px}.simShell{display:grid;grid-template-columns:minmax(0,1fr) 350px;gap:14px}.simViewportWrap{position:relative;min-height:650px;background:#050708;border:1px solid #292f36;overflow:hidden;border-radius:12px}.simViewportWrap #sim3d{position:absolute;inset:0}.simViewportWrap canvas{width:100%!important;height:100%!important;display:block}.simHUD{position:absolute;z-index:5;background:rgba(7,9,11,.8);border:1px solid rgba(255,255,255,.12);padding:9px 11px;border-radius:7px}.simHUD span{display:block;font-size:8px;color:#98a1aa}.simHUD strong{font-size:12px}.topLeft{left:12px;top:12px}.topRight{right:12px;top:12px}.bottomLeft{left:12px;bottom:12px}.crosshair{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);font-size:24px;color:rgba(255,255,255,.35)}.simPanel{background:#101419;border:1px solid #292f36;padding:16px;max-height:650px;overflow:auto;border-radius:12px}.panelSection{padding:5px 0 16px;border-bottom:1px solid #292f36;margin-bottom:14px}.meterRow{display:flex;justify-content:space-between;margin:11px 0;color:#9ca5ae}.meterRow strong{color:#fff}.actionBtn{width:100%;text-align:left;background:#171d23;color:#fff;border:1px solid #303740;padding:12px;margin:5px 0;cursor:pointer;border-radius:7px}.actionBtn:hover{border-color:var(--accent)}.actionBtn small{display:block;color:#808a94;margin-top:4px}.simLog{font-size:11px;color:#9ba4ad;max-height:170px;overflow:auto}.simLog div{padding:6px 0;border-bottom:1px solid #242a31}.simNotice{color:#69727c;font-size:10px}.trainingHead{display:flex;justify-content:space-between;align-items:end}.questionProgress{font-size:28px;font-weight:800}.trainingLayout{display:grid;grid-template-columns:minmax(0,1.35fr) 340px;gap:18px}.knowledgePanel,.evaluationSide{background:#101419;border:1px solid #292f36;border-radius:12px;padding:28px}.questionMeta span{display:block;color:#7f8993;font-size:9px}.questionMeta strong{color:var(--accent);font-size:11px}.knowledgePanel h2{font-size:30px}.optionBtn{display:block;width:100%;text-align:left;background:#171d23;color:white;border:1px solid #303740;padding:15px;margin:9px 0;cursor:pointer;border-radius:8px}.optionBtn.selectedCorrect{border-color:var(--good)}.optionBtn.selectedWrong{border-color:#e37a69}.feedbackBox{margin-top:18px;padding:18px;background:#0c1014;border-left:3px solid var(--accent);line-height:1.6}.feedbackBox.correct{border-color:var(--good)}.hidden{display:none!important}.sessionMetric{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #292f36}.report{max-width:1000px;background:#101419;border:1px solid #292f36;padding:26px;margin:28px 0;border-radius:10px}.entry{padding:17px 0;border-bottom:1px solid #292f36}.analysisTop{display:flex;gap:40px;align-items:center}.finalScore strong{font-size:86px}.finalScore span{font-size:28px;color:#8d959e}footer{display:grid;grid-template-columns:1fr 1fr 1fr;gap:25px;padding:22px 5vw;border-top:1px solid #23282e;background:#0b0e11;color:#69727c;font-size:10px}footer>div{display:flex;flex-direction:column;gap:5px}.credit{text-align:center}.right{text-align:right}@keyframes flicker{from{transform:scale(.9)}to{transform:scale(1.08)}}@keyframes drift{from{transform:translateY(25px);opacity:.1}to{transform:translate(35px,-80px) scale(1.4);opacity:0}}@media(max-width:1100px){.hero{grid-template-columns:1fr}.pathGrid{grid-template-columns:1fr 1fr}.briefLayout,.trainingLayout,.simShell{grid-template-columns:1fr}.briefCard{position:static}.simPanel{max-height:none}.topnav{display:none}footer{grid-template-columns:1fr}.credit,.right{text-align:left}}@media(max-width:680px){.topbar{min-height:64px;padding:10px 14px}.brand{font-size:13px}.subtitle{font-size:9px}.status{font-size:8px}.screen{padding:28px 14px 65px}h1{font-size:42px}.hero{min-height:auto;gap:24px}.heroVisual{height:230px}.pathGrid{grid-template-columns:1fr}.pathCard{min-height:210px}.briefFacts{grid-template-columns:1fr}.simulatorScreen{padding-left:0;padding-right:0}.simTop{padding:0 14px}.simViewportWrap{height:44vh;min-height:44vh;border-left:0;border-right:0;border-radius:0;position:sticky;top:64px;z-index:15}.simShell{gap:0}.simPanel{border-radius:0;border-left:0;border-right:0}.telemetryPanel{display:grid;grid-template-columns:1fr 1fr;gap:4px 16px}.telemetryPanel .panelLabel{grid-column:1/-1}.knowledgePanel,.evaluationSide{padding:18px}.heroActions{flex-direction:column}.heroActions button{width:100%}}"""

APP = r"""const API_URL="https://egs-academia-bomberos-api.onrender.com";
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
async function launchScenario(id){showScreen("simulator");document.getElementById("simScenarioTitle").textContent=selectedScenario.name;const e=await loadEGS3D();await e.init();e.loadScenario(id);renderScenarioActions(id);e.start()}
function exitSimulation(){window.EGS3D?.pause?.();openSimulatorCatalog()}
function renderScenarioActions(id){const A={house:[["recognition","Reconocimiento 360°"],["open_access","Abrir acceso"],["open_window","Abrir ventana"],["cooling","Aplicar agua"],["search","Buscar víctima"]],apartment:[["recognition","Reconocimiento"],["control_door","Controlar puerta"],["cooling","Enfriar"],["open_window","Ventilar"],["search","Buscar"]],warehouse:[["recognition","Reconocimiento"],["protect","Proteger exposición"],["cooling","Ataque con agua"],["ventilate","Ventilar"]],vehicle_fire:[["recognition","Asegurar escena"],["isolate","Aislar"],["deploy_line","Desplegar línea"],["cooling","Aplicar agua"]],vehicle_rescue:[["recognition","Evaluar"],["isolate","Aislar riesgos"],["stabilize","Estabilizar"],["access","Crear acceso"],["extricate","Extricar"]],fire_behavior:[["observe","Observar"],["rollover","Rollover"],["ventilate","Aumentar ventilación"],["flashover","Transición térmica"]],lines:[["deploy_line","Desplegar línea"],["select_fog","Patrón niebla"],["select_straight","Chorro pleno"],["cooling","Abrir agua"]],era:[["era_check","Comprobar ERA"],["enter","Ingresar"],["search","Buscar"],["exit","Salir"]]};document.getElementById("simActions").innerHTML=(A[id]||A.house).map(a=>`<button class="actionBtn" onclick="simAction('${a[0]}')">${a[1]}</button>`).join("")}
async function startTraining(id){runTraining(await api(`/academy/module/${id}/training?shuffle=true`),id)}async function startIntegral(){runTraining(await api("/academy/integral?limit=20"),"integral")}
function runTraining(d,id){activeTraining=d.training||[];activeMeta=d.metadata||{};activeMeta._id=id;current=0;correctCount=0;reviewed=0;log=[];seconds=0;answered=false;document.getElementById("trainingTitle").textContent=activeMeta.module_name||"Evaluación integral";showScreen("training");renderStep();startTimer()}
function renderStep(){const q=activeTraining[current];if(!q){finishTraining();return}answered=false;document.getElementById("nextQuestionBtn").classList.add("hidden");document.getElementById("feedback").innerHTML="";document.getElementById("question").textContent=q.question;document.getElementById("stepCounter").textContent=`${current+1}/${activeTraining.length}`;document.getElementById("sourceBadge").textContent=q.source_id||"—";document.getElementById("reviewedCount").textContent=reviewed;const opts=(q.options||[]).slice().sort(()=>Math.random()-.5);document.getElementById("options").innerHTML=opts.map((o,i)=>`<button class="optionBtn" data-i="${i}">${txt(o.text)}</button>`).join("");document.querySelectorAll(".optionBtn").forEach(b=>b.onclick=()=>chooseAnswer(opts[Number(b.dataset.i)],b,opts))}
function chooseAnswer(o,b,opts){if(answered)return;answered=true;reviewed++;const ok=o.status==="correct";if(ok)correctCount++;document.querySelectorAll(".optionBtn").forEach(x=>x.disabled=true);b.classList.add(ok?"selectedCorrect":"selectedWrong");const expected=opts.find(x=>x.status==="correct"),q=activeTraining[current];log.push({n:current+1,question:q.question,answer:o.text,correct:ok,expected:expected?.text||"",source:q.source_id||"—"});document.getElementById("reviewedCount").textContent=reviewed;document.getElementById("feedback").innerHTML=`<div class="feedbackBox ${ok?"correct":""}"><strong>${ok?"Respuesta adecuada":"Respuesta a revisar"}</strong><div>${ok?"Coincide con la respuesta marcada como correcta en el material cargado.":`Respuesta esperada: ${txt(expected?.text||"—")}`}</div><div><b>Fuente:</b> ${txt(q.source_id||"—")}</div></div>`;document.getElementById("nextQuestionBtn").classList.remove("hidden")}
function nextQuestion(){current++;renderStep()}function startTimer(){stopTimer();timer=setInterval(()=>{seconds++;document.getElementById("time").textContent=`${String(Math.floor(seconds/60)).padStart(2,"0")}:${String(seconds%60).padStart(2,"0")}`},1000)}function stopTimer(){if(timer){clearInterval(timer);timer=null}}
function finishTraining(){stopTimer();const pct=Math.round(correctCount/Math.max(1,reviewed)*100);document.getElementById("finalScore").textContent=pct;document.getElementById("analysisSummary").innerHTML=`<p>Respuestas revisadas: <strong>${reviewed}</strong></p><p>Adecuadas: <strong>${correctCount}</strong></p><p>Este resultado no crea un perfil personal: sirve para decidir qué repasar.</p>`;document.getElementById("decisionLog").innerHTML=log.map(x=>`<div class="entry"><strong>${x.n}. ${x.correct?"Adecuada":"Revisar"}</strong><p>${txt(x.question)}</p><p>Tu respuesta: ${txt(x.answer)}</p>${x.correct?"":`<p>Esperada: ${txt(x.expected)}</p>`}<p>Fuente: ${txt(x.source)}</p></div>`).join("");showScreen("analysis")}
let egs3dModulePromise=null;async function loadEGS3D(){if(window.EGS3D)return window.EGS3D;if(egs3dModulePromise)return egs3dModulePromise;egs3dModulePromise=import("./simulator.js?v=20").then(()=>window.EGS3D);return egs3dModulePromise}async function setSimulatorQuality(v){(await loadEGS3D()).setQuality(v)}async function reset3DScenario(){(await loadEGS3D()).reset()}async function simAction(a){(await loadEGS3D()).action(a)}async function finish3DSimulation(){(await loadEGS3D()).finish()}
document.addEventListener("DOMContentLoaded",boot);"""

SIM = r"""console.log("EGS 3D Experience 2.0");import * as THREE from "./three.module.js";
let scene,camera,renderer,container,running=false,last=0,elapsed=0,quality="media",activeScenario="house",objects={},fires=[],smoke=[],water=[],state={},cameraReset=null;
const Q={baja:{n:60,p:1},media:{n:120,p:1.1},alta:{n:210,p:1.25}},I={house:[120,35,72,20.2,"Reconocer"],apartment:[155,48,58,19.5,"Evaluar acceso"],warehouse:[190,42,64,19.9,"Reconocer volumen"],vehicle_fire:[230,45,65,20.4,"Asegurar escena"],vehicle_rescue:[28,0,100,20.9,"Evaluar y estabilizar"],fire_behavior:[180,55,48,18.8,"Observar indicadores"],lines:[65,12,90,20.8,"Desplegar línea"],era:[95,68,25,18.9,"Comprobar ERA"]};
function e(id){return document.getElementById(id)}function m(c){return new THREE.MeshStandardMaterial({color:c,roughness:.85})}function box(p,s,pos,ma){const x=new THREE.Mesh(new THREE.BoxGeometry(...s),ma);x.position.set(...pos);x.castShadow=true;x.receiveShadow=true;p.add(x);return x}function fmt(s){return `${String(Math.floor(s/60)).padStart(2,"0")}:${String(Math.floor(s%60)).padStart(2,"0")}`}
function log(t){const b=e("simLog");if(!b)return;const d=document.createElement("div");d.textContent=`${fmt(elapsed)} · ${t}`;b.prepend(d)}
function hud(){const a=I[activeScenario]||I.house;if(e("simClock"))e("simClock").textContent=fmt(elapsed);if(e("simTemp"))e("simTemp").textContent=`${Math.round(state.t)} °C`;if(e("simSmoke"))e("simSmoke").textContent=`${Math.round(state.s)} %`;if(e("simVisibility"))e("simVisibility").textContent=`${Math.round(state.v)} %`;if(e("simOxygen"))e("simOxygen").textContent=`${state.o.toFixed(1)} %`;if(e("simObjective"))e("simObjective").textContent=state.obj;if(e("simCondition"))e("simCondition").textContent=state.c||"Activo"}
function clear(){fires=[];smoke=[];water=[];objects={};while(scene.children.length)scene.remove(scene.children[0]);scene.background=new THREE.Color(0x0e1419);scene.fog=new THREE.FogExp2(0x252b30,.018);scene.add(new THREE.HemisphereLight(0xd5e8f5,0x211a16,1.9));const l=new THREE.DirectionalLight(0xffe6c5,2.5);l.position.set(-8,14,10);scene.add(l);const g=new THREE.Mesh(new THREE.BoxGeometry(40,.25,34),m(0x263027));g.position.y=-.25;scene.add(g)}
function fire(pos,s=1){const g=new THREE.Group();g.position.set(...pos);g.scale.setScalar(s);scene.add(g);fires.push(g);for(let i=0;i<10;i++){const f=new THREE.Mesh(new THREE.ConeGeometry(.12+Math.random()*.1,.45+Math.random()*.5,7),new THREE.MeshStandardMaterial({color:i%2?0xff6200:0xffc044,emissive:0xff3500,emissiveIntensity:2,transparent:true,opacity:.9}));f.position.set((Math.random()-.5),Math.random()*.3,(Math.random()-.5)*.7);g.add(f)}const l=new THREE.PointLight(0xff5818,6,7);l.position.y=1;g.add(l)}
function smokeTex(){const c=document.createElement("canvas");c.width=c.height=64;const x=c.getContext("2d"),g=x.createRadialGradient(32,32,2,32,32,30);g.addColorStop(0,"rgba(70,70,70,.5)");g.addColorStop(1,"rgba(20,20,20,0)");x.fillStyle=g;x.fillRect(0,0,64,64);return new THREE.CanvasTexture(c)}
function cloud(o,sp){const t=smokeTex();for(let i=0;i<Q[quality].n;i++){const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t,transparent:true,opacity:.2,depthWrite:false}));s.position.set(o[0]+Math.random()*sp[0],o[1]+Math.random()*sp[1],o[2]+Math.random()*sp[2]);const k=.6+Math.random()*1.3;s.scale.set(k,k,k);s.userData.dy=.06+Math.random()*.08;scene.add(s);smoke.push(s)}}
function victim(pos){const v=new THREE.Mesh(new THREE.CapsuleGeometry(.28,.9,4,8),m(0x202428));v.position.set(...pos);v.rotation.z=Math.PI/2;scene.add(v);objects.victim=v}
function house(){const g=new THREE.Group();scene.add(g),w=m(0xc5b49f),f=m(0x45494d),wood=m(0x573923);box(g,[12,.25,9],[0,0,0],f);box(g,[12,3.2,.22],[0,1.7,-4.4],w);box(g,[.22,3.2,9],[-5.9,1.7,0],w);box(g,[.22,3.2,9],[5.9,1.7,0],w);box(g,[4,3.2,.22],[-4,1.7,4.4],w);box(g,[4,3.2,.22],[4,1.7,4.4],w);objects.door=box(g,[1.2,2.3,.12],[1.2,1.2,4.28],wood);objects.window=box(g,[2,1.3,.08],[-2.1,1.9,4.28],new THREE.MeshStandardMaterial({color:0x78a9ba,transparent:true,opacity:.42}));box(g,[.22,3,5],[.8,1.6,-1.2],w);return g}
function car(color=0x8e2525){const g=new THREE.Group();scene.add(g);objects.vehicle=box(g,[4.2,.9,1.9],[0,.85,0],m(color));box(g,[2.3,.8,1.75],[-.2,1.55,0],m(color));return g}
function build(){clear();const a=I[activeScenario]||I.house;state={t:a[0],s:a[1],v:a[2],o:a[3],obj:a[4],c:"Activo"};elapsed=0;if(activeScenario==="house"){house();victim([-3.5,.6,-2.7]);fire([3.7,.3,-3.1]);cloud([2,1.2,-4],[4,2.2,5])}if(activeScenario==="apartment"){house();victim([-3,.6,-2]);fire([-2.4,.35,1.3]);cloud([-4,1.2,-1],[5,2.2,6])}if(activeScenario==="warehouse"){const g=new THREE.Group();scene.add(g);box(g,[18,.25,12],[0,0,0],m(0x414448));for(let x=-6;x<=6;x+=4)for(let z=-3;z<=2;z+=2.5)box(g,[2.2,2.2,1.4],[x,1.1,z],m(0x6b4d2e));fire([4,.3,-2],1.2);cloud([0,1.4,-5],[14,3,7])}if(activeScenario==="vehicle_fire"){car();fire([1.5,.5,0]);cloud([.8,1.2,-1.5],[4,2.5,3])}if(activeScenario==="vehicle_rescue"){car(0x2f5d8c);objects.vehicle.rotation.y=.18;victim([-.3,1.1,0])}if(activeScenario==="fire_behavior"){house();fire([0,.3,-2.4]);cloud([-4,1.2,-3],[8,2.5,6])}if(activeScenario==="lines"){objects.hose=[];for(let i=0;i<7;i++){const h=new THREE.Mesh(new THREE.CylinderGeometry(.09,.09,1.5,10),m(0xe7c24d));h.rotation.z=Math.PI/2;h.position.set(-4+i*1.4,.12,0);h.visible=false;scene.add(h);objects.hose.push(h)}fire([7,.3,-1.8],.8)}if(activeScenario==="era"){house();victim([3,.6,-2]);cloud([-5,.8,-4],[10,2.6,8]);objects.era=false}hud();log("Escenario preparado")}
function resize(){const r=container.getBoundingClientRect();renderer.setSize(Math.max(300,r.width),Math.max(260,r.height),false);camera.aspect=Math.max(300,r.width)/Math.max(260,r.height);camera.updateProjectionMatrix()}
function controls(){let d=false,lx=0,ly=0,y=.72,p=.48,r=20;const u=()=>{camera.position.set(r*Math.cos(p)*Math.cos(y),1.2+r*Math.sin(p),r*Math.cos(p)*Math.sin(y));camera.lookAt(0,1.2,0)};renderer.domElement.onpointerdown=x=>{d=true;lx=x.clientX;ly=x.clientY};renderer.domElement.onpointerup=()=>d=false;renderer.domElement.onpointermove=x=>{if(!d)return;y-=(x.clientX-lx)*.008;p=Math.max(.14,Math.min(1.25,p-(x.clientY-ly)*.006));lx=x.clientX;ly=x.clientY;u()};renderer.domElement.onwheel=x=>{x.preventDefault();r=Math.max(5,Math.min(34,r+x.deltaY*.012));u()};u();cameraReset=u}
function waterBurst(){for(let i=0;i<70;i++){const p=new THREE.Mesh(new THREE.SphereGeometry(.025,5,4),new THREE.MeshBasicMaterial({color:0x78c8ff}));p.position.set(0,1.2,2.5);p.userData.v=new THREE.Vector3((Math.random()-.5)*.5,.1+Math.random()*.2,-4-Math.random()*2);scene.add(p);water.push(p)}}
async function init(){container=e("sim3d");if(renderer){resize();return}scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(58,1,.1,100);renderer=new THREE.WebGLRenderer({antialias:true});renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setPixelRatio(Math.min(devicePixelRatio,Q[quality].p));container.innerHTML="";container.appendChild(renderer.domElement);controls();build();resize();window.addEventListener("resize",resize);animate(performance.now())}
function animate(n){requestAnimationFrame(animate);const dt=Math.min(.05,last?(n-last)/1000:0);last=n;if(running){elapsed+=dt;fires.forEach(g=>g.children.forEach((f,i)=>{if(f.isMesh)f.scale.y=.8+Math.sin(n*.012+i)*.18}));smoke.forEach(s=>{s.position.y+=s.userData.dy*dt;if(s.position.y>4.8)s.position.y=1.1});for(let i=water.length-1;i>=0;i--){const p=water[i];p.position.addScaledVector(p.userData.v,dt);p.userData.v.y-=1.2*dt;if(p.position.y<-.2){scene.remove(p);water.splice(i,1)}}if(!["vehicle_rescue","lines"].includes(activeScenario)){state.t=Math.min(850,state.t+.25*dt);state.s=Math.min(100,state.s+.05*dt);state.v=Math.max(3,state.v-.035*dt);state.o=Math.max(12,state.o-.003*dt)}hud()}renderer.render(scene,camera)}
function start(){running=true;last=performance.now()}function pause(){running=false}function loadScenario(id){activeScenario=I[id]?id:"house";build();running=true}function setQuality(v){quality=Q[v]?v:"media";if(renderer){renderer.setPixelRatio(Math.min(devicePixelRatio,Q[quality].p));build();resize()}}function reset(){build();running=true}
function action(a){if(a==="recognition"||a==="observe"){state.obj="Interpretar condiciones";log("Reconocimiento realizado")}if(a==="open_access"){if(objects.door)objects.door.rotation.y=-1.4;state.t+=28;state.o=Math.min(20.9,state.o+.35);state.s=Math.max(0,state.s-5);state.obj="Reevaluar flujo";log("Acceso abierto")}if(a==="control_door"){if(objects.door)objects.door.rotation.y=-.2;state.obj="Mantener control";log("Puerta controlada")}if(a==="open_window"||a==="ventilate"){if(objects.window)objects.window.position.y=3;state.o=Math.min(20.9,state.o+.55);state.s=Math.max(0,state.s-10);state.t+=34;state.obj="Observar respuesta";log("Ventilación modificada")}if(a==="cooling"){waterBurst();state.t=Math.max(35,state.t-110);state.s=Math.max(0,state.s-6);fires.forEach(g=>g.scale.multiplyScalar(.62));state.obj="Reevaluar";log("Agua aplicada")}if(a==="search"){if(objects.victim)objects.victim.material.color.set(0xffd166);state.obj="Completar búsqueda";log("Búsqueda ejecutada")}if(a==="protect"){fires.forEach(g=>g.scale.multiplyScalar(.85));log("Exposición protegida")}if(a==="isolate"){state.c="Zona aislada";log("Riesgos aislados")}if(a==="deploy_line"){objects.hose?.forEach(x=>x.visible=true);state.obj="Aplicar agente";log("Línea desplegada")}if(a==="stabilize"){objects.stable=true;box(scene,[.6,.3,.8],[-1.6,.15,.8],m(0xe5a532));box(scene,[.6,.3,.8],[1.6,.15,.8],m(0xe5a532));state.c="Vehículo estabilizado";log("Vehículo estabilizado")}if(a==="access"){state.c=objects.stable?"Acceso creado":"Riesgo: sin estabilizar";log(state.c)}if(a==="extricate"){if(objects.victim){objects.victim.position.set(3,.6,2);objects.victim.material.color.set(0x6fd3a1)}state.c="Víctima extricada";log("Extricación ejecutada")}if(a==="rollover"){state.t=430;state.s=76;fires.forEach(g=>g.scale.set(1.9,.35,1.9));log("Rollover visualizado")}if(a==="flashover"){state.t=690;state.s=92;for(let i=0;i<5;i++)fire([-4+i*2,.25,-1+Math.random()*2],.8);state.c="Transición térmica";log("Transición térmica visualizada")}if(a==="select_fog"){state.c="Patrón: niebla";log("Patrón niebla")}if(a==="select_straight"){state.c="Patrón: chorro pleno";log("Chorro pleno")}if(a==="era_check"){objects.era=true;state.c="ERA comprobado";log("Chequeo ERA")}if(a==="enter"){state.c=objects.era?"Ingreso realizado":"Riesgo: ERA sin comprobar";log(state.c)}if(a==="exit"){state.c="Salida completada";cameraReset?.();log("Salida")}hud()}
function finish(){running=false;state.c="Finalizado";hud();alert(`Escenario finalizado · ${fmt(elapsed)}`)}window.EGS3D={init,start,pause,loadScenario,setQuality,reset,action,finish};"""

for rel, content in {
    "index.html": INDEX, "styles.css": STYLES, "app.js": APP, "simulator.js": SIM,
    "web/index.html": INDEX, "web/styles.css": STYLES, "web/app.js": APP, "web/simulator.js": SIM,
}.items():
    p = ROOT / rel
    if p.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(p, BACKUP / f"{rel.replace('/','__')}.{stamp}.bak")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("[OK]", rel)

print()
print("="*76)
print("EGS EXPERIENCE 2.0 APLICADA")
print("="*76)
print("[OK] Inicio rediseñado para experiencia")
print("[OK] Sin métricas personales en portada")
print("[OK] Evaluaciones con revisión antes de avanzar")
print("[OK] Catálogo multi-escenario")
print("[OK] 8 escenarios 3D")
print("[OK] Simulador móvil con visor persistente")
print("[OK] Acciones con respuesta visual y telemetría")
print("[OK] Copias raíz + web sincronizadas")
print("Backup:", BACKUP)
print()
print("Siguiente: reiniciar web y probar antes de hacer git push.")
