#!/usr/bin/env python3
"""V4.3: riproduce e analizza UNA ipotesi di ingombro SMA su copia.
NON e' la geometria approvata TE; NON e' KiCad DRC; NO FAB.
Richiede Python3 e Shapely >= 2.0 e gli audit storici V4.1-V4.2.
"""
from __future__ import annotations
from pathlib import Path
from shapely.ops import unary_union
import re, hashlib, json, math, importlib.util, sys, shutil
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb'
CANDIDATE=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.3_STUDIO_SMA/S3900E_RX_TEST_50R_V4_3_SMA_ENVELOPE_HYPOTHESIS_NOT_FOR_FAB.kicad_pcb'
OUT=Path(__file__).resolve().parent
EXPECTED_SHA='57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489'
modpath=ROOT/'03_Verifiche/V4.2/audit_geometria_rf_v42.py'
spec=importlib.util.spec_from_file_location('s3900v42_auditor',modpath)
v42=importlib.util.module_from_spec(spec)
old_bytecode=sys.dont_write_bytecode;sys.dont_write_bytecode=True
try:spec.loader.exec_module(v42)
finally:sys.dont_write_bytecode=old_bytecode
v41=v42.v41
# Match ONLY the custom pads present in the V3.8 PCB (16 in 4 SMA).
PAD=r'(\(pad "2" smd custom \(at [+-]?2\.850 )([+-]?2\.950)(\))'

def candidate_text():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED_SHA,'Original altered: STOP'
    src=SOURCE.read_text(encoding='utf-8')
    target,count=re.subn(PAD,lambda m:m.group(1)+('-3.130' if m.group(2).startswith('-') else '3.130')+m.group(3),src)
    assert count==16,'Expected exactly sixteen SMA GND pad center adjustments'
    assert target!=src
    return src,target

def inspect_board(t):
    tree=v41.legacy.parse_sexpr(t)
    assert tree[0]=='kicad_pcb'
    fp=v41.footprint_map(tree)
    copper=v42.copper_items(tree)
    distances=[]
    for i,a in enumerate(copper):
        if a['net']==0:continue
        for b in copper[i+1:]:
            if b['net']==0 or b['net']==a['net'] or not (set(a['layers'])&set(b['layers'])):continue
            distances.append((a['geom'].distance(b['geom']),a['id'],b['id']))
    distances.sort()
    ground=[c for c in copper if c['net']==1 and 'F.Cu' in c['layers']]
    united=unary_union([c['geom'] for c in ground]);parts=list(united.geoms) if united.geom_type=='MultiPolygon' else [united]
    ground_vias=[c for c in ground if c['kind']=='via'];ground_pads=[c for c in ground if c['kind']=='pad']
    not_reaching=[]
    for pad in ground_pads:
        connected=[p for p in parts if p.intersects(pad['geom'])]
        if len(connected)!=1 or not any(p.intersects(v['geom']) for p in connected for v in ground_vias):not_reaching.append(pad['id'])
    signal=[]
    for net_id in range(2,9):
        gs=[c['geom'] for c in copper if c['net']==net_id and 'F.Cu' in c['layers']]
        united=unary_union(gs)
        signal.append({'net_id':net_id,'islands':len(united.geoms) if united.geom_type=='MultiPolygon' else 1})
    sma={}
    for ref in ('J101','J102','J103','J104'):
        shape=v41.custom_ground_envelope(fp[ref]);padset=v41.subs(fp[ref],'pad')
        gnd=[p for p in padset if p[1]=='2']
        sma[ref]={
           'gnd_pad_count':len(gnd),
           'local_ground_span_mm':round(shape[3]-shape[2],5),
           'pad_centers_y_mm':[float(v41.val(p,'at')[1]) for p in gnd],
           'rotation_degrees':float(v41.val(fp[ref],'at')[2]) if len(v41.val(fp[ref],'at'))>2 else 0,
           'paste_layers_all':all('F.Paste' in v41.val(p,'layers') for p in gnd)
        }
    stats={'board_footprints':len(v41.subs(tree,'footprint')),
           'segments':len(v41.subs(tree,'segment')),
           'vias':len(v41.subs(tree,'via')),
           'unfilled_zones':sum(not bool(v41.subs(z,'filled_polygon')) for z in v41.subs(tree,'zone')),
           'nets':len(v41.subs(tree,'net'))-1,
           'minimum_inter_net_gap_FCu_mm':round(distances[0][0],5),
           'pairs_under_0p20mm':sum(d[0]<.20-1e-8 for d in distances),
           'ground_pads':len(ground_pads),'ground_pads_without_via_path':not_reaching,
           'signal_nets':signal,'sma':sma,
           'copper_items':len(copper)}
    return stats

def run(write=True):
    original,candidate=candidate_text()
    a=inspect_board(original);b=inspect_board(candidate)
    # Reproducibly compare current deliverable; do not silently overwrite it.
    if CANDIDATE.exists() and CANDIDATE.read_text(encoding='utf-8')!=candidate:
        raise AssertionError('Existing candidate differs from reproducible generator')
    if write and not CANDIDATE.exists():CANDIDATE.write_text(candidate,encoding='utf-8')
    same=['board_footprints','segments','vias','unfilled_zones','nets','copper_items']
    assert all(a[k]==b[k] for k in same)
    assert a['minimum_inter_net_gap_FCu_mm']==b['minimum_inter_net_gap_FCu_mm']==.45
    assert b['pairs_under_0p20mm']==0 and b['ground_pads_without_via_path']==[]
    assert all(net['islands']==1 for net in b['signal_nets'])
    assert all(abs(x['local_ground_span_mm']-7.76)<1e-6 for x in b['sma'].values())
    report={'revision':'V4.3','qualification':'HYPOTHESIS ONLY; NOT TE-APPROVED; NO DRC / NO FAB',
       'source_sha256':hashlib.sha256(original.encode()).hexdigest(),
       'candidate_sha256':hashlib.sha256(candidate.encode()).hexdigest(),
       'edits_exactly_16_ground_pad_centers':True,
       'action':'Y pos of custom GND pads +/-2.950 -> +/-3.130 (0.18 mm outward) for J101..J104; no other edits',
       'original':a,'candidate':b,
       'native_kicad_cli_present':bool(shutil.which('kicad-cli')),
       'native_kicad_DRC':'NOT RUN','schematic_parity':'NOT RUN; latest RX schematic V3.1 does not match V3.8 PCB',
       'te_cad_imported':False,'te_land_pattern_approved':False,
       'adl5535_thermal_approved':False,'fabrication':'BLOCKED'}
    if write:(OUT/'RISULTATI_CANDIDATO_SMA_V4.3.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    result=run()
    print('V4.3 hypothetical land envelope: 7.76 mm all SMA; min 2D clearance 0.45 mm; NO FAB')
