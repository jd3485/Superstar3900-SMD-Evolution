#!/usr/bin/env python3
"""V4.6: risk inventory over immutable KiCad V4.5 candidate (not a DRC)."""
from pathlib import Path
import json, re, math, sys, importlib.util, hashlib
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB'
BRD=P/'S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB.kicad_pcb'
OUT=ROOT/'03_Verifiche/V4.6/AUDIT_TERMICA_SMA_V4.6.json'
M=ROOT/'03_Verifiche/V4.5/crea_librerie_v45.py'
spec=importlib.util.spec_from_file_location('parser',M)
parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)

def property_value(expr,key):
    m=re.search(r'\(property "'+re.escape(key)+r'" "([^"]+)"',expr)
    return m.group(1) if m else None

def xy(expr,head):
    m=re.search(r'\('+re.escape(head)+r'\s+(-?[\d.]+)\s+(-?[\d.]+)',expr)
    if not m:raise ValueError(f'Missing {head} position: {expr[:80]}')
    return (float(m.group(1)),float(m.group(2)))

def first_numeric(expr,head):
    m=re.search(r'\('+re.escape(head)+r'\s+([\d.]+)',expr)
    if not m:raise ValueError(f'Missing {head}')
    return float(m.group(1))

def run():
    board=BRD.read_text('utf8')
    footprints=parser.child(board,'footprint')
    amps=[f for f in footprints if property_value(f,'Reference')=='U101']
    assert len(amps)==1, 'Amplifier reference U101 absent or duplicated'
    amp=amps[0]
    ux,uy=xy(amp,'at')
    pads=parser.child(amp,'pad')
    gnd_pads=[p for p in pads if re.search(r'\(net\s+1\s+"GND_RF"\)',p)]
    assert len(gnd_pads)==2, f'Expected 2 GND copper pads; found {len(gnd_pads)}'
    paddle=[p for p in gnd_pads if '(size 1.800 3.480)' in p]
    assert len(paddle)==1, 'Footprint exposed pad changed: audit manual review'
    pad=paddle[0]
    px,py=xy(pad,'at');sx,sy=xy(pad,'size')
    rect=[ux+px-sx/2,uy+py-sy/2,ux+px+sx/2,uy+py+sy/2]
    via_nodes=parser.child(board,'via')
    gnd_vias=[]
    for v in via_nodes:
        if not re.search(r'\(net\s+1\)',v):continue
        x,y=xy(v,'at');size=first_numeric(v,'size');drill=first_numeric(v,'drill')
        cx=max(rect[0],min(rect[2],x));cy=max(rect[1],min(rect[3],y))
        edge=max(0,math.hypot(x-cx,y-cy)-size/2)
        center_inside=(rect[0]<=x<=rect[2] and rect[1]<=y<=rect[3])
        gnd_vias.append({'x_mm':x,'y_mm':y,'drill_mm':drill,'diameter_mm':size,'copper_edge_gap_mm':round(edge,5),'center_inside_paddle':center_inside})
    gnd_vias.sort(key=lambda v:(v['copper_edge_gap_mm'],v['x_mm'],v['y_mm']))
    zones=parser.child(board,'zone')
    z_layers=[]
    for z in zones:
        m=re.search(r'\(layer\s+"([^"]+)"\)',z)
        if m:z_layers.append(m.group(1))
    smaz=[]
    for f in footprints:
        ref=property_value(f,'Reference')
        if ref and ref in ('J101','J102','J103','J104'):
            ss=parser.child(f,'pad')
            assert len(ss)==5,ref
            smaz.append({'ref':ref,'position_mm':xy(f,'at'),'custom_ground_pad_count':sum(' smd custom ' in p for p in ss),'status':'UNVERIFIED_AGAINST_TE_CAD'})
    assert len(smaz)==4
    assert len(gnd_vias)>0
    assert not any(v['center_inside_paddle'] for v in gnd_vias)
    assert abs(gnd_vias[0]['copper_edge_gap_mm']-0.50)<1e-5
    assert len(zones)==4 and set(z_layers)=={'F.Cu','In1.Cu','In2.Cu','B.Cu'}
    result={'version':'4.6','scope':'STATIC_GEOMETRIC_RISK_INVENTORY_ONLY','pcb_sha256':hashlib.sha256(BRD.read_bytes()).hexdigest(),
      'amplifier':'ADL5535','ref':'U101','paddle_net':'GND_RF','paddle_rect_mm':rect,
      'paddle_size_mm':[sx,sy], 'paddle_copper_area_mm2':round(sx*sy,4),
      'ground_vias_count':len(gnd_vias),'vias_centered_inside_paddle':0,
      'closest_ground_via':gnd_vias[0], 'closest_five_ground_vias':gnd_vias[:5],
      'local_copper_gap_not_thermal_resistance':True,
      'ground_zones_layers':sorted(z_layers), 'ground_zone_count':len(zones),
      'ground_zone_refill':'NOT_RUN_NATIVE_KICAD','sma':sorted(smaz,key=lambda a:a['ref']),
      'manufacturer_cad_te':'LINK_VERIFIED_DOWNLOAD_NOT_AVAILABLE_NO_FULL_APPROVAL',
      'board_copper_modified':False,'kicad_erc_drc':'NOT_RUN',
      'decision':'NO_FAB_NO_PCBWAY_NO_TX'}
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    return result

if __name__=='__main__':
    r=run();print('STATIC AUDIT: U101 pad',r['paddle_rect_mm'],'nearest via gap',r['closest_ground_via']['copper_edge_gap_mm'],'mm; no via in pad; NO FAB')
