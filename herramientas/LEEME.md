# Actualización mensual de la web de seguimiento de fondos

Este repositorio es la web pública (GitHub Pages) y también la fuente de verdad de los datos.
Cada día 10 una sesión de Claude descarga las fichas nuevas, actualiza `data/` y `fichas/`, y hace push.
La web (`index.html`) no se toca: lee `data/*.json` al cargarse.

## Estructura
- `index.html`: la página. Solo cambiarla si algo falla.
- `data/renta_fija.json`, `data/renta_variable.json`, `data/vision_general.json`, `data/meta.json`: datos que lee la web.
- `fichas/<Nombre del fondo> - Ficha <mes abreviado> <año>.pdf`: una ficha por fondo (mes abreviado: ene feb mar abr may jun jul ago sep oct nov dic).
- `herramientas/`: este proceso. `rf.tsv` (fondos de renta fija) y `rv.tsv` (renta variable, mixtos y metales; 4ª columna: RV, MX o MT) con ISIN de la clase EN EUR. `navret.py` y `ftnav.py` (rentabilidades por valor liquidativo), `ext*.py` (extracción de texto de las fichas).

## Esquema de los datos (porcentajes en unidades de %, p. ej. 12.92 = 12,92 %)
`renta_fija.json`, lista de objetos: isin, fondo, gestora, tipo, fecha (dd/mm/aaaa de la ficha), tir, tipo_yield, duracion, mes, ytd, a1, breakeven_pb, patrimonio, fuente, que_ha_pasado, posicionamiento, perspectivas, aporta, resta, ficha (siempre ""), pdf ("fichas/<archivo>.pdf").
- `breakeven_pb = round(tir / duracion * 100)`; null si falta tir o duración.
- `mes`, `ytd`, `a1`: rentabilidad de la clase EUR a fin de mes. Null si no hay dato.
`renta_variable.json`: isin, fondo, gestora, bloque ("Renta variable", "Mixto" o "Metales / recursos"), estilo, fecha_ficha ("dd/mm/aaaa" o "Sin ficha"), mes, ytd, a1, per, dividendo, posiciones, comentario, lectura, ficha (""), pdf.
`vision_general.json`: lista de {bloque ("Renta fija" o "Renta variable"), seccion, texto}; las secciones salen en orden; usa los mismos títulos de sección que los actuales.
`meta.json`: {"cierre": "dd/mm/aaaa" (fin de mes de las rentabilidades), "actualizado": "dd/mm/aaaa" (día de la ejecución)}.

## Pasos
1. Partir de los datos actuales de `data/` (son los del mes anterior: punto de comparación y plantilla).
2. Fichas: para cada ISIN de `rf.tsv` y `rv.tsv`, ficha mensual más reciente de la clase EUR.
   - fundinfo (la mayoría): `curl -b "DU=ES-prof; PrivacyPolicy=true" -H "X-Requested-With: XMLHttpRequest" "https://www.fundinfo.com/es/ES-prof/Fund/Data?&OFST020000=<ISIN>"` devuelve JSON con enlaces `https://api.fundinfo.com/document/..._MR_ES_<es|en>_<ISIN>_..._<fecha>.pdf`. Coger el MR más reciente (preferir español). El usuario aceptó el aviso legal de fundinfo como inversor profesional en España el 12/11/2026. Fondos de gestoras que no son miembros devuelven "Únicamente publica información..." y se buscan en su web.
   - Renta 4: `https://www.r4.com/productos-inversion/fondos/fichas/<ISIN>` → enlace `https://www.r4.com/fondos/<isin en minúsculas>_mes.pdf`.
   - Carmignac: `https://www.carmignac.com/assets/yoda/FLFPRO_CCR_LU3003216580_LU_en/Monthly-Factsheet-PRO_Carmignac-Portfolio-Credit-E-EUR-Acc_LU3003216580_LU_en.pdf` y `.../FLFPRO_CGB_LU0336083497_ES_es/Monthly-Factsheet-PRO_Carmignac-Portfolio-Global-Bond-A-EUR-Acc_LU0336083497_ES_es.pdf`.
   - Buy & Hold (curl --http1.1 con reintentos): `https://www.buyandhold.es/ftpdata/files/BH%20Renta%20Fija%20Sicav%20WEB.pdf` (Bonds), `PR%20BH%20Debt.pdf` (Debt), `Pigmanort%20Sicav%20WEB.pdf` (Flexible).
   - Storm: renderizar `https://stormcapital.no/storm-bond-fund/` con Playwright y coger el último adjunto mensual. DNB: `https://documents.anevis-solutions.com/dnb/FACTSHEET-EN-CH-<ISIN>.pdf`.
   - Morgan Stanley bloquea accesos automáticos: no forzar. Para MS EM Debt Opp A (EUR, LU2784406998) se usa la ficha de la clase AH (misma cartera).
   - No saltarse webs con login ni captcha. Sin ficha: `fecha`/`fecha_ficha` = "Sin ficha", `pdf` = "" y comentario "Sin ficha mensual pública".
   - Comprimir con `pypdf` los PDF de más de 3 MB.
