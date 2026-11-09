#!/usr/bin/env python3
"""V3.7 — repeatable, non-fabrication KiCad footprint/connector review.
Copy the immutable V3.6 PCB, mark SMA land as NO-DRILL, orient right-angle
connectors left/right and generate review-only footprint candidates. No claim of DRC.
"""
import csv, importlib.util, json, math, re, shutil, sys, uuid
from pathlib import Path
from collections import Counter
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.6/S3900E_RX_TEST_50R_V3_6_GND_RETURN_STUDY_NOT_FOR_FAB.kicad_pcb'
TARGET_DIR=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.7'
DST=TARGET_DIR/'S3900E_RX_TEST_50R_V3_7_SMA_FOOTPRINT_REVIEW_NOT_FOR_FAB.kicad_pcb'
LIB=TARGET_DIR/'S3900E_Review.pretty'
OUT=ROOT/'03_Verifiche/V3.7'
DOCS='''FONTI PRIMARIE (consultate 2026-11-07):
TE/Linx CONSMA002-SMD-* rev D, foglio 2/3, impronta consigliata:
https://www.ic-components.cz/files/17/CONSMA002-SMD.pdf
Analog Devices ADL5535 rev A, Fig. 17 pagina 11 e Fig. 16:
https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf
KiCad CLI v9 DRC reference:
https://docs.kicad.org/9.0/en/cli/cli.html
'''

def balanced_span(s, start):
    assert s[start]=='('
    dep=0; instr=False; esc=False
    for i in range(start,len(s)):
        ch=s[i]
        if instr:
            if esc:esc=False
            elif ch=='\\':esc=True
            elif ch=='"':instr=False
        elif ch=='"':instr=True
        elif ch=='(':dep+=1
        elif ch==')':
            dep-=1
            if dep==0:return start,i+1
    raise ValueError('unbalanced KiCad S-expression')

def patch_footprints(s):
    starts=[m.start() for m in re.finditer(r'\(footprint\s+"',s)]
    spans=[];changes=[]
    for i in starts:
        a,b=balanced_span(s,i);fp=s[a:b]
        m=re.search(r'\(property "Reference" "(J10[1-4]|U101)"',fp)
        if not m:continue
        ref=m.group(1)
        if ref[0]=='J':
            fp=fp.replace('S3900E_v35:CONSMA002_REVIEW_CENTER_FEATURE_UNRESOLVED','S3900E_Review:CONSMA002_SMD_LAND_DRAFT_NO_DRILL',1)
            if ref in ('J102','J104'):
                # PCB copper is symmetric about the pad centre; 180 degrees reverses connector barrel direction.
                fp=re.sub(r'\(at (122) (36|65)\)',r'(at \1 \2 180)',fp,count=1)
            marker='''
    (fp_line (start -1.6 0) (end -6.6 0) (stroke (width 0.16) (type solid)) (layer "Dwgs.User") (tstamp "%s"))
    (fp_line (start -6.6 0) (end -5.6 -0.6) (stroke (width 0.16) (type solid)) (layer "Dwgs.User") (tstamp "%s"))
    (fp_line (start -6.6 0) (end -5.6 0.6) (stroke (width 0.16) (type solid)) (layer "Dwgs.User") (tstamp "%s"))
    '''%tuple(str(uuid.uuid5(uuid.NAMESPACE_URL,f'V3.7/{ref}/mech/{j}')) for j in range(3))
            # Arrows on documentation layer: assumed port direction, NOT 3D collision proof.
            fp=fp[:-1]+marker+'\n  )'
        else:
            fp=fp.replace('S3900E_v35:ADL5535_SOT89_FIG17_REVIEW','S3900E_Review:ADL5535_SOT89_FIG17_LAND_DRAFT',1)
        spans.append((a,b,fp));changes.append(ref)
    for a,b,fp in reversed(spans):s=s[:a]+fp+s[b:]
    assert sorted(changes)==['J101','J102','J103','J104','U101']
    s=s.replace('s3900e_v36_return_study','s3900e_v37_footprint_review')
    s=s.replace('V3.6 GND STUDY - NOT FOR FAB','V3.7 SMA LAND + PORT DIRECTION - NOT FOR FAB')
    s=s.replace('RF ROUTING STUDY ONLY - DRC/MECHANICS OPEN','V3.7 FOOTPRINT REVIEW - NO NATIVE DRC - NO FAB')
    # Cu routing/zone state deliberately unchanged.
    return s

