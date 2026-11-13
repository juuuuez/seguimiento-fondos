"""Miniatura (primera página) de cada ficha PDF. Uso: python3 -I herramientas/miniaturas.py <repo_dir>
Escribe fichas/miniaturas/<mismo nombre>.jpg y el campo `mini` en data/*.json. Borra miniaturas huérfanas."""
import json, os, subprocess, sys, tempfile, glob
repo = sys.argv[1]
dest = os.path.join(repo, 'fichas', 'miniaturas'); os.makedirs(dest, exist_ok=True)
usadas = set()
for nom in ('renta_fija', 'renta_variable'):
    p = os.path.join(repo, 'data', nom + '.json'); filas = json.load(open(p))
    for f in filas:
        f['mini'] = ''
        if not f.get('pdf'): continue
        base = os.path.splitext(os.path.basename(f['pdf']))[0]
        out = os.path.join(dest, base + '.jpg')
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(['pdftoppm', '-jpeg', '-jpegopt', 'quality=72', '-scale-to-x', '420', '-scale-to-y', '-1', '-f', '1', '-l', '1', '-singlefile', os.path.join(repo, f['pdf']), os.path.join(td, 'p')], check=True)
            os.replace(os.path.join(td, 'p.jpg'), out)
        f['mini'] = 'fichas/miniaturas/' + base + '.jpg'; usadas.add(out)
    json.dump(filas, open(p, 'w'), ensure_ascii=False, indent=1)
for old in glob.glob(os.path.join(dest, '*.jpg')):
    if old not in usadas: os.remove(old)
print(len(usadas), 'miniaturas')
