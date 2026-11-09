#!/usr/bin/env python3
"""V5.7 — idealized GND zone envelope / via-access geometric audit.

Not a KiCad zone filler. Uses planar Shapely subtraction to identify gross
obstructions only. Does NOT model KiCad thermal spokes, min-neck removal,
island rules, pad overrides, stackup, copper thickness, drills or DRC.
All results are REVIEW/NO FAB, never native KiCad validation.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'03_Verifiche/V5.5'))
from audit_rame_v55 import PCB, actual_board_copper, parse, children, child, numpair
LAYERS=('F.Cu','In1.Cu','In2.Cu','B.Cu')
EDGE_MARGIN_MIN_MM=0.5   # analytical screen, NOT fab's edge requirement


def polygon_list(shape):
    if shape.is_empty:return []
    if shape.geom_type=='Polygon':return [shape]
    if hasattr(shape,'geoms'):
        return [g for x in shape.geoms for g in polygon_list(x)]
    return []


def approximate_pour(outline:Polygon, obstacles,clearance_mm=0.30):
    """Over-permissive upper-bound geometric fill; NO thermal connections!"""
    if not (0.05<=clearance_mm<=1.00): raise ValueError('Only analytical clearance 0.05–1.0mm')
    exclusions=unary_union([g.buffer(clearance_mm,quad_segs=20) for g in obstacles]) if obstacles else Polygon()
    return outline.difference(exclusions)


def audit(text: str,clearance_mm:float=0.30):
    board=parse(text)
    items,count,nets=actual_board_copper(text)
    zs=children(board,'zone'); edge=[r for r in children(board,'gr_rect') if child(r,'layer')[1]=='Edge.Cuts']
    errors=[]
    if len(edge)!=1:
        errors.append('EDGE_OUTLINE_NOT_SINGLE_RECTANGLE')
        outline=box(20,20,130,82)  # only to allow diagnostic on malformed mutants
    else:
        e=edge[0]; outline=box(*numpair(child(e,'start')),*numpair(child(e,'end')))
    via_nodes=children(board,'via')
    if len(via_nodes)!=70:errors.append('VIA_COUNT_CHANGED')
    if any(int(child(v,'net')[1])!=1 for v in via_nodes):errors.append('VIA_NET_NOT_GND')
    if any(child(v,'layers')[1:]!=['F.Cu','B.Cu'] or not isinstance(v[1],list) for v in via_nodes):
        errors.append('VIA_NOT_STANDARD_F_TO_B')
    zone_by_layer={}
    for z in zs:
        layer=child(z,'layer')[1];net=int(child(z,'net')[1]);name=child(z,'net_name')[1]
        if layer in zone_by_layer:errors.append('DUPLICATE_ZONE_LAYER:'+layer)
        zone_by_layer[layer]=z
        if net!=1 or name!='GND_RF':errors.append('ZONE_NET_NOT_GND:'+layer)
        if children(z,'filled_polygon'):errors.append('ZONE_ALREADY_FILLED_NATIVE_REAUDIT_REQUIRED:'+layer)
        fill=child(z,'fill'); cp=child(z,'connect_pads')
        gap=child(fill,'thermal_gap') if fill else None
        spoke=child(fill,'thermal_bridge_width') if fill else None
        if not (cp and child(cp,'clearance') and abs(float(child(cp,'clearance')[1])-0.3)<1e-8):
            errors.append('ZONE_CLEARANCE_CHANGED:'+layer)
        if not (gap and spoke and abs(float(gap[1])-0.4)<1e-8 and abs(float(spoke[1])-0.5)<1e-8):
            errors.append('ZONE_THERMAL_PARAMETERS_CHANGED:'+layer)
    if len(zs)!=4 or set(zone_by_layer)!=set(LAYERS):errors.append('ZONE_LAYER_SET_CHANGED')
    if count['pads']!=44 or count['segments']!=44 or count['vias']!=70:
        errors.append('TOP_COPPER_OBJECT_COUNTS_CHANGED')
    if len(nets)-1!=8:errors.append('NET_COUNT_CHANGED')
    if nets.get(1)!='GND_RF':errors.append('GND_NET_ID_CHANGED')
    if any(int(child(s,'net')[1])!=1 and child(s,'layer')[1]!='F.Cu' for s in children(board,'segment')):
        errors.append('NON_GND_TRACK_ON_INNER_OR_BACK_LAYER')
    # Report pad pad types on other layers; current baseline uses only SMD pads on F.Cu.
    foreign_multilayer_pads=[]
    for fp in children(board,'footprint'):
        for pad in children(fp,'pad'):
            padnet=child(pad,'net');net=int(padnet[1]) if padnet else 0
            layers=child(pad,'layers')
            if net!=1 and layers and any(l in ('*.Cu','In1.Cu','In2.Cu','B.Cu') for l in layers[1:]):
                foreign_multilayer_pads.append({'number':pad[1],'layers':layers[1:]})
    if foreign_multilayer_pads:errors.append('UNMODELED_FOREIGN_NET_MULTILAYER_PADS')
    gnd_pads=[x for x in items if x['kind']=='pad' and x['net']==1]
    gnd_vias=[x for x in items if x['kind']=='via' and x['net']==1]
    foreign=[x for x in items if x['net'] not in (0,1)]
    results={}
    for layer in LAYERS:
        zone=zone_by_layer.get(layer)
        if zone is None:continue
        polytag=child(zone,'polygon'); pts=child(polytag,'pts') if polytag else None
        xy=[numpair(x) for x in children(pts,'xy')] if pts else []
        if len(xy)<3:
            errors.append('ZONE_POLYGON_INVALID:'+layer);continue
        zpoly=Polygon(xy)
        if not zpoly.is_valid or zpoly.area<1:
            errors.append('ZONE_POLYGON_INVALID:'+layer);continue
        if not outline.covers(zpoly) or outline.boundary.distance(zpoly)<EDGE_MARGIN_MIN_MM-1e-8:
            errors.append('ZONE_EDGE_MARGIN_TOO_SMALL:'+layer)
        # Key upper-bound assumption: only F.Cu carries non-GND copper in this board.
        # A zone pour on other layers is its raw outline if no foreign-net copper there.
        other_copper=[x['geometry'] for x in foreign] if layer=='F.Cu' else []
        hypothetical=approximate_pour(zpoly,other_copper,clearance_mm)
        pieces=sorted(polygon_list(hypothetical),key=lambda p:-p.area)
        large=pieces[0] if pieces else Polygon()
        vcovers=sum(large.intersects(v['geometry']) for v in gnd_vias)
        pcovers=sum(large.intersects(p['geometry']) for p in gnd_pads) if layer=='F.Cu' else None
        all_via_in_outline=sum(zpoly.covers(v['geometry']) for v in gnd_vias)
        via_edge_dist=min(v['geometry'].distance(zpoly.boundary) for v in gnd_vias) if gnd_vias else None
        results[layer]={
            'zone_area_mm2':round(zpoly.area,4),
            'analytical_clearance_mm':clearance_mm,
            'hypothetical_region_count':len(pieces),
            'largest_hypothetical_area_mm2':round(large.area,4),
            'all_hypothetical_areas_mm2':[round(p.area,4) for p in pieces],
            'largest_region_fraction_of_outline':round(large.area/zpoly.area,6),
            'gnd_vias_geom_in_zone':all_via_in_outline,
            'gnd_vias_geom_touch_largest_hypothetical_region':vcovers,
            'fcu_gnd_pads_geom_touch_largest_hypothetical_region':pcovers,
            'min_via_annulus_to_zone_outline_mm':round(via_edge_dist,4),
            'pad_thermal_spokes':'NOT_MODELED',
            'actual_fill':'UNFILLED'}
        if all_via_in_outline!=70:errors.append('VIA_ANNULUS_OUTSIDE_ZONE:'+layer)
        if vcovers!=70:errors.append('VIA_POTENTIAL_LARGEST_REGION_MISSING:'+layer)
        if len(pieces)!=1:errors.append('HYPOTHETICAL_ZONE_SPLIT:'+layer)
        if layer=='F.Cu' and pcovers!=24:errors.append('GND_PAD_NOT_TOUCHING_HYPOTHETICAL_REGION')
    return {
        'revision':'V5.7', 'study_type':'IDEALIZED_ZONE_ENVELOPE_UPPER_BOUND_NOT_KICAD_FILL',
        'board_sha256':hashlib.sha256(text.encode()).hexdigest(),
        'zone_clearance_screen_mm':clearance_mm,
        'ground_pads_fcu':len(gnd_pads),'ground_vias_fcu':len(gnd_vias),
        'ground_zones_unfilled':count['zones'],'individual_grounds_before_fill':64,
        'layers':results,'errors':sorted(set(errors)),
        'status':'STATIC_ENVELOPE_PASS_NATIVE_PENDING' if not errors else 'STATIC_ENVELOPE_FAIL',
        'native_zone_refill':'NOT_RUN','native_erc':'NOT_RUN','native_drc':'NOT_RUN',
        'fabrication_allowed':False, 'tx_allowed':False,
        'limitations':[
            'Hypothetical fill is geometrically OVER-PERMISSIVE. It does NOT compute KiCad zones.',
            'Subtracts only 0.30mm clearance from other-net F.Cu pads and tracks; actual PCB rules may require larger clearances.',
            'It omits all thermal relief gaps/spokes, min thickness and narrow-neck removal, zone island-removal rules, board-stackup behavior and actual connectivity.',
            'Inner layers are modeled as polygon envelopes because this baseline has no foreign-net inner copper or via; this is NOT an actual layer fill.',
            'Overlaps with a GND pad or via indicate possible geometric access, not a verified electrical or manufacturable connection.',
            'Only a KiCad native zone fill + DRC including unconnected items and manual RF review can validate ground return.',
            'NO FAB, NO PCBWay, NO TX']}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pcb',type=Path,default=PCB)
    ap.add_argument('--clearance',type=float,default=0.30)
    ap.add_argument('--output',type=Path)
    a=ap.parse_args()
    result=audit(a.pcb.read_text(encoding='utf-8'),a.clearance)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='limitations'},ensure_ascii=False,indent=2))
    return 0 if result['status']=='STATIC_ENVELOPE_PASS_NATIVE_PENDING' else 2
if __name__=='__main__':raise SystemExit(main())
