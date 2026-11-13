"""Rentabilidades (mes, YTD, 1 año) de la clase EUR de cada fondo a partir del valor liquidativo historico de quefondos.com.

Uso:  python3 -I navret.py <lista.tsv> <salida.json> <AAAA-MM-DD fin de mes>
Ejemplo: python3 -I navret.py rv.tsv rv_nav.json 2026-11-30
La lista es un TSV con el ISIN en la primera columna. Los fondos sin dato salen como null (probar entonces ftnav.py).
"""
import re, sys, subprocess, datetime as dt, json, html

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
END = dt.date.fromisoformat(sys.argv[3])
PREV_END = END.replace(day=1) - dt.timedelta(days=1)
YEAR_END = dt.date(END.year - 1, 12, 31)
try:
    YEAR_AGO = END.replace(year=END.year - 1)
except ValueError:
    YEAR_AGO = END.replace(year=END.year - 1, day=28)


def get(u):
    return subprocess.run(['curl', '-sSL', '-A', UA, '-m', '30', u], capture_output=True, text=True, errors='ignore').stdout


res = {}
for l in open(sys.argv[1]):
    isin = l.split('\t')[0].strip()
    if not isin:
        continue
    s = get(f'https://www.quefondos.com/es/fondos/ficha/index.html?isin={isin}')
    m = re.search(r'var fondo = (\[\[.*?\]\])', s, re.S)
    d = {}
    if m:
        for mo, da, y, v in re.findall(r'\["(\d\d)/(\d\d)/(\d{4})",\s*([\d.]+)\]', m.group(1)):
            d[dt.date(int(y), int(mo), int(da))] = float(v)
    t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)))
    pm = re.search(r'Patrimonio \(miles de euros\): ([\d.,]+)', t)
    if not d:
        res[isin] = None
        print(isin, 'sin datos')
        continue
    ks = sorted(d)

    def at(x):
        c = [k for k in ks if k <= x]
        return (d[c[-1]], c[-1]) if c else (None, None)

    e, a, y, o = at(END), at(PREV_END), at(YEAR_END), at(YEAR_AGO)
    ok = e[1] and e[1] >= END - dt.timedelta(days=6)

    def r(x):
        return round((e[0] / x[0] - 1) * 100, 2) if (ok and x[0] and (e[1] - x[1]).days > 15) else None

    res[isin] = {'mes': r(a), 'ytd': r(y), '1a': r(o), 'nav': e[0], 'navdate': str(e[1]), 'patr_miles': pm.group(1) if pm else None}
    print(isin, res[isin])
json.dump(res, open(sys.argv[2], 'w'))
