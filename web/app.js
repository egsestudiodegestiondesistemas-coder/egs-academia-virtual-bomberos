const API_URL = "http://127.0.0.1:8001";

let cache = {
    academy: null,
    sources: null,
    scenarios: null
};

let activeModule = null;
let activeTraining = [];
let activeMeta = null;
let current = 0;
let score = 100;
let log = [];
let timer = null;
let seconds = 0;
let lastResult = null;

function showScreen(id) {
    document.querySelectorAll(".screen").forEach(x => x.classList.remove("active"));
    document.getElementById(id)?.classList.add("active");
    window.scrollTo(0, 0);
}

function goHome() {
    stopTimer();
    showScreen("home");
    updateCampus();
}

async function api(path) {
    const r = await fetch(API_URL + path);

    if (!r.ok) {
        throw new Error("HTTP " + r.status);
    }

    return r.json();
}

function txt(v) {
    return String(v ?? "");
}

function getProgress() {
    try {
        return JSON.parse(localStorage.getItem("egs_bomberos_progress")) || {
            intentos: 0,
            mejor_puntaje: null,
            evaluaciones_completadas: 0,
            por_modulo: {}
        };
    } catch (e) {
        return {
            intentos: 0,
            mejor_puntaje: null,
            evaluaciones_completadas: 0,
            por_modulo: {}
        };
    }
}

function saveProgress(p) {
    localStorage.setItem("egs_bomberos_progress", JSON.stringify(p));
    updateCampus();
}

function updateCampus() {
    const p = getProgress();

    document.getElementById("moduleCount").textContent =
        cache.academy?.modules?.length || 8;

    document.getElementById("completedCount").textContent =
        p.evaluaciones_completadas || 0;

    document.getElementById("bestScore").textContent =
        p.mejor_puntaje == null ? "—" : p.mejor_puntaje;

    document.getElementById("attemptCount").textContent =
        p.intentos || 0;
}

/* =========================================================
   INICIO / API
========================================================= */

async function boot() {
    try {
        const s = await api("/");

        document.getElementById("apiStatus").textContent =
            `ALFA 0.9 · ${txt(s.status).toUpperCase()}`;

        [
            cache.academy,
            cache.sources,
            cache.scenarios
        ] = await Promise.all([
            api("/academy/modules"),
            api("/sources"),
            api("/scenarios")
        ]);

        updateCampus();

    } catch (e) {
        document.getElementById("apiStatus").textContent =
            "ALFA 0.9 · SERVIDOR DESCONECTADO";

        console.warn(e);
    }
}

/* =========================================================
   ACADEMIA
========================================================= */

async function openAcademy() {

    if (!cache.academy) {
        cache.academy = await api("/academy/modules");
    }

    const grid = document.getElementById("academyGrid");

    grid.innerHTML = cache.academy.modules.map(m => `
        <article
            class="tile clickable"
            onclick="openModule('${m.id}')"
        >
            <span>${txt(m.area)}</span>

            <h2>${txt(m.name)}</h2>

            <p>${txt(m.description)}</p>

            <span class="moduleStatus">
                ${txt(m.status).toUpperCase()}
            </span>
        </article>
    `).join("");

    showScreen("academy");
}

/* =========================================================
   MÓDULO
========================================================= */

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
        `${(activeModule.training || []).length} preguntas`;

    const sections = activeModule.sections || [];

    document.getElementById("moduleSections").innerHTML =
        sections.map((s, index) => `
            <article
                class="tile clickable"
                onclick="openSection(${index})"
            >
                <h2>${txt(s.title)}</h2>

                <p>
                    ${txt(
                        s.summary ||
                        s.concepts?.join(" · ") ||
                        ""
                    )}
                </p>

                <span class="moduleStatus">
                    ${txt(s.source_id || "")}
                </span>

                <p style="margin-top:12px;">
                    <strong>ABRIR FICHA →</strong>
                </p>
            </article>
        `).join("");

    const b = document.getElementById("moduleTrainingButton");

    if (b) {
        b.style.display =
            (activeModule.training || []).length
                ? "inline-block"
                : "none";

        b.onclick = () => startTraining(id);
    }

    showScreen("module");
}

/* =========================================================
   FICHAS DE ESTUDIO
========================================================= */

