"""Genera el Excel de seguimiento a partir de los datos del repositorio (data/*.json).

Uso:  python3 -I herramientas/generar_excel.py <carpeta_repo> <salida.xlsx> <web|local> [AAAA-MM]
  web   -> los enlaces a las fichas apuntan a la web publica (para el Excel de descargas/ del repositorio)
  local -> los enlaces son relativos: "Fichas fondos/<AAAA-MM>/<archivo>.pdf" (para el Excel de Drive, junto a la carpeta de fichas)
Despues recalcular con LibreOffice y comprobar cero errores de formula.
"""
import json, os, re, sys, urllib.parse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

REPO, OUTFILE, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
MONTH = sys.argv[4] if len(sys.argv) > 4 else ''
WEB = 'https://juuuuez.github.io/seguimiento-fondos/'
D = lambda n: json.load(open(os.path.join(REPO, 'data', n), encoding='utf-8'))
rf, rv, vis, meta = D('renta_fija.json'), D('renta_variable.json'), D('vision_general.json'), D('meta.json')
CIERRE = meta.get('cierre', '')


def link(pdf):
    if not pdf:
        return None
    return WEB + urllib.parse.quote(pdf) if MODE == 'web' else 'Fichas fondos/%s/%s' % (MONTH, os.path.basename(pdf))