def make_library():
    LIB.mkdir(parents=True,exist_ok=True)
    # Standalone examples derived from embedded draft pads; GROUND GEOMETRY NOT YET APPROVED.
    pads='\n'.join('  (pad "2" smd rect (at %s %s) (size 1.5 1.5) (layers "F.Cu" "F.Paste" "F.Mask"))'%(x,y) for x in (-2.85,2.85) for y in (-2.95,2.95))
    sma=f'''(footprint "CONSMA002_SMD_LAND_DRAFT_NO_DRILL" (version 20221018) (generator "S3900E_V37") (layer "F.Cu")
  (descr "REVIEW ONLY: center 2.05 mm SMD land NO DRILL; GND pads and enclosure NOT verified")
  (attr smd)
  (fp_text reference "REF**" (at 0 -6.1) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.13))))
  (fp_text value "CONSMA002-SMD REVIEW" (at 0 5.9) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_rect (start -4.1 -4.5) (end 4.1 4.5) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
  (pad "1" smd circle (at 0 0) (size 2.05 2.05) (layers "F.Cu" "F.Paste" "F.Mask"))
{pads}
  (fp_circle (center 0 0) (end 1.025 0) (stroke (width 0.08) (type solid)) (fill none) (layer "Dwgs.User"))
)
'''
    (LIB/'CONSMA002_SMD_LAND_DRAFT_NO_DRILL.kicad_mod').write_text(sma)
    adl='''(footprint "ADL5535_SOT89_FIG17_LAND_DRAFT" (version 20221018) (generator "S3900E_V37") (layer "F.Cu")
  (descr "REVIEW ONLY: Analog Devices Fig.17 approx; GND exposed paddle, paste/thermal not approved")
  (attr smd)
  (fp_text reference "REF**" (at 0 -5.4) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.13))))
  (fp_text value "ADL5535" (at 0 3.1) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))
  (fp_rect (start -2.7 -4.5) (end 2.7 2.15) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
  (pad "1" smd rect (at -1.5 0.635) (size 0.86 1.27) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "2" smd rect (at 0 0.635) (size 0.86 1.27) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "3" smd rect (at 1.5 0.635) (size 0.86 1.27) (layers "F.Cu" "F.Paste" "F.Mask"))
  (pad "2" smd rect (at 0 -2.36) (size 1.8 3.48) (layers "F.Cu" "F.Paste" "F.Mask"))
)
'''
    (LIB/'ADL5535_SOT89_FIG17_LAND_DRAFT.kicad_mod').write_text(adl)

