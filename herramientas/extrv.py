import re,sys
f=sys.argv[1]; T=open(f'crv/{f}.txt',errors='ignore').read(); L=open(f'crv/{f}.lay',errors='ignore').read()
flat=re.sub(r'\s+',' ',T)
out=[]
for pat in [r'(PER|P/E|Price.?to.?earnings|Precio/beneficio|Ratio PER)[^\n]{0,60}',r'(Rentabilidad por dividendo|Dividend yield|Rendimiento por dividendo|Yield)[^\n]{0,50}',r'(Patrimonio|Tamaño del fondo|Fund size|Activos netos|Total net assets|AUM|Patrimonio total)[^\n]{0,60}',r'(Beta|Volatilidad)[^\n]{0,40}',r'(Número de (posiciones|valores|títulos)|Number of holdings)[^\n]{0,30}']:
    m=re.search(pat,L,re.I)
    if m: out.append(re.sub(r'\s+',' ',m.group(0))[:110])
# return table lines
for m in re.finditer(r'\n[^\n]*(1 ?(mes|M|month|Mes)\b)[^\n]*\n(?:[^\n]*\n){0,4}',L):
    out.append('RT: '+re.sub(r'\s+',' ',m.group(0))[:300]); break
cm=re.search(r'(comentario[^.]{0,40}|commentary|análisis de los gestores|revisión del mercado|market review|resumen del gestor|evolución del fondo|perspectivas|portfolio review|fund review|performance review)(.{0,1300})',flat,re.I)
print('\n'.join(out)); print('CM:',(cm.group(0) if cm else flat[:600])[:800])
