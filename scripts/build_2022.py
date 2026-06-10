#!/usr/bin/env python3
"""Genera los datasets 2022 (1V y 2V) con el mismo esquema que los de 2026.

Insumos:
  /tmp/cali_2022_1V.json y /tmp/cali_2022_2V.json — agregados por puesto desde los
  CSV oficiales mesa a mesa del Observatorio de la Registraduría
  (MMV_NACIONAL_PRESIDENTE_2022_{1v,2v}.zip, DEP=31 VALLE, MUN=001 CALI).
  data/puestos_resultados.json  — puestos 2026 (para comuna de cada puesto)
  data/puesto_barrio.json       — mapeo puesto→barrio reconstruido (2026)
  data/resultados.json          — barrios y comunas de referencia

Convenciones (idénticas a 2026):
  - total por puesto/barrio/comuna = votos brutos (incluye NoValidos)
  - pct = sobre votos válidos (total - NoValidos)
  - barrio "directo" = tiene ≥1 puesto geolocalizado con datos en 2022
  - barrio "inferido" = hereda pct/ganador de su comuna
"""
import json, sys

PU26 = json.load(open('data/puestos_resultados.json'))
MAPEO = json.load(open('data/puesto_barrio.json'))['puestos']
RES26 = json.load(open('data/resultados.json'))
COMNOM = json.load(open('data/comunas_resultados.json'))['comnom']

# códigos 2022 → 2026 (El Hormiguero cambió de código entre elecciones)
RECODE = {'99-A1': '99-13', '99-A2': '99-14'}

ELECCIONES = {
    '2022_1v': {
        'src': '/tmp/cali_2022_1V.json',
        'eleccion': 'Presidencial 1V · 29 may 2022',
        'cands': {
            'GUSTAVO PETRO': 'Petro',
            'RODOLFO HERNÁNDEZ': 'Rodolfo',
            'FEDERICO GUTIÉRREZ': 'Fico',
            'SERGIO FAJARDO': 'Fajardo',
            'VOTOS EN BLANCO .': 'Blanco',
        },
        'otros': ['JOHN MILTON RODRÍGUEZ', 'ENRIQUE GÓMEZ MARTÍNEZ',
                  'INGRID BETANCOURT', 'LUIS PÉREZ'],
        'novalidos': ['VOTOS NULOS .', 'VOTOS NO MARCADOS .'],
        'keys': ['Petro', 'Rodolfo', 'Fico', 'Fajardo', 'Blanco', 'Otros'],
    },
    '2022_2v': {
        'src': '/tmp/cali_2022_2V.json',
        'eleccion': 'Presidencial 2V · 19 jun 2022',
        'cands': {
            'GUSTAVO PETRO': 'Petro',
            'RODOLFO HERNÁNDEZ': 'Rodolfo',
            'VOTOS EN BLANCO .': 'Blanco',
        },
        'otros': [],
        'novalidos': ['VOTOS NULOS .', 'VOTOS NO MARCADOS .'],
        'keys': ['Petro', 'Rodolfo', 'Blanco'],
    },
}


def normaliza(p22, cfg):
    """votos por candidato normalizado + NoValidos para un puesto 2022."""
    v = {k: 0 for k in cfg['keys']}
    v['NoValidos'] = 0
    for can, n in p22['votos'].items():
        if can in cfg['cands']:
            v[cfg['cands'][can]] += n
        elif can in cfg['otros']:
            v['Otros'] = v.get('Otros', 0) + n
        elif can in cfg['novalidos']:
            v['NoValidos'] += n
        else:
            sys.exit(f'candidato sin clasificar: {can!r}')
    return v


def stats(votos, keys, cand_keys):
    total = sum(votos.values())
    valid = total - votos.get('NoValidos', 0)
    pct = {k: round(votos.get(k, 0) / valid, 4) for k in keys}
    orden = sorted(cand_keys, key=lambda k: -votos.get(k, 0))
    ganador = orden[0]
    margen = round((votos.get(orden[0], 0) - votos.get(orden[1], 0)) / valid, 4)
    return total, valid, pct, ganador, margen


for tag, cfg in ELECCIONES.items():
    raw = json.load(open(cfg['src']))
    keys = cfg['keys']
    cand_keys = [k for k in keys if k not in ('Blanco', 'Otros')]  # ganador solo entre candidatos
    # ── puestos ──
    puestos = {}
    for code, d in raw.items():
        code26 = RECODE.get(code, code)
        ref = PU26.get(code26)
        if ref is None:
            sys.exit(f'puesto 2022 sin referencia 2026: {code}')
        votos = normaliza(d, cfg)
        total, valid, pct, ganador, margen = stats(votos, keys, cand_keys)
        z, p = code26.split('-')
        puestos[code26] = {'zona': z, 'puesto': p, 'nombre': d['nombre'],
                           'comuna': ref['comuna'], 'comnom': ref['comnom'],
                           'total': total, 'votos': votos,
                           'ganador': ganador, 'margen': margen}

    # ── comunas (solo las 22 urbanas, como en 2026) ──
    comunas = {}
    for code, d in puestos.items():
        c = d['comuna']
        if c not in COMNOM:
            continue
        acc = comunas.setdefault(c, {k: 0 for k in keys + ['NoValidos']})
        for k in acc:
            acc[k] += d['votos'].get(k, 0)
    comunas_out = {}
    for c, votos in sorted(comunas.items()):
        total, valid, pct, ganador, margen = stats(votos, keys, cand_keys)
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
            votos = {k: 0 for k in keys + ['NoValidos']}
            for p in ps:
                for k in votos:
                    votos[k] += puestos[p]['votos'].get(k, 0)
            total, valid, pct, ganador, margen = stats(votos, keys, cand_keys)
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
    city = {k: 0 for k in keys + ['NoValidos']}
    for d in puestos.values():
        for k in city:
            city[k] += d['votos'].get(k, 0)
    total, valid, pct, ganador, margen = stats(city, keys, cand_keys)
    ganados = {k: sum(1 for b in barrios.values() if b['ganador'] == k) for k in cand_keys}

    meta = {'fuente': 'Escrutinio oficial Registraduría 2022 (archivos mesa a mesa, '
                      'Observatorio de la Registraduría) — mismos puestos geolocalizados de 2026',
            'eleccion': cfg['eleccion'], 'nivel': 'barrio',
            'ciudad': {'pct': pct, 'votos_validos': valid,
                       'barrios_ganados': ganados, 'barrios_directos': n_directos}}

    json.dump({'_meta': meta, 'barrios': barrios},
              open(f'data/resultados_{tag}.json', 'w'), ensure_ascii=False)
    json.dump(puestos, open(f'data/puestos_resultados_{tag}.json', 'w'), ensure_ascii=False)
    json.dump({'comnom': COMNOM, 'comunas': comunas_out},
              open(f'data/comunas_resultados_{tag}.json', 'w'), ensure_ascii=False)

    print(f'== {tag}: {len(puestos)} puestos, {n_directos} barrios directos, '
          f'válidos={valid:,}')
    print('   ciudad:', {k: f'{v:.1%}' for k, v in pct.items()})
    print('   barrios ganados:', ganados)
