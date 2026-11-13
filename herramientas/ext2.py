import re, sys
i = sys.argv[1]
L = open(f'crv/{i}.lay', errors='ignore').read()
T = re.sub(r'\s+', ' ', open(f'crv/{i}.txt', errors='ignore').read())

def g(p, n=90):
    m = re.search(p, L, re.I)
    return re.sub(r'\s+', ' ', m.group(0))[:n] if m else ''

o = [g(r'(\bPER\b|\bP/E\b|Precio ?/ ?beneficio|Price/Earnings|PE ratio)[^\n]{0,70}'),
     g(r'(Rentabilidad por dividendo|Dividend yield|Rend\. por dividendo|Rendimiento por dividendo|Rentabilidad de dividendo)[^\n]{0,60}'),
     g(r'(Número de (posiciones|valores|títulos|acciones|emisores)|Number of (holdings|stocks))[^\n]{0,40}')]
m = re.search(r'(?:Diez (?:principales|mayores) posiciones|Principales posiciones|10 principales|Top 10|Mayores posiciones|Principales valores|Top holdings|Ten largest|Principales inversiones|Posiciones principales)(?P<t>.{0,260})', T, re.I)
o.append('TOP: ' + (m.group('t')[:240] if m else ''))
cm = None
for k in [r'Comentario del (?:gestor|fondo)', r'Comentarios? de (?:gestión|mercado|rentabilidad)', r'Comentarios sobre rentabilidad',
          r'Comentario mensual', r'(?:Fund|Portfolio|Manager.s|Market) (?:commentary|review)', r'Commentary',
          r'Revisión (?:del mercado|de la cartera)', r'Análisis de (?:los gestores|mercado)', r'Rentabilidad y posicionamiento',
          r'Resumen (?:mensual|del mes)', r'Perspectivas']:
    mm = re.search(k + r'.{0,1100}', T, re.I)
    if mm:
        cm = mm.group(0)
        break
print(' | '.join(x for x in o if x))
print('CM:', (cm or '—')[:700])
