const API_URL = "https://egs-academia-bomberos-api.onrender.com";

let cache = {
    academy: null,
    sources: null
};

let activeModule = null;
let activeTraining = [];
let activeMeta = null;
let current = 0;
let correctCount = 0;
let reviewed = 0;
let log = [];
let timer = null;
let seconds = 0;
let answered = false;
let selectedScenario = null;


/* =========================================================
   CATÁLOGO GENERAL
   ========================================================= */

const SIM_SCENARIOS = [

    {
        id: "house",
        category: "structural",
        icon: "⌂",
        name: "Incendio en vivienda",
        difficulty: "Inicial–Intermedio",
        description: "Vivienda con fuego interior, humo, aberturas y posible víctima.",
        dispatch: "22:14 h. Humo visible en una vivienda. Posible persona en el interior.",
        facts: [
            ["Tipo", "Vivienda"],
            ["Condición", "Noche"],
            ["Dotación", "6 bomberos"],
            ["Riesgo", "Víctima posible"]
        ],
        objectives: [
            "Reconocer",
            "Interpretar condiciones",
            "Controlar aberturas",
            "Aplicar agua",
            "Buscar víctima"
        ]
    },

    {
        id: "apartment",
        category: "structural",
        icon: "▦",
        name: "Incendio en departamento",
        difficulty: "Intermedio",
        description: "Compartimentación, ventilación limitada y víctima.",
        dispatch: "03:38 h. Humo en departamento. Una persona sin localizar.",
        facts: [
            ["Tipo", "Departamento"],
            ["Acceso", "Pasillo"],
            ["Ventilación", "Limitada"],
            ["Riesgo", "Propagación"]
        ],
        objectives: [
            "Evaluar acceso",
            "Controlar puerta",
            "Enfriar",
            "Ventilar con criterio",
            "Buscar"
        ]
    },

    {
        id: "warehouse",
        category: "structural",
        icon: "▤",
        name: "Incendio en depósito",
        difficulty: "Avanzado",
        description: "Gran volumen, carga combustible y exposiciones.",
        dispatch: "17:26 h. Columna de humo desde depósito. Personal evacuando.",
        facts: [
            ["Tipo", "Depósito"],
            ["Volumen", "Grande"],
            ["Carga", "Combustible"],
            ["Riesgo", "Propagación"]
        ],
        objectives: [
            "Reconocer volumen",
            "Proteger exposición",
            "Seleccionar ataque",
            "Controlar propagación"
        ]
    },

    {
        id: "vehicle_fire",
        category: "vehicle",
        icon: "▰",
        name: "Incendio vehicular",
        difficulty: "Intermedio",
        description: "Vehículo liviano con foco en sector motor.",
        dispatch: "19:02 h. Vehículo en vía pública con fuego visible.",
        facts: [
            ["Tipo", "Vehículo"],
            ["Entorno", "Vía pública"],
            ["Foco", "Motor"],
            ["Tránsito", "Presente"]
        ],
        objectives: [
            "Asegurar escena",
            "Aislar",
            "Desplegar línea",
            "Enfriar"
        ]
    },

    {
        id: "vehicle_rescue",
        category: "vehicle",
        icon: "✚",
        name: "Rescate vehicular",
        difficulty: "Intermedio–Avanzado",
        description: "Colisión con víctima atrapada y vehículo inestable.",
        dispatch: "06:41 h. Colisión. Una persona atrapada, consciente.",
        facts: [
            ["Evento", "Colisión"],
            ["Víctima", "1"],
            ["Vehículo", "Inestable"],
            ["Riesgo", "Movimiento"]
        ],
        objectives: [
            "Evaluar",
            "Aislar riesgos",
            "Estabilizar",
            "Crear acceso",
            "Extricar"
        ]
    },

    {
        id: "fire_behavior",
        category: "behavior",
        icon: "≈",
        name: "Laboratorio de comportamiento del fuego",
        difficulty: "Formativo",
        description: "Experiencias sobre combustible, comburente, calor, humo y ventilación.",
        dispatch: "Laboratorio didáctico. Observá, predecí, decidí y explicá qué ocurre.",
        facts: [
            ["Entorno", "Laboratorio didáctico"],
            ["Objetivo", "Comprender el fuego"],
            ["Variables", "Combustible / oxígeno / calor"],
            ["Modo", "Interactivo"]
        ],
        objectives: [
            "Reconocer el triángulo del fuego",
            "Identificar qué componente se elimina",
            "Relacionar ventilación y combustión",
            "Interpretar humo y temperatura",
            "Reconocer fenómenos térmicos"
        ]
    },

    {
        id: "lines",
        category: "operations",
        icon: "↝",
        name: "Líneas y aplicación de agua",
        difficulty: "Formativo",
        description: "Despliegue, selección y utilización de líneas de ataque.",
        dispatch: "Práctica operacional. Prepará una línea y tomá decisiones.",
        facts: [
            ["Recurso", "Línea"],
            ["Objetivo", "Despliegue"],
            ["Agente", "Agua"],
            ["Modo", "Práctica"]
        ],
        objectives: [
            "Desplegar",
            "Seleccionar configuración",
            "Aplicar agua",
            "Reevaluar"
        ]
    },

    {
        id: "era",
        category: "operations",
        icon: "◉",
        name: "Ingreso con ERA y búsqueda",
        difficulty: "Intermedio",
        description: "Ingreso con humo, control de equipo y búsqueda.",
        dispatch: "Ambiente con humo y visibilidad reducida. Posible víctima.",
        facts: [
            ["EPP", "ERA"],
            ["Visibilidad", "Reducida"],
            ["Víctima", "Posible"],
            ["Riesgo", "Consumo de aire"]
        ],
        objectives: [
            "Comprobar ERA",
            "Ingresar",
            "Mantener orientación",
            "Buscar",
            "Salir"
        ]
    }
];


/* =========================================================
   NAVEGACIÓN
   ========================================================= */

function showScreen(id) {
    document.querySelectorAll(".screen").forEach(x => {
        x.classList.remove("active");
    });

    document.getElementById(id)?.classList.add("active");
    window.scrollTo(0, 0);
}


function goHome() {
    stopTimer();
    showScreen("home");
}


async function api(path) {

    const response = await fetch(API_URL + path);

    if (!response.ok) {
        throw new Error("HTTP " + response.status);
    }

    return response.json();
}


