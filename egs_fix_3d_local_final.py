from pathlib import Path
import shutil, urllib.request
from datetime import datetime

ROOT = Path.cwd()
if not (ROOT/"web").exists() and (ROOT/"05 - Código Fuente"/"egs-fire-academy"/"web").exists():
    ROOT = ROOT/"05 - Código Fuente"/"egs-fire-academy"

WEB = ROOT/"web"
INDEX = WEB/"index.html"
SIM = WEB/"simulator.js"
THREE = WEB/"three.module.js"

if not INDEX.exists() or not SIM.exists():
    raise SystemExit("ERROR: no encuentro web/index.html o web/simulator.js")

BACKUP = ROOT/"_backup_fix_3d_local"
BACKUP.mkdir(exist_ok=True)

for p in (INDEX, SIM):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(p, BACKUP/f"{p.name}.{stamp}.bak")

print("Descargando Three.js para usarlo LOCALMENTE...")
urls = [
    "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
    "https://unpkg.com/three@0.180.0/build/three.module.js"
]
ok = False
last_error = None
for url in urls:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = r.read()
        if len(data) < 100000:
            raise RuntimeError("archivo Three.js demasiado pequeño")
        THREE.write_bytes(data)
        print("[OK] web/three.module.js descargado:", len(data), "bytes")
        ok = True
        break
    except Exception as e:
        last_error = e
        print("[AVISO] Falló", url, "->", e)

if not ok:
    raise SystemExit("ERROR: no pude descargar Three.js. Último error: "+str(last_error))

sim = SIM.read_text(encoding="utf-8")

# Reemplazar cualquier import remoto / import-map por módulo local.
import_lines = []
for line in sim.splitlines():
    s = line.strip()
    if s.startswith('import * as THREE from '):
        import_lines.append('import * as THREE from "./three.module.js";')
    elif s.startswith('import { OrbitControls } from '):
        # El simulador restaurado funcional no necesita OrbitControls.
        continue
    else:
        import_lines.append(line)
sim = "\n".join(import_lines)

# Si no tiene import de THREE, agregarlo.
if 'import * as THREE from "./three.module.js";' not in sim:
    sim = 'import * as THREE from "./three.module.js";\n' + sim

# Prueba visible de carga.
if 'EGS_3D_LOCAL_READY' not in sim:
    sim += '\nwindow.EGS_3D_LOCAL_READY = true;\nconsole.log("EGS 3D LOCAL: motor listo");\n'

SIM.write_text(sim, encoding="utf-8")

index = INDEX.read_text(encoding="utf-8")

# Quitar referencias anteriores al simulator.js.
import re
index = re.sub(r'<script[^>]*src=["\']simulator\.js[^"\']*["\'][^>]*></script>', '', index, flags=re.I)

# Quitar importmap viejo si existe.
index = re.sub(r'<!-- EGS_THREE_IMPORTMAP_START -->.*?<!-- EGS_THREE_IMPORTMAP_END -->', '', index, flags=re.S)

# Asegurar app.js + simulator module en orden estable.
index = index.replace('<script src="app.js"></script>',
                      '<script src="app.js?v=final3d"></script>\n<script type="module" src="simulator.js?v=final3d"></script>')

INDEX.write_text(index, encoding="utf-8")

print()
print("="*78)
print("FIX 3D LOCAL APLICADO")
print("="*78)
print("[OK] Three.js ya no depende de CDN durante el uso")
print("[OK] simulator.js usa ./three.module.js")
print("[OK] index.html fuerza carga nueva")
print("[OK] backup creado")
print()
print("Ahora:")
print("1) Ctrl+C al servidor WEB si está corriendo")
print("2) python -m http.server 8000 -d web")
print("3) Chrome -> Ctrl+Shift+R")
print()
print("NO hace falta reiniciar la API.")
print("Backup:", BACKUP)