function openSection(index) {

    if (!activeModule) return;

    const section = activeModule.sections?.[index];

    if (!section) return;

    const container =
        document.getElementById("moduleSections");

    if (!container) return;

    const summary =
        section.summary ||
        section.concepts?.join(" · ") ||
        "Contenido en desarrollo.";

    container.innerHTML = `
        <article class="tile section-detail">

            <span class="moduleStatus">
                FICHA DE ESTUDIO
            </span>

            <h2 style="margin-top:18px;">
                ${txt(section.title)}
            </h2>

            <p style="font-size:1.05rem; line-height:1.7;">
                ${txt(summary)}
            </p>

            ${
                section.concepts?.length
                    ? `
                        <div style="margin-top:20px;">
                            <strong>CONCEPTOS CLAVE</strong>

                            <ul>
                                ${section.concepts
                                    .map(c => `<li>${txt(c)}</li>`)
                                    .join("")}
                            </ul>
                        </div>
                    `
                    : ""
            }

            <div style="margin-top:22px;">
                <strong>FUENTE DOCTRINARIA</strong>

                <p>
                    ${txt(
                        section.source_id ||
                        "Material académico"
                    )}
                </p>
            </div>

            <div style="margin-top:28px;">
                <button
                    class="btn secondary"
                    id="backToModuleButton"
                    type="button"
                >
                    ← VOLVER AL MÓDULO
                </button>
            </div>

        </article>
    `;

    const back =
        document.getElementById("backToModuleButton");

    if (back) {
        back.addEventListener("click", () => {
            openModule(activeModule._id);
        });
    }

    window.scrollTo(0, 0);
}

/* =========================================================
   BIBLIOTECA / FUENTES
========================================================= */

async function showSources() {

    if (!cache.sources) {
        cache.sources = await api("/sources");
    }

    document.getElementById("sourceList").innerHTML =
        cache.sources.sources.map(s => `
            <article class="sourceCard">

                <strong>
                    ${txt(s.title)}
                </strong>

                <p>
                    ${txt(s.organization)}
                </p>

                <p>
                    Estado: ${txt(s.status)}
                </p>

                <p>
                    Rol: ${txt(s.role)}
                </p>

            </article>
        `).join("");

    showScreen("sources");
}

/* =========================================================
   ESCENARIOS
========================================================= */

async function openScenarios() {

    if (!cache.scenarios) {
        cache.scenarios = await api("/scenarios");
    }

    document.getElementById("scenarioGrid").innerHTML =
        cache.scenarios.scenarios.map(s => {

            const action =
                s.module_id === "integral"
                    ? "startIntegral()"
                    : `startTraining('${s.module_id}')`;

            return `
                <article
                    class="scenarioCard clickable"
                    onclick="${action}"
                >
                    <span class="moduleStatus">
                        ${txt(s.status).toUpperCase()}
                    </span>

                    <h2>
                        ${txt(s.name)}
                    </h2>

                    <p>
                        ${txt(s.description)}
                    </p>
                </article>
            `;

        }).join("");

    showScreen("scenarios");
}

/* =========================================================
   ENTRENAMIENTO
========================================================= */

async function startTraining(id) {

    const d =
        await api(
            `/academy/module/${id}/training?shuffle=true`
        );

    runTraining(d, id);
}

async function startIntegral() {

    const d =
        await api("/academy/integral?limit=20");

    runTraining(d, "integral");
}

function runTraining(d, id) {

    activeTraining = d.training || [];
    activeMeta = d.metadata || {};
    activeMeta._id = id;

    current = 0;
    score = 100;
    log = [];
    seconds = 0;

    const p = getProgress();

    p.intentos =
        (p.intentos || 0) + 1;

    saveProgress(p);

    document.getElementById("trainingTitle").textContent =
        activeMeta.module_name ||
        "Entrenamiento";

    document.getElementById("liveScore").textContent =
        score;

    showScreen("training");

    renderStep();
    startTimer();
}

