from pathlib import Path
import shutil, re
from datetime import datetime

ROOT = Path.cwd()
ALT = ROOT / "05 - Código Fuente" / "egs-fire-academy"
if not (ROOT / "web").exists() and (ALT / "web").exists():
    ROOT = ALT

if not (ROOT / "web").exists():
    raise SystemExit("ERROR: ejecutá este archivo dentro de egs-fire-academy.")

BACKUP = ROOT / "_backup_before_ui_encoding_repair"
BACKUP.mkdir(exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

targets = []
for rel in [
    "index.html","app.js","styles.css","simulation-core-client.js",
    "web/index.html","web/app.js","web/styles.css","web/simulation-core-client.js"
]:
    p = ROOT / rel
    if p.exists():
        targets.append(p)

MOJI = ("Ã","Â","â€","â†","ðŸ","ï¿½","Ãƒ")

def score(s):
    return sum(s.count(x) for x in MOJI)

def decode_once(s):
    candidates = [s]
    for enc in ("cp1252","latin1"):
        try:
            candidates.append(s.encode(enc).decode("utf-8"))
        except Exception:
            pass
    return min(candidates, key=score)

def repair(s):
    prev = s
    for _ in range(4):
        nxt = decode_once(prev)
        if score(nxt) >= score(prev):
            break
        prev = nxt
    return prev

print("Reparación segura de codificación UI")
print("-"*70)

for p in targets:
    original = p.read_text(encoding="utf-8", errors="replace")
    before = score(original)
    fixed = repair(original)
    after = score(fixed)
    shutil.copy2(p, BACKUP / f"{p.parent.name}__{p.name}.{stamp}.bak")
    if after < before:
        p.write_text(fixed, encoding="utf-8", newline="\n")
        print(f"[OK] {p.relative_to(ROOT)} | mojibake {before} -> {after}")
    else:
        print(f"[SIN CAMBIOS] {p.relative_to(ROOT)} | mojibake {before}")

pairs = [
    (ROOT/"index.html", ROOT/"web"/"index.html"),
    (ROOT/"app.js", ROOT/"web"/"app.js"),
    (ROOT/"styles.css", ROOT/"web"/"styles.css"),
    (ROOT/"simulation-core-client.js", ROOT/"web"/"simulation-core-client.js"),
]
for src,dst in pairs:
    if src.exists() and dst.exists():
        a = src.read_text(encoding="utf-8", errors="replace")
        b = dst.read_text(encoding="utf-8", errors="replace")
        best = a if score(a) <= score(b) else b
        src.write_text(best, encoding="utf-8", newline="\n")
        dst.write_text(best, encoding="utf-8", newline="\n")

for p in [ROOT/"index.html", ROOT/"web"/"index.html"]:
    if p.exists():
        t = p.read_text(encoding="utf-8", errors="replace")
        if '<meta charset="UTF-8">' not in t and "<head>" in t:
            t = t.replace("<head>", '<head>\n<meta charset="UTF-8">', 1)
        t = re.sub(r'simulation-core-client\.js\?v=\d+', 'simulation-core-client.js?v=60', t)
        t = re.sub(r'app\.js\?v=\d+', 'app.js?v=60', t)
        t = re.sub(r'styles\.css\?v=\d+', 'styles.css?v=60', t)
        p.write_text(t, encoding="utf-8", newline="\n")

print("-"*70)
print("TERMINADO")
print("Backup:", BACKUP)
print("No hace git push.")