3. Rentabilidades: `python3 -I herramientas/navret.py herramientas/rv.tsv rv_nav.json AAAA-MM-DD` (y lo mismo con rf.tsv), donde la fecha es el fin de mes. Si un fondo sale null, `ftnav.py ISIN:AAAA-MM-DD`. Siempre la clase EUR (Dunas clase R, Storm RC EUR, B&H clase 2 salen del valor liquidativo, no de la ficha).
4. Lectura de fichas: `pdftotext -layout`; `ext.py`, `ext2.py`, `extrv.py` ayudan a localizar TIR, duración, PER, dividendo, posiciones y comentario.
   - Renta fija: tir (%), duración (años), patrimonio, qué ha pasado, posicionamiento, perspectivas, qué aporta y resta.
   - PIMCO Income (IE00B84J9L26), Man Global IG Opp (IE000MI53C66) y Man Dynamic Income (IE000WFG9PJ8) publican el yield en USD: `tir = publicado − (Fed − BCE)` con los tipos oficiales del momento (a 12/11/2026: Fed 3,875 % punto medio, BCE depósito 2,5 %) y dejarlo dicho en `tipo_yield`.
   - Jupiter Merian Global Equity Absolute Return (RV market neutral) y GAM Cat Bond no tienen tir ni duración (null).
   - No inventar comentarios: si la ficha no trae, "Sin comentario en la ficha" y el análisis propio en `lectura`/`perspectivas`, marcado como "Lectura propia".
5. `vision_general.json`: qué dicen las gestoras, en qué coinciden y discrepan, ganadores y perdedores del año, qué ha cambiado respecto al mes anterior, conclusiones propias (no es recomendación personalizada).
6. Poner `pdf` en cada fila, borrar de `fichas/` las del mes anterior y escribir las nuevas. Actualizar `meta.json`.
7. Comprobar: JSON válido, 29 filas de renta fija y 51 de variable, cada `pdf` existe, ningún archivo supera 25 MB.
8. Excel del repositorio: `python3 -I herramientas/generar_excel.py . descargas/Seguimiento_Fondos.xlsx web`, y recalcular con LibreOffice (el skill `xlsx` trae `scripts/recalc.py`; debe dar 0 errores). La web lo ofrece en «Descargar el Excel».
9. `git add -A`, commit y `git -c push.negotiate=true push origin main`. Esperar 1-2 minutos y comprobar con curl que `https://juuuuez.github.io/seguimiento-fondos/data/meta.json` muestra la fecha nueva.
10. Google Drive (solo si hay conector de Drive en la sesión; si no, decirlo en el resumen):
    - Carpeta raíz "Asesor Financiero Renta 4 Banco": id `15WahWLXw9kLS2VIfU-LYDJJZYrKpwLm4`. Dentro, "Fichas fondos": id `1ZsPThxHxR1ltbz7Yk7qUIPGoZGsmgiYb`, con una subcarpeta por mes (`AAAA-MM`).
    - Crear la subcarpeta del mes y subir ahí las fichas nuevas con el mismo nombre que en `fichas/` (una por llamada; límite de ~3 MB por archivo en el conector: comprimir con pypdf los PDF mayores).
    - Excel para Drive, con enlaces relativos a la carpeta de fichas: `python3 -I herramientas/generar_excel.py . Seguimiento_Fondos.xlsx local AAAA-MM`, recalcular, mandar a la papelera el `Seguimiento_Fondos.xlsx` anterior de la carpeta raíz y subir el nuevo con ese mismo nombre.
    - Mantener la carpeta "_Herramientas (no tocar)" (id `1bwj66qaqc7DXislCgG5n_uRncQ7Xne-s`) como copia de seguridad opcional de `herramientas/`.

## Pendiente conocido
LBPAM (FR0014004IP7), Cartesio Income (LU1966822956) y Sigma (LU1984948874, ISIN dudoso) no tienen ficha pública: van como "Sin ficha".
