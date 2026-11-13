# Actualización mensual de la web de seguimiento de fondos

Este repositorio es la web pública (GitHub Pages) y también la fuente de verdad de los datos.
Cada día 10 una sesión de Claude descarga las fichas nuevas, actualiza `data/` y `fichas/`, y hace push.
La web (`index.html`) no se toca: lee `data/*.json` al cargarse.

## Estructura
- `index.html`: la página («Cuaderno de fondos»): portada con dos botones y buscador, listas por bloque, ficha de cada fondo y visión general. Todo el texto sale de `data/`. Solo cambiarla si algo falla o el usuario pide cambios de diseño. Diseño sobrio, colores neutros, sin textos descriptivos.
- `data/renta_fija.json`, `data/renta_variable.json`, `data/vision_general.json`, `data/meta.json`: datos que lee la web.
- `fichas/<Nombre del fondo> - Ficha <mes abreviado> <año>.pdf`: una ficha por fondo (mes abreviado: ene feb mar abr may jun jul ago sep oct nov dic).
- `fichas/miniaturas/<mismo nombre>.jpg`: primera página de cada ficha (la web la enseña como cuadro que descarga el PDF).
- `herramientas/`: este proceso. `rf.tsv` (fondos de renta fija) y `rv.tsv` (renta variable, mixtos y metales; 4ª columna: RV, MX o MT) con ISIN de la clase EN EUR. `navret.py` y `ftnav.py` (rentabilidades por valor liquidativo), `ext*.py` (extracción de texto de las fichas).

## Esquema de los datos (porcentajes en unidades de %, p. ej. 12.92 = 12,92 %)
`renta_fija.json`, lista de objetos: isin, fondo, gestora, tipo, fecha (dd/mm/aaaa de la ficha), tir, tipo_yield, duracion, mes, ytd, a1, r3, r5, r10, breakeven_pb, patrimonio, fuente, que_ha_pasado (resumen propio), literal (palabras literales del gestor, solo si la ficha las trae en español; "" si no), posicionamiento, aporta, resta, ficha (siempre ""), pdf ("fichas/<archivo>.pdf"), mini ("fichas/miniaturas/<archivo>.jpg"). NO hay campo `perspectivas`: se eliminó a petición del usuario y no debe volver.
- `breakeven_pb = round(tir / duracion * 100)`; null si falta tir o duración.
- `mes`, `ytd`, `a1`: rentabilidad de la clase EUR a fin de mes. Null si no hay dato.
- `r3`, `r5`, `r10`: rentabilidad ANUALIZADA a 3, 5 y 10 años (también en renta variable). Null si el fondo no tiene tanto historial. Salen de `navret.py` (quefondos: llega a 3 y 5 años, su historial empieza en 2018) y de `ftnav.py --lista` (FT: llega a 10 años y cubre fondos que quefondos no tiene). Regla: r3 y r5 de quefondos y, si faltan, de FT; r10 siempre de FT. La web y el Excel los muestran tal cual.
`renta_variable.json`: isin, fondo, gestora, bloque ("Renta variable", "Mixto" o "Metales / recursos"), estilo, fecha_ficha ("dd/mm/aaaa" o "Sin ficha"), mes, ytd, a1, r3, r5, r10, per, dividendo, posiciones, comentario (resumen), literal (igual que en renta fija), lectura, ficha (""), pdf, mini.
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
3. Rentabilidades: `python3 -I herramientas/navret.py <lista.tsv> nav.json AAAA-MM-DD` (fin de mes; lista = rf.tsv y rv.tsv juntos, solo ISIN en la 1ª columna) y `python3 -I herramientas/ftnav.py --lista <lista.tsv> AAAA-MM-DD ft.json`. Combinar según la regla de r3/r5/r10 de arriba. Para un fondo suelto: `ftnav.py ISIN:AAAA-MM-DD`. Siempre la clase EUR (Dunas clase R, Storm RC EUR, B&H clase 2 salen del valor liquidativo, no de la ficha).
4. Lectura de fichas: `pdftotext -layout`; `ext.py`, `ext2.py`, `extrv.py` ayudan a localizar TIR, duración, PER, dividendo, posiciones y comentario.
   - Renta fija: tir (%), duración (años), patrimonio, qué ha pasado, posicionamiento, qué aporta y resta (SIN perspectivas).
   - Comentario literal: `python3 -I herramientas/comentarios.py .` copia las palabras exactas del gestor de las fichas que las traen en español (Renta 4, DNCA, Lazard, Carmignac Global Bond, Robeco BP, Dunas; reglas en ese script). Si el mes siguiente otra ficha en español trae comentario del gestor (o cambia el formato), añadir/ajustar su regla en `REGLAS`/`POR_ISIN`; no traducir ni resumir nada en `literal`. Las fichas en inglés o sin comentario dejan `literal` vacío y la web enseña el resumen.
   - PIMCO Income (IE00B84J9L26), Man Global IG Opp (IE000MI53C66) y Man Dynamic Income (IE000WFG9PJ8) publican el yield en USD: `tir = publicado − (Fed − BCE)` con los tipos oficiales del momento (a 12/11/2026: Fed 3,875 % punto medio, BCE depósito 2,5 %) y dejarlo dicho en `tipo_yield`.
   - Jupiter Merian Global Equity Absolute Return (RV market neutral) y GAM Cat Bond no tienen tir ni duración (null).
   - No inventar comentarios: si la ficha no trae, "Sin comentario en la ficha" y el análisis propio en `lectura` (renta variable) o en `posicionamiento` (renta fija), marcado como "Lectura propia".
