"""Comentario LITERAL del gestor (solo si está en español) de cada ficha PDF.
Uso: python3 -I herramientas/comentarios.py <repo_dir>
Lee data/*.json, abre cada pdf con pdftotext -raw y escribe el campo `literal` en cada fila
(cadena vacía si la ficha no trae comentario en español; entonces la web enseña el resumen `que_ha_pasado`).
Reglas por familia de ficha (inicio -> fin). Si una gestora cambia el formato, ajustar REGLAS."""
import json, re, subprocess, sys, os

# (regex de inicio, regex de fin) sobre el texto -raw. El texto va desde el final del inicio hasta el principio del fin.
REGLAS = {
    'r4':      (r'Comentario del Gestor\n', r'\nDatos del Fondo'),                       # Renta 4 (ISIN ES0173xxxx, ES0128xxxx, ES0176xxxx)
    'dnca':    (r'Comentario de gestión\n', r'\nTerminado de redactar'),
    'lazard':  (r'Comentario de gestión\n', r'\n\x0cLAZARD CREDIT OPPORTUNITIES'),
    'carmig':  (r'ENTORNO DE MERCADO\n', r'\nPERSPECTIVAS Y ESTRATEGIA'),               # Carmignac Global Bond (entorno + rendimiento)
    'robeco':  (r'Comentarios sobre rentabilidad\n', r'\nExpectativas del gestor'),
    'olea':    (r'Comentario de mercado\nOlea Neutral FI,\nValor Liquidativo desde Inicio del Fondo\n', r'\nRegistrado y regulado:'),
    'dunas':   (r'Vuelve la diferenciación|Los mercados|Septiembre|Octubre', r'media histórica\.'),
}
POR_ISIN = {
    'ES0128520006': 'r4', 'ES0176954008': 'r4', 'ES0128522002': 'r4', 'ES0173321003': 'r4',
    'ES0173286008': 'r4', 'ES0173130024': 'r4', 'ES0173128002': 'r4', 'ES0173130016': 'r4',
    'LU1694789535': 'dnca', 'FR0010230490': 'lazard', 'LU0336083497': 'carmig', 'LU0203975437': 'robeco',
    'ES0118537002': 'olea', 'ES0175414012': 'dunas', 'ES0175316019': 'dunas',
}


def reflow(txt):
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    if not lines:
        return ''
    ancho = max(len(l) for l in lines)
    out, cur = [], ''
    for l in lines:
        cur = (cur + ' ' + l).strip()
        if re.search(r'[.:»”)]$', l) and len(l) < ancho * 0.88:
            out.append(cur); cur = ''
    if cur:
        out.append(cur)
    return '\n\n'.join(out)


def extraer(pdf, regla):
    t = subprocess.run(['pdftotext', '-raw', pdf, '-'], capture_output=True, text=True).stdout
    ini, fin = REGLAS[regla]
    if regla == 'dunas':
        m = re.search(r'(Vuelve la diferenciación.*?media histórica\.)', t, re.S)
        return reflow(m.group(1)) if m else ''
    m = re.search(ini + r'(.*?)(?=' + fin + ')', t, re.S)
    return reflow(m.group(1)) if m else ''


if __name__ == '__main__':
    repo = sys.argv[1]
    for nom in ('renta_fija', 'renta_variable'):
        p = os.path.join(repo, 'data', nom + '.json')
        filas = json.load(open(p))
        for f in filas:
            regla = POR_ISIN.get(f['isin'])
            f['literal'] = extraer(os.path.join(repo, f['pdf']), regla) if regla and f.get('pdf') else ''
            print(nom, f['isin'], len(f['literal']))
        json.dump(filas, open(p, 'w'), ensure_ascii=False, indent=1)
