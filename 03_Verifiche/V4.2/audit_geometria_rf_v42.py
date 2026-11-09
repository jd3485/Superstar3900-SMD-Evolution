#!/usr/bin/env python3
"""Static PCB copper audit, shape-aware for custom pads. V4.2, NOT a KiCad DRC.

Processes the ORIGINAL V3.8 PCB unmodified. Requires Shapely >=2.0.0.
Layers: explicitly model all F.Cu pads/tracks/vias; other copper planes only
have unfilled zone declarations so are not treated as connected. Treat
rectangular approximation of roundrect pads as conservative; ignore
minuscule curved tolerance and mask/paste manufacturing geometry.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math
from collections import defaultdict
from pathlib import Path
from shapely.geometry import Point, LineString, Polygon, box
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'03_Verifiche/V4.1/audit_rf_v41.py'
PCB=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb'
EXPECTED_SHA='57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489'
spec=importlib.util.spec_from_file_location('audit_rf_v41_for_v42',BASE)
v41=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v41)


def pad_top_geom(fp, pad):
    """Convert pad into F.Cu geometry, including custom polygon(s), pad angle,
    footprint rotation and translation. Not a substitute for KiCad's engine.
    """
    kind=pad[3]
    x,y=(float(v) for v in v41.val(pad,'at')[:2]);w,h=(float(v) for v in v41.val(pad,'size')[:2])
    if kind=='circle': geom=Point(0,0).buffer(w/2,quad_segs=48)
    elif kind in ('rect','roundrect','oval'):geom=box(-w/2,-h/2,w/2,h/2)
    elif kind=='custom':
        pieces=[box(-w/2,-h/2,w/2,h/2)]
        for polygon in v41.subs(v41.one(pad,'primitives'),'gr_poly'):
            pts=[(float(q[1]),float(q[2])) for p in v41.subs(polygon,'pts') for q in v41.subs(p,'xy')]
            if len(pts)>=3:pieces.append(Polygon(pts))
        if len(pieces)==1: raise ValueError('Custom pad without gr_poly')
        geom=unary_union(pieces)
    else:raise ValueError('Unhandled pad shape: '+kind)
    at=v41.val(pad,'at');angle=float(at[2]) if len(at)>2 else 0.0
    geom=translate(rotate(geom,-angle,origin=(0,0)),xoff=x,yoff=y)
    at=v41.val(fp,'at');angle=float(at[2]) if len(at)>2 else 0.0
    geom=translate(rotate(geom,-angle,origin=(0,0)),xoff=float(at[0]),yoff=float(at[1]))
    if geom.is_empty or not geom.is_valid:raise ValueError('Invalid custom copper polygon')
    return geom


def copper_items(tree):
    things=[]
    for fp in v41.subs(tree,'footprint'):
        props={q[1]:q[2] for q in v41.subs(fp,'property')};ref=props['Reference']
        for i,pad in enumerate(v41.subs(fp,'pad')):
            if 'F.Cu' not in v41.val(pad,'layers'):continue
            net=int(v41.val(pad,'net')[0]); geo=pad_top_geom(fp,pad)
            things.append(dict(kind='pad',ref=ref,pin=pad[1],net=net,geom=geo,
                               id=f'{ref}.{pad[1]}#{i}',layers=('F.Cu',)))
    for i,seg in enumerate(v41.subs(tree,'segment')):
        x,y=map(float,v41.val(seg,'start'))
        xx,yy=map(float,v41.val(seg,'end'))
        w=float(v41.val(seg,'width')[0]); net=int(v41.val(seg,'net')[0]);ly=v41.val(seg,'layer')[0]
        geo=LineString(((x,y),(xx,yy))).buffer(w/2,cap_style=1,quad_segs=16)
        things.append(dict(kind='segment',net=net,geom=geo,id=f'segment#{i}',layers=(ly,)))
    for i,via in enumerate(v41.subs(tree,'via')):
        x,y=map(float,v41.val(via,'at')); dia=float(v41.val(via,'size')[0])
        layers=tuple(v41.val(via,'layers')) if v41.subs(via,'layers') else ('F.Cu','In1.Cu','In2.Cu','B.Cu')
        things.append(dict(kind='via',net=int(v41.val(via,'net')[0]),geom=Point(x,y).buffer(dia/2,quad_segs=48),
                           id=f'via#{i}',layers=layers))
    return things


def microstrip_ideal(w_mm,h_mm,er):
    """Zero-thickness isolated microstrip approximation; CPWG geometry not modelled."""
    r=w_mm/h_mm
    ee=(er+1)/2+(er-1)/2/math.sqrt(1+12/r)
    if r<=1:z=60/math.sqrt(ee)*math.log(8/r+r/4)
    else:z=120*math.pi/(math.sqrt(ee)*(r+1.393+0.667*math.log(r+1.444)))
    return z


def analyze():
    sh=hashlib.sha256(PCB.read_bytes()).hexdigest()
    if sh!=EXPECTED_SHA:raise AssertionError('Baseline V3.8 PCB SHA mismatch; do not silently audit a changed board')
    tree=v41.parse_board();things=copper_items(tree)
    netnames={int(x[1]):x[2] for x in v41.subs(tree,'net')}
    minpair=(float('inf'),None,None);violations=[]
    min_recommended_clearance=.20  # analytical threshold, not complete DRC setup
    for i,a in enumerate(things):
        if a['net']==0:continue
        for b in things[i+1:]:
            if a['net']==b['net'] or b['net']==0 or not (set(a['layers'])&set(b['layers'])):continue
            d=a['geom'].distance(b['geom'])
            if d<minpair[0]:minpair=(d,a['id'],b['id'])
            if d<min_recommended_clearance-1e-7:
                violations.append(dict(a=a['id'],b=b['id'],a_net=netnames[a['net']],b_net=netnames[b['net']],gap_mm=round(d,5)))
    signal=[]
    for net_id in range(2,9):
        gs=[a['geom'] for a in things if a['net']==net_id and 'F.Cu' in a['layers']]
        u=unary_union(gs)
        islands=len(u.geoms) if u.geom_type=='MultiPolygon' else 1
        signal.append(dict(net=netnames[net_id],copper_islands_without_zone_fill=islands))
    g_items=[a for a in things if a['net']==1 and 'F.Cu' in a['layers']]
    g_pads=[a for a in g_items if a['kind']=='pad']
    g_vias=[a for a in g_items if a['kind']=='via']
    ground_union=unary_union([a['geom'] for a in g_items])
    pieces=list(ground_union.geoms) if ground_union.geom_type=='MultiPolygon' else [ground_union]
    no_via=[]
    for pad in g_pads:
        connected=[poly for poly in pieces if poly.intersects(pad['geom'])]
        if len(connected)!=1:raise AssertionError('Unresolved geometric island for ground pad '+pad['id'])
        if not any(connected[0].intersects(via['geom']) for via in g_vias):no_via.append(pad['id'])
    fpmap=v41.footprint_map(tree)
    sma={}
    for ref in ('J101','J102','J103','J104'):
        fp=fpmap[ref]; ground=[p for p in things if p['kind']=='pad' and p.get('ref')==ref and p['pin']=='2']
        copper=unary_union([p['geom'] for p in ground]);bounds=copper.bounds
        local=v41.custom_ground_envelope(fp)
        sma[ref]={
           'rotation_deg':float(v41.val(fp,'at')[2]) if len(v41.val(fp,'at'))>2 else 0,
           'ground_custom_polygon_count':len(ground),
           'ground_bounds_board_coords_mm':[round(x,4) for x in bounds],
           'ground_span_mm':round(local[3]-local[2],4),
           'te_recommended_span_mm':7.76,
           'difference_from_recommended_span_mm':round(local[3]-local[2]-7.76,4),
           'footprint_status':'OPEN; not approved by TE or assembler'}
    # Footprint courtyards may extend outside Edge.Cuts intentionally for right-angle SMA connectors.
    edge=[n for n in v41.subs(tree,'gr_rect') if v41.val(n,'layer')[0]=='Edge.Cuts']
    if len(edge)!=1:raise AssertionError('Exactly one board outline expected')
    e0=[float(x) for x in v41.val(edge[0],'start')];e1=[float(x) for x in v41.val(edge[0],'end')]
    board_bounds=(min(e0[0],e1[0]),min(e0[1],e1[1]),max(e0[0],e1[0]),max(e0[1],e1[1]))
    mechanical={}
    for ref in ('J101','J102','J103','J104'):
        fp=fpmap[ref]
        courts=[c for c in v41.subs(fp,'fp_rect') if v41.val(c,'layer')[0]=='F.CrtYd']
        if len(courts)!=1:raise AssertionError('Missing/unexpected courtyard for '+ref)
        c=courts[0];p0=[float(x) for x in v41.val(c,'start')];p1=[float(x) for x in v41.val(c,'end')]
        cr=box(min(p0[0],p1[0]),min(p0[1],p1[1]),max(p0[0],p1[0]),max(p0[1],p1[1]))
        at=v41.val(fp,'at'); rot=float(at[2]) if len(at)>2 else 0
        cr=translate(rotate(cr,-rot,origin=(0,0)),xoff=float(at[0]),yoff=float(at[1]))
        b=cr.bounds
        mechanical[ref]={'courtyard_bounds_mm':[round(q,3) for q in b],
                         'beyond_left_edge_mm':round(max(0,board_bounds[0]-b[0]),3),
                         'beyond_right_edge_mm':round(max(0,b[2]-board_bounds[2]),3),
                         'meaning':'Approximate courtyard/overhang, not TE 3D body or mechanical signoff'}
    zone_count=len(v41.subs(tree,'zone'))
    zone_filled=sum(bool(v41.subs(z,'filled_polygon')) for z in v41.subs(tree,'zone'))
    hcases={f'{h:.2f}':round(microstrip_ideal(.28,h,4.2),2) for h in (.08,.10,.12,.14,.16,.18,.20,.25,.30)}
    out={
      'revision':'V4.2','baseline':'V3.8 immutable NOT_FOR_FAB board','pcb_sha256':sh,
      'geometry_engine':'Shapely top-copper geometric model, NOT KiCad DRC/zone fill',
      'pad_geometry':'custom gr_poly + anchor, footprint rotation, nominal circles; roundrect as conservative box',
      'copper_shape_count':len(things),
      'top_copper_inter_net_clearance':{
         'review_threshold_mm':min_recommended_clearance,
         'closest_distance_mm':round(minpair[0],5),
         'closest_pair':[minpair[1],minpair[2]],
         'clearance_below_review_threshold_count':len(violations),
         'violations_first_30':violations[:30],
         'meaning':'Nominal F.Cu 2D review only; excludes mask, paste, board house limits, non-F.Cu tracks/planes, DRC',
      },
      'signal_net_copper_components':signal,
      'ground_top_copper':{
        'ground_pad_count':len(g_pads),'ground_via_count':len(g_vias),
        'ground_pads_not_reaching_a_local_via_over_explicit_F_Cu':no_via,
        'islands_without_plane_fill':len(pieces),
        'meaning':'No claim of global GND connectivity until four zones are refilled and DRC passes',
      },
      'sma':sma,
      'board_outline_bounds_mm':[round(q,3) for q in board_bounds],
      'sma_courtyard_envelopes':mechanical,
      'zone_status':{'declared':zone_count,'filled':zone_filled},
      'microstrip_sensitivity_STUDY_ONLY':{
        'trace_width_mm':.28,'epsilon_r_assumed':4.2,
        'dielectric_height_mm_to_Z0_ohm':hcases,
        'assumptions':'Isolated ideal zero-thickness microstrip, no adjacent ground pour, no soldermask or weave. NOT a model of actual CPWG routing.',
        'action':'Obtain manufacturer 4-layer stack-up and solve real grounded coplanar waveguide with mask before impedance signoff'
      },
      'approval':{'kicad_native_DRC':'NOT RUN','kicad_native_ERC':'NOT RUN','te_mechanical':'OPEN','adi_thermal':'OPEN','stackup':'OPEN','rf_bench':'NOT BUILT','fabrication':'BLOCKED'},
    }
    return out

if __name__=='__main__':
    result=analyze()
    dest=OUT/'RISULTATO_GEOMETRIA_RF_V4.2.json'
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    m=result['top_copper_inter_net_clearance']
    print('V4.2 STATIC ONLY; min copper clearance %.3f mm; violations %d; signal nets %d; NO FAB' %
          (m['closest_distance_mm'],m['clearance_below_review_threshold_count'],len(result['signal_net_copper_components'])))
    print(dest)
