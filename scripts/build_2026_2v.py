#!/usr/bin/env python3
"""Genera los datasets de la 2ª vuelta 2026 con el mismo esquema que el resto.

Insumo crudo (mesa a mesa, escrutinio oficial Registraduría 2026):
  data/MMV_XXX_31_001_XXX_XX_XX_XXX_2947.csv  — votos por mesa × candidato
  (formato largo, separador ';', ya filtrado a DEP=31 VALLE, MUN=001 CALI).
  El MMS (metadatos de mesa) no se usa: todos los votos están en el MMV.

Insumos de referencia (de 2026 1V, para mantener comuna/nombre idénticos):
  data/puestos_resultados.json  — comuna/comnom/nombre de cada puesto
  data/puesto_barrio.json       — mapeo puesto→barrio
  data/resultados.json          — barrios y comunas de referencia
  data/comunas_resultados.json  — nombres de comuna

Convenciones (idénticas al resto del sitio):
  - total por puesto/barrio/comuna = votos brutos (incluye NoValidos)
  - pct = sobre votos válidos (total - NoValidos); Blanco cuenta como válido
  - barrio "directo" = tiene ≥1 puesto geolocalizado; "inferido" = hereda su comuna
"""
import csv, json, sys

MMV_SRC = 'data/MMV_XXX_31_001_XXX_XX_XX_XXX_2947.csv'

PU26 = json.load(open('data/puestos_resultados.json'))
MAPEO = json.load(open('data/puesto_barrio.json'))['puestos']
RES26 = json.load(open('data/resultados.json'))
COMNOM = json.load(open('data/comunas_resultados.json'))['comnom']

CANDS = {
    'IVÁN CEPEDA CASTRO': 'Cepeda',
    'ABELARDO DE LA ESPRIELLA': 'Abelardo',
    'VOTOS EN BLANCO': 'Blanco',
}
NOVALIDOS = {'VOTOS NULOS', 'VOTOS NO MARCADOS'}
KEYS = ['Cepeda', 'Abelardo', 'Blanco']
CAND_KEYS = ['Cepeda', 'Abelardo']  # ganador solo entre candidatos (Blanco no cuenta)
ELECCION = 'Presidencial 2V · 21 jun 2026'


def stats(votos):
    total = sum(votos.values())
    valid = total - votos.get('NoValidos', 0)
    pct = {k: round(votos.get(k, 0) / valid, 4) for k in KEYS}
    orden = sorted(CAND_KEYS, key=lambda k: -votos.get(k, 0))
    ganador = orden[0]
    margen = round((votos.get(orden[0], 0) - votos.get(orden[1], 0)) / valid, 4)
    return total, valid, pct, ganador, margen


# ── crudo MMV → votos agregados por puesto ──
raw = {}  # code -> {cand: votos}
with open(MMV_SRC, newline='') as f:
    for d in csv.DictReader(f, delimiter=';'):
        code = f"{d['ZONA']}-{d['PUESTO']}"
        acc = raw.setdefault(code, {k: 0 for k in KEYS + ['NoValidos']})
        n = int(d['VOTOS'] or 0)
        nombre = d['CANNOMBRE'].strip()
        if nombre in CANDS:
            acc[CANDS[nombre]] += n
        elif nombre in NOVALIDOS:
            acc['NoValidos'] += n
        else:
            sys.exit(f'candidato sin clasificar: {nombre!r}')

# ── puestos ──
puestos = {}
for code, votos in raw.items():
    ref = PU26.get(code)
    if ref is None:
        sys.exit(f'puesto 2V sin referencia 2026 1V: {code}')
    total, valid, pct, ganador, margen = stats(votos)
    z, p = code.split('-')
    puestos[code] = {'zona': z, 'puesto': p, 'nombre': ref['nombre'],
                     'comuna': ref['comuna'], 'comnom': ref['comnom'],
                     'total': total, 'votos': votos,
                     'ganador': ganador, 'margen': margen}

# ── comunas (solo las que tienen nombre en COMNOM, como en el resto) ──
comunas = {}
for d in puestos.values():
    c = d['comuna']
    if c not in COMNOM:
        continue
    acc = comunas.setdefault(c, {k: 0 for k in KEYS + ['NoValidos']})
    for k in acc:
        acc[k] += d['votos'].get(k, 0)
comunas_out = {}
for c, votos in sorted(comunas.items()):
    total, valid, pct, ganador, margen = stats(votos)
    comunas_out[c] = {'nombre': COMNOM[c], 'total': total,
                      'ganador': ganador, 'margen': margen, 'pct': pct}

# ── barrios ──
barrio_puestos = {}
for pcode, info in MAPEO.items():
    barrio_puestos.setdefault(info['barrio_id'], []).append(pcode)
barrios = {}
n_directos = 0
for bid, d26 in RES26['barrios'].items():
    comuna3 = '0' + d26['comuna']
    ps = [p for p in barrio_puestos.get(bid, []) if p in puestos]
    if ps:
        votos = {k: 0 for k in KEYS + ['NoValidos']}
        for p in ps:
            for k in votos:
                votos[k] += puestos[p]['votos'].get(k, 0)
        total, valid, pct, ganador, margen = stats(votos)
        barrios[bid] = {'ganador': ganador, 'margen': margen, 'pct': pct,
                        'total': total, 'comuna': d26['comuna'],
                        'comnom': d26['comnom'], 'nivel': 'directo',
                        'npuestos': len(ps)}
        n_directos += 1
    else:
        cm = comunas_out[comuna3]
        barrios[bid] = {'ganador': cm['ganador'], 'margen': cm['margen'],
                        'pct': cm['pct'], 'total': cm['total'],
                        'comuna': d26['comuna'], 'comnom': d26['comnom'],
                        'nivel': 'inferido', 'npuestos': 0}

# ── ciudad ──
city = {k: 0 for k in KEYS + ['NoValidos']}
for d in puestos.values():
    for k in city:
        city[k] += d['votos'].get(k, 0)
total, valid, pct, ganador, margen = stats(city)
ganados = {k: sum(1 for b in barrios.values() if b['ganador'] == k) for k in CAND_KEYS}

meta = {'fuente': 'Escrutinio oficial Registraduría 2026 (archivos mesa a mesa, MMV) — '
                  'mismos puestos geolocalizados de la primera vuelta',
        'eleccion': ELECCION, 'nivel': 'barrio',
        'ciudad': {'pct': pct, 'votos_validos': valid,
                   'barrios_ganados': ganados, 'barrios_directos': n_directos}}

json.dump({'_meta': meta, 'barrios': barrios},
          open('data/resultados_2026_2v.json', 'w'), ensure_ascii=False)
json.dump(puestos, open('data/puestos_resultados_2026_2v.json', 'w'), ensure_ascii=False)
json.dump({'comnom': COMNOM, 'comunas': comunas_out},
          open('data/comunas_resultados_2026_2v.json', 'w'), ensure_ascii=False)

print(f'== 2026_2v: {len(puestos)} puestos, {n_directos} barrios directos, válidos={valid:,}')
print('   ciudad:', {k: f'{v:.1%}' for k, v in pct.items()})
print('   barrios ganados:', ganados)
