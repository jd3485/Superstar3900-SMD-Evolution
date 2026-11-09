#!/usr/bin/env python3
"""Audit riproducibile, SOLO statico, dello stencil U101 V4.8.
Nessuna generazione CAM; mai interpretare questo risultato come DRC/DFM.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V48 = '04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB'
BOARD = f'{V48}/S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB.kicad_pcb'
AUDIT48 = '03_Verifiche/V4.8/AUDIT_VARIANTE_TERMICA_V4.8.json'


def block(s: str, start: int) -> str:
    assert s[start] == '('
    level = 0
    quoted = False
    escaped = False
    for i in range(start, len(s)):
        c = s[i]
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
        elif c == '"': quoted = True
        elif c == '(': level += 1
        elif c == ')':
            level -= 1
            if level == 0: return s[start:i + 1]
    raise ValueError('Unclosed KiCad expression')


def rx(pattern: str, text: str, label: str):
    m = re.search(pattern, text)
    if not m: raise ValueError('Missing ' + label)
    return m


def analyse(root: Path = ROOT) -> dict:
    original = (root / BOARD).read_bytes()
    s = original.decode('utf-8')
    prior = json.loads((root / AUDIT48).read_text('utf-8'))
    pad_component = 'S3900E_V38_Review:ADL5535_SOT89_PASTE_REVIEW'
    idx = s.index(f'(footprint "{pad_component}"')
    f = block(s, idx)
    ref = rx(r'\(property "Reference" "([^"]+)"', f, 'reference').group(1)
    if ref != 'U101': raise ValueError('unexpected reference')
    at = rx(r'\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)', f, 'location')
    fx, fy = float(at[1]), float(at[2]); angle=float(at[3] or 0)
    if angle != 0: raise ValueError('rotation no longer zero; update calculation')
    pads = [block(f, m.start()) for m in re.finditer(r'\(pad "2" smd rect', f)]
    pads = [p for p in pads if '(solder_paste_margin_ratio' in p]
    if len(pads) != 1: raise ValueError('thermal pad ambiguous')
    pad = pads[0]
    p_at = rx(r'\(at ([\d.\-]+) ([\d.\-]+)\)', pad, 'pad position')
    p_size = rx(r'\(size ([\d.\-]+) ([\d.\-]+)\)', pad, 'pad size')
    px, py = fx + float(p_at[1]), fy + float(p_at[2])
    w,h = float(p_size[1]),float(p_size[2])
    ratio = float(rx(r'\(solder_paste_margin_ratio ([\d.\-]+)\)',pad,'paste ratio')[1])
    if '"F.Paste"' not in pad or '"F.Mask"' not in pad: raise ValueError('pad layer changed')
    if '"F.Cu"' not in pad or '(net 1 "GND_RF")' not in pad: raise ValueError('thermal GND changed')
    paste_w, paste_h = w*(1+ratio), h*(1+ratio)
    if min(paste_w,paste_h) <=0: raise ValueError('negative paste aperture')
    bbox=(px-w/2,py-h/2,px+w/2,py+h/2)
    pbbox=(px-paste_w/2, py-paste_h/2, px+paste_w/2, py+paste_h/2)
    all_via = [block(s,m.start()) for m in re.finditer(r'\(via \(at ',s)]
    assigned=[]
    for x,y in prior['via_positions_mm']:
        located=[]
        for via in all_via:
            atv=rx(r'\(at ([\d.\-]+) ([\d.\-]+)\)',via,'via position')
            if abs(float(atv[1])-x)<1e-6 and abs(float(atv[2])-y)<1e-6: located.append(via)
        if len(located)!=1: raise ValueError(f'missing/duplicated via {x} {y}')
        via=located[0]
        d=float(rx(r'\(drill ([\d.]+)\)',via,'via drill')[1]); D=float(rx(r'\(size ([\d.]+)\)',via,'via size')[1])
        net=int(rx(r'\(net (\d+)\)',via,'via net')[1])
        x=float(x); y=float(y); r=d/2; cr=D/2
        centered = (pbbox[0] < x < pbbox[2] and pbbox[1] < y < pbbox[3])
        hole_fully_inside = min(x-pbbox[0],pbbox[2]-x,y-pbbox[1],pbbox[3]-y) >= r
        hole_gap = min(x-pbbox[0],pbbox[2]-x,y-pbbox[1],pbbox[3]-y)-r
        assigned.append(dict(x=x,y=y,drill=d,copper_diameter=D,net=net,
                             under_paste_center=centered, hole_fully_under_paste=hole_fully_inside,
                             min_hole_edge_to_paste_edge_mm=round(hole_gap,6),
                             copper_inside_pad=(x-cr > bbox[0] and x+cr < bbox[2] and y-cr > bbox[1] and y+cr < bbox[3])))
    t=float(rx(r'\(general \(thickness ([\d.]+)\)',s,'board thickness')[1])
    layers=block(s, s.index('(layers'))
    copper=re.findall(r'\(\d+ "(?:F|In\d+|B)\.Cu" (?:signal|power)\)',layers)
    count=len(copper)
    dr=sorted(set(v['drill'] for v in assigned))
    report={
        'revision':'V4.9','scope':'static_paste_overlap_of_V4.8_variant','authorized_for_fabrication':False,
        'native_kicad_erc':'NOT_RUN','native_kicad_drc':'NOT_RUN','pcbway_process_approval':'NOT_RECEIVED',
        'board_file':BOARD,'board_sha256':hashlib.sha256(original).hexdigest(),
        'board_thickness_mm':t,'copper_layer_count':count,
        'U101': {'reference':ref,'center_mm':[px,py], 'thermal_pad_size_mm':[w,h],
                 'thermal_pad_bbox_mm':list(bbox),'paste_margin_ratio':ratio,
                 'paste_bbox_mm':list(pbbox),'paste_size_mm':[round(paste_w,6),round(paste_h,6)],
                 'paste_area_mm2':round(paste_w*paste_h,6),
                 'paste_coverage_ratio_vs_pad':round(paste_w*paste_h/(w*h),6)},
        'vias':assigned,'via_count':len(assigned),
        'six_via_centers_under_paste':all(v['under_paste_center'] for v in assigned),
        'all_six_holes_fully_under_paste':all(v['hole_fully_under_paste'] for v in assigned),
        'all_six_via_copper_inside_pad':all(v['copper_inside_pad'] for v in assigned),
        'all_six_gnd':all(v['net']==1 for v in assigned),
        'nominal_annular_ring_mm':round((assigned[0]['copper_diameter']-assigned[0]['drill'])/2,6),
        'nominal_aspect_ratio':round(t/assigned[0]['drill'],3),
        'total_hole_area_as_fraction_of_paste':round(len(assigned)*math.pi*(assigned[0]['drill']/2)**2/(paste_w*paste_h),6),
        'previous_v48_candidate_sha256_match':hashlib.sha256(original).hexdigest()==prior['board_candidate_sha256'],
        'sources': [
            'https://www.analog.com/en/products/adl5535.html',
            'https://www.pcbway.com/pcb_prototype/PCB_Via_in_Pad.html',
            'https://www.pcbway.com/capabilities.html',
            'https://www.pcbway.com/helpcenter/ordering_parameter_instruction/Via_Filled_with_Copper.html',
            'https://www.te.com/en/product-CONSMA002-SMD-G.html',
            'https://docs.kicad.org/10.0/en/cli/cli.html',
        ],
        'limit': 'Geometric static audit only: no stencil proof, thermal FEA, solder-joint evaluation, impedance, CAD TE, native DRC/ERC, BOM or measurements.'
    }
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    v=analyse(args.root)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('V4.9 U101 paste/copper: ',v['via_count'],'holes; all under paste =',v['all_six_holes_fully_under_paste'])
    print('t=',v['board_thickness_mm'],'mm, layers=',v['copper_layer_count'],' aspect=',v['nominal_aspect_ratio'])
    print('paste opening',v['U101']['paste_size_mm'], 'mask/DFM/DRC not validated')

if __name__=='__main__':main()
