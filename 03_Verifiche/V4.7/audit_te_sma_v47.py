#!/usr/bin/env python3
"""V4.7: read-only dimension check of study SMA footprint against selected TE drawing data.

Scope deliberately limited: this is NOT a CAD overlay, KiCad DRC, solderability check,
3D interference test, or approval for manufacturing. Only STL Python dependencies.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, importlib.util, json, re

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB'
FP = LIB/'S3900E_V38_Review.pretty/CONSMA002_SMD_SHAPED_REVIEW.kicad_mod'
AMP = LIB/'S3900E_V38_Review.pretty/ADL5535_SOT89_PASTE_REVIEW.kicad_mod'
BOARD = LIB/'S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB.kicad_pcb'
SCH = LIB/'S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB.kicad_sch'
DST = ROOT/'03_Verifiche/V4.7'

spec=importlib.util.spec_from_file_location('s3900e_parser',ROOT/'03_Verifiche/V4.5/crea_librerie_v45.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def pos(expr, tag='at'):
    m=re.search(r'\('+re.escape(tag)+r'\s+(-?[0-9.]+)\s+(-?[0-9.]+)',expr)
    if not m: raise ValueError(f'Coordinate not found ({tag})')
    return (float(m.group(1)),float(m.group(2)))
def is_ground_custom_pad(node):
    return bool(re.match(r'\(pad "2" smd custom\s',node))

def custom_bounds(node):
    if not is_ground_custom_pad(node): raise ValueError('Not a GND custom pad')
    cx,cy=pos(node)
    # gr_poly is footprint-local to pad's center. Pad anchor is a 0.300 x 0.300 rect.
    poly=p.child(p.child(node,'primitives')[0],'gr_poly')
    if len(poly)!=1:raise ValueError('Expected one custom polygon')
    xy=p.child(p.child(poly[0],'pts')[0],'xy')
    pts=[(cx+pos(n,'xy')[0],cy+pos(n,'xy')[1]) for n in xy]
    return {'at_mm':[cx,cy], 'bounds_mm':[min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)], 'polygon_local_mm': [[x-cx,y-cy] for x,y in pts], 'polygon_mm':[[x,y] for x,y in pts]}

def audit():
    fp=FP.read_text(encoding='utf8')
    pads=p.child(fp,'pad')
    assert len(pads)==5
    central=[a for a in pads if re.match(r'\(pad "1" smd circle\s',a)]
    ground=[a for a in pads if is_ground_custom_pad(a)]
    assert len(central)==1 and len(ground)==4
    m=re.search(r'\(size\s+([0-9.]+)\s+([0-9.]+)\)',central[0])
    assert m
    center=[float(m.group(1)),float(m.group(2))]
    bounds=[custom_bounds(n) for n in ground]
    bottom=min(b['bounds_mm'][1] for b in bounds)
    top=max(b['bounds_mm'][3] for b in bounds)
    sides=sorted(set((round(b['bounds_mm'][0],3),round(b['bounds_mm'][2],3)) for b in bounds))
    board_txt=BOARD.read_text('utf8')
    fp_nodes=p.child(board_txt,'footprint')
    sma=[]
    for f in fp_nodes:
        m=re.search(r'\(property "Reference" "(J10[1-4])"',f)
        if m:
            # Embedded pad signatures match extracted library in V4.5; repeat check.
            if p.pad_signature(f)!=p.pad_signature(fp):raise AssertionError('Footprint geometry changed '+m.group(1))
            at=re.search(r'\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)\s+(-?[0-9.]+)\)',f)
            assert at
            sma.append({'ref':m.group(1),'x_mm':float(at.group(1)), 'y_mm':float(at.group(2)), 'angle_deg':float(at.group(3))})
    assert len(sma)==4
    u=AMP.read_text('utf8'); upads=p.child(u,'pad')
    exposed=[n for n in upads if '(size 1.800 3.480)' in n]
    assert len(exposed)==1
    ratio=re.search(r'\(solder_paste_margin_ratio\s+(-?[0-9.]+)\)',exposed[0])
    ratio=float(ratio.group(1)) if ratio else None
    # KiCad paste margin ratio adjusts both dimensions; this is a derived nominal area only,
    # not an inspected solder mask/paste manufacturing stack.
    parea=1.8*3.48*(1+ratio)**2 if ratio is not None else None
    drawing={'part_number':'CONSMA002-SMD-G','reference':'TE C-CONSMA002-SMD-X-X','revision':'D',
             'url':'https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocFormat=pdf&DocLang=English&DocNm=C-CONSMA002-SMD-X-X&DocType=Customer+Drawing&PartCntxt=CONSMA002-SMD-G',
             'recommended_center_diameter_mm':2.05,'recommended_ground_vertical_envelope_mm':7.76,
             'other_reference_dimensions_mm':[2.44,2.88,4.56],
             'note':'Additional TE dimensions have NOT been mapped onto individual custom-pad polygons; no CAD overlay performed.'}
    result={'version':'4.7','scope':'READ_ONLY_STATIC_COMPARISON_NOT_MANUFACTURING_APPROVAL',
            'manufacturer_drawing':drawing,
            'cad_dxf_step':'LISTED_BY_TE_BUT_NOT_DOWNLOADED',
            'study_library_sha256':sha(FP),'study_board_sha256':sha(BOARD),'study_schematic_sha256':sha(SCH),
            'te_2_05_matches_study_center_pad':abs(center[0]-2.05)<1e-6 and center[0]==center[1],
            'center_pad_size_mm':center,
            'gnd_pad_count_per_connector':len(ground),
            'gnd_vertical_bounds_mm':[round(bottom,4),round(top,4)],
            'gnd_vertical_envelope_mm':round(top-bottom,4),
            'te_7_76_matches_study_vertical_envelope':abs(top-bottom-7.76)<1e-6,
            'lateral_custom_copper_x_bounds_mm':sides,
            'custom_gnd_pad_solder_paste_present':all('"F.Paste"' in n for n in ground),
            'custom_gnd_pad_paste_relief_explicit':any('solder_paste_margin' in n for n in ground),
            'sma_placements':sorted(sma,key=lambda d:d['ref']),
            'amplifier_exposed_pad_size_mm':[1.8,3.48],
            'amplifier_paste_margin_ratio':ratio,
            'amplifier_nominal_paste_fraction_of_copper':round((1+ratio)**2,3) if ratio is not None else None,
            'amplifier_nominal_paste_area_mm2':round(parea,4) if parea is not None else None,
            'thermal_finite_element_analysis':'NOT_RUN',
            'native_kicad_erc_drc':'NOT_RUN',
            'conformity':'NOT_APPROVED: agreement on 2 selected dimensions does not establish copper/mask/paste/courtyard/3D compatibility',
            'fabrication_authorized':False}
    DST.mkdir(parents=True,exist_ok=True)
    (DST/'AUDIT_SMA_TE_V4.7.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n','utf8')
    return result

if __name__=='__main__':
    r=audit()
    print('STATIC_CHECK_OK:',r['gnd_vertical_envelope_mm'],'mm GND span; central',r['center_pad_size_mm'],'mm; CAD 3D NOT ACQUIRED; NO FAB')