4b. Exposición (sectores, geografía, calidad del emisor): `herramientas/exposicion.json` guarda, por ISIN, `sec` y `geo` ([nombre, % fondo, % índice o null], de la renta variable; top 6) y `cal` ({ig, hy, sr, nota}; solo renta fija: investment grade / high yield / sin rating) leídos de cada ficha (tablas con pdftotext; si solo hay gráfico, leer el gráfico y poner `aprox: true`). Después `python3 -I herramientas/exposicion_aplicar.py .` vuelca eso en `data/*.json` (campos sectores, geografia, calidad, destaca, aprox; `destaca` se genera solo con las mayores sobre/infraponderaciones frente al índice). Cubierto a 13/11/2026: 31 fondos de renta variable y 2 de renta fija; el resto, pendiente de leer. Si una ficha no trae el dato, dejar el fondo sin entrada (la web no enseña el bloque).
5. `vision_general.json`: qué dicen las gestoras, en qué coinciden y discrepan, ganadores y perdedores del año, qué ha cambiado respecto al mes anterior, conclusiones propias (no es recomendación personalizada).
6. Poner `pdf` en cada fila, borrar de `fichas/` las del mes anterior y escribir las nuevas. Ejecutar `python3 -I herramientas/miniaturas.py .` (genera `fichas/miniaturas/` y el campo `mini`; es después de `comentarios.py`, que no toca `mini`). Actualizar `meta.json`.
7. Comprobar: JSON válido, 29 filas de renta fija y 51 de variable, cada `pdf` existe, ningún archivo supera 25 MB.
8. Excel del repositorio: `python3 -I herramientas/generar_excel.py . descargas/Seguimiento_Fondos.xlsx web`, y recalcular con LibreOffice (el skill `xlsx` trae `scripts/recalc.py`; debe dar 0 errores). La web lo ofrece en «Descargar el Excel».
9. `git add -A`, commit y `git -c push.negotiate=true push origin main`. Esperar 1-2 minutos y comprobar con curl que `https://juuuuez.github.io/seguimiento-fondos/data/meta.json` muestra la fecha nueva.
10. Google Drive (solo si hay conector de Drive en la sesión; si no, decirlo en el resumen):
    - Carpeta raíz "Asesor Financiero Renta 4 Banco": id `15WahWLXw9kLS2VIfU-LYDJJZYrKpwLm4`. Dentro, "Fichas fondos": id `1ZsPThxHxR1ltbz7Yk7qUIPGoZGsmgiYb`, con una subcarpeta por mes (`AAAA-MM`).
    - Crear la subcarpeta del mes y subir ahí las fichas nuevas con el mismo nombre que en `fichas/` (una por llamada; límite de ~3 MB por archivo en el conector: comprimir con pypdf los PDF mayores).
    - Excel para Drive, con enlaces relativos a la carpeta de fichas: `python3 -I herramientas/generar_excel.py . Seguimiento_Fondos.xlsx local AAAA-MM`, recalcular, mandar a la papelera el `Seguimiento_Fondos.xlsx` anterior de la carpeta raíz y subir el nuevo con ese mismo nombre.
    - Mantener la carpeta "_Herramientas (no tocar)" (id `1bwj66qaqc7DXislCgG5n_uRncQ7Xne-s`) como copia de seguridad opcional de `herramientas/`.

## Cómo buscar fichas nuevas (y las que faltan)
1. `python3 -I herramientas/buscar_fichas.py .` mira en fundinfo la ficha mensual más reciente de los 80 ISIN y marca NUEVA donde hay una más reciente que la nuestra (deja `/tmp/fichas_nuevas.json` con la URL). Las gestoras publican entre el día 5 y el 25: a día 10 muchas siguen en el mes anterior. Por eso hay una segunda pasada hacia el día 20 (`buscar_fichas.py` otra vez, y solo actualizar los fondos con ficha nueva).
2. Fuentes directas que funcionan sin registro (comprobadas el 13/11/2026):
   - Olea Neutral (ES0118537002): página `https://oleagestion.com/fondo-de-inversion/` → enlace `30102026_Informe-Mensual.pdf` (cambia el nombre cada mes; leerlo del HTML).
   - Seilern World Growth EUR U R (IE00B2NXKW18): `https://www.seilernfunds.com/individual-strategies/` → enlace `Seilern-World-Growth-EUR-U-R-as-at-31st-October-2026.pdf`.
   - Renta 4 (fondos propios): `https://www.r4.com/fondos/<isin en minúsculas>_mes.pdf` (suele salir antes que fundinfo).
   - Carmignac, Buy & Hold, Storm, DNB (`documents.anevis-solutions.com/dnb/FACTSHEET-EN-LU-<ISIN>.pdf`; la variante `-CH-` da 403): ver pasos de arriba.
3. Sin ficha mensual accesible a fecha 13/11/2026 (se reintenta cada mes): Avantage Fund FI B (r4.com solo tiene folleto/semestral), Numantia Patrimonio Global (igual), Horos Patrimonio (web horosam.com devolvía 502), Groupama Global Disruption y Global Active Equity (el informe público de h24finance sigue en marzo de 2026), DIP Paradigma, Ardtur, MFS Blended Research US Core (clase EUR), Finserve Global Defence, Polar Capital Global Insurance (polarcapitalfunds.com pide registrarse como inversor: no aceptar el aviso por el usuario), Goehring & Rozencwajg (solo ficha trimestral en gr-funds.com). No usar otros portales de fundinfo (LU, GB, CH, DE…): el usuario solo aceptó el aviso legal de España.
4. Orden al incorporar una ficha nueva: copiar el PDF a `fichas/<Nombre> - Ficha <mes> <año>.pdf`, borrar el anterior, actualizar `fecha`/`fecha_ficha`, `pdf` y los datos de la ficha (tir, duración, posiciones, exposición en `exposicion.json`), y volver a pasar `comentarios.py`, `miniaturas.py` y `exposicion_aplicar.py`.

## Pendiente conocido
LBPAM (FR0014004IP7), Cartesio Income (LU1966822956) y Sigma (LU1984948874, ISIN dudoso) no tienen ficha pública: van como "Sin ficha".
