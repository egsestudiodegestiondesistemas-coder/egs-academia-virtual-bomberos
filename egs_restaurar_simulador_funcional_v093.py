from pathlib import Path
import shutil

ROOT=Path.cwd()
if not (ROOT/"web").exists() and (ROOT/"05 - Código Fuente"/"egs-fire-academy"/"web").exists():
    ROOT=ROOT/"05 - Código Fuente"/"egs-fire-academy"

SOURCE=ROOT/"_backup_v100"
WEB=ROOT/"web"

if not SOURCE.exists():
    raise SystemExit("ERROR: no encuentro _backup_v100. No se realizó ningún cambio.")

def latest(prefix):
    files=sorted(SOURCE.glob(prefix+"*.bak"), key=lambda p:p.stat().st_mtime, reverse=True)
    if not files:
        raise SystemExit(f"ERROR: no encuentro backup para {prefix}")
    return files[0]

mapping={
    "index.html": latest("index.html."),
    "app.js": latest("app.js."),
    "simulator.js": latest("simulator.js.")
}

safety=ROOT/"_backup_antes_de_restaurar_v093"
safety.mkdir(exist_ok=True)

for name,src in mapping.items():
    dst=WEB/name
    if dst.exists():
        shutil.copy2(dst,safety/name)
    shutil.copy2(src,dst)
    print("[OK]",name,"<-",src.name)

print()
print("="*72)
print("SIMULADOR RESTAURADO A LA ULTIMA BASE FUNCIONAL ANTERIOR A v1.0")
print("="*72)
print("No se modificaron los módulos académicos ni la base de conocimiento.")
print()
print("Ahora reiniciá únicamente el servidor web:")
print("python -m http.server 8000 -d web")
print("y recargá Chrome con Ctrl+Shift+R.")
