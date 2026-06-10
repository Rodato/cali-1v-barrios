# El mapa de Cali, barrio por barrio — Presidenciales 2026 y 2022

Mapa interactivo de los resultados presidenciales en Santiago de Cali, barrio por barrio: la **primera vuelta de 2026** (31 de mayo) y las **dos vueltas de 2022** (29 de mayo y 19 de junio), con un selector para comparar.

🔗 **En vivo:** https://cali-1v-barrios.vercel.app

Inspirado en el [mapa de Bogotá de Ricardo Ruiz](https://x.com/RicardoRuiz_/status/2061968087369265423).

## Qué muestra

- Los **339 barrios** de Cali coloreados por candidato ganador, con la intensidad según el margen, en tres votaciones conmutables.
- **2026 (1V):** Iván Cepeda ganó la ciudad (51,5%) sobre Abelardo de la Espriella (35,3%) — al revés del resultado nacional.
- **2022 (1V):** Gustavo Petro ganó con el 53,4% y se impuso en 21 de las 22 comunas; Fico Gutiérrez (22,6%) solo ganó la comuna 22.
- **2022 (2V):** Petro 63,9% – Rodolfo Hernández 33,8%. Rodolfo ganó las comunas 2, 17, 19 y 22.
- **La misma frontera:** las 4 comunas de mayor estrato (2, 17, 19, 22) votaron Rodolfo en 2022 y Abelardo en 2026; el oriente y la ladera populares votaron Petro y luego Cepeda.
- **Cambio 2022→2026:** vista de contraste entre primeras vueltas (Petro vs. Cepeda, sobre los 190 puestos presentes en ambas). La ciudad se polarizó: la izquierda creció hasta +4 pts en el oriente popular (Potrero Grande, Mojica) y cayó hasta −8 en las comunas 17, 22, 2 y 5 — con los retrocesos más fuertes en los puestos universitarios (Univalle Meléndez −11,6, Icesi −10,7).
- Tablas con los puestos de votación más extremos de cada lado en cada elección.

## Datos y metodología

| Pieza | Fuente |
|---|---|
| Geometría de barrios | [Capa de Barrios — IDESC / Alcaldía de Cali](https://datos.cali.gov.co/dataset/capa-de-barrios-de-santiago-de-cali) vía WFS GeoServer, reproyectada a WGS84 (339 barrios, 22 comunas) |
| Resultados 2026 | [Escrutinio oficial de la Registraduría Nacional](https://escrutiniospresidente2026.registraduria.gov.co/publicadas) — actas publicadas por mesa (216 puestos, 5.158 mesas, 1.056.380 votos válidos) |
| Resultados 2022 | Escrutinio oficial mesa a mesa, archivos `MMV_NACIONAL_PRESIDENTE_2022_{1v,2v}.zip` del [Visor de histórico de resultados electorales — Observatorio de la Registraduría](https://observatorio.registraduria.gov.co/views/electoral/historicos-resultados.php) (190 puestos; 989.928 votos válidos en 1V, 1.033.345 en 2V) |
| Geolocalización de puestos | Cruce con la capa `educacion:esf_establecimiento_educativo` de IDESC + geocodificación OpenStreetMap |

**Granularidad (importante):** el escrutinio georreferencia cada voto a su **comuna**, no a su barrio. Para bajar a barrio se geolocalizaron los puestos de 2026: **117 barrios** contienen al menos un puesto y muestran su resultado directo (validado por comuna); el resto hereda la tendencia de su comuna. Para 2022 se reutiliza la misma geolocalización cruzando los puestos por código de zona-puesto (188 de 190 coinciden; los 2 de El Hormiguero se emparejan por nombre): **108 barrios** quedan con resultado directo, porque 26 puestos de 2026 aún no existían en 2022. Es una aproximación, no un conteo barrio a barrio puro.

El mapeo puesto→barrio está en `data/puesto_barrio.json` (reconstruido por coincidencia exacta de totales y porcentajes; ver `scripts/build_2022.py`, que regenera los datasets de 2022).

## Stack

Sitio estático: HTML + [Leaflet](https://leafletjs.com/). Sin build. Datos en `/data/*.json`. Desplegado en Vercel. La vista activa se refleja en el hash (`#2022-1v`, `#2022-2v`, `#2026-1v`, `#cambio`) para enlazar directo.

```
data/
  barrios.geojson                  # 339 barrios (WGS84, simplificado)
  resultados.json                  # 2026-1V por barrio (directo / inferido)
  resultados_2022_1v.json          # 2022-1V por barrio
  resultados_2022_2v.json          # 2022-2V por barrio
  cambio_1v.json                   # cambio Petro-22 → Cepeda-26 por barrio
  cambio_puestos.json              # cambio por puesto (190 comunes)
  comunas_resultados*.json         # agregados oficiales por comuna
  puestos_resultados*.json         # agregados por puesto de votación
  puesto_barrio.json               # mapeo puesto → barrio (geolocalización 2026)
scripts/
  build_2022.py                    # regenera los datasets 2022 desde los CSV oficiales
  build_cambio.py                  # regenera la vista de cambio 2022→2026
```

## Licencia

Datos oficiales y abiertos de la Registraduría Nacional e IDESC. Código bajo MIT.

Hecho por [Daniel Otero](https://danielotero.dev/) con [Claude Code](https://claude.com/claude-code).
