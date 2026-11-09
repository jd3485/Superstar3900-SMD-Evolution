#!/usr/bin/env python3
"""Revisione nominale read-only V3.9 del PCB sperimentale V3.8.

Usa soltanto il parser S-expression interno gia' presente. Non esegue
KiCad/ERC/DRC, non certifica footprint o saldabilita'; non muta il PCB.
La geometria pubblicata nel disegno TE e' da verificare nel CAD ufficiale.
"""
from pathlib import Path
import importlib.util, json, shutil, hashlib
R=Path(__file__).resolve().parents[2]
BASE=R/'03_Verifiche/V3.6/audit_v36.py'
BOARD=R/'04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb'
OUTPUT=R/'03_Verifiche/V3.9/Esito_Confronto_Footprint_V3.9.json'
s=importlib.util.spec_from_file_location('v36_parser_for_v39',BASE)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
tree=m.parse_sexpr(BOARD.read_text(encoding='utf8'))
assert tree[0]=='kicad_pcb'
footprints={}
for fp in m.subs(tree,'footprint'):
 props={p[1]:p[2] for p in m.subs(fp,'property')}
 if 'Reference' in props: footprints[props['Reference']]=fp

def oval_pad_extents(fp):
    # V3.8 SMA custom pads have local gr_poly coordinates in mm.
    xs=[];ys=[]
    for p in m.subs(fp,'pad'):
        if p[1]!='2': continue
        pos=m.one(p,'at'); px,py=float(pos[1]),float(pos[2])
        for pr in m.subs(m.one(p,'primitives'),'gr_poly'):
            pts=m.one(pr,'pts')
            for q in m.subs(pts,'xy'):
                xs.append(px+float(q[1]));ys.append(py+float(q[2]))
    return (round(min(xs),3),round(max(xs),3),round(min(ys),3),round(max(ys),3))

conns={}
for ref in ['J101','J102','J103','J104']:
 fp=footprints[ref]
 pads=m.subs(fp,'pad')
 center=[p for p in pads if p[1]=='1']
 grounds=[p for p in pads if p[1]=='2']
 assert len(center)==1 and len(grounds)==4
 size=[float(v) for v in m.one(center[0],'size')[1:]]
 envelope=oval_pad_extents(fp)
 height=round(envelope[3]-envelope[2],3)
 conns[ref]={
  'center_smd_diameter_mm':size[0] if size[0]==size[1] and center[0][2]=='smd' else None,
  'center_drill_present':bool(m.subs(center[0],'drill')),
  'ground_pad_count':len(grounds),
  'ground_envelope_local_mm':envelope,
  'ground_envelope_height_mm':height,
  'te_recommended_footprint_nominal_height_mm':7.76,
  'total_height_delta_vs_te_mm':round(height-7.76,3),
  'all_ground_pads_custom_smd':all(p[2]=='smd' and p[3]=='custom' for p in grounds),
  'all_ground_pads_have_mask_and_paste':all('F.Mask' in str(m.one(p,'layers')) and 'F.Paste' in str(m.one(p,'layers')) for p in grounds),
 }

u=footprints['U101']
upads=m.subs(u,'pad')
paddle=[p for p in upads if p[1]=='2' and [float(v) for v in m.one(p,'size')[1:]]==[1.8,3.48]]
assert len(paddle)==1
zones=m.subs(tree,'zone')
rev={
 'revision':'V3.9 - documentary and independent nominal CAD audit',
 'reference_board_revision':'V3.8',
 'source_board_sha256':hashlib.sha256(BOARD.read_bytes()).hexdigest(),
 'manufacturer':'TE Connectivity / Linx',
 'exact_part_number':'CONSMA002-SMD-G',
 'primary_drawing':'https://www.te.com/en/product-CONSMA002-SMD-G.html (Customer Drawing C-CONSMA002-SMD-X-X rev D, sheet 2)',
 'manufacturer_version_crosswalk':'Drawing rev D covers CONSMA002-SMD and CONSMA002-SMD-G; -G denotes gold body finish in drawing table',
 'te_nominal_center_diameter_mm':2.05,
 'te_nominal_circular_clearance_feature_diameter_mm':4.56,
 'te_nominal_footprint_height_mm':7.76,
 'connectors':conns,
 'adl5535':{
   'paddle_copper_mm':[1.8,3.48],
   'paste_margin_ratio':str(m.one(paddle[0],'solder_paste_margin_ratio')[1]),
   'thermal_process_validated':False,
 },
 'segments':len(m.subs(tree,'segment')),
 'vias':len(m.subs(tree,'via')),
 'zones_declared':len(zones),
 'zones_filled':any(m.subs(z,'filled_polygon') or m.subs(z,'fill_segments') for z in zones),
 'native_kicad_available':shutil.which('kicad-cli') is not None,
 'native_kicad_drc_performed':False,
 'production_release':'BLOCKED - no Gerber or PCBWay order',
 'remaining_actions':['Acquire official TE DXF/STEP for exact land and 3D signoff',
 'Approve gold-part BOM, custom copper/GND geometry and paste/mask',
 'KiCad PCB load + zone refill + DRC; schematic ERC and parity',
 'Approve ADL5535 thermal/stencil process; PCBWay stackup and 50-ohm impedance',
 'VNA and bench tests with TX physically disconnected'],
 'disclaimer':'Not an ERC, DRC, 3D fit check, thermal sign-off, RF verification, or manufacturer CAD certification'
}
OUTPUT.write_text(json.dumps(rev,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('V3.9 review generated:',OUTPUT)
print('SMA center 2.05 mm; copper GND vertical extent:',[v['ground_envelope_height_mm'] for v in conns.values()])
print('vs TE nominal 7.76 mm; DRC native run:',rev['native_kicad_drc_performed'])