function renderStep() {

    const s =
        activeTraining[current];

    if (!s) {
        finishTraining();
        return;
    }

    document.getElementById("question").textContent =
        s.question;

    document.getElementById("stepCounter").textContent =
        `${current + 1}/${activeTraining.length}`;

    document.getElementById("sourceBadge").textContent =
        s.source_id || "—";

    document.getElementById("feedback").innerHTML =
        "";

    const opts =
        (s.options || [])
            .slice()
            .sort(() => Math.random() - 0.5);

    document.getElementById("options").innerHTML =
        opts.map((o, i) => `
            <button
                class="optionBtn"
                data-i="${i}"
            >
                ${txt(o.text)}
            </button>
        `).join("");

    document
        .querySelectorAll(".optionBtn")
        .forEach(b => {

            b.onclick = () =>
                choose(
                    opts[
                        Number(b.dataset.i)
                    ]
                );
        });
}

function choose(o) {

    score = Math.max(
        0,
        Math.min(
            100,
            score + Number(o.score || 0)
        )
    );

    document.getElementById("liveScore").textContent =
        score;

    const status =
        o.status === "correct"
            ? "Adecuada"
            : o.status === "critical_error"
                ? "Error crítico"
                : "Requiere revisión";

    const question =
        activeTraining[current];

    log.push({
        n: current + 1,
        text: o.text,
        status: status,
        impact: Number(o.score || 0),
        source: question?.source_id,
        module:
            question?.module_name ||
            activeMeta.module_name
    });

    document.getElementById("feedback").innerHTML = `
        <div class="feedbackBox">

            <strong>
                ${status}
            </strong>

            <br>

            ${
                o.status === "correct"
                    ? "Respuesta coherente con la fuente cargada."
                    : "Revisar el fundamento doctrinario en el análisis posterior."
            }

        </div>
    `;

    document
        .querySelectorAll(".optionBtn")
        .forEach(b => {
            b.disabled = true;
        });

    current++;

    setTimeout(
        renderStep,
        750
    );
}

/* =========================================================
   CRONÓMETRO
========================================================= */

function startTimer() {

    stopTimer();

    timer = setInterval(() => {

        seconds++;

        document.getElementById("time").textContent =
            `${String(
                Math.floor(seconds / 60)
            ).padStart(2, "0")}:${String(
                seconds % 60
            ).padStart(2, "0")}`;

    }, 1000);
}

function stopTimer() {

    if (timer) {
        clearInterval(timer);
        timer = null;
    }
}

/* =========================================================
   RESULTADOS
========================================================= */

function finishTraining() {

    stopTimer();

    const correct =
        log.filter(
            x => x.status === "Adecuada"
        ).length;

    const critical =
        log.filter(
            x => x.status === "Error crítico"
        ).length;

    document.getElementById("finalScore").textContent =
        score;

    document.getElementById("analysisSummary").innerHTML = `
        <p>
            Respuestas adecuadas:
            <strong>${correct}</strong>
        </p>

        <p>
            Errores críticos:
            <strong>${critical}</strong>
        </p>

        <p>
            Tiempo:
            <strong>
                ${String(
                    Math.floor(seconds / 60)
                ).padStart(2, "0")}
                :
                ${String(
                    seconds % 60
                ).padStart(2, "0")}
            </strong>
        </p>
    `;

    const p = getProgress();

    p.evaluaciones_completadas =
        (p.evaluaciones_completadas || 0) + 1;

    p.mejor_puntaje =
        p.mejor_puntaje == null
            ? score
            : Math.max(
                p.mejor_puntaje,
                score
            );

    p.ultimo_puntaje =
        score;

    p.por_modulo =
        p.por_modulo || {};

    const id =
        activeMeta._id || "general";

    const old =
        p.por_modulo[id] || {
            intentos: 0,
            mejor: null
        };

    old.intentos++;

    old.mejor =
        old.mejor == null
            ? score
            : Math.max(
                old.mejor,
                score
            );

    p.por_modulo[id] =
        old;

    saveProgress(p);

    document.getElementById("decisionLog").innerHTML =
        log.length
            ? log.map(x => `
                <div class="entry">

                    <strong>
                        ${x.n}. ${txt(x.status)}
                    </strong>

                    <p>
                        ${txt(x.text)}
                    </p>

                    <p>
                        Impacto ${x.impact}
                        · Fuente ${txt(x.source)}
                        · ${txt(x.module)}
                    </p>

                </div>
            `).join("")
            : "Sin decisiones registradas.";

    lastResult = {
        fecha:
            new Date().toISOString(),

        modulo:
            activeMeta.module_name,

        puntaje:
            score,

        tiempo_segundos:
            seconds,

        decisiones:
            log
    };

    showScreen("analysis");
}

