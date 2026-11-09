#!/usr/bin/env python3
"""V5.6: audit topology of *unfilled* F.Cu from KiCad board S-expressions.

This is a conservative, static, single-layer topology screen, NOT KiCad DRC,
NOT a zone refill, NOT electrical continuity across copper layers, NOT FAB.
Geometrics are imported from the already-tested V5.5 Shapely clearance auditor.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import argparse, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '03_Verifiche/V5.5'))
from audit_rame_v55 import actual_board_copper, PCB, parse, child, children

V48 = ROOT / '04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB.kicad_pcb'
COPPER_LAYERS = ('F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu')
EPSILON_MM = 1e-5


def components_for_items(items, epsilon=EPSILON_MM):
    """Connected components per net; geometry is copper intersection/touch on F.Cu.

    Never connect elements of unlike nets. A via here represents *its F.Cu pad*;
    its existence does not establish continuity on unfilled inner planes.
    """
    if epsilon < 0 or epsilon > 0.005: raise ValueError('EPSILON must be <= 5 um')
    parent = list(range(len(items)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i,a in enumerate(items):
        if a['net'] == 0:continue
        for j in range(i+1,len(items)):
            b=items[j]
            if a['net'] != b['net']:continue
            if a['geometry'].distance(b['geometry']) <= epsilon:
                parent[find(i)] = find(j)
    comps=defaultdict(list)
    for i,item in enumerate(items):
        comps[(item['net'],find(i))].append(item)
    return comps


def audit_board(text, reference_text=None, minimum_signal_groups=7):
    items,counts,nets=actual_board_copper(text)
    pcb=parse(text)
    zones=children(pcb,'zone')
    zone_rows=[]
    for z in zones:
        layer=child(z,'layer')
        zone_rows.append({'layer':layer[1] if layer else None,
                          'net':int(child(z,'net')[1]),
                          'name':child(z,'net_name')[1] if child(z,'net_name') else '',
                          'filled_polygons':len(children(z,'filled_polygon'))})
    comps=components_for_items(items)
    net_rows={}
    comps_per_net=defaultdict(list)
    for (net,_),c in comps.items():
        comps_per_net[net].append(c)
    for net in sorted(nets):
        if net==0:continue
        clusters=comps_per_net.get(net,[])
        net_rows[nets[net]]={
            'net_id':net,'component_count':len(clusters),
            'pad_count':sum(x['kind']=='pad' for c in clusters for x in c),
            'track_count':sum(x['kind']=='segment' for c in clusters for x in c),
            'via_count':sum(x['kind']=='via' for c in clusters for x in c),
            'pad_containing_islands':sum(any(x['kind']=='pad' for x in c) for c in clusters),
            'via_only_islands':sum(all(x['kind']=='via' for x in c) for c in clusters),
        }
    gnd=net_rows.get('GND_RF',{})
    ground_pad_islands=[]
    for c in comps_per_net.get(1,[]):
        pads=sorted(x['id'] for x in c if x['kind']=='pad')
        if pads:
            ground_pad_islands.append({'pads':pads,'tracks':sum(x['kind']=='segment' for x in c),
              'vias':sum(x['kind']=='via' for x in c)})
    ground_pad_islands.sort(key=lambda x:x['pads'])
    copper_reference_match=None
    if reference_text is not None:
        other,refcounts,refnets=actual_board_copper(reference_text)
        copper_reference_match=(counts==refcounts and nets==refnets and len(items)==len(other)
          and all(a['kind']==b['kind'] and a['id']==b['id'] and a['net']==b['net']
             and a['geometry'].equals_exact(b['geometry'],tolerance=0)
             for a,b in zip(items,other)))
    errors=[]
    signal_nets=[n for n in net_rows if n!='GND_RF']
    if len(signal_nets)!=minimum_signal_groups:errors.append('SIGNAL_NET_COUNT_CHANGED')
    for n in signal_nets:
        if net_rows[n]['component_count']!=1:errors.append('SIGNAL_COPPER_DISCONNECTED:'+n)
        if net_rows[n]['pad_count'] < 2:errors.append('SIGNAL_INSUFFICIENT_PADS:'+n)
    if 'GND_RF' not in net_rows:errors.append('GROUND_NET_MISSING')
    if len(zone_rows)!=4 or sorted(x['layer'] for x in zone_rows)!=sorted(COPPER_LAYERS) or any(
        x['net']!=1 or x['name']!='GND_RF' for x in zone_rows):errors.append('GROUND_ZONE_CONFIG_MISMATCH')
    if any(x['filled_polygons'] for x in zone_rows):errors.append('ZONE_STATE_CHANGED_REAUDIT_REQUIRED')
    if any(x['net']!=1 for x in items if x['kind']=='via'):errors.append('VIA_NET_UNEXPECTED')
    if copper_reference_match is False:errors.append('COPPER_NOT_IDENTICAL_TO_V48')
    return {
        'revision':'V5.6','scope':'TOP_COPPER_ONLY_UNFILLED_GEOMETRY',
        'board_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),
        'reference_v48_sha256':hashlib.sha256(reference_text.encode('utf-8')).hexdigest() if reference_text else None,
        'copper_identical_to_v48_study':copper_reference_match,
        'geometry_counts':counts,'net_count':len(nets)-1,
        'fcu_networks':net_rows,'ground_pad_islands':ground_pad_islands,
        'ground_zones':zone_rows,
        'ground_pad_islands_count':gnd.get('pad_containing_islands',0),
        'ground_via_only_islands_count':gnd.get('via_only_islands',0),
        'ground_top_islands_count':gnd.get('component_count',0),
        'ground_connectivity':'PENDING_ZONE_REFILL_AND_NATIVE_DRC',
        'signal_connectivity':'STATIC_PASS' if not any('SIGNAL_' in x for x in errors) else 'STATIC_FAIL',
        'errors':errors,
        'status':'STATIC_TOPOLOGY_PASS_GROUND_PENDING' if not errors else 'STATIC_TOPOLOGY_FAIL',
        'native_erc':'NOT_RUN','native_drc':'NOT_RUN','fabrication_allowed':False,
        'limitations':[
          'Ground islands are NOT DRC violations: four GND zones are present but UNFILLED.',
          'This does not compute zone pours, thermal reliefs, drill clearance, netlist validity or interlayer paths.',
          'Round pads/vias are polygonal Shapely approximations. 0.00001mm tolerance only avoids numerical noise.',
          'A through-via on F.Cu does NOT prove that a ground plane is attached on any internal layer.',
          'The V4.8 copper comparison is a static geometry identity check, not a native KiCad check.',
          'Never use as a PCB fabrication authorization or radio TX authorization.'
        ]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pcb',type=Path,default=PCB)
    p.add_argument('--reference-pcb',type=Path,default=V48)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=audit_board(args.pcb.read_text(encoding='utf-8'),args.reference_pcb.read_text(encoding='utf-8'))
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('ground_pad_islands','limitations','fcu_networks')},ensure_ascii=False,indent=2))
    return 0 if result['status']=='STATIC_TOPOLOGY_PASS_GROUND_PENDING' else 2

if __name__=='__main__':raise SystemExit(main())
