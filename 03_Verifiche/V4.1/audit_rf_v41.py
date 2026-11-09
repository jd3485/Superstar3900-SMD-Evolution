#!/usr/bin/env python3
"""S3900E V4.1 - independent, reproducible *static* preflight on V3.8 KiCad PCB.

Never modifies KiCad inputs, creates manufacturing files, or claims native DRC.
Only Python stdlib and earlier project parser needed; see RAPPORTO_V4.1.md.
"""
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PCB = ROOT / '04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb'
PARSER = ROOT / '03_Verifiche/V3.6/audit_v36.py'
REPORT = Path(__file__).with_name('ESITO_PREFLIGHT_RF_V4.1.json')

spec = importlib.util.spec_from_file_location('s3900_parser_v36', PARSER)
legacy = importlib.util.module_from_spec(spec)
_prev_dont_write_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True  # preserve historical bytecode files in cumulative archive
try:
    spec.loader.exec_module(legacy)
finally:
    sys.dont_write_bytecode = _prev_dont_write_bytecode
subs = legacy.subs
one = legacy.one


def val(node, key):
    return one(node, key)[1:]


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def footprint_map(tree):
    out = {}
    for fp in subs(tree, 'footprint'):
        props = {x[1]: x[2] for x in subs(fp, 'property')}
        ref = props.get('Reference')
        if not ref or ref in out:
            raise ValueError('Duplicate/missing reference: ' + str(ref))
        out[ref] = fp
    return out


def parse_board():
    tree = legacy.parse_sexpr(PCB.read_text(encoding='utf-8'))
    if tree[0] != 'kicad_pcb':
        raise ValueError('Not a KiCad PCB')
    return tree


def local_to_board(fp, x, y):
    p = val(fp, 'at')
    cx, cy = float(p[0]), float(p[1]); a = float(p[2]) if len(p) > 2 else 0
    theta = math.radians(a)
    return (cx + x * math.cos(theta) + y * math.sin(theta),
            cy - x * math.sin(theta) + y * math.cos(theta))


def custom_ground_envelope(fp):
    coords = []
    for p in subs(fp, 'pad'):
        if p[1] != '2':
            continue
        x, y = (float(z) for z in val(p, 'at')[:2])
        for poly in subs(one(p, 'primitives'), 'gr_poly'):
            for q in subs(one(poly, 'pts'), 'xy'):
                coords.append((x + float(q[1]), y + float(q[2])))
    if not coords:
        raise ValueError('No custom GND primitives')
    xs, ys = zip(*coords)
    return [min(xs), max(xs), min(ys), max(ys)]


def pad_rectangle_abs(fp, pad):
    x, y = (float(z) for z in val(pad, 'at')[:2])
    w, h = (float(z) for z in val(pad, 'size')[:2])
    # this board's U101 has zero rotation; rectangle is axis aligned
    pt = local_to_board(fp, x, y)
    return (pt[0] - w/2, pt[1] - h/2, pt[0] + w/2, pt[1] + h/2)


def circle_to_box_distance(x, y, radius, bounds):
    x1, y1, x2, y2 = bounds
    dx = max(x1-x, 0, x-x2)
    dy = max(y1-y, 0, y-y2)
    return max(0.0, math.hypot(dx, dy)-radius)


def pi_attenuator(shunt1, series, shunt2, z0=50.):
    """ABCD cascade of passive shunt-series-shunt resistive pi, real Z0."""
    def mm(a, b):
        return ((a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3]),
                (a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3]))
    y1 = 1.0/shunt1; y2 = 1.0/shunt2
    # matrix multiplication tuple flatten
    A = 1 + series*y2
    B = series
    C = y1 + y2 + series*y1*y2
    D = 1 + series*y1
    den = A + B/z0 + C*z0 + D
    s21 = 2/den
    s11 = (A + B/z0 - C*z0 - D)/den
    loss = -20 * math.log10(abs(s21))
    ret = -20 * math.log10(abs(s11)) if abs(s11)>0 else math.inf
    return {'s21':s21, 's11':s11,'insertion_loss_db':loss,'input_return_loss_db':ret}


