from pathlib import Path
import shutil, re, json
from datetime import datetime

ROOT = Path.cwd()
ALT = ROOT / "05 - Código Fuente" / "egs-fire-academy"
if not (ROOT / "web").exists() and (ALT / "web").exists():
    ROOT = ALT

WEB = ROOT / "web"
if not WEB.exists():
    raise SystemExit("ERROR: ejecutá este archivo dentro de egs-fire-academy.")

BACKUP = ROOT / "_backup_release_candidate_v1"
BACKUP.mkdir(exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for rel in ["index.html","web/index.html","app.js","web/app.js","styles.css","web/styles.css"]:
    p = ROOT / rel
    if p.exists():
        shutil.copy2(p, BACKUP / f"{rel.replace('/','__')}.{stamp}.bak")

# 1) UX / naming / cache-busting
for rel in ["index.html","web/index.html"]:
    p = ROOT / rel
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8")

    replacements = {
        "ENTRAR AL SIMULADOR 3D":"IR AL SIMULADOR",
        "ENTRENAR EN 3D":"SIMULADOR",
        "Entrenar 3D":"Simulador",
        "Simulador 3D":"Simulador",
        "SIMULADOR OPERACIONAL 3D":"SIMULADOR OPERACIONAL"
    }
    for a,b in replacements.items():
        t = t.replace(a,b)

    t = re.sub(r'styles\.css\?v=\d+', 'styles.css?v=40', t)
    t = re.sub(r'app\.js\?v=\d+', 'app.js?v=40', t)
    t = re.sub(r'simulator\.js\?v=\d+', 'simulator.js?v=40', t)
    t = re.sub(r'simulation-core-client\.js\?v=\d+', 'simulation-core-client.js?v=40', t)

    if '<p class="simNotice">' in t:
        t = re.sub(
            r'<p class="simNotice">.*?</p>',
            '<p class="simNotice"><strong>Simulador interactivo beta.</strong> '
            'El entorno actual entrena secuencias, decisiones y análisis doctrinario. '
            'No constituye CFD, gemelo digital físico ni reemplaza prácticas presenciales. '
            'La arquitectura está preparada para integrar un motor de alta fidelidad.</p>',
            t,
            flags=re.S
        )

    p.write_text(t, encoding="utf-8")

# 2) release styling
extra_css = '''
/* ===== EGS RELEASE CANDIDATE v1 ===== */
.releaseBadge{display:inline-flex;align-items:center;gap:7px;padding:6px 9px;border:1px solid #3a424b;border-radius:999px;color:#aeb6bf;font-size:9px;letter-spacing:1px}
.simNotice strong{color:#cfd5db}
'''

for rel in ["styles.css","web/styles.css"]:
    p = ROOT / rel
    if p.exists():
        t = p.read_text(encoding="utf-8")
        if "EGS RELEASE CANDIDATE v1" not in t:
            t += "\n" + extra_css
        p.write_text(t, encoding="utf-8")

# 3) release documentation
release = {
    "product":"EGS | Academia Virtual de Bomberos",
    "release":"RC1",
    "date":datetime.now().isoformat(timespec="seconds"),
    "status":"candidate",
    "components":{
        "academy":"operational",
        "evaluations":"operational",
        "library":"operational",
        "simulation_core":"development-integrated",
        "web_simulator":"beta",
        "high_fidelity_digital_twin":"planned"
    },
    "deployment":{
        "frontend":"GitHub Pages",
        "api":"Render",
        "api_url":"https://egs-academia-bomberos-api.onrender.com"
    },
    "professional_scope":{
        "web_simulator":"Entrenamiento interactivo de secuencias, decisiones y AAR.",
        "not_claimed":[
            "CFD certificado",
            "gemelo digital físico",
            "predicción científica exacta del incendio",
            "sustitución del entrenamiento práctico"
        ]
    }
}

(ROOT/"RELEASE_RC1.json").write_text(
    json.dumps(release, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

readme = '''# EGS | Academia Virtual de Bomberos — Release Candidate 1

## Qué se entrega
- Campus orientado a experiencia de usuario.
- Academia modular.
- Fichas de estudio.
- Evaluaciones con revisión y fuente.
- Biblioteca doctrinaria.
- Catálogo de simulaciones.
- Simulation Core con estados, eventos, timeline y After Action Review.
- Simulador web interactivo beta.

## Alcance del simulador beta
El simulador web permite entrenar secuencias, decisiones y registrar AAR.
No debe presentarse como CFD, gemelo digital físico ni como reemplazo del entrenamiento práctico.

## Arquitectura futura
El Simulation Core está desacoplado del motor gráfico y preparado para conectar un motor de alta fidelidad sin rehacer Academia, reglas, trazabilidad ni AAR.

## Producción
Frontend: GitHub Pages.
API: Render.

## Regla de publicación
Probar localmente antes de commit/push.
'''
(ROOT/"README_RELEASE_RC1.md").write_text(readme, encoding="utf-8")

# 4) integrity checks
required = [
    WEB/"index.html",
    WEB/"app.js",
    WEB/"styles.css",
    WEB/"simulator.js",
    WEB/"simulation-core-client.js",
]
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit("ERROR: faltan archivos requeridos:\n" + "\n".join(missing))

print("="*78)
print("EGS RELEASE CANDIDATE 1 PREPARADA")
print("="*78)
print("[OK] Academia preservada")
print("[OK] Evaluaciones preservadas")
print("[OK] Biblioteca preservada")
print("[OK] SIMULADOR como nombre definitivo")
print("[OK] Simulador beta con alcance profesional explícito")
print("[OK] Simulation Core + AAR preservados")
print("[OK] Documentación de entrega creada")
print("[OK] Backup automático creado")
print()
print("Backup:", BACKUP)
print("NO hace git push.")
print()
print("Prueba local:")
print("python -m http.server 8000 -d web")
