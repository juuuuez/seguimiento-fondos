import sys,re,glob
R=re.compile(r'^(?:[^\w]*)(AAA|AA|A|BBB|BB|B|CCC|CC|C|D|NR|N/R|Sin rating|Sin calificar|Sin calificaci[oó]n|Not rated|No rated|Other|Otros|Investment Grade|High Yield|Grado de inversi[oó]n|Alto rendimiento|Efectivo|Cash|Liquidez)\b[^\d]{0,25}[-+]?\d',re.I)
G=re.compile(r'estados unidos|ee\.? ?uu|usa\b|reino unido|francia|alemania|jap[oó]n|china|suiza|pa[ií]ses bajos|espa[ñn]a|italia|irlanda|canad|europa|emergent|united states|germany|france|netherlands|united kingdom|italy|spain|norway|sweden|brasil|m[eé]xico|australia|luxemb|portugal|b[eé]lgica|noruega|suecia|dinamarca|finlandia|grecia|turqu|polonia|rumania|hungr',re.I)
for isin in sys.argv[2:]:
    f=glob.glob('/tmp/t/*_%s.txt'%isin)[0]; t=open(f).read().split('\f')
    best=None
    for i,p in enumerate(t[:6]):
        r=[re.sub(r'\s{3,}',' ¦ ',l.strip()) for l in p.split('\n') if R.search(l.strip())]
        g=[re.sub(r'\s{3,}',' ¦ ',l.strip()) for l in p.split('\n') if G.search(l) and re.search(r'\d',l) and len(l.strip())<150 and not re.search(r'(?i)copyright|©|inscrit|folleto|www\.|domicil|autoriz|sede|suiza,',l)]
        sc=len(r)*2+len(g)
        if best is None or sc>best[0]: best=(sc,i+1,r,g)
    print('#####',isin,'p',best[1]); n=int(sys.argv[1])
    print('RAT:',' | '.join(x[:60] for x in best[2][:14])); print('GEO:',' | '.join(x[:70] for x in best[3][:n]))