function txt(value) {
    return String(value ?? "");
}


/* =========================================================
   INICIO
   ========================================================= */

async function boot() {

    try {

        const status = await api("/");

        const statusBox = document.getElementById("apiStatus");

        if (statusBox) {
            statusBox.textContent =
                txt(status.status || "EN LÍNEA").toUpperCase();
        }

        [cache.academy, cache.sources] = await Promise.all([
            api("/academy/modules"),
            api("/sources")
        ]);

    } catch (error) {

        const statusBox = document.getElementById("apiStatus");

        if (statusBox) {
            statusBox.textContent = "SERVICIO INICIANDO";
        }

        console.warn(error);
    }

    renderSimCatalog();
}


/* =========================================================
   ACADEMIA
   ========================================================= */

async function openAcademy() {

    if (!cache.academy) {
        cache.academy = await api("/academy/modules");
    }

    const grid = document.getElementById("academyGrid");

    grid.innerHTML = cache.academy.modules.map((m, i) => `

        <article
            class="tile clickable"
            onclick="openModule('${m.id}')"
        >

            <span class="moduleStatus">
                MÓDULO ${String(i + 1).padStart(2, "0")} · ${txt(m.area)}
            </span>

            <h2>${txt(m.name)}</h2>

            <p>${txt(m.description)}</p>

            <strong>Explorar módulo →</strong>

        </article>

    `).join("");

    showScreen("academy");
}


async function openModule(id) {

    activeModule = await api(`/academy/module/${id}`);
    activeModule._id = id;

    document.getElementById("moduleTitle").textContent =
        activeModule.metadata?.module_name || id;

    document.getElementById("moduleStatus").textContent =
        (activeModule.metadata?.status || "módulo").toUpperCase();

    document.getElementById("moduleSourceCount").textContent =
        `${(activeModule.metadata?.source_ids || []).length} fuentes`;

    document.getElementById("moduleQuestionCount").textContent =
        `${(activeModule.training || []).length} preguntas disponibles`;

    document.getElementById("moduleSections").innerHTML =
        (activeModule.sections || []).map((section, i) => `

            <article
                class="tile clickable"
                onclick="openSection(${i})"
            >

                <span class="moduleStatus">FICHA</span>

                <h2>${txt(section.title)}</h2>

                <p>
                    ${txt(
                        section.summary ||
                        section.concepts?.join(" · ") ||
                        ""
                    )}
                </p>

                <strong>Abrir ficha →</strong>

            </article>

        `).join("");

    const button =
        document.getElementById("moduleTrainingButton");

    button.style.display =
        (activeModule.training || []).length
            ? "inline-block"
            : "none";

    button.onclick = () => startTraining(id);

    showScreen("module");
}


function openSection(index) {

    const section = activeModule?.sections?.[index];

    if (!section) return;

    document.getElementById("moduleSections").innerHTML = `

        <article class="tile section-detail">

            <span class="moduleStatus">
                FICHA DE ESTUDIO
            </span>

            <h2>${txt(section.title)}</h2>

            <p style="font-size:1.08rem">
                ${txt(
                    section.summary ||
                    section.concepts?.join(" · ") ||
                    "Contenido en desarrollo."
                )}
            </p>

            ${
                section.concepts?.length
                    ? `
                        <h3>Conceptos clave</h3>

                        <ul>
                            ${section.concepts
                                .map(c => `<li>${txt(c)}</li>`)
                                .join("")}
                        </ul>
                    `
                    : ""
            }

            <h3>Fuente doctrinaria</h3>

            <p>
                ${txt(section.source_id || "Material académico")}
            </p>

            <div class="heroActions">

                <button
                    class="secondary"
                    onclick="openModule('${activeModule._id}')"
                >
                    ← Volver
                </button>

                ${
                    (activeModule.training || []).length
                        ? `
                            <button
                                class="primary"
                                onclick="startTraining('${activeModule._id}')"
                            >
                                Practicar
                            </button>
                        `
                        : ""
                }

            </div>

        </article>
    `;
}


/* =========================================================
   BIBLIOTECA
   ========================================================= */

async function showSources() {

    if (!cache.sources) {
        cache.sources = await api("/sources");
    }

    document.getElementById("sourceList").innerHTML =
        cache.sources.sources.map(source => `

            <article class="sourceCard">

                <span class="moduleStatus">
                    ${txt(source.status || "FUENTE").toUpperCase()}
                </span>

                <h3>${txt(source.title)}</h3>

                <p>${txt(source.organization)}</p>

                <p>
                    <strong>Rol:</strong>
                    ${txt(source.role)}
                </p>

            </article>

        `).join("");

    showScreen("sources");
}


/* =========================================================
   BUSCADOR
   ========================================================= */

async function searchContent(q) {

    const box =
        document.getElementById("searchResults");

    q = q.trim().toLowerCase();

    if (q.length < 2) {
        box.innerHTML = "";
        return;
    }

    if (!cache.academy) {
        cache.academy = await api("/academy/modules");
    }

    let results = [];

    for (const module of cache.academy.modules) {

        if (
            (
                module.name + " " +
                module.description + " " +
                module.area
            )
            .toLowerCase()
            .includes(q)
        ) {

            results.push({
                type: "Módulo",
                title: module.name,
                id: module.id,
                desc: module.description
            });
        }

        try {

            const detail =
                await api(`/academy/module/${module.id}`);

            for (const section of detail.sections || []) {

                if (
                    (
                        section.title + " " +
                        (section.summary || "")
                    )
                    .toLowerCase()
                    .includes(q)
                ) {

                    results.push({
                        type: "Tema",
                        title: section.title,
                        id: module.id,
                        desc: module.name
                    });
                }
            }

        } catch (e) {}
    }

    box.innerHTML =
        results.slice(0, 10).map(result => `

            <article
                class="tile clickable"
                onclick="openModule('${result.id}')"
            >

                <span class="moduleStatus">
                    ${result.type}
                </span>

                <h3>${txt(result.title)}</h3>

                <p>${txt(result.desc)}</p>

            </article>

        `).join("");
}


/* =========================================================
   CATÁLOGO DEL SIMULADOR
   ========================================================= */

