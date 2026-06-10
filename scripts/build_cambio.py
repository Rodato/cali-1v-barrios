#!/usr/bin/env python3
"""Genera data/cambio_1v.json y data/cambio_puestos.json: el cambio del voto
de izquierda entre primeras vueltas (Petro 2022 → Cepeda 2026), barrio por barrio.

Metodología: solo se comparan los puestos presentes en AMBAS elecciones (190; los 216 de 2026 incluyen 26 nuevos), de modo que el cambio no se contamine con puestos nuevos. Barrio
"directo" = tiene ≥1 puesto común; el resto hereda el cambio de su comuna
(agregado de los puestos comunes de la comuna).

izq = Petro (2022) / Cepeda (2026); der = Fico+Rodolfo (2022) / Abelardo+Paloma (2026).
Porcentajes sobre votos válidos de cada año.
"""
import json

PU26 = json.load(open('data/puestos_resultados.json'))
PU22 = json.load(open('data/puestos_resultados_2022_1v.json'))
MAPEO = json.load(open('data/puesto_barrio.json'))['puestos']
RES26 = json.load(open('data/resultados.json'))['barrios']
COMNOM = json.load(open('data/comunas_resultados.json'))['comnom']

COMMON = sorted(set(PU26) & set(PU22))


def blocs(pids):
    """(izq22, izq26, der22, der26) sobre votos válidos, para un conjunto de puestos."""
    def share(pu, keys):
        tot = sum(pu[p]['total'] - pu[p]['votos'].get('NoValidos', 0) for p in pids)
        v = sum(pu[p]['votos'].get(k, 0) for p in pids for k in keys)
        return v / tot
    return (share(PU22, ['Petro']), share(PU26, ['Cepeda']),
            share(PU22, ['Fico', 'Rodolfo']), share(PU26, ['Abelardo', 'Paloma']))


# ── por puesto ──
puestos = {}
for code in COMMON:
    i22, i26, d22, d26 = blocs([code])
    puestos[code] = {'nombre': PU26[code]['nombre'], 'comuna': PU26[code]['comuna'],
                     'comnom': PU26[code]['comnom'],
                     'izq22': round(i22, 4), 'izq26': round(i26, 4),
                     'der22': round(d22, 4), 'der26': round(d26, 4),
                     'd': round(i26 - i22, 4)}

# ── por comuna (solo puestos comunes) ──
from collections import defaultdict
pcom = defaultdict(list)
for code in COMMON:
    c = PU26[code]['comuna']
    if c in COMNOM:
        pcom[c].append(code)
comunas = {}
for c, pids in pcom.items():
    i22, i26, d22, d26 = blocs(pids)
    comunas[c] = {'izq22': round(i22, 4), 'izq26': round(i26, 4),
                  'der22': round(d22, 4), 'der26': round(d26, 4),
                  'd': round(i26 - i22, 4)}

# ── por barrio ──
barrio_puestos = defaultdict(list)
for pcode, info in MAPEO.items():
    if pcode in puestos:
        barrio_puestos[info['barrio_id']].append(pcode)

barrios = {}
n_directos = 0
for bid, d26 in RES26.items():
    ps = barrio_puestos.get(bid, [])
    if ps:
        i22, i26, dd22, dd26 = blocs(ps)
        barrios[bid] = {'izq22': round(i22, 4), 'izq26': round(i26, 4),
                        'der22': round(dd22, 4), 'der26': round(dd26, 4),
                        'd': round(i26 - i22, 4), 'comuna': d26['comuna'],
                        'comnom': d26['comnom'], 'nivel': 'directo',
                        'npuestos': len(ps)}
        n_directos += 1
    else:
        cm = comunas['0' + d26['comuna']]
        barrios[bid] = {**cm, 'comuna': d26['comuna'], 'comnom': d26['comnom'],
                        'nivel': 'inferido', 'npuestos': 0}

# ── ciudad ──
i22, i26, d22, d26 = blocs(COMMON)
mejora = sum(1 for b in barrios.values() if b['d'] > 0)
meta = {'fuente': 'Escrutinios Registraduría 2022 y 2026, primeras vueltas — '
                  f'{len(COMMON)} puestos presentes en ambas elecciones',
        'eleccion': 'Cambio 1V 2022 → 1V 2026',
        'ciudad': {'izq22': round(i22, 4), 'izq26': round(i26, 4),
                   'der22': round(d22, 4), 'der26': round(d26, 4),
                   'd': round(i26 - i22, 4),
                   'barrios_mejora': mejora, 'barrios_retrocede': len(barrios) - mejora,
                   'barrios_directos': n_directos}}

json.dump({'_meta': meta, 'barrios': barrios}, open('data/cambio_1v.json', 'w'),
          ensure_ascii=False)
json.dump(puestos, open('data/cambio_puestos.json', 'w'), ensure_ascii=False)

print(f'{len(COMMON)} puestos comunes, {n_directos} barrios directos')
print(f"ciudad: izq {i22:.1%} → {i26:.1%} ({(i26-i22)*100:+.1f} pts) | "
      f"der {d22:.1%} → {d26:.1%} ({(d26-d22)*100:+.1f} pts)")
print(f"barrios donde mejora: {mejora} | retrocede: {len(barrios)-mejora}")
ds = sorted(abs(b['d']) for b in barrios.values())
print('|d| p50:', f"{ds[len(ds)//2]:.3f}", 'p90:', f"{ds[int(len(ds)*.9)]:.3f}",
      'max:', f"{ds[-1]:.3f}")