def load_v36_module():
    f=ROOT/'03_Verifiche/V3.6/audit_v36.py'
    spec=importlib.util.spec_from_file_location('audit_v36',f)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def rotated_inspect(m, pcb):
    node=m.parse_sexpr(pcb.read_text())
    nets={int(x[1]):x[2] for x in m.subs(node,'net')}
    from collections import defaultdict
    pads=defaultdict(list);padmap={};items=[]
    for fp in m.subs(node,'footprint'):
        prop={q[1]:q[2] for q in m.subs(fp,'property')};ref=prop.get('Reference','?')
        at=m.one(fp,'at');x0,y0=float(at[1]),float(at[2]);rot=float(at[3]) if len(at)>3 else 0.
        assert rot in (0.,180.),f'Unexpected footprint rotation {ref}/{rot}'
        k=1 if rot==0 else -1
        for p in m.subs(fp,'pad'):
            atp=m.one(p,'at');size=m.one(p,'size');net=m.one(p,'net'); pin=p[1]
            x=x0+k*float(atp[1]);y=y0+k*float(atp[2]);w,h=float(size[1]),float(size[2]);n=int(net[1]);
            if p[3]=='circle':geom=Point(x,y).buffer(w/2,resolution=32)
            else:geom=box(x-w/2,y-h/2,x+w/2,y+h/2)
            d={'kind':'pad','ref':ref,'pin':pin,'net':n,'x':x,'y':y,'width':w,'height':h,'geom':geom}
            items.append(d);pads[n].append(d);padmap.setdefault(f'{ref}.{pin}',set()).add(n)
    for e in m.subs(node,'segment'):
        a=m.one(e,'start');b=m.one(e,'end');w=float(m.one(e,'width')[1]);n=int(m.one(e,'net')[1]);
        x,y,xx,yy=map(float,[a[1],a[2],b[1],b[2]])
        items.append({'kind':'segment','net':n,'start':(x,y),'end':(xx,yy),'width':w,'geom':LineString([(x,y),(xx,yy)]).buffer(w/2,cap_style=1,resolution=12)})
    for e in m.subs(node,'via'):
        a=m.one(e,'at');size=float(m.one(e,'size')[1]);n=int(m.one(e,'net')[1]);x,y=float(a[1]),float(a[2]);
        items.append({'kind':'via','net':n,'x':x,'y':y,'diameter':size,'geom':Point(x,y).buffer(size/2,resolution=24)})
    return node,nets,items,pads,padmap

def test_footprint(m,node):
    entries={}
    for fp in m.subs(node,'footprint'):
        props={x[1]:x[2] for x in m.subs(fp,'property')};ref=props.get('Reference','')
        entries[ref]=fp
    assert len(entries)==15
    for ref,rot in [('J101',0),('J102',180),('J103',0),('J104',180)]:
        fp=entries[ref];assert 'CONSMA002_SMD_LAND_DRAFT_NO_DRILL' in fp[1]
        loc=m.one(fp,'at');assert (float(loc[3]) if len(loc)>3 else 0)==rot
        pp=m.subs(fp,'pad');assert len(pp)==5
        p1=[p for p in pp if p[1]=='1'];assert len(p1)==1
        cp=p1[0]
        assert cp[2]=='smd' and cp[3]=='circle' and [float(x) for x in m.one(cp,'size')[1:]]==[2.05,2.05]
        assert not m.subs(cp,'drill')
        assert len([p for p in pp if p[1]=='2'])==4
        assert all(p[2]=='smd' and not m.subs(p,'drill') for p in pp)
    u=entries['U101'];assert 'ADL5535_SOT89_FIG17_LAND_DRAFT' in u[1]
    p2=[p for p in m.subs(u,'pad') if p[1]=='2'];assert len(p2)==2
    assert any([float(x) for x in m.one(p,'size')[1:]]==[1.8,3.48] for p in p2)
    return entries

