"""Busca en fundinfo la ficha mensual (MR) más reciente de cada ISIN y la compara con la que ya tenemos.
Uso: python3 -I herramientas/buscar_fichas.py <repo_dir> [--todo]
Imprime isin, fecha actual, fecha más reciente en fundinfo, idioma y URL. Escribe /tmp/fichas_nuevas.json = {isin: {fecha, idioma, url}}
(solo las que son más nuevas que la actual, o todas con --todo)."""
import json, os, re, subprocess, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor

def fundinfo(isin):
    t = subprocess.run(['curl', '-s', '-m', '40', '-b', 'DU=ES-prof; PrivacyPolicy=true', '-H', 'X-Requested-With: XMLHttpRequest',
                        'https://www.fundinfo.com/es/ES-prof/Fund/Data?&OFST020000=' + isin], capture_output=True, text=True).stdout
    docs = []
    for u in set(re.findall(r'https://api\.fundinfo\.com/document/[^"\s<>\\]+', t)):
        m = re.search(r'/MR_([A-Z]{2})_([a-z]{2})_%s_[A-Z]+_(\d{4}-\d{2}-\d{2})\.pdf' % isin, u)
        if m:
            docs.append((m.group(3), 1 if m.group(2) == 'es' else 0, m.group(2), u))
    return sorted(docs, reverse=True)

if __name__ == '__main__':
    repo = sys.argv[1]; todo = '--todo' in sys.argv
    filas = []
    for n, k in (('renta_fija', 'fecha'), ('renta_variable', 'fecha_ficha')):
        for r in json.load(open(os.path.join(repo, 'data', n + '.json'))):
            d = r[k]; iso = '%s-%s-%s' % (d[6:], d[3:5], d[:2]) if re.match(r'\d\d/\d\d/\d{4}$', d) else ''
            filas.append((r['isin'], r['fondo'], iso))
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda x: fundinfo(x[0]), filas))
    nuevas = {}
    for (isin, fondo, iso), docs in zip(filas, res):
        if docs:
            f, _, idi, u = docs[0]
            marca = 'NUEVA' if f > iso else '='
            print(isin, fondo[:34].ljust(34), iso or 'sin', '->', f, idi, marca)
            if f > iso or todo: nuevas[isin] = {'fecha': f, 'idioma': idi, 'url': u}
        else:
            print(isin, fondo[:34].ljust(34), iso or 'sin', '-> fundinfo sin ficha')
    json.dump(nuevas, open('/tmp/fichas_nuevas.json', 'w'), indent=1)