function exportResult() {

    if (!lastResult) return;

    const blob =
        new Blob(
            [
                JSON.stringify(
                    lastResult,
                    null,
                    2
                )
            ],
            {
                type: "application/json"
            }
        );

    const a =
        document.createElement("a");

    a.href =
        URL.createObjectURL(blob);

    a.download =
        `egs_resultado_${Date.now()}.json`;

    a.click();

    URL.revokeObjectURL(a.href);
}

/* =========================================================
   BUSCADOR
========================================================= */

async function searchContent(q) {

    const box =
        document.getElementById("searchResults");

    q =
        q.trim().toLowerCase();

    if (q.length < 2) {
        box.innerHTML = "";
        return;
    }

    if (!cache.academy) {
        cache.academy =
            await api("/academy/modules");
    }

    let results = [];

    for (const m of cache.academy.modules) {

        if (
            (
                m.name +
                " " +
                m.description +
                " " +
                m.area
            )
                .toLowerCase()
                .includes(q)
        ) {
            results.push({
                type: "Módulo",
                title: m.name,
                id: m.id,
                desc: m.description
            });
        }

        try {

            const d =
                await api(
                    `/academy/module/${m.id}`
                );

            for (const s of d.sections || []) {

                if (
                    (
                        s.title +
                        " " +
                        (s.summary || "")
                    )
                        .toLowerCase()
                        .includes(q)
                ) {
                    results.push({
                        type: "Tema",
                        title: s.title,
                        id: m.id,
                        desc: m.name
                    });
                }
            }

        } catch (e) {
            console.warn(e);
        }
    }

    box.innerHTML =
        results
            .slice(0, 12)
            .map(r => `
                <article
                    class="tile clickable"
                    onclick="openModule('${r.id}')"
                >
                    <span>
                        ${txt(r.type)}
                    </span>

                    <h2>
                        ${txt(r.title)}
                    </h2>

                    <p>
                        ${txt(r.desc)}
                    </p>

                </article>
            `)
            .join("");
}

/* =========================================================
   SIMULADOR 3D
========================================================= */

let egs3dModulePromise = null;

function egs3dMessage(message, error = false) {

    const target =
        document.getElementById("sim3d");

    if (!target) return;

    target.innerHTML = `
        <div class="${error ? "simError" : "simLoading"}">
            ${txt(message)}
        </div>
    `;
}

async function loadEGS3D() {

    if (window.EGS3D) {
        return window.EGS3D;
    }

    if (egs3dModulePromise) {
        return egs3dModulePromise;
    }

    egs3dMessage(
        "Cargando escenario 3D..."
    );

    egs3dModulePromise =
        import("./simulator.js")
            .then(() => {

                if (!window.EGS3D) {
                    throw new Error(
                        "El módulo 3D no registró su API."
                    );
                }

                return window.EGS3D;
            })
            .catch(err => {

                console.error(
                    "EGS 3D:",
                    err
                );

                egs3dMessage(
                    "No se pudo iniciar el simulador 3D. " +
                    String(
                        err.message || err
                    ),
                    true
                );

                egs3dModulePromise =
                    null;

                throw err;
            });

    return egs3dModulePromise;
}

async function openSimulator() {

    showScreen("simulator");

    try {
        const e =
            await loadEGS3D();

        await e.init();
        e.start();

    } catch (e) {
        console.error(e);
    }
}

async function setSimulatorQuality(v) {

    try {
        const e =
            await loadEGS3D();

        e.setQuality(v);

    } catch (e) {
        console.error(e);
    }
}

async function reset3DScenario() {

    try {
        const e =
            await loadEGS3D();

        e.reset();

    } catch (e) {
        console.error(e);
    }
}

async function simAction(action) {

    try {
        const e =
            await loadEGS3D();

        e.action(action);

    } catch (e) {
        console.error(e);
    }
}

async function finish3DSimulation() {

    try {
        const e =
            await loadEGS3D();

        e.finish();

    } catch (e) {
        console.error(e);
    }
}

/* =========================================================
   ARRANQUE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    boot
);