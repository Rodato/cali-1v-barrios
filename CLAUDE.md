# El mapa de Cali, barrio por barrio

Sitio estático (HTML + Leaflet, sin build) con los resultados presidenciales en Cali
por barrio: 1V-2026, 2V-2026, 1V-2022, 2V-2022 y una vista de cambio 2022→2026.
Producción: https://cali-1v-barrios.vercel.app · Deploy: `vercel --prod` (no hay auto-deploy por git).
Dev local: `python3 -m http.server` (los `fetch()` de `/data` no funcionan con file://).

## Arquitectura de datos (convenciones críticas)

- Toda la lógica de vistas vive en `index.html` (objeto `ELECCIONES`); cada vista define
  sus archivos de datos, candidatos, colores y textos. La vista activa va en el hash
  (`#2022-1v`, `#2022-2v`, `#2026-1v`, `#cambio`).
- `total` por puesto/barrio/comuna = votos **brutos** (incluye `NoValidos`).
  Los `pct` son sobre votos **válidos** (`total - NoValidos`). No mezclar.
- Barrio `directo` = tiene ≥1 puesto geolocalizado; `inferido` = hereda los pct de su comuna.
- `data/puesto_barrio.json` es el mapeo puesto→barrio (151 puestos → 117 barrios).
  **No regenerable desde fuentes**: se reconstruyó por coincidencia exacta de totales+pct
  desde resultados.json 2026. Si se cambia la geolocalización, actualizar este archivo.
- Códigos: puesto = `ZZ-PP` (zona-puesto, estables entre elecciones); comuna = 3 dígitos
  en puestos/comunas (`001`) y 2 dígitos en barrios (`01`); id de barrio = `CCNN` (`0610`).
- Hay 4 puestos cuya comuna oficial no coincide con la del barrio donde están
  (cárcel Villanueva, Coliseo del Pueblo, La Castilla, La Buitrera). Es correcto, no un bug.

## Scripts (regeneran data/, corren desde la raíz)

- `scripts/build_2026_2v.py` — datasets 2V-2026 desde el crudo mesa a mesa de la
  Registraduría (`data/MMV_*_31_001_*.csv`, formato largo `;`, ya filtrado a VALLE/CALI;
  el MMS no se usa). Reusa comuna/nombre por puesto de `puestos_resultados.json` (1V) y el
  mapeo `puesto_barrio.json`. Los crudos `data/MM*.csv` están en `.gitignore` (insumos, no
  assets). Nota: la 1V-2026 llegó ya construida en el primer commit — no hay `build_2026.py`.
- `scripts/build_2022.py` — datasets 2022 desde los CSV oficiales mesa a mesa
  (`MMV_NACIONAL_PRESIDENTE_2022_{1v,2v}.zip` del Observatorio de la Registraduría,
  https://observatorio.registraduria.gov.co/anexos/ — filtrar DEP=31 VALLE, MUN=001 CALI).
  Espera los agregados por puesto en `/tmp/cali_2022_{1V,2V}.json`.
- `scripts/build_cambio.py` — vista de cambio: SOLO los 190 puestos presentes en ambas
  elecciones (los 2 de El Hormiguero cambiaron de código: 99-A1/A2 en 2022 → 99-13/14 en 2026).
  izq = Petro/Cepeda; der = Fico+Rodolfo (2022) / Abelardo+Paloma (2026).

## Fuentes que ya fallaron (no perder tiempo)

- Los xlsx de la MOE en Google Drive (2V 2022) están borrados (404).
- datos.gov.co no tiene los resultados 2022 por mesa; la fuente buena es el
  Visor de histórico del Observatorio de la Registraduría (zips MMV por elección).

## Estilo del sitio

Tipografías Syne/Arima/DM Mono, fondo papel `#f7f4ee`. Colores por candidato en
`ELECCIONES` (Cepeda `#138086`, Abelardo `#e4572e`, Petro `#7b3fa0`, Fico `#2f5fa5`,
Rodolfo `#cf8a00`). Textos del sitio en español, decimales con punto (`51.5%`),
pero en tweets/posts el usuario usa coma (`51,5%`).