def build_preview(m,node,items):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, PathPatch, Polygon, Circle
    from matplotlib.patches import FancyArrowPatch
    from shapely.geometry import Polygon as SP, MultiPolygon
    fig,ax=plt.subplots(figsize=(15,7.4));fig.patch.set_facecolor('#f4f8fb')
    ax.add_patch(Rectangle((20,20),110,62,facecolor='#12324a',edgecolor='#f1d487',lw=2))
    def draw_geom(g,color,alpha):
        if isinstance(g,SP):
            x,y=g.exterior.xy;ax.fill(x,y,color=color,alpha=alpha,linewidth=0)
        elif isinstance(g,MultiPolygon):
            for t in g.geoms:draw_geom(t,color,alpha)
    for e in items:
        if e['net']==1:color='#b8a665'
        elif e['net'] in (6,4):color='#e9977f'
        else:color='#37ddbf'
        draw_geom(e['geom'],color,1. if e['kind']=='pad' else .83)
        if e['kind']=='via':ax.add_patch(Circle((e['x'],e['y']),radius=.15,facecolor='#152538',edgecolor='none'))
    for fp in m.subs(node,'footprint'):
        props={q[1]:q[2] for q in m.subs(fp,'property')};ref=props.get('Reference','')
        loc=m.one(fp,'at');x,y=float(loc[1]),float(loc[2]);
        if ref.startswith('J10') and ref!='J105':
            left=ref in ('J101','J103');to=x+(-7.0 if left else 7.0)
            ax.add_patch(FancyArrowPatch((x,y),(to,y),arrowstyle='-|>',color='#ffce62',mutation_scale=18,linewidth=2))
            ax.text(x,y+6,ref+(' LEFT' if left else ' RIGHT'),color='#d8f6f6',fontsize=8,ha='center',weight='bold')
        elif ref=='U101':
            ax.text(x,y-7.0,'ADL5535',color='white',fontsize=9,ha='center')
        elif ref=='J105':ax.text(x,y+3,'+5 V BENCH',color='white',fontsize=8,ha='center')
    ax.text(21,23.5,'V3.7 • footprint & orientation review • NOT FOR FABRICATION',fontsize=10,weight='bold',color='#e6ebef')
    ax.set_aspect('equal');ax.set_xlim(17,133);ax.set_ylim(84,18);ax.set_xlabel('X [mm]');ax.set_ylabel('Y [mm]');ax.set_title('Superstar 3900 — RX 50 Ω coupon / V3.7',weight='bold',fontsize=14)
    ax.grid(alpha=.1);fig.tight_layout();fig.savefig(TARGET_DIR/'Anteprima_Orientamento_SMA_V3.7.png',dpi=165)
    fig.savefig(TARGET_DIR/'Anteprima_Orientamento_SMA_V3.7.svg');plt.close(fig)

