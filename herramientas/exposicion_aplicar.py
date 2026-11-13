"""Vuelca herramientas/exposicion.json en data/*.json. Uso: python3 -I herramientas/exposicion_aplicar.py <repo_dir>
exposicion.json: {isin: {sec: [[nombre, % fondo, % índice|null]], geo: [...], cal: {ig, hy, sr (sin rating), nota}, aprox: true}}
Campos que escribe en cada fila: sectores, geografia, calidad, destaca (texto automático: mayores sobre/infraponderaciones frente al índice), aprox.
Los porcentajes salen de la ficha del mes (tablas; si solo había gráfico, se leyó el gráfico y va aprox: true)."""
import json, os, sys

def destaca(lista, etiqueta):
    c = [(n, p, i) for n, p, *r in lista for i in [r[0] if r else None] if i is not None]
    if len(c) < 3:
        return ''
    d = sorted(((p - i, n, p, i) for n, p, i in c), reverse=True)
    sob, sub = d[0], d[-1]
    t = []
    if sob[0] >= 3:
        t.append('%s: %s (%s %% frente a %s %% del índice)' % ('Sobreponderación' if etiqueta == 's' else 'Más peso', sob[1], str(sob[2]).replace('.', ','), str(sob[3]).replace('.', ',')))
    if sub[0] <= -3:
        t.append('%s: %s (%s %% frente a %s %%)' % ('Infraponderación' if etiqueta == 's' else 'Menos peso', sub[1], str(sub[2]).replace('.', ','), str(sub[3]).replace('.', ',')))
    return '. '.join(t)

repo = sys.argv[1]
ex = json.load(open(os.path.join(repo, 'herramientas', 'exposicion.json')))
for nom in ('renta_fija', 'renta_variable'):
    p = os.path.join(repo, 'data', nom + '.json'); filas = json.load(open(p))
    for f in filas:
        e = ex.get(f['isin'], {})
        f['sectores'] = e.get('sec', []); f['geografia'] = e.get('geo', []); f['calidad'] = e.get('cal', {})
        partes = [x for x in (destaca(f['sectores'], 's'), destaca(f['geografia'], 'g')) if x]
        f['destaca'] = (e.get('dest', '') or ('. '.join(partes) + ('.' if partes else '')))
        f['aprox'] = bool(e.get('aprox'))
    json.dump(filas, open(p, 'w'), ensure_ascii=False, indent=1)
print({k: sum(1 for f in json.load(open(os.path.join(repo, 'data', k + '.json'))) if f['sectores'] or f['geografia'] or f['calidad']) for k in ('renta_fija', 'renta_variable')})
