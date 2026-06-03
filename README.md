# El mapa de Cali, barrio por barrio — Primera vuelta 2026

Mapa interactivo de los resultados de la **primera vuelta presidencial de Colombia (31 de mayo de 2026)** en Santiago de Cali, barrio por barrio.

🔗 **En vivo:** https://cali-1v-barrios.vercel.app

Inspirado en el [mapa de Bogotá de Ricardo Ruiz](https://ricardoruiz.co/bogota-1v-barrios.html).

## Qué muestra

- Los **339 barrios** de Cali coloreados por candidato ganador, con la intensidad según el margen.
- En Cali ganó **Iván Cepeda (51,5%)** sobre Abelardo de la Espriella (35,3%) — al revés del resultado nacional.
- Una divisoria socioeconómica clara: Cepeda domina el oriente y la ladera populares (Aguablanca, Siloé); Abelardo gana en las 4 comunas de mayor estrato (22, 2, 17, 19).
- Tablas con los puestos de votación más extremos de cada lado.

## Datos y metodología

| Pieza | Fuente |
|---|---|
| Geometría de barrios | [Capa de Barrios — IDESC / Alcaldía de Cali](https://datos.cali.gov.co/dataset/capa-de-barrios-de-santiago-de-cali) vía WFS GeoServer, reproyectada a WGS84 (339 barrios, 22 comunas) |
| Resultados | [Escrutinio oficial de la Registraduría Nacional](https://escrutiniospresidente2026.registraduria.gov.co/publicadas) — actas publicadas por mesa (216 puestos, 5.158 mesas, 1.056.380 votos válidos) |
| Geolocalización de puestos | Cruce con la capa `educacion:esf_establecimiento_educativo` de IDESC + geocodificación OpenStreetMap |

**Granularidad (importante):** el escrutinio georreferencia cada voto a su **comuna**, no a su barrio. Para bajar a barrio se geolocalizaron los 216 puestos: **117 barrios** contienen al menos un puesto y muestran su resultado directo (validado por comuna); los **222 restantes** heredan la tendencia de su comuna. Es una aproximación, no un conteo barrio a barrio puro.

## Stack

Sitio estático: HTML + [Leaflet](https://leafletjs.com/). Sin build. Datos en `/data/*.json`. Desplegado en Vercel.

```
data/
  barrios.geojson          # 339 barrios (WGS84, simplificado)
  resultados.json          # resultado por barrio (directo / inferido)
  comunas_resultados.json  # agregado oficial por comuna
  puestos_resultados.json  # agregado por puesto de votación
```

## Licencia

Datos oficiales y abiertos de la Registraduría Nacional e IDESC. Código bajo MIT.

Hecho por [Estudio Plural](https://plural-estudio.co) con [Claude Code](https://claude.com/claude-code).