def main():
    TARGET_DIR.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    assert SRC.exists(),'v3.6 PCB not found'
    DST.write_text(patch_footprints(SRC.read_text()))
    make_library();m=load_v36_module();m.inspect=lambda pcb:rotated_inspect(m,pcb)
    report,items=m.audit(DST,record=False)
    node,nets,_,pads,pmap=m.inspect(DST);entry=test_footprint(m,node)
    assert not report['2d_clashes'],report['2d_clashes'][:3]
    assert not report['unconnected_nonground_nets'],report['unconnected_nonground_nets']
    assert not report['schematic_pin_mismatches'],report['schematic_pin_mismatches']
    assert not report['ground_pads_without_explicit_local_via'],report['ground_pads_without_explicit_local_via']
    assert report['schematic_pin_assignments_ok']==31
    assert len(m.subs(node,'zone'))==4
    assert not m.subs(node,'filled_polygon')  # zone fill not performed in external generator
    assert len(m.subs(node,'via'))==64
    # detect a mechanically invalid mutation: through-hole center pad must be caught
    fake=m.parse_sexpr(DST.read_text().replace('(pad "1" smd circle','(pad "1" thru_hole circle',1))
    try:test_footprint(m,fake)
    except AssertionError:negative_ok=True
    else:raise AssertionError('hole mutation escaped test')
    # detect incorrect port orientation
    fake2=m.parse_sexpr(DST.read_text().replace('(at 122 36 180)','(at 122 36)',1))
    try:test_footprint(m,fake2)
    except AssertionError:negative_rot_ok=True
    else:raise AssertionError('orientation mutation escaped test')
    import shutil
    from datetime import date
    report.update(revision='V3.7',footprint_2p05_land_interpretation='SMD circular COPPER LAND from TE recommended footprint, NO DRILL (source page 2). The 4 GND geometry pads remain REVIEW ONLY.',
                  connector_orientation=dict(J101='0 left-facing (ASSUMED local axis)',J102='180 right-facing (ASSUMED local axis)',J103='0 left-facing',J104='180 right-facing'),
                  kicad_cli_present=bool(shutil.which('kicad-cli')),
                  repeated_sma_center_copper_smd_count=4,
                  negative_test_unwanted_center_hole=negative_ok,
                  negative_test_reversed_port=negative_rot_ok,
                  adl5535_paddle='Pad 2 exposed: 1.80x3.48mm model; solder paste via strategy OPEN.',
                  explicitly_unverified=['manufacturer-recommended curved TE grounds vs square pads','right angle mechanical overhang / 3D collision','native DRC & zone refill','SMD stencil and pad-in-via treatment','RF S11/S21 and controlled impedance'])
    report['manufacturing_release']='BLOCKED — NOT FABRICABLE; NO GERBERS'
    (OUT/'Audit_Elettrico_Meccanico_V3.7.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    with (OUT/'Mappa_Connettori_V3.7.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Ref','X_mm','Y_mm','Rot_deg','Port direction (assumed)','Central land diameter mm','Central hole','Ground pattern','mechanical validation'])
        for ref in ('J101','J102','J103','J104'):
            fp=entry[ref];a=m.one(fp,'at');w.writerow([ref,a[1],a[2],a[3] if len(a)>3 else 0,'LEFT' if ref in ('J101','J103') else 'RIGHT',2.05,'NONE','4 square pads candidate','REVIEW'])
    with (OUT/'Confronto_Footprint_Rispetto_Datasheet_V3.7.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Item','Manufacturer source','V3.7 footprint','Assessment','Next verification'])
        w.writerow(['SMA center land','TE rev D sheet 2 circular Ø2.05','SMD circular Ø2.05 NO DRILL','size and role visually corroborated','confirm physical part contact footprint in KiCad 3D'])
        w.writerow(['SMA ground pattern','TE rev D sheet 2 shaped lobed ground areas','four square 1.5mm grounds at x±2.85/y±2.95','DIFFERS from recommended shape','redraw exactly from manufacturer CAD/ECAD'])
        w.writerow(['SMA mechanical fit','TE rev D sheet 1 right-angle body 15.20mm overall','board-relative direction indicated, x center 8mm from edge','NOT CERTIFIED','3D model / exact body axis and edge overhang'])
        w.writerow(['ADL5535 paddle','ADI Rev A Fig17 central GND region 1.80x3.48mm','pad2 1.80x3.48mm F.Cu','rough outline check','thermal vias and solder paste stencil'])
        w.writerow(['ADL5535 signal leads','ADI Rev A Fig17 outer pads width0.86mm and pitch1.50mm','pads 1,2,3 0.86x1.27 at -1.5/0/+1.5','partial correspondence','dimensioned package + paste DFM'])
    build_preview(m,node,items)
    (OUT/'FONTI_E_RISULTATI_V3.7.md').write_text('# V3.7 — SMA land, lato di accoppiamento e footprint ADL5535\n\n'+DOCS+'\n'
      '## Conclusioni\n\n'
      '- Ø2,05 appare nel **RECOMMENDED FOOTPRINT** TE: è il diametro del land centrale; non appare come prescrizione di foratura. Il layout usa un pad SMD circolare senza drill.\n'
      '- I quattro connettori ad angolo retto hanno verso di accoppiamento esplicitato; due ruotati di 180°, senza cambiare la connettività elettrica data la simmetria della disposizione di prova.\n'
      '- Le quattro piazzole quadrate GND del candidato **NON riproducono ancora** il contorno di massa sagomato dal fabbricante. Il footprint è **NON APPROVATO**.\n'
      '- L’ADL5535 riproduce le quote principali della Fig.17, ma mancano revisione paste/termica e veri controlli ERC/DRC.\n'
      '- KiCad CLI assente (installazione Debian tentata, repository non raggiungibile). Nessuna zona riempita, nessun Gerber, nessun hardware misurato.\n')
    print(json.dumps({k:report[k] for k in ['footprints','nets','segments','vias','schematic_pin_assignments_ok','ground_pad_count','2d_clash_count','min_2d_inter_net_copper_clearance_mm','kicad_cli_present']},indent=2))
    print('V3.7 built OK;',DST)

if __name__=='__main__':main()