function renderSimCatalog(filter = "all") {

    const grid =
        document.getElementById("simCatalogGrid");

    if (!grid) return;

    grid.innerHTML =
        SIM_SCENARIOS
        .filter(s =>
            filter === "all" ||
            s.category === filter
        )
        .map(scenario => `

            <article
                class="simCard"
                onclick="selectScenario('${scenario.id}')"
            >

                <div class="simIcon">
                    ${scenario.icon}
                </div>

                <span class="simDifficulty">
                    ${scenario.difficulty}
                </span>

                <h3>${scenario.name}</h3>

                <p>${scenario.description}</p>

                <strong>
                    Ver despacho →
                </strong>

            </article>

        `).join("");
}


function filterSimCatalog(filter, button) {

    document
        .querySelectorAll(".chip")
        .forEach(x =>
            x.classList.remove("active")
        );

    button.classList.add("active");

    renderSimCatalog(filter);
}


function openSimulatorCatalog() {

    renderSimCatalog();
    showScreen("simCatalog");
}


function selectScenario(id) {

    selectedScenario =
        SIM_SCENARIOS.find(s => s.id === id);

    if (!selectedScenario) return;

    document.getElementById("briefTitle").textContent =
        selectedScenario.name;

    document.getElementById("briefDescription").textContent =
        selectedScenario.dispatch;

    document.getElementById("briefFacts").innerHTML =
        selectedScenario.facts
        .map(fact => `

            <div class="briefFact">

                <span>${fact[0]}</span>

                <strong>${fact[1]}</strong>

            </div>

        `)
        .join("");

    document.getElementById("briefObjectives").innerHTML = `

        <ul>

            ${selectedScenario.objectives
                .map(x => `<li>${x}</li>`)
                .join("")}

        </ul>
    `;

    document.getElementById("launchScenarioBtn").onclick =
        () => launchScenario(id);

    showScreen("simBrief");
}


/* =========================================================
   NUEVO LABORATORIO DIDÁCTICO
   ========================================================= */

let labState = {
    scenario: null,
    step: 0,
    score: 0,
    decisions: [],
    temp: 20,
    smoke: 0,
    visibility: 100,
    oxygen: 20.9
};


/* =========================================================
   EXPERIENCIAS
   ========================================================= */

