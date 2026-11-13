import re,glob,os,sys
KM=r'(TIR|yield to (maturity|worst)|rentabilidad a vencimiento|rendimiento a vencimiento|YTM|YTW|duraci[oó]n|duration|rating medio|calificaci[oó]n media|average rating|patrimonio|AUM|fund size|tama[ñn]o del fondo|activos netos|net assets|YTD|en el a[ñn]o|año en curso|1 a[ñn]o|1 year|1 mes|1 month|mes\b|spread)'
CM=r'(comentario|commentary|comentarios del gestor|an[aá]lisis de los gestores|market review|revisi[oó]n del mercado|perspectivas|outlook|evoluci[oó]n|lo que ha pasado|fund review|portfolio review|rentabilidad del fondo|resumen del gestor|positioning|posicionamiento|contribu)'
f=sys.argv[1]
L=open(f,encoding='utf-8',errors='ignore').read().split('\n')
met=[]
for i,l in enumerate(L):
    if re.search(KM,l,re.I) and len(l)<160:
        ctx=' '.join(L[i:i+3])[:200]
        if re.search(r'\d',ctx): met.append(ctx)
seen=set(); m2=[]
for x in met:
    k=x[:60]
    if k not in seen: seen.add(k); m2.append(x)
# commentary: longest prose block near commentary keywords
text='\n'.join(L)
best=''
for m in re.finditer(CM,text,re.I):
    seg=text[m.start():m.start()+3000]
    prose=sum(1 for l in seg.split('\n') if len(l)>70)
    if prose>len(best.split('\n'))*0 and prose>sum(1 for l in best.split('\n') if len(l)>70): best=seg
print('### METRICS'); print('\n'.join(m2[:16]))
print('### COMMENT'); print(re.sub(r'\n',' ',best)[:2200])
