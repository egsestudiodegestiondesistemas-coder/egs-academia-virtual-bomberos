
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path.cwd()
ALT = ROOT / "05 - Código Fuente" / "egs-fire-academy"
if not (ROOT / "web").exists() and (ALT / "web").exists():
    ROOT = ALT

if not (ROOT / "web").exists():
    raise SystemExit("ERROR: ejecutá este archivo dentro de egs-fire-academy.")

BACKUP = ROOT / "_backup_utf8_final"
BACKUP.mkdir(exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

targets = [
    ROOT/"index.html",
    ROOT/"web"/"index.html",
    ROOT/"simulation-core-client.js",
    ROOT/"web"/"simulation-core-client.js",
]

replacements = {
    "Ã¡":"á","Ã©":"é","Ã­":"í","Ã³":"ó","Ãº":"ú","Ã±":"ñ",
    "Ã":"Á","Ã‰":"É","Ã":"Í","Ã“":"Ó","Ãš":"Ú","Ã‘":"Ñ",
    "Â¿":"¿","Â¡":"¡","Â°":"°","Â·":"·",
    "â†’":"→","â€”":"—","â€“":"–","â€œ":"“","â€":"”",
    "â€˜":"‘","â€™":"’","â€¢":"•","â€¦":"…",
    "Ã¼":"ü","Ãœ":"Ü","Ã§":"ç","Ã‡":"Ç",
}

def repair(text):
    # 1) deterministic replacements
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # 2) safe line-level recovery for remaining common mojibake
    fixed = []
    for line in text.splitlines(True):
        if any(mark in line for mark in ("Ã","Â","â€","â†")):
            for enc in ("cp1252","latin1"):
                try:
                    candidate = line.encode(enc).decode("utf-8")
                    # accept only if it removes mojibake markers
                    old_score = sum(line.count(m) for m in ("Ã","Â","â€","â†"))
                    new_score = sum(candidate.count(m) for m in ("Ã","Â","â€","â†"))
                    if new_score < old_score:
                        line = candidate
                        break
                except Exception:
                    pass
        fixed.append(line)
    return "".join(fixed)

for p in targets:
    if not p.exists():
        continue
    shutil.copy2(p, BACKUP / f"{p.name}.{stamp}.bak")
    text = p.read_text(encoding="utf-8", errors="replace")
    text = repair(text)
    # ensure HTML explicitly declares UTF-8
    if p.name == "index.html":
        if '<meta charset="UTF-8">' not in text and "<head>" in text:
            text = text.replace("<head>", '<head>\n<meta charset="UTF-8">', 1)
        text = text.replace("simulation-core-client.js?v=30","simulation-core-client.js?v=51")
        text = text.replace("simulation-core-client.js?v=50","simulation-core-client.js?v=51")
    p.write_text(text, encoding="utf-8", newline="\n")
    print("[OK]", p)

# Ensure web client is exact copy of root client
root_client = ROOT/"simulation-core-client.js"
web_client = ROOT/"web"/"simulation-core-client.js"
if root_client.exists():
    shutil.copy2(root_client, web_client)

print("="*72)
print("UTF-8 CORREGIDO")
print("="*72)
print("[OK] Textos mojibake reparados")
print("[OK] UTF-8 explícito en HTML")
print("[OK] Cache del cliente actualizado a v51")
print("[OK] Cliente raíz y web sincronizados")
print("Backup:", BACKUP)
print("NO hace git push.")