const LAB_EXPERIENCES = {

    fire_behavior: {

        title:
            "Laboratorio de comportamiento del fuego",

        objective:
            "Observar, interpretar, decidir y explicar.",

        initial: {
            temp: 25,
            smoke: 0,
            visibility: 100,
            oxygen: 20.9
        },

        situations: [

            {
                title:
                    "Experiencia 01 · El encendedor",

                description:
                    "Tenés un encendedor. Para que aparezca y se mantenga la llama deben estar presentes los componentes necesarios para la combustión.",

                question:
                    "¿Qué elementos del triángulo del fuego reconocés?",

                options: [

                    {
                        text:
                            "Combustible, comburente y calor",

                        correct: true,

                        consequence:
                            "Identificaste correctamente los tres componentes básicos.",

                        explanation:
                            "El combustible es el material que puede arder, el comburente es normalmente el oxígeno presente en el aire y el calor aporta la energía necesaria para iniciar la combustión.",

                        effects: {
                            temp: 20,
                            smoke: 2,
                            visibility: -2,
                            oxygen: -0.1
                        }
                    },

                    {
                        text:
                            "Solamente combustible y calor",

                        correct: false,

                        consequence:
                            "Falta un componente fundamental.",

                        explanation:
                            "Sin comburente no puede mantenerse la combustión.",

                        effects: {}
                    },

                    {
                        text:
                            "Agua, humo y temperatura",

                        correct: false,

                        consequence:
                            "Esos no constituyen el triángulo del fuego.",

                        explanation:
                            "El triángulo está formado por combustible, comburente y calor.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Experiencia 02 · Llama cubierta",

                description:
                    "Una pequeña llama queda cubierta por un recipiente que limita progresivamente el intercambio con el aire exterior.",

                question:
                    "¿Sobre qué componente actuamos principalmente?",

                options: [

                    {
                        text:
                            "Comburente",

                        correct: true,

                        consequence:
                            "El oxígeno disponible disminuye y la llama termina extinguiéndose.",

                        explanation:
                            "Al limitar el aporte de aire reducimos el comburente disponible para sostener la combustión.",

                        effects: {
                            temp: -10,
                            smoke: 4,
                            visibility: -3,
                            oxygen: -1.5
                        }
                    },

                    {
                        text:
                            "Combustible",

                        correct: false,

                        consequence:
                            "El combustible continúa presente.",

                        explanation:
                            "En esta experiencia la acción principal consiste en limitar el aporte de oxígeno.",

                        effects: {}
                    },

                    {
                        text:
                            "No se modifica ningún componente",

                        correct: false,

                        consequence:
                            "La cobertura sí altera las condiciones de combustión.",

                        explanation:
                            "La disponibilidad de comburente cambia cuando se limita el intercambio con el ambiente.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Experiencia 03 · Fuente de calor",

                description:
                    "Pensá en un calefactor próximo a materiales capaces de arder. Todavía no existe llama, pero existe una fuente que aporta energía.",

                question:
                    "¿Qué componente del triángulo representa principalmente el calefactor?",

                options: [

                    {
                        text:
                            "Calor",

                        correct: true,

                        consequence:
                            "Reconociste una fuente capaz de transferir energía al combustible.",

                        explanation:
                            "El calor puede elevar la temperatura de un material hasta favorecer su ignición si se cumplen las demás condiciones.",

                        effects: {
                            temp: 40
                        }
                    },

                    {
                        text:
                            "Comburente",

                        correct: false,

                        consequence:
                            "El calefactor no representa el oxígeno.",

                        explanation:
                            "El comburente está asociado principalmente al oxígeno del aire.",

                        effects: {}
                    },

                    {
                        text:
                            "Agente extintor",

                        correct: false,

                        consequence:
                            "No corresponde.",

                        explanation:
                            "En este caso estamos analizando una fuente de energía térmica.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Experiencia 04 · Alcohol y agua",

                description:
                    "Comparás dos líquidos: agua y alcohol. A simple vista ambos son líquidos, pero su comportamiento frente al fuego es muy diferente.",

                question:
                    "¿Cuál puede actuar como combustible en condiciones adecuadas?",

                options: [

                    {
                        text:
                            "El alcohol",

                        correct: true,

                        consequence:
                            "Reconocés que no todos los líquidos tienen el mismo comportamiento frente al fuego.",

                        explanation:
                            "El alcohol puede producir vapores combustibles. El agua, en cambio, no actúa como combustible en este contexto.",

                        effects: {
                            temp: 10
                        }
                    },

                    {
                        text:
                            "El agua",

                        correct: false,

                        consequence:
                            "La clasificación es incorrecta.",

                        explanation:
                            "En esta comparación el agua no constituye el combustible.",

                        effects: {}
                    },

                    {
                        text:
                            "Ambos se comportan exactamente igual",

                        correct: false,

                        consequence:
                            "La apariencia física no determina por sí sola el comportamiento frente al fuego.",

                        explanation:
                            "Las propiedades de cada sustancia determinan su comportamiento.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Experiencia 05 · Combustible líquido",

                description:
                    "En un combustible líquido inflamable, la combustión se relaciona principalmente con los vapores combustibles presentes sobre su superficie.",

                question:
                    "¿Qué es importante comprender?",

                options: [

                    {
                        text:
                            "Que los vapores pueden formar una mezcla combustible con el aire",

                        correct: true,

                        consequence:
                            "Interpretás correctamente el peligro asociado a los vapores.",

                        explanation:
                            "La presencia de vapores y una fuente de ignición puede generar condiciones favorables para la combustión.",

                        effects: {
                            temp: 20,
                            smoke: 5
                        }
                    },

                    {
                        text:
                            "Que solamente importa el color del líquido",

                        correct: false,

                        consequence:
                            "Ese dato no explica su comportamiento frente al fuego.",

                        explanation:
                            "Las propiedades físico-químicas y la producción de vapores son relevantes.",

                        effects: {}
                    },

                    {
                        text:
                            "Que los vapores no tienen importancia",

                        correct: false,

                        consequence:
                            "Se subestima un factor fundamental.",

                        explanation:
                            "En líquidos inflamables, comprender la presencia de vapores es esencial.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Experiencia 06 · Humo",

                description:
                    "En un compartimiento incendiado el humo aumenta, se vuelve más denso y el plano neutro comienza a descender.",

                question:
                    "¿Qué conducta corresponde?",

                options: [

                    {
                        text:
                            "Observar en conjunto humo, temperatura, ventilación y evolución del fuego",

                        correct: true,

                        consequence:
                            "Construís una lectura integral de las condiciones.",

                        explanation:
                            "Los indicadores deben interpretarse conjuntamente y reevaluarse durante toda la intervención.",

                        effects: {
                            temp: 40,
                            smoke: 20,
                            visibility: -25,
                            oxygen: -0.5
                        }
                    },

                    {
                        text:
                            "Ignorar el humo y actuar sin evaluación",

                        correct: false,

                        consequence:
                            "Perdés información importante sobre la evolución del incendio.",

                        explanation:
                            "El humo constituye uno de los indicadores que deben formar parte de la evaluación.",

                        effects: {
                            temp: 70,
                            smoke: 25,
                            visibility: -30,
                            oxygen: -0.8
                        }
                    }
                ]
            },


            {
                title:
                    "Experiencia 07 · Ventilación",

                description:
                    "Un incendio en un compartimiento dispone de ventilación limitada. Se considera abrir una nueva abertura.",

                question:
                    "¿Qué puede ocurrir al aumentar el aporte de aire?",

                options: [

                    {
                        text:
                            "Puede modificarse intensamente el comportamiento del incendio",

                        correct: true,

                        consequence:
                            "Reconocés que ventilación y combustión están relacionadas.",

                        explanation:
                            "Una abertura modifica el movimiento de gases y el aporte de oxígeno, por lo que debe coordinarse con la estrategia de intervención.",

                        effects: {
                            temp: 70,
                            smoke: -10,
                            visibility: 10,
                            oxygen: 0.8
                        }
                    },

                    {
                        text:
                            "Nunca cambia nada",

                        correct: false,

                        consequence:
                            "La interpretación subestima el efecto de la ventilación.",

                        explanation:
                            "El aporte de aire puede alterar significativamente la combustión.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Experiencia 08 · Rollover",

                description:
                    "Aparecen llamas desplazándose en la capa superior de gases calientes.",

                question:
                    "¿Qué fenómeno estás reconociendo?",

                options: [

                    {
                        text:
                            "Rollover",

                        correct: true,

                        consequence:
                            "Reconociste combustión en gases de la capa superior.",

                        explanation:
                            "La presencia de llamas en la capa de gases calientes constituye un indicador relevante de evolución térmica.",

                        effects: {
                            temp: 80,
                            smoke: 10,
                            visibility: -15,
                            oxygen: -0.5
                        }
                    },

                    {
                        text:
                            "Extinción completa",

                        correct: false,

                        consequence:
                            "La interpretación es incompatible con las condiciones observadas.",

                        explanation:
                            "La aparición de llamas en gases superiores no indica extinción.",

                        effects: {
                            temp: 100,
                            smoke: 15,
                            visibility: -20,
                            oxygen: -0.7
                        }
                    }
                ]
            },


            {
                title:
                    "Experiencia 09 · Transición térmica",

                description:
                    "La temperatura aumenta rápidamente y numerosos materiales del compartimiento reciben intensa radiación térmica.",

                question:
                    "¿Qué concepto debe formar parte de tu evaluación?",

                options: [

                    {
                        text:
                            "Posible evolución hacia una transición térmica generalizada",

                        correct: true,

                        consequence:
                            "Reconocés una situación de rápida evolución térmica.",

                        explanation:
                            "Los indicadores térmicos y el comportamiento general del compartimiento deben interpretarse continuamente.",

                        effects: {
                            temp: 100,
                            smoke: 10,
                            visibility: -10,
                            oxygen: -0.7
                        }
                    },

                    {
                        text:
                            "Que la temperatura ya no es importante",

                        correct: false,

                        consequence:
                            "Se ignora una variable crítica.",

                        explanation:
                            "La temperatura y los indicadores térmicos forman parte de la evaluación del incendio.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Experiencia 10 · Aplicación de agua",

                description:
                    "Necesitás reducir la energía térmica presente en el compartimiento.",

                question:
                    "¿Cuál es uno de los objetivos principales de la aplicación adecuada de agua?",

                options: [

                    {
                        text:
                            "Absorber energía y reducir las condiciones térmicas",

                        correct: true,

                        consequence:
                            "La temperatura comienza a disminuir.",

                        explanation:
                            "El agua puede absorber gran cantidad de energía térmica y contribuir al control del incendio.",

                        effects: {
                            temp: -180,
                            smoke: -15,
                            visibility: 20
                        }
                    },

                    {
                        text:
                            "Aumentar deliberadamente la energía del incendio",

                        correct: false,

                        consequence:
                            "No corresponde al objetivo del agente extintor.",

                        explanation:
                            "La aplicación busca controlar el incendio y reducir la energía térmica.",

                        effects: {}
                    }
                ]
            }
        ]
    },


    house: {

        title:
            "Incendio en vivienda",

        objective:
            "Evaluar condiciones y tomar decisiones progresivas.",

        initial: {
            temp: 160,
            smoke: 35,
            visibility: 60,
            oxygen: 20
        },

        situations: [

            {
                title:
                    "Arribo a la vivienda",

                description:
                    "Arribás a una vivienda con humo visible y posible persona en el interior. Todavía no conocés el foco ni las condiciones internas.",

                question:
                    "¿Qué hacés primero?",

                options: [

                    {
                        text:
                            "Realizar reconocimiento exterior y obtener información",

                        correct: true,

                        consequence:
                            "Construís una lectura inicial antes de comprometer recursos.",

                        explanation:
                            "El reconocimiento permite identificar riesgos, accesos, condiciones, exposiciones y posibles víctimas.",

                        effects: {
                            temp: 10,
                            smoke: 5,
                            visibility: -5,
                            oxygen: -0.1
                        }
                    },

                    {
                        text:
                            "Ingresar inmediatamente",

                        correct: false,

                        consequence:
                            "Te comprometés en un ambiente todavía no evaluado.",

                        explanation:
                            "La posible víctima aumenta la urgencia, pero no elimina la evaluación inicial ni el control de riesgos.",

                        effects: {
                            temp: 40,
                            smoke: 15,
                            visibility: -15,
                            oxygen: -0.4
                        }
                    }
                ]
            },


            {
                title:
                    "Control de abertura",

                description:
                    "La puerta permanece cerrada y hay humo por una abertura existente.",

                question:
                    "¿Qué decisión es más adecuada?",

                options: [

                    {
                        text:
                            "Evaluar y coordinar antes de modificar aberturas",

                        correct: true,

                        consequence:
                            "Mantenés control sobre una variable crítica.",

                        explanation:
                            "La ventilación debe coordinarse con la estrategia de ataque y las condiciones observadas.",

                        effects: {
                            temp: 10,
                            smoke: 0,
                            visibility: 0,
                            oxygen: 0
                        }
                    },

                    {
                        text:
                            "Abrir todo para sacar humo",

                        correct: false,

                        consequence:
                            "Aumenta el aire disponible.",

                        explanation:
                            "Ventilar puede modificar intensamente la combustión.",

                        effects: {
                            temp: 90,
                            smoke: -5,
                            visibility: 5,
                            oxygen: 0.8
                        }
                    }
                ]
            },


            {
                title:
                    "Condiciones térmicas",

                description:
                    "Aumenta la radiación térmica y existe una capa de gases calientes.",

                question:
                    "¿Qué acción puede contribuir al control?",

                options: [

                    {
                        text:
                            "Aplicar agua adecuadamente para reducir la energía térmica",

                        correct: true,

                        consequence:
                            "Las condiciones térmicas comienzan a mejorar.",

                        explanation:
                            "La aplicación de agua busca controlar el incendio y reducir la energía térmica.",

                        effects: {
                            temp: -100,
                            smoke: -10,
                            visibility: 15
                        }
                    },

                    {
                        text:
                            "Continuar sin reevaluar",

                        correct: false,

                        consequence:
                            "Las condiciones siguen deteriorándose.",

                        explanation:
                            "La intervención requiere reevaluación continua.",

                        effects: {
                            temp: 70,
                            smoke: 15,
                            visibility: -20,
                            oxygen: -0.5
                        }
                    }
                ]
            },


            {
                title:
                    "Búsqueda",

                description:
                    "La posible víctima todavía no fue localizada.",

                question:
                    "¿Cómo debe realizarse la búsqueda?",

                options: [

                    {
                        text:
                            "De forma organizada manteniendo orientación y comunicación",

                        correct: true,

                        consequence:
                            "La búsqueda progresa de manera sistemática.",

                        explanation:
                            "La orientación, la coordinación y el control de las condiciones deben mantenerse durante la búsqueda.",

                        effects: {}
                    },

                    {
                        text:
                            "Separándose sin coordinación",

                        correct: false,

                        consequence:
                            "Aumenta el riesgo de desorganización.",

                        explanation:
                            "La coordinación forma parte de una operación segura.",

                        effects: {}
                    }
                ]
            }
        ]
    },


    lines: {

        title:
            "Líneas y aplicación de agua",

        objective:
            "Preparar, utilizar y reevaluar una línea de ataque.",

        initial: {
            temp: 140,
            smoke: 25,
            visibility: 75,
            oxygen: 20.5
        },

        situations: [

            {
                title:
                    "Sistema de línea",

                description:
                    "Necesitás establecer una línea de ataque antes de avanzar.",

                question:
                    "¿Qué debe comprobarse?",

                options: [

                    {
                        text:
                            "Fuente, alimentación, recorrido, conexiones y disponibilidad de agua",

                        correct: true,

                        consequence:
                            "La línea queda preparada para operar.",

                        explanation:
                            "El sistema debe conducir y aplicar el agente extintor de forma operativa.",

                        effects: {}
                    },

                    {
                        text:
                            "Solo el color de la manguera",

                        correct: false,

                        consequence:
                            "La comprobación resulta incompleta.",

                        explanation:
                            "Debe evaluarse el sistema completo.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Aplicación",

                description:
                    "La línea está cargada y existe un foco que requiere control.",

                question:
                    "¿Cuál es el objetivo de la aplicación?",

                options: [

                    {
                        text:
                            "Controlar el fuego y reducir la energía térmica",

                        correct: true,

                        consequence:
                            "Las condiciones comienzan a mejorar.",

                        explanation:
                            "La aplicación debe responder al objetivo táctico y ser seguida por una reevaluación.",

                        effects: {
                            temp: -90,
                            smoke: -10,
                            visibility: 15
                        }
                    },

                    {
                        text:
                            "Aplicar agua sin observar resultados",

                        correct: false,

                        consequence:
                            "No evaluás la efectividad de la acción.",

                        explanation:
                            "Toda acción debe acompañarse de reevaluación.",

                        effects: {}
                    }
                ]
            }
        ]
    },


    era: {

        title:
            "Ingreso con ERA y búsqueda",

        objective:
            "Comprobar equipo, ingresar, orientarse y salir.",

        initial: {
            temp: 90,
            smoke: 55,
            visibility: 35,
            oxygen: 19.5
        },

        situations: [

            {
                title:
                    "Antes de ingresar",

                description:
                    "Debés ingresar a un ambiente con humo y visibilidad reducida.",

                question:
                    "¿Qué corresponde hacer primero?",

                options: [

                    {
                        text:
                            "Comprobar ERA y condiciones del equipo",

                        correct: true,

                        consequence:
                            "El equipo queda verificado antes de la exposición.",

                        explanation:
                            "La comprobación previa forma parte de la preparación para el ingreso.",

                        effects: {}
                    },

                    {
                        text:
                            "Ingresar y revisar después",

                        correct: false,

                        consequence:
                            "Ingresás sin haber verificado completamente el equipo.",

                        explanation:
                            "La comprobación debe realizarse antes de exponerse al ambiente.",

                        effects: {}
                    }
                ]
            },


            {
                title:
                    "Orientación",

                description:
                    "Durante la búsqueda la visibilidad disminuye.",

                question:
                    "¿Qué prioridad mantenés?",

                options: [

                    {
                        text:
                            "Orientación, comunicación y evaluación continua",

                        correct: true,

                        consequence:
                            "La progresión se mantiene organizada.",

                        explanation:
                            "Mantener referencias y evaluar las condiciones permite controlar la progresión.",

                        effects: {}
                    },

                    {
                        text:
                            "Avanzar sin referencias",

                        correct: false,

                        consequence:
                            "Se pierde referencia de la progresión.",

                        explanation:
                            "La orientación debe conservarse durante toda la operación.",

                        effects: {}
                    }
                ]
            }
        ]
    }
};


/* =========================================================
   EXPERIENCIA GENÉRICA PARA OTROS ESCENARIOS
   ========================================================= */

function getLabExperience(id) {

    if (LAB_EXPERIENCES[id]) {
        return LAB_EXPERIENCES[id];
    }

    return {

        title:
            selectedScenario?.name ||
            "Simulación operacional",

        objective:
            "Evaluar, decidir y reevaluar.",

        initial: {
            temp: 100,
            smoke: 30,
            visibility: 70,
            oxygen: 20.5
        },

        situations: [

            {
                title:
                    "Evaluación inicial",

                description:
                    selectedScenario?.dispatch ||
                    "Analizá la situación antes de intervenir.",

                question:
                    "¿Cuál es la conducta inicial más adecuada?",

                options: [

                    {
                        text:
                            "Evaluar escena, riesgos, recursos y condiciones",

                        correct: true,

                        consequence:
                            "La intervención comienza con una lectura organizada.",

                        explanation:
                            "La evaluación inicial permite fundamentar las decisiones posteriores.",

                        effects: {}
                    },

                    {
                        text:
                            "Actuar inmediatamente sin evaluación",

                        correct: false,

                        consequence:
                            "La intervención comienza sin información suficiente.",

                        explanation:
                            "La evaluación forma parte de la toma de decisiones operativa.",

                        effects: {
                            temp: 25,
                            smoke: 10,
                            visibility: -10,
                            oxygen: -0.3
                        }
                    }
                ]
            },


            {
                title:
                    "Reevaluación",

                description:
                    "La situación cambia después de la primera decisión.",

                question:
                    "¿Qué corresponde hacer?",

                options: [

                    {
                        text:
                            "Reevaluar las condiciones y ajustar la intervención",

                        correct: true,

                        consequence:
                            "La estrategia se adapta a la evolución observada.",

                        explanation:
                            "La evaluación debe mantenerse durante toda la intervención.",

                        effects: {
                            temp: -10,
                            smoke: -5,
                            visibility: 5
                        }
                    },

                    {
                        text:
                            "Mantener la misma acción sin observar resultados",

                        correct: false,

                        consequence:
                            "No comprobás la efectividad de lo realizado.",

                        explanation:
                            "Las decisiones deben revisarse según los cambios observados.",

                        effects: {
                            temp: 30,
                            smoke: 10,
                            visibility: -10
                        }
                    }
                ]
            }
        ]
    };
}


/* =========================================================
   LANZAR LABORATORIO
   ========================================================= */

function launchScenario(id) {

    selectedScenario =
        SIM_SCENARIOS.find(s => s.id === id) ||
        selectedScenario;

    const experience =
        getLabExperience(id);

    labState = {
        scenario: id,
        step: 0,
        score: 0,
        decisions: [],
        temp: experience.initial.temp,
        smoke: experience.initial.smoke,
        visibility: experience.initial.visibility,
        oxygen: experience.initial.oxygen
    };

    showScreen("simulator");

    const title =
        document.getElementById("simScenarioTitle");

    if (title) {
        title.textContent = experience.title;
    }

    renderLab();
}


/* =========================================================
   RENDER LABORATORIO
   ========================================================= */

function renderLab() {

    const experience =
        getLabExperience(labState.scenario);

    const situation =
        experience.situations[labState.step];

    if (!situation) {
        finishLab();
        return;
    }

    updateLabIndicators();

    const objective =
        document.getElementById("simObjective");

    if (objective) {
        objective.textContent =
            `Situación ${labState.step + 1} de ${experience.situations.length}`;
    }

    const condition =
        document.getElementById("simCondition");

    if (condition) {
        condition.textContent =
            experience.objective;
    }

    const actions =
        document.getElementById("simActions");

    actions.innerHTML = `

        <div class="egsLabSituation">

            <span class="panelLabel">
                EXPERIENCIA ${String(labState.step + 1).padStart(2, "0")}
                ·
                ${labState.step + 1}/${experience.situations.length}
            </span>

            <h2 style="
                margin-top:14px;
                font-size:2rem;
            ">
                ${situation.title}
            </h2>

            <div style="
                padding:18px;
                margin:18px 0;
                border-left:3px solid #ff6b35;
                background:rgba(255,255,255,.03);
            ">

                <span class="panelLabel">
                    SITUACIÓN
                </span>

                <p style="
                    font-size:1.08rem;
                    line-height:1.65;
                    margin-top:10px;
                ">
                    ${situation.description}
                </p>

            </div>

            <h3 style="
                font-size:1.35rem;
                margin:22px 0 14px;
            ">
                ${situation.question}
            </h3>

            <div id="labOptions"></div>

            <div id="labFeedback"></div>

        </div>
    `;

    document.getElementById("labOptions").innerHTML =
        situation.options
        .map((option, index) => `

            <button
                class="actionBtn"
                onclick="chooseLabOption(${index})"
                style="
                    width:100%;
                    margin-bottom:10px;
                    text-align:left;
                    padding:18px;
                "
            >
                ${option.text}
            </button>

        `)
        .join("");

    renderLabLog();
}


/* =========================================================
   RESPONDER
   ========================================================= */

function chooseLabOption(index) {

    const experience =
        getLabExperience(labState.scenario);

    const situation =
        experience.situations[labState.step];

    const option =
        situation.options[index];

    if (!option) return;

    document
        .querySelectorAll("#labOptions button")
        .forEach(button => {
            button.disabled = true;
        });

    if (option.correct) {
        labState.score++;
    }

    applyLabEffects(option.effects || {});

    labState.decisions.push({
        title: situation.title,
        answer: option.text,
        correct: option.correct,
        consequence: option.consequence,
        explanation: option.explanation
    });

    updateLabIndicators();

    document.getElementById("labFeedback").innerHTML = `

        <div
            class="feedbackBox ${option.correct ? "correct" : ""}"
            style="margin-top:22px"
        >

            <strong>
                ${
                    option.correct
                        ? "DECISIÓN ADECUADA"
                        : "DECISIÓN A REVISAR"
                }
            </strong>

            <h3 style="margin-top:18px">
                CONSECUENCIA
            </h3>

            <p style="line-height:1.6">
                ${option.consequence}
            </p>

            <h3 style="margin-top:18px">
                ¿POR QUÉ?
            </h3>

            <p style="line-height:1.6">
                ${option.explanation}
            </p>

            <button
                class="primary full"
                onclick="nextLabSituation()"
                style="margin-top:20px"
            >
                ${
                    labState.step + 1 <
                    experience.situations.length

                    ? "CONTINUAR EXPERIENCIA"

                    : "FINALIZAR Y ANALIZAR"
                }
            </button>

        </div>
    `;

    renderLabLog();
}


/* =========================================================
   EFECTOS
   ========================================================= */

function applyLabEffects(effects) {

    labState.temp +=
        effects.temp || 0;

    labState.smoke +=
        effects.smoke || 0;

    labState.visibility +=
        effects.visibility || 0;

    labState.oxygen +=
        effects.oxygen || 0;

    labState.temp =
        Math.max(20, labState.temp);

    labState.smoke =
        Math.max(
            0,
            Math.min(100, labState.smoke)
        );

    labState.visibility =
        Math.max(
            0,
            Math.min(100, labState.visibility)
        );

    labState.oxygen =
        Math.max(
            10,
            Math.min(21, labState.oxygen)
        );
}


/* =========================================================
   INDICADORES
   ========================================================= */

function updateLabIndicators() {

    const temp =
        document.getElementById("simTemp");

    const smoke =
        document.getElementById("simSmoke");

    const visibility =
        document.getElementById("simVisibility");

    const oxygen =
        document.getElementById("simOxygen");

    if (temp) {
        temp.textContent =
            `${Math.round(labState.temp)} °C`;
    }

    if (smoke) {
        smoke.textContent =
            `${Math.round(labState.smoke)} %`;
    }

    if (visibility) {
        visibility.textContent =
            `${Math.round(labState.visibility)} %`;
    }

    if (oxygen) {
        oxygen.textContent =
            `${Number(labState.oxygen).toFixed(1)} %`;
    }
}


/* =========================================================
   REGISTRO DIDÁCTICO
   ========================================================= */

function renderLabLog() {

    const box =
        document.getElementById("simLog");

    if (!box) return;

    if (!labState.decisions.length) {

        box.innerHTML = `
            <p style="opacity:.65">
                El registro aparecerá a medida que tomes decisiones.
            </p>
        `;

        return;
    }

    box.innerHTML =
        labState.decisions
        .map((decision, index) => `

            <div
                class="entry"
                style="
                    margin-bottom:14px;
                    padding-bottom:14px;
                    border-bottom:1px solid #293038;
                "
            >

                <strong>
                    ${index + 1}.
                    ${
                        decision.correct
                            ? "DECISIÓN ADECUADA"
                            : "DECISIÓN A REVISAR"
                    }
                </strong>

                <p style="margin:6px 0">
                    ${decision.title}
                </p>

                <small>
                    ${decision.answer}
                </small>

            </div>

        `)
        .join("");
}


/* =========================================================
   SIGUIENTE SITUACIÓN
   ========================================================= */

function nextLabSituation() {

    labState.step++;

    const experience =
        getLabExperience(labState.scenario);

    if (
        labState.step >=
        experience.situations.length
    ) {

        finishLab();

    } else {

        renderLab();
        window.scrollTo(0, 0);
    }
}


/* =========================================================
   RESULTADO
   ========================================================= */

function finishLab() {

    const experience =
        getLabExperience(labState.scenario);

    const total =
        experience.situations.length;

    const percentage =
        Math.round(
            (
                labState.score /
                Math.max(1, total)
            ) * 100
        );

    document.getElementById("simActions").innerHTML = `

        <div class="egsLabResult">

            <span class="panelLabel">
                ANÁLISIS POSTERIOR
            </span>

            <h2 style="
                font-size:2rem;
                margin:14px 0;
            ">
                Experiencia finalizada
            </h2>

            <div style="
                font-size:4rem;
                font-weight:800;
                margin:20px 0;
            ">
                ${percentage}%
            </div>

            <p>
                Decisiones adecuadas:
                <strong>
                    ${labState.score} de ${total}
                </strong>
            </p>

            <p style="
                margin-top:12px;
                line-height:1.6;
            ">
                El resultado es formativo.
                Revisá especialmente las decisiones
                marcadas como “A revisar” y su explicación.
            </p>

            <button
                class="primary full"
                onclick="restartLab()"
                style="margin-top:20px"
            >
                REPETIR EXPERIENCIA
            </button>

            <button
                class="secondary full"
                onclick="exitSimulation()"
                style="margin-top:10px"
            >
                VOLVER A ESCENARIOS
            </button>

        </div>
    `;

    const box =
        document.getElementById("simLog");

    if (box) {

        box.innerHTML =
            labState.decisions
            .map((decision, index) => `

                <div
                    class="entry"
                    style="
                        margin-bottom:18px;
                        padding-bottom:18px;
                        border-bottom:1px solid #293038;
                    "
                >

                    <strong>
                        ${index + 1}.
                        ${
                            decision.correct
                                ? "ADECUADA"
                                : "REVISAR"
                        }
                    </strong>

                    <p>
                        <b>${decision.title}</b>
                    </p>

                    <p>
                        Decisión:
                        ${decision.answer}
                    </p>

                    <p>
                        Consecuencia:
                        ${decision.consequence}
                    </p>

                    <p>
                        Explicación:
                        ${decision.explanation}
                    </p>

                </div>

            `)
            .join("");
    }
}


function restartLab() {
    launchScenario(labState.scenario);
}


function exitSimulation() {
    openSimulatorCatalog();
}


/* =========================================================
   COMPATIBILIDAD CON HTML ANTERIOR
   ========================================================= */

function reset3DScenario() {
    restartLab();
}


function setSimulatorQuality() {
    // Sin efecto.
    // El laboratorio didáctico ya no utiliza 3D.
}


function simAction() {
    // Compatibilidad con versiones anteriores.
}


function finish3DSimulation() {
    finishLab();
}


/* =========================================================
   EVALUACIÓN
   ========================================================= */

async function startTraining(id) {

    const data =
        await api(
            `/academy/module/${id}/training?shuffle=true`
        );

    runTraining(data, id);
}


async function startIntegral() {

    const data =
        await api(
            "/academy/integral?limit=20"
        );

    runTraining(
        data,
        "integral"
    );
}


function runTraining(data, id) {

    activeTraining =
        data.training || [];

    activeMeta =
        data.metadata || {};

    activeMeta._id =
        id;

    current = 0;
    correctCount = 0;
    reviewed = 0;
    log = [];
    seconds = 0;
    answered = false;

    document.getElementById("trainingTitle").textContent =
        activeMeta.module_name ||
        "Evaluación integral";

    showScreen("training");

    renderStep();
    startTimer();
}


function renderStep() {

    const question =
        activeTraining[current];

    if (!question) {
        finishTraining();
        return;
    }

    answered = false;

    document
        .getElementById("nextQuestionBtn")
        .classList
        .add("hidden");

    document.getElementById("feedback").innerHTML =
        "";

    document.getElementById("question").textContent =
        question.question;

    document.getElementById("stepCounter").textContent =
        `${current + 1}/${activeTraining.length}`;

    document.getElementById("sourceBadge").textContent =
        question.source_id || "—";

    document.getElementById("reviewedCount").textContent =
        reviewed;

    const options =
        (question.options || [])
        .slice()
        .sort(() => Math.random() - 0.5);

    document.getElementById("options").innerHTML =
        options.map((option, i) => `

            <button
                class="optionBtn"
                data-i="${i}"
            >
                ${txt(option.text)}
            </button>

        `).join("");

    document
        .querySelectorAll(".optionBtn")
        .forEach(button => {

            button.onclick =
                () => chooseAnswer(
                    options[Number(button.dataset.i)],
                    button,
                    options
                );
        });
}


function chooseAnswer(option, button, options) {

    if (answered) return;

    answered = true;
    reviewed++;

    const correct =
        option.status === "correct";

    if (correct) {
        correctCount++;
    }

    document
        .querySelectorAll(".optionBtn")
        .forEach(x => {
            x.disabled = true;
        });

    button.classList.add(
        correct
            ? "selectedCorrect"
            : "selectedWrong"
    );

    const expected =
        options.find(
            x => x.status === "correct"
        );

    const question =
        activeTraining[current];

    log.push({
        n: current + 1,
        question: question.question,
        answer: option.text,
        correct,
        expected: expected?.text || "",
        source: question.source_id || "—"
    });

    document.getElementById("reviewedCount").textContent =
        reviewed;

    document.getElementById("feedback").innerHTML = `

        <div
            class="feedbackBox ${correct ? "correct" : ""}"
        >

            <strong>
                ${
                    correct
                        ? "Respuesta adecuada"
                        : "Respuesta a revisar"
                }
            </strong>

            <div>

                ${
                    correct

                    ? "Coincide con la respuesta marcada como correcta en el material cargado."

                    : `Respuesta esperada: ${txt(expected?.text || "—")}`
                }

            </div>

            <div>
                <b>Fuente:</b>
                ${txt(question.source_id || "—")}
            </div>

        </div>
    `;

    document
        .getElementById("nextQuestionBtn")
        .classList
        .remove("hidden");
}


function nextQuestion() {
    current++;
    renderStep();
}


function startTimer() {

    stopTimer();

    timer = setInterval(() => {

        seconds++;

        const time =
            document.getElementById("time");

        if (time) {

            time.textContent =
                `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
        }

    }, 1000);
}


function stopTimer() {

    if (timer) {
        clearInterval(timer);
        timer = null;
    }
}


function finishTraining() {

    stopTimer();

    const percentage =
        Math.round(
            correctCount /
            Math.max(1, reviewed) *
            100
        );

    document.getElementById("finalScore").textContent =
        percentage;

    document.getElementById("analysisSummary").innerHTML = `

        <p>
            Respuestas revisadas:
            <strong>${reviewed}</strong>
        </p>

        <p>
            Adecuadas:
            <strong>${correctCount}</strong>
        </p>

        <p>
            Este resultado no crea un perfil personal:
            sirve para decidir qué repasar.
        </p>
    `;

    document.getElementById("decisionLog").innerHTML =
        log.map(entry => `

            <div class="entry">

                <strong>
                    ${entry.n}.
                    ${
                        entry.correct
                            ? "Adecuada"
                            : "Revisar"
                    }
                </strong>

                <p>
                    ${txt(entry.question)}
                </p>

                <p>
                    Tu respuesta:
                    ${txt(entry.answer)}
                </p>

                ${
                    entry.correct
                        ? ""
                        : `
                            <p>
                                Esperada:
                                ${txt(entry.expected)}
                            </p>
                        `
                }

                <p>
                    Fuente:
                    ${txt(entry.source)}
                </p>

            </div>

        `).join("");

    showScreen("analysis");
}


/* =========================================================
   INICIO AUTOMÁTICO
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    boot
);