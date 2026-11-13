import sys,re,glob
S=r'tecnolog|financ|finanz|industria|salud|sanit|consumo|energ[ií]a|materiales|comunicaci|inmobil|servicios p|utilities|telecom|health|technology|financials|staples|discretionary|materials|real estate|software|semicond|farma|biotec|banc|seguros|oro\b|plata|metal|miner|gold|silver|defen|aeroesp|bienes|producto'
G=r'estados unidos|ee\.? ?uu|usa\b|reino unido|francia|alemania|jap[oó]n|china|suiza|pa[ií]ses bajos|espa[ñn]a|canad|europa|emergent|asia|am[eé]rica|italia|irlanda|corea|taiw|india|brasil|australia|north america|united states|europe|japan|uk\b|germany|france|netherlands|switzerland|norteam|sud[aá]frica|m[eé]xico|noruega|suecia|dinamarca|per[uú]|chile|ghana|tanzania|burkina'
def lines(p):
    o=[]
    for l in p.split('\n'):
        c=re.sub(r'\s{3,}',' ¦ ',l.strip())
        if re.search(r'\d',c) and re.search(S+'|'+G,c,re.I) and len(c)<170 and not re.search(r'(?i)copyright|©|inscrit|folleto|ISIN|www\.|Suiza,|domicil|autoriz',c): o.append(c)
    return o
for isin in sys.argv[2:]:
    f=glob.glob('/tmp/t/*_%s.txt'%isin)[0]; t=open(f).read().split('\f')
    sc=[len(lines(p)) for p in t[:6]]; pg=sc.index(max(sc))
    L=lines(t[pg]); print('#####',isin,'p',pg+1,sc)
    print('\n'.join(L[:int(sys.argv[1])]))
