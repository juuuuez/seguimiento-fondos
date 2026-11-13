"""Alternativa a navret.py: rentabilidades de la clase EUR con el historico de precios de FT (markets.ft.com).

Uso:  python3 -I ftnav.py ISIN:AAAA-MM-DD [ISIN:AAAA-MM-DD ...]
donde la fecha es el ultimo dia habil del mes de referencia (p. ej. LU0336083497:2026-11-30).
Imprime NAV final, NAV mes anterior, NAV cierre del año anterior y NAV hace un año, y las tres rentabilidades.
"""
import json, re, html, subprocess, sys, datetime as dt

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"


def get(u):
    return subprocess.run(['curl', '-sSL', '-A', UA, '-m', '30', u], capture_output=True, text=True).stdout


def navs(isin, end, cur='EUR'):
    p = get(f'https://markets.ft.com/data/funds/tearsheet/historical?s={isin}:{cur}')
    m = re.search(r'xid&quot;:&quot;(\d+)', p)
    if not m:
        return None
    xid = m.group(1)
    out = {}
    try:
        ago = end.replace(year=end.year - 1)
    except ValueError:
        ago = end.replace(year=end.year - 1, day=28)
    ranges = [(ago - dt.timedelta(days=10), ago + dt.timedelta(days=10)),
              (dt.date(end.year - 1, 12, 15), dt.date(end.year, 1, 10)),
              (end - dt.timedelta(days=70), end + dt.timedelta(days=7))]
    for a, b in ranges:
        try:
            d = json.loads(get('https://markets.ft.com/data/equities/ajax/get-historical-prices?startDate=%s&endDate=%s&symbol=%s'
                               % (a.strftime('%Y/%m/%d'), b.strftime('%Y/%m/%d'), xid)))
        except Exception:
            continue
        t = re.sub(r'\|+', '|', html.unescape(re.sub(r'<[^>]+>', '|', d.get('html', ''))))
        for mm in re.finditer(r'[A-Z][a-z]+day, ([A-Z][a-z]+ \d\d, \d{4})\|[^|]*\|[\d.,]+\|[\d.,]+\|[\d.,]+\|([\d.,]+)', t):
            out[dt.datetime.strptime(mm.group(1), '%B %d, %Y').date()] = float(mm.group(2).replace(',', ''))
    return out


def at(d, x):
    c = [k for k in d if k <= x]
    return (d[max(c)], max(c)) if c else (float('nan'), None)


for arg in sys.argv[1:]:
    isin, end = arg.split(':')
    E = dt.date.fromisoformat(end)
    d = navs(isin, E)
    if not d:
        print(isin, 'sin datos')
        continue
    try:
        ago = E.replace(year=E.year - 1)
    except ValueError:
        ago = E.replace(year=E.year - 1, day=28)
    e, m, y, o = at(d, E), at(d, E.replace(day=1) - dt.timedelta(days=1)), at(d, dt.date(E.year - 1, 12, 31)), at(d, ago)
    print(isin, 'fin', e, 'mes ant.', m, 'cierre año ant.', y, 'hace 1 año', o,
          '| mes %.2f ytd %.2f 1a %.2f' % ((e[0] / m[0] - 1) * 100, (e[0] / y[0] - 1) * 100, (e[0] / o[0] - 1) * 100))