ARIAL = 'Arial'
H = Font(name=ARIAL, bold=True, color='FFFFFF', size=10); HF = PatternFill('solid', fgColor='1F3864')
B = Font(name=ARIAL, size=10); BB = Font(name=ARIAL, size=10, bold=True); T = Font(name=ARIAL, size=14, bold=True, color='1F3864')
H2 = Font(name=ARIAL, size=11, bold=True, color='1F3864'); SMALL = Font(name=ARIAL, size=9, italic=True)
BLUE = Font(name=ARIAL, size=10, color='0000FF'); LINK = Font(name=ARIAL, size=10, color='0563C1', underline='single')
GREEN = Font(name=ARIAL, size=10, color='008000')
thin = Side(style='thin', color='BFBFBF'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
ALT = PatternFill('solid', fgColor='F2F2F2'); WR = Alignment(wrap_text=True, vertical='top')
PCT = '0.00%;[Red]-0.00%;-'; NUM = '0.00'
fr = lambda v: None if v is None else v / 100


def header(ws, row, names):
    for c, h in enumerate(names, 1):
        x = ws.cell(row, c, h); x.font = H; x.fill = HF; x.border = BOX
        x.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')


def num(ws, r, c, v, fmt):
    x = ws.cell(r, c, v if v is not None else 'n.d.')
    x.font = BLUE if v is not None else B
    x.alignment = Alignment(horizontal='right')
    if v is not None:
        x.number_format = fmt


def vision_sheet(wb, title, bloque, idx):
    ws = wb.create_sheet(title, idx); ws.column_dimensions['A'].width = 125
    ws['A1'] = 'Visión general — ' + bloque + (' (cierre %s)' % CIERRE if CIERRE else ''); ws['A1'].font = T
    row, sec = 2, None
    for r in [r for r in vis if r['bloque'] == bloque]:
        if r['seccion'] and r['seccion'] != sec:
            sec = r['seccion']; x = ws.cell(row, 1, sec); x.font = H2; ws.row_dimensions[row].height = 20; row += 1
        x = ws.cell(row, 1, r['texto']); x.font = B; x.alignment = WR
        ws.row_dimensions[row].height = max(15, 15 * (len(r['texto']) // 150 + 1)); row += 1


wb = Workbook()
# ---------------- Resumen RF
ws = wb.active; ws.title = 'Resumen RF'
ws['A1'] = 'Seguimiento de fondos de renta fija' + (' — cierre %s' % CIERRE if CIERRE else ''); ws['A1'].font = T
ws['A2'] = ('Datos tal como los publica cada gestora en su ficha (fecha en la columna F). Rentabilidades de la clase en EUR. '
            'Azul = dato; negro = fórmula. Los yields de PIMCO y de dos fondos de Man se muestran ya ajustados a EUR (ver "Tipo de yield").'); ws['A2'].font = SMALL
hdr = ['Fondo', 'ISIN', 'Gestora', 'Tipo', 'Fuente', 'Fecha ficha', 'TIR / Yield', 'Tipo de yield', 'Duración (años)', 'Rent. último mes', 'Rent. YTD',
       'Rent. 1 año', 'Rent. 3 años (anual.)', 'Rent. 5 años (anual.)', 'Rent. 10 años (anual.)', 'Breakeven 12m (pb)', 'Ranking YTD', 'Patrimonio', 'Ficha (PDF)', 'Pestaña']
header(ws, 4, hdr)
first, last = 5, 4 + len(rf)
tabs = {}
for k, f in enumerate(rf):
    r = first + k
    tab = re.sub(r'[\[\]\*\?/\\:]', '', f['fondo'])[:26].strip() + ' ' + f['isin'][-4:]
    tabs[f['isin']] = tab
    for c, v in enumerate([f['fondo'], f['isin'], f['gestora'], f['tipo'], f['fuente'], f['fecha']], 1):
        ws.cell(r, c, v).font = B
    num(ws, r, 7, fr(f['tir']), PCT); ws.cell(r, 8, f['tipo_yield']).font = B
    num(ws, r, 9, f['duracion'], NUM); num(ws, r, 10, fr(f['mes']), PCT); num(ws, r, 11, fr(f['ytd']), PCT); num(ws, r, 12, fr(f['a1']), PCT)
    num(ws, r, 13, fr(f.get('r3')), PCT); num(ws, r, 14, fr(f.get('r5')), PCT); num(ws, r, 15, fr(f.get('r10')), PCT)
    x = ws.cell(r, 16, f'=IFERROR(IF(AND(ISNUMBER(G{r}),ISNUMBER(I{r}),I{r}>0),G{r}/I{r}*10000,"n.a."),"n.a.")'); x.number_format = '0'; x.font = B; x.alignment = Alignment(horizontal='right')
    x = ws.cell(r, 17, f'=IF(ISNUMBER(K{r}),RANK(K{r},$K${first}:$K${last},0),"n.d.")'); x.font = B; x.alignment = Alignment(horizontal='center')
    ws.cell(r, 18, f['patrimonio']).font = B
    u = link(f['pdf'])
    if u:
        x = ws.cell(r, 19, 'Abrir PDF'); x.hyperlink = u; x.font = LINK
    else:
        ws.cell(r, 19, '—').font = B
    x = ws.cell(r, 20, 'Ver detalle'); x.hyperlink = f"#'{tab}'!A1"; x.font = LINK
    for c in range(1, 21):
        ws.cell(r, c).border = BOX
        if k % 2:
            ws.cell(r, c).fill = ALT
s = last + 2
ws.cell(s, 1, 'Estadísticas del universo').font = BB
stats = [('Media TIR', f'=AVERAGE(G{first}:G{last})', PCT), ('Mediana TIR', f'=MEDIAN(G{first}:G{last})', PCT), ('Media duración', f'=AVERAGE(I{first}:I{last})', NUM),
         ('Media rent. YTD', f'=AVERAGE(K{first}:K{last})', PCT), ('Fondos con YTD negativo', f'=COUNTIF(K{first}:K{last},"<0")', '0'),
         ('Fondos con dato YTD', f'=COUNT(K{first}:K{last})', '0'),
         ('Mejor YTD', f'=INDEX(A{first}:A{last},MATCH(MAX(K{first}:K{last}),K{first}:K{last},0))', None),
         ('Peor YTD', f'=INDEX(A{first}:A{last},MATCH(MIN(K{first}:K{last}),K{first}:K{last},0))', None)]
for j, (l, fm, fmt) in enumerate(stats):
    ws.cell(s + 1 + j, 1, l).font = B; x = ws.cell(s + 1 + j, 2, fm); x.font = B
    if fmt:
        x.number_format = fmt
ws.cell(s + 10, 1, 'Notas').font = BB
notes = ['Breakeven 12m (pb) = TIR / duración × 10.000: cuántos puntos básicos pueden subir los tipos en un año antes de que el cupón deje de compensar la pérdida de precio. Aproximación; no aplica a fondos sin TIR o duración.',
         'Los yields no son homogéneos: YTM, YTW, TIR de devengo o rentabilidad promedio según la gestora. Storm publica el suyo en NOK.',
         'Todas las rentabilidades son de la clase en EUR (cuando la ficha era de otra clase se recalculan con el valor liquidativo de la clase correcta). A 3, 5 y 10 años, rentabilidad anualizada; vacío si el fondo no tiene tanto historial.',
         'Fondos sin ficha este mes: ver la pestaña "Pendientes".']
for j, t in enumerate(notes):
    ws.merge_cells(start_row=s + 11 + j, start_column=1, end_row=s + 11 + j, end_column=12)
    x = ws.cell(s + 11 + j, 1, '• ' + t); x.font = Font(name=ARIAL, size=9); x.alignment = WR; ws.row_dimensions[s + 11 + j].height = 30
for i, w in enumerate([38, 15, 20, 24, 22, 11, 10, 26, 10, 10, 10, 10, 11, 11, 11, 11, 9, 14, 11, 11], 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[4].height = 44; ws.freeze_panes = 'C5'; ws.auto_filter.ref = f'A4:T{last}'

vision_sheet(wb, 'Visión RF', 'Renta fija', 1)

# ---------------- Resumen RV
BL = ['Renta variable', 'Mixto', 'Metales / recursos']
rv = sorted(rv, key=lambda f: BL.index(f['bloque']) if f['bloque'] in BL else 9)
wr = wb.create_sheet('Resumen RV', 2)
wr['A1'] = 'Seguimiento de renta variable, mixtos y metales' + (' — cierre %s' % CIERRE if CIERRE else ''); wr['A1'].font = T
wr['A2'] = 'Rentabilidades de la clase en EUR calculadas con el valor liquidativo; métricas y posiciones de la ficha mensual (fecha en la columna F). Azul = dato; negro = fórmula.'; wr['A2'].font = SMALL
header(wr, 4, ['Fondo', 'ISIN', 'Gestora', 'Bloque', 'Estilo / categoría', 'Fecha ficha', 'Rent. último mes', 'Rent. YTD', 'Rent. 1 año', 'Rent. 3 años (anual.)',
               'Rent. 5 años (anual.)', 'Rent. 10 años (anual.)', 'Ranking YTD (bloque)', 'PER', 'Rent. dividendo', 'Principales posiciones', 'Ficha (PDF)', 'Detalle'])
f1, l1 = 5, 4 + len(rv)
for k, f in enumerate(rv):
    r = f1 + k
    for c, v in enumerate([f['fondo'], f['isin'], f['gestora'], f['bloque'], f['estilo'], f['fecha_ficha']], 1):
        wr.cell(r, c, v).font = B
    num(wr, r, 7, fr(f['mes']), PCT); num(wr, r, 8, fr(f['ytd']), PCT); num(wr, r, 9, fr(f['a1']), PCT)
    num(wr, r, 10, fr(f.get('r3')), PCT); num(wr, r, 11, fr(f.get('r5')), PCT); num(wr, r, 12, fr(f.get('r10')), PCT)
    x = wr.cell(r, 13, f'=IF(ISNUMBER(H{r}),SUMPRODUCT(($D${f1}:$D${l1}=D{r})*ISNUMBER($H${f1}:$H${l1})*($H${f1}:$H${l1}>H{r}))+1,"n.d.")'); x.font = B; x.alignment = Alignment(horizontal='center')
    wr.cell(r, 14, f['per'] or '—').font = B; wr.cell(r, 15, f['dividendo'] or '—').font = B; wr.cell(r, 16, f['posiciones'] or '—').font = B
    u = link(f['pdf'])
    if u:
        x = wr.cell(r, 17, 'Abrir PDF'); x.hyperlink = u; x.font = LINK
    else:
        wr.cell(r, 17, '—').font = B
    for c in range(1, 19):
        wr.cell(r, c).border = BOX
        if k % 2:
            wr.cell(r, c).fill = ALT
s2 = l1 + 2
wr.cell(s2, 1, 'Estadísticas por bloque').font = BB
for j, (l, fm, fmt) in enumerate([
        ('Media YTD renta variable', f'=AVERAGEIF(D{f1}:D{l1},"Renta variable",H{f1}:H{l1})', PCT),
        ('Media YTD mixtos', f'=AVERAGEIF(D{f1}:D{l1},"Mixto",H{f1}:H{l1})', PCT),
        ('Media YTD metales / recursos', f'=AVERAGEIF(D{f1}:D{l1},"Metales / recursos",H{f1}:H{l1})', PCT),
        ('Fondos RV con YTD negativo', f'=COUNTIFS(D{f1}:D{l1},"Renta variable",H{f1}:H{l1},"<0")', '0'),
        ('Mejor YTD', f'=INDEX(A{f1}:A{l1},MATCH(MAX(H{f1}:H{l1}),H{f1}:H{l1},0))', None),
        ('Peor YTD', f'=INDEX(A{f1}:A{l1},MATCH(MIN(H{f1}:H{l1}),H{f1}:H{l1},0))', None)]):
    wr.cell(s2 + 1 + j, 1, l).font = B; x = wr.cell(s2 + 1 + j, 2, fm); x.font = B
    if fmt:
        x.number_format = fmt
for i, w in enumerate([40, 15, 22, 18, 30, 11, 10, 10, 10, 11, 11, 11, 10, 14, 14, 55, 11, 9], 1):
    wr.column_dimensions[get_column_letter(i)].width = w
wr.row_dimensions[4].height = 44; wr.freeze_panes = 'C5'; wr.auto_filter.ref = f'A4:R{l1}'

# ---------------- Detalle RV
dd = wb.create_sheet('Detalle RV', 3); dd.column_dimensions['A'].width = 24; dd.column_dimensions['B'].width = 110
dd['A1'] = 'Detalle por fondo — renta variable, mixtos y metales'; dd['A1'].font = T
x = dd['A2']; x.value = '← Volver al resumen'; x.hyperlink = "#'Resumen RV'!A1"; x.font = LINK
i = 4
for k, f in enumerate(rv):
    x = dd.cell(i, 1, f['fondo']); x.font = H2; dd.merge_cells(start_row=i, start_column=1, end_row=i, end_column=2)
    y = wr.cell(f1 + k, 18, 'Ver'); y.hyperlink = f"#'Detalle RV'!A{i}"; y.font = LINK
    i += 1
    rent = '   '.join(lab + ': ' + (('%+.2f%%' % f[key]).replace('.', ',') if f.get(key) is not None else 'n.d.')
                     for lab, key in [('Último mes', 'mes'), ('YTD', 'ytd'), ('1 año', 'a1'), ('3 años', 'r3'), ('5 años', 'r5'), ('10 años', 'r10')])
    for l, v in [('ISIN / Gestora', '%s · %s' % (f['isin'], f['gestora'])), ('Estilo', f['estilo']), ('Rentabilidades', rent), ('Principales posiciones', f['posiciones'] or '—'),
                 ('Qué dice la gestora', f['comentario']), ('Lectura propia', f['lectura'])]:
        dd.cell(i, 1, l).font = BB; x = dd.cell(i, 2, v); x.font = B; x.alignment = WR
        dd.row_dimensions[i].height = max(15, 15 * (len(str(v)) // 125 + 1)); i += 1
    i += 1

vision_sheet(wb, 'Visión RV', 'Renta variable', 4)

# ---------------- Una pestaña por fondo de renta fija
for k, f in enumerate(rf):
    w = wb.create_sheet(tabs[f['isin']]); r = first + k
    w.column_dimensions['A'].width = 26; w.column_dimensions['B'].width = 105
    w['A1'] = f['fondo']; w['A1'].font = T
    x = w['A2']; x.value = '← Volver al resumen'; x.hyperlink = "#'Resumen RF'!A1"; x.font = LINK
    i = 4
    for l, key in [('Fondo', 'fondo'), ('ISIN', 'isin'), ('Gestora', 'gestora'), ('Tipo', 'tipo'), ('Fecha de la ficha', 'fecha'), ('Fuente', 'fuente')]:
        w.cell(i, 1, l).font = BB; w.cell(i, 2, f[key]).font = B; i += 1
    for l, col, fmt in [('TIR / Yield', 'G', PCT), ('Tipo de yield', 'H', None), ('Duración (años)', 'I', NUM), ('Rentabilidad último mes', 'J', PCT),
                        ('Rentabilidad YTD', 'K', PCT), ('Rentabilidad 1 año', 'L', PCT), ('Rentabilidad 3 años (anualizada)', 'M', PCT),
                        ('Rentabilidad 5 años (anualizada)', 'N', PCT), ('Rentabilidad 10 años (anualizada)', 'O', PCT), ('Patrimonio', 'R', None)]:
        w.cell(i, 1, l).font = BB; x = w.cell(i, 2, f"='Resumen RF'!{col}{r}"); x.font = GREEN; x.alignment = Alignment(horizontal='left')
        if fmt:
            x.number_format = fmt
        i += 1
    i += 1
    for l, key in [('Qué ha pasado', 'que_ha_pasado'), ('Posicionamiento', 'posicionamiento'), ('Perspectivas / opinión', 'perspectivas'), ('Ha aportado (+)', 'aporta'), ('Ha restado (−)', 'resta')]:
        w.cell(i, 1, l).font = BB; w.cell(i, 1).alignment = WR
        x = w.cell(i, 2, f[key]); x.font = B; x.alignment = WR; w.row_dimensions[i].height = max(15, 15 * (len(f[key]) // 120 + 1)); i += 1
    u = link(f['pdf'])
    if u:
        i += 1; w.cell(i, 1, 'Ficha (PDF)').font = BB; y = w.cell(i, 2, os.path.basename(f['pdf'])); y.hyperlink = u; y.font = LINK

# ---------------- Pendientes
p = wb.create_sheet('Pendientes')
p['A1'] = 'Fondos sin ficha mensual este mes'; p['A1'].font = T
header(p, 3, ['Fondo', 'ISIN', 'Motivo', 'Acción propuesta'])
pend = [('LBPAM ISR Absolute Return Credit L', 'FR0014004IP7', 'No está en fundinfo; el reporting del distribuidor es un PDF de imágenes sin texto.', 'Reintentar en la web de LBPAM o subir la ficha a mano.'),
        ('Cartesio Funds Income R', 'LU1966822956', 'Cartesio no publica informe mensual en abierto.', 'Usar la carta trimestral o pedir la ficha al comercial.'),
        ('Sigma Investments', 'LU1984948874', 'El ISIN no coincide con ninguna clase de Sigma Short Mid-Term encontrada.', 'Confirmar el ISIN.')]
for f in rf:
    if not f['pdf']:
        pend.append((f['fondo'], f['isin'], 'Sin ficha mensual pública. ' + (f.get('que_ha_pasado') or ''), 'Reintentar el próximo mes.'))
for f in rv:
    if not f['pdf']:
        pend.append((f['fondo'], f['isin'], 'Sin ficha mensual pública o web no accesible. ' + (f.get('comentario') or ''), 'Rentabilidades por valor liquidativo en Resumen RV; reintentar el próximo mes.'))
for j, row in enumerate(pend):
    for c, v in enumerate(row, 1):
        x = p.cell(4 + j, c, v); x.font = B; x.alignment = WR
for c, wd in zip('ABCD', [36, 15, 60, 55]):
    p.column_dimensions[c].width = wd

wb.save(OUTFILE)
print('guardado', OUTFILE, len(wb.sheetnames), 'hojas')
