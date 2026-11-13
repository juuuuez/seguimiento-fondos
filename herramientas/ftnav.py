"""Rentabilidades de la clase EUR con el historico de precios de FT (markets.ft.com). Mas historia que quefondos: sirve para 10 años
y para los fondos que quefondos no tiene.

Modo 1 (un fondo):   python3 -I ftnav.py ISIN:AAAA-MM-DD [ISIN:AAAA-MM-DD ...]
    imprime mes, YTD, 1 año, 3, 5 y 10 años anualizados. La fecha es el ultimo dia habil del mes de referencia.
Modo 2 (lista):      python3 -I ftnav.py --lista <lista.tsv> <AAAA-MM-DD> <salida.json>
    para todos los ISIN del TSV (primera columna). Salida: {isin: {mes, ytd, 1a, 3a, 5a, 10a}} con null donde no hay historico.
"""
import json, re, html, subprocess, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"


def get(u):
    return subprocess.run(['curl', '-sSL', '-A', UA, '-m', '40', u], capture_output=True, text=True, errors='ignore').stdout


def years_ago(d, n):
    try:
        return d.replace(year=d.year - n)
    except ValueError:
        return d.replace(year=d.year - n, day=28)


def xid_of(isin, cur='EUR'):
    p = get(f'https://markets.ft.com/data/funds/tearsheet/historical?s={isin}:{cur}')
    m = re.search(r'xid&quot;:&quot;(\d+)', p)
    return m.group(1) if m else None


def prices(xid, a, b):
    out = {}
    try:
        d = json.loads(get('https://markets.ft.com/data/equities/ajax/get-historical-prices?startDate=%s&endDate=%s&symbol=%s'
                           % (a.strftime('%Y/%m/%d'), b.strftime('%Y/%m/%d'), xid)))
    except Exception:
        return out
    t = re.sub(r'\|+', '|', html.unescape(re.sub(r'<[^>]+>', '|', d.get('html', ''))))
    for m in re.finditer(r'[A-Z][a-z]+day, ([A-Z][a-z]+ \d\d, \d{4})\|[^|]*\|[\d.,]+\|[\d.,]+\|[\d.,]+\|([\d.,]+)', t):
        out[dt.datetime.strptime(m.group(1), '%B %d, %Y').date()] = float(m.group(2).replace(',', ''))
    return out


def near(xid, target, back=12):
    """ultimo precio <= target (ventana de `back` dias hacia atras)."""
    p = prices(xid, target - dt.timedelta(days=back), target + dt.timedelta(days=2))
    c = [k for k in p if k <= target]
    return (p[max(c)], max(c)) if c else (None, None)


def rets(isin, end):
    xid = xid_of(isin)
    if not xid:
        return None
    e = near(xid, end, 8)
    if e[0] is None or (end - e[1]).days > 6:
        return None
    out = {}
    for key, tgt in [('mes', end.replace(day=1) - dt.timedelta(days=1)), ('ytd', dt.date(end.year - 1, 12, 31)), ('1a', years_ago(end, 1))]:
        v = near(xid, tgt)
        out[key] = round((e[0] / v[0] - 1) * 100, 2) if v[0] else None
    for key, n in [('3a', 3), ('5a', 5), ('10a', 10)]:
        v = near(xid, years_ago(end, n), 12)
        yrs = (e[1] - v[1]).days / 365.25 if v[0] else 0
        out[key] = round(((e[0] / v[0]) ** (1 / yrs) - 1) * 100, 2) if v[0] and yrs > 0 else None
    return out


if __name__ == '__main__':
    if sys.argv[1] == '--lista':
        isins = [l.split('\t')[0].strip() for l in open(sys.argv[2]) if l.strip()]
        end = dt.date.fromisoformat(sys.argv[3])
        with ThreadPoolExecutor(6) as ex:
            res = dict(zip(isins, ex.map(lambda i: rets(i, end), isins)))
        json.dump(res, open(sys.argv[4], 'w'))
        print('con datos:', sum(1 for v in res.values() if v), 'de', len(res))
    else:
        for arg in sys.argv[1:]:
            isin, end = arg.split(':')
            print(isin, rets(isin, dt.date.fromisoformat(end)))