def read_resistor(fp):
    props = {q[1]:q[2] for q in subs(fp, 'property')}
    raw = props['Value'].upper().replace('Ω','R')
    if raw.endswith('R'): return float(raw[:-1])
    if 'R' in raw:
        a, b = raw.split('R')
        return float(a + '.' + b)
    raise ValueError('Unsupported resistor value: ' + raw)


def generate():
    tree = parse_board()
    fpmap = footprint_map(tree)
    edge = [s for s in subs(tree, 'gr_rect') if val(s, 'layer')[0]=='Edge.Cuts']
    if len(edge) != 1: raise AssertionError('Expected exactly one rectangular Edge.Cuts outline')
    p0 = [float(x) for x in val(edge[0], 'start')]
    p1 = [float(x) for x in val(edge[0], 'end')]
    width, height = abs(p1[0]-p0[0]), abs(p1[1]-p0[1])
    sma = {}
    for ref in ('J101','J102','J103','J104'):
        fp = fpmap[ref]
        pads = subs(fp,'pad')
        c = [p for p in pads if p[1]=='1']
        grounds = [p for p in pads if p[1]=='2']
        if len(c)!=1 or len(grounds)!=4:raise AssertionError('Invalid pad count for '+ref)
        s = [float(v) for v in val(c[0],'size')]
        g = custom_ground_envelope(fp)
        sma[ref] = {
            'rf_pad_diameter_mm':s[0] if approx(s[0],s[1]) else None,
            'ground_custom_pad_count':len(grounds),
            'ground_envelope_local_xmin_xmax_ymin_ymax_mm':g,
            'ground_y_span_mm':round(g[3]-g[2],4),
            'te_drawing_y_span_mm':7.76,
            'vertical_difference_mm':round((g[3]-g[2])-7.76,4),
            'custom_pad_mask_paste_present':all('F.Mask' in val(p,'layers') and 'F.Paste' in val(p,'layers') for p in grounds),
            'rotation_deg':float(val(fp,'at')[2]) if len(val(fp,'at'))>2 else 0,
            'status':'OPEN - NOT A TE APPROVED FOOTPRINT'
        }
    U=fpmap['U101']
    thermal = [p for p in subs(U,'pad') if p[1]=='2' and [float(v) for v in val(p,'size')]==[1.8,3.48]]
    if len(thermal)!=1: raise AssertionError('U101 thermal pad not found')
    bbox=pad_rectangle_abs(U,thermal[0]); vn=[]
    for v in subs(tree,'via'):
        if val(v,'net')[0]!='1': continue
        x,y=map(float,val(v,'at')[:2]); radius=float(val(v,'size')[0])/2
        dist=circle_to_box_distance(x,y,radius,bbox)
        vn.append({'center_mm':[x,y],'diameter_mm':2*radius,'copper_edge_distance_to_paddle_mm':round(dist,4),
                   'center_inside_paddle_bounds':bbox[0]<=x<=bbox[2] and bbox[1]<=y<=bbox[3]})
    closest=min(vn,key=lambda v:v['copper_edge_distance_to_paddle_mm'])
    grounded=False
    # Explicit F.Cu copper segment intersects pad copper, and its other end is the nearest GND via.
    # Invariant limited to this board / reference path, no copper-plane assumptions.
    for seg in subs(tree,'segment'):
        if val(seg,'net')[0]!='1' or val(seg,'layer')[0]!='F.Cu': continue
        a=[float(z) for z in val(seg,'start')]; b=[float(z) for z in val(seg,'end')]
        if (math.dist(a, closest['center_mm'])<0.01 and bbox[0]<=b[0]<=bbox[2] and bbox[1]<=b[1]<=bbox[3]) or (math.dist(b, closest['center_mm'])<0.01 and bbox[0]<=a[0]<=bbox[2] and bbox[1]<=a[1]<=bbox[3]):
            grounded=True
    refvals={r:read_resistor(fpmap[r]) for r in ('R201','R203','R202')}
    nominal=pi_attenuator(refvals['R201'],refvals['R203'],refvals['R202'])
    tol=0.01
    corners=[pi_attenuator(a,b,c) for a,b,c in itertools.product(*[[v*(1-tol),v*(1+tol)] for v in (refvals['R201'],refvals['R203'],refvals['R202'])])]
    res={
      'revision':'V4.1', 'source_board':'V3.8, read-only',
      'pcb_sha256':hashlib.sha256(PCB.read_bytes()).hexdigest(),
      'pcb_outline_mm':[round(width,3),round(height,3)],
      'footprint_count':len(subs(tree,'footprint')),
      'signal_nets_count':len(subs(tree,'net'))-1,
      'segments_count':len(subs(tree,'segment')),
      'vias_count':len(subs(tree,'via')),
      'ground_zones':{'declared':len(subs(tree,'zone')),'refilled':sum(bool(subs(z,'filled_polygon')) for z in subs(tree,'zone'))},
      'sma':sma,
      'adl5535':{
         'supply_v_typical':5.0,'quiescent_current_a_typical':0.097,
         'quiescent_input_power_w_typical':round(5*0.097,3),
         'power_limit_w_max_abs_rating_with_soldered_paddle':0.650,
         'theta_ja_C_per_W_datasheet_reference_with_soldered_paddle':30.7,
         'quiescent_delta_T_C_reference_only':round(5*0.097*30.7,3),
         'paddle_copper_bounds_mm':[round(v,3) for v in bbox],
         'paddle_size_mm':[1.8,3.48],
         'paste_margin_ratio_setting':float(val(thermal[0],'solder_paste_margin_ratio')[0]),
         'via_centers_within_paddle_count':sum(v['center_inside_paddle_bounds'] for v in vn),
         'closest_ground_via':closest,
         'explicit_track_paddle_to_nearest_via':grounded,
         'thermal_signoff':'OPEN - no thermal/stencil/PCB measurements'
      },
      'attenuator':{
         'network':'R201(shunt)-R203(series)-R202(shunt)',
         'resistors_ohm':refvals,'reference_impedance_ohm':50,
         'ideal_dc_nominal':{k:round(v,6) for k,v in nominal.items()},
         'hypothetical_1percent_corner_analysis':{
              'assumption':'Illustrative ±1% for each resistor; no manufacturing tolerance approved',
              'corner_count':len(corners),
              'loss_db_min':round(min(x['insertion_loss_db'] for x in corners),4),
              'loss_db_max':round(max(x['insertion_loss_db'] for x in corners),4),
              'worst_input_return_loss_db':round(min(x['input_return_loss_db'] for x in corners),4),
         },
         'status':'CALCULATED IDEAL RESISTIVE ONLY - NO RF MEASUREMENT'
      },
      'native_kicad_cli_available':shutil.which('kicad-cli') is not None,
      'native_erc_drc_performed':False,
      'manufacturing_release':'BLOCKED - no Gerber, no PCBWay, no TX',
      'limitations':['not native KiCad ERC or DRC','does not refill zones','no complete 3D official TE alignment',
                     'no circuit parasitics, RF impedance extraction or VNA','theoretical ADL thermal estimate does not validate junction temperature',
                     'no manufacturer-approved BOM tolerance or paste pattern','no proof of full ground connectivity on filled layers']
    }
    REPORT.write_text(json.dumps(res,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return res

if __name__=='__main__':
    r=generate()
    print('PRE-FLIGHT V4.1; NO FAB; PCB SHA256',r['pcb_sha256'])
    print('SMA span', [r['sma'][j]['ground_y_span_mm'] for j in r['sma']])
    print('Thermal nearest via gap',r['adl5535']['closest_ground_via']['copper_edge_distance_to_paddle_mm'])
    print('Pi attenuator dB',r['attenuator']['ideal_dc_nominal']['insertion_loss_db'])
    print('Results:',REPORT)
