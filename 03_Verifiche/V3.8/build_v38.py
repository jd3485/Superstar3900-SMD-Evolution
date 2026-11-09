#!/usr/bin/env python3
"""V3.8 experimental footprint, thermal-return and mechanical audit.
Not a substitute for KiCad native DRC, manufacturer footprint approval, or 3D checks.
Primary documentation: TE/Linx CONSMA002-SMD-G rev B recommended footprint;
Analog Devices ADL5535 rev A Fig.17; KiCad custom pad reference.
"""
from __future__ import annotations
import csv, json, math, re, sys, uuid, importlib.util
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPolygon, Circle, Rectangle
from shapely.geometry import Point, LineString, box, Polygon, MultiPolygon
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[2]
PCB0=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.7/S3900E_RX_TEST_50R_V3_7_SMA_FOOTPRINT_REVIEW_NOT_FOR_FAB.kicad_pcb'
MOD=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.8'
PCB=MOD/'S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb'
LIB=MOD/'S3900E_V38_Review.pretty'
OUT=ROOT/'03_Verifiche/V3.8'


def module(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
    return obj
m36=module(ROOT/'03_Verifiche/V3.6/audit_v36.py','audit_v36_v38')
m37=module(ROOT/'03_Verifiche/V3.7/build_v37.py','build_v37_v38')

def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'superstar/v3.8/'+s))

# Polygon stays within TE's four contact footprints but extends the inner side
# with a symmetrical bevel; deliberately labelled REVIEW CANDIDATE (not exact official CAD).
def pad_poly(x,y):
    sign=-1 if x<0 else 1
    # pad center in footprint local coordinates, all units mm.
    # outer edge +/-0.75, beveled inner extension to +/-1.12 (relative).
    if sign<0:
        pts=[(-.75,-.75),(.36,-.75),(.75,-.49),(1.12,-.12),(1.12,.12),(.75,.49),(.36,.75),(-.75,.75)]
    else:
        pts=[(.75,-.75),(-.36,-.75),(-.75,-.49),(-1.12,-.12),(-1.12,.12),(-.75,.49),(-.36,.75),(.75,.75)]
    return pts

def pad_block(x,y,net,ref,i,with_net=True):
    pts=pad_poly(x,y)
    poly=' '.join(f'(xy {xx:.3f} {yy:.3f})' for xx,yy in pts)
    nettext=f' (net {net} "GND_RF")' if with_net else ''
    return f'''(pad "2" smd custom (at {x:.3f} {y:.3f}) (size 0.300 0.300)
      (layers "F.Cu" "F.Paste" "F.Mask") {nettext}
      (options (clearance outline) (anchor rect))
      (primitives (gr_poly (pts {poly}) (width 0) (fill yes)))
      (tstamp "{uid(ref+'/ground'+str(i))}"))'''

def rewrite():
    s=PCB0.read_text()
    spans=[];summary={}
    starts=[mm.start() for mm in re.finditer(r'\(footprint\s+"',s)]
    for st in starts:
        a,b=m37.balanced_span(s,st); f=s[a:b]
        refm=re.search(r'\(property "Reference" "([A-Z]\d+)"',f)
        if not refm:continue
        ref=refm.group(1)
        if ref in ('J101','J102','J103','J104'):
            f=f.replace('S3900E_Review:CONSMA002_SMD_LAND_DRAFT_NO_DRILL','S3900E_V38_Review:CONSMA002_SMD_SHAPED_REVIEW',1)
            f=f.replace('fp_rect (start -4.100 -4.500) (end 4.100 4.500)','fp_rect (start -15.200 -5.400) (end 4.100 5.400)',1)
            # 4 ground pins redefined, preserving net pin 2 and mechanical orientation.
            padspans=[]
            for mm in re.finditer(r'\(pad "2" smd rect',f):
                pa,pb=m37.balanced_span(f,mm.start()); p=f[pa:pb]
                loc=re.search(r'\(at ([-\d.]+) ([-\d.]+)\)',p)
                assert loc
                x,y=float(loc.group(1)),float(loc.group(2))
                padspans.append((pa,pb,pad_block(x,y,1,ref,len(padspans))))
            assert len(padspans)==4,(ref,len(padspans))
            for pa,pb,new in reversed(padspans):f=f[:pa]+new+f[pb:]
            # 2D only envelope of the assumed 15.2 mm connector, not a 3D fit proof.
            f=f[:-1]+f'''
    (fp_rect (start -15.2 -5.4) (end 4.1 5.4)
      (stroke (width 0.1) (type dash)) (fill none) (layer "Dwgs.User")
      (tstamp "{uid(ref+'/mechanics')}"))
  )'''
            summary[ref]={'ground_pads':'4 shaped custom candidate','port_orientation':0 if ref in ('J101','J103') else 180}
        if ref=='U101':
            f=f.replace('S3900E_Review:ADL5535_SOT89_FIG17_LAND_DRAFT','S3900E_V38_Review:ADL5535_SOT89_PASTE_REVIEW',1)
            # Exposed pad gets a mild, *provisional* paste reduction; avoid under-pad holes.
            target='(pad "2" smd rect (at 0.000 -2.360) (size 1.800 3.480) (layers "F.Cu" "F.Mask" "F.Paste")'
            replacement='(pad "2" smd rect (at 0.000 -2.360) (size 1.800 3.480) (layers "F.Cu" "F.Mask" "F.Paste") (solder_paste_margin_ratio -0.100) (zone_connect 2)'
            assert target in f
            f=f.replace(target,replacement,1)
            summary[ref]={'paddle_mm':[1.8,3.48],'paste_ratio_candidate':-0.1,'via_in_paddle':False}
        spans.append((a,b,f))
    for a,b,f in reversed(spans):s=s[:a]+f+s[b:]
    assert all(r in summary for r in ('J101','J102','J103','J104','U101'))
    # Add exposed-paddle to near GND via (not via-in-pad), exposing trace to 2D checker.
    # Top edge of paddle: y=31.900; via center y=31.050, copper dia .700.
    assert '(via (at 68 31.05)' in s
    thermal=f'''  (segment (start 68.000 31.050) (end 68.000 32.300) (width 0.350)
      (layer "F.Cu") (net 1) (tstamp "{uid('U101/thermaltop')}"))\n'''
    # Insert before first top-level segment, preserving S-expression balance.
    ins=s.find('\n  (segment ')
    assert ins>0
    s=s[:ins]+'\n'+thermal+s[ins:]
    s=s.replace('s3900e_v37_footprint_review','s3900e_v38_paste_thermal_mechanics')
    s=s.replace('V3.7 SMA LAND + PORT DIRECTION - NOT FOR FAB','V3.8 CUSTOM PAD + THERMAL - NOT FOR FAB')
    s=s.replace('V3.7 FOOTPRINT REVIEW - NO NATIVE DRC - NO FAB','V3.8 SMD SHAPED REVIEW - NO NATIVE DRC - NO FAB')
    s=s.replace('V3.6 GND STUDY - ALL ZONES UNFILLED','V3.8 CUSTOM PADS - ZONES UNFILLED - NO FAB')
    assert 'filled_polygon' not in s
    PCB.write_text(s)
    return summary

def audit_geometry(path=PCB):
    tree=m36.parse_sexpr(path.read_text())
    nets={int(x[1]):x[2] for x in m36.subs(tree,'net')}
    items=[];pads=defaultdict(list);pinmap={}
    for fp in m36.subs(tree,'footprint'):
        pro={x[1]:x[2] for x in m36.subs(fp,'property')}
        ref=pro.get('Reference','?');loc=m36.one(fp,'at')
        x0,y0=float(loc[1]),float(loc[2]);rot=float(loc[3]) if len(loc)>3 else 0
        assert rot in (0,180)
        factor=1 if rot==0 else -1
        for p in m36.subs(fp,'pad'):
            pos=m36.one(p,'at');size=m36.one(p,'size');net=m36.one(p,'net')
            px,py=float(pos[1]),float(pos[2]);x=x0+factor*px;y=y0+factor*py
            sx,sy=float(size[1]),float(size[2]);n=int(net[1]);pin=p[1]
            if p[3]=='custom':
                prim=m36.one(p,'primitives');points=m36.one(m36.one(prim,'gr_poly'),'pts')
                q=[(x+factor*float(v[1]),y+factor*float(v[2])) for v in m36.subs(points,'xy')]
                shape=Polygon(q).union(box(x-sx/2,y-sy/2,x+sx/2,y+sy/2))
                assert shape.is_valid and shape.area>1.0
            elif p[3]=='circle':shape=Point(x,y).buffer(sx/2,resolution=32)
            else:shape=box(x-sx/2,y-sy/2,x+sx/2,y+sy/2)
            d={'kind':'pad','ref':ref,'pin':pin,'net':n,'x':x,'y':y,'width':sx,'height':sy,'geom':shape}
            pads[n].append(d);items.append(d);pinmap.setdefault(ref+'.'+pin,set()).add(n)
    for e in m36.subs(tree,'segment'):
        a=m36.one(e,'start');b=m36.one(e,'end');w=float(m36.one(e,'width')[1]);n=int(m36.one(e,'net')[1]);
        x,y,xx,yy=map(float,[a[1],a[2],b[1],b[2]])
        items.append({'kind':'segment','net':n,'start':(x,y),'end':(xx,yy),'width':w,'geom':LineString([(x,y),(xx,yy)]).buffer(w/2,cap_style=1,resolution=12)})
    for e in m36.subs(tree,'via'):
        at=m36.one(e,'at');diam=float(m36.one(e,'size')[1]);n=int(m36.one(e,'net')[1]);x,y=float(at[1]),float(at[2]);
        items.append({'kind':'via','net':n,'x':x,'y':y,'diameter':diam,'geom':Point(x,y).buffer(diam/2,resolution=24)})
    return tree,nets,items,pads,pinmap

def manuf_review_and_tests():
    # Reuse rigorous V3.6 net/topology audit with actual custom polygon support.
    m36.inspect=audit_geometry
    report,items=m36.audit(PCB,record=False)
    tree,nets,items,pads,pmap=audit_geometry()
    byref={next((p[2] for p in m36.subs(f,'property') if p[1]=='Reference'),''):f for f in m36.subs(tree,'footprint')}
    checks={
        'complete_sexpr':tree[0]=='kicad_pcb',
        '15_footprints':len(byref)==15,
        '8_named_nets':len(nets)==9,
        '44_segments':len(m36.subs(tree,'segment'))==44,
        '64_vias':len(m36.subs(tree,'via'))==64,
        '4_unfilled_ground_planes':len(m36.subs(tree,'zone'))==4 and not m36.subs(tree,'filled_polygon'),
        '31_schematic_pin_assignments':report['schematic_pin_assignments_ok']==31 and not report['schematic_pin_mismatches'],
        '7_nonground_nets_connected':not report['unconnected_nonground_nets'],
        '24_ground_pads_locally_stitched':report['ground_pad_count']==24 and not report['ground_pads_without_explicit_local_via'],
        'clearance_0_2mm_static':report['min_2d_inter_net_copper_clearance_mm']>=.2 and not report['2d_clashes'],
        'thermal_trace_reaches_paddle_and_via':next(p for p in pads[1] if p['ref']=='U101' and p['geom'].area>5).get('geom').intersects(next(x['geom'] for x in items if x['kind']=='segment' and x['net']==1 and x['start']==(68.0,31.05))),
        'no_underpad_drill':not any(v['kind']=='via' and v['geom'].intersects(next(p['geom'] for p in pads[1] if p['ref']=='U101' and p['geom'].area>5)) for v in items),
        'no_native_fabrication_outputs':not list(ROOT.rglob('*.gbr')) and not list(ROOT.rglob('*.drl')),
        'ki_cli_unavailable':__import__('shutil').which('kicad-cli') is None,
    }
    for name,angle in [('J101',0),('J102',180),('J103',0),('J104',180)]:
        f=byref[name];at=m36.one(f,'at');a=float(at[3]) if len(at)>3 else 0
        pp=m36.subs(f,'pad');g=[p for p in pp if p[1]=='2']
        checks[name+'_four_shaped_smd_ground_pads']=len(g)==4 and all(p[2]=='smd' and p[3]=='custom' and not m36.subs(p,'drill') for p in g)
        checks[name+'_correct_port_orientation']=a==angle
        checks[name+'_central_copper_land_no_drill']=len([p for p in pp if p[1]=='1' and p[2]=='smd' and p[3]=='circle' and not m36.subs(p,'drill')])==1
        # Conservative center to adjacent GND nominal separation
        center=next(p for p in pads[2 if name=='J101' else 5 if name=='J102' else 7 if name=='J103' else 8] if p['ref']==name)
        dist=min(center['geom'].distance(p['geom']) for p in pads[1] if p['ref']==name)
        checks[name+'_center_to_ground_0_2mm']=dist>=.2
    u=byref['U101'];ep=[p for p in m36.subs(u,'pad') if p[1]=='2' and m36.one(p,'size')[1:]==['1.800','3.480']]
    checks['adl_paste_margin_documented']=len(ep)==1 and abs(float(m36.one(ep[0],'solder_paste_margin_ratio')[1])+.1)<1e-7
    checks['adl_paddle_solid_zone_connect']=len(ep)==1 and m36.one(ep[0],'zone_connect')[1]=='2'
    # Negative tests: the audit must respond when we change one nets or a segment.
    s=PCB.read_text()
    try:
        fake=m36.parse_sexpr(s.replace('(pad "1" smd circle','(pad "1" thru_hole circle',1))
        changed=next(p for f in m36.subs(fake,'footprint') for p in m36.subs(f,'pad') if p[1]=='1' and p[2]=='thru_hole')
        checks['negative_detects_illegal_hole']=changed[2]=='thru_hole'
    except Exception:checks['negative_detects_illegal_hole']=False
    # Mutate a large RF pad: the same checker should detect an inter-net violation.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as td:
        mutated=Path(td)/'candidate.kicad_pcb'
        mutated.write_text(s.replace('(size 2.050 2.050)','(size 7.000 7.000)',1))
        bad,_=m36.audit(mutated,record=False)
        checks['negative_large_center_pad_detects_short']=bad['2d_clash_count']>0
    # 2D center-distance sanity for component bodies; NOT 3D mating validation.
    footprints=[('J101',28,36,-1),('J102',122,36,1),('J103',28,65,-1),('J104',122,65,1)]
    envelopes=[box(x-15.2 if facing==-1 else x-4.1,y-5.4,
                   x+4.1 if facing==-1 else x+15.2,y+5.4)
               for name,x,y,facing in footprints]
    checks['mechanical_2d_envelopes_separate']=all(not envelopes[i].intersects(envelopes[j]) for i in range(4) for j in range(i+1,4))
    checks['sma_barrel_overhang_7_2mm_each_side']=abs((20-envelopes[0].bounds[0])-7.2)<1e-6 and abs((envelopes[1].bounds[2]-130)-7.2)<1e-6
    # Replace inherited V3.6 notes with current V3.8 scope; preserve the audit calculations.
    report['revision']='V3.8'
    report['sma_center_2_05mm']='SMD copper land, NO DRILL; based on TE drawing, exact grounding copper still provisional'
    report['model_limitations']=[x for x in report.get('model_limitations',[]) if x not in ('pad shape roundrect treated as rect (conservative)','does not verify formal KiCad file load')]
    report['model_limitations']+=['custom GND pads modeled as exact polygon + rectangular anchor, roundrect as conservative rectangle','KiCad formal PCB load and DRC NOT executed','3D mechanical fit NOT verified']
    d={'revision':'V3.8','all_pass':all(checks.values()),'checks':checks,'audit':report,
       'manufacturing_release':'BLOCKED/NOT FOR FAB','native_kicad_drc_ran':False,
       'sma_ground_geometry':'custom convex bevel candidates; DOES NOT certify exact TE official footprint',
       'mechanical':'body envelope approximated from TE 15.2mm and 10.8mm external dimensions, 3D fit NOT checked',
       'sma_part_suffix':'datasheet reviewed for CONSMA002-SMD-G; verify interchangeability with BOM suffix',
       'adl_solder_paste':'-0.10 ratio candidate not qualified by assembly house; windowed stencil remains option',
       'soldermask_clearances':'NOT checked',
       'thermals':'one short copper path from paddle to neighboring tented via proposed; NO thermal FEM or heat-rise validation',
       'stackup':'PCBWay stackup of reference only, final thickness and impedance not agreed',
       'open':'official footprint sign-off, native KiCad DRC/ERC, zone fill, physical SMA mate, stencil review, thermal/RF validation'}
    (OUT/'Audit_Footprint_Termico_V3.8.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
    assert d['all_pass'],[k for k,v in checks.items() if not v]
    return d,items

def make_library():
    # Standalone candidates mirroring modified board; no production library release.
    t=PCB.read_text()
    for ref,outname in [('J101','CONSMA002_SMD_SHAPED_REVIEW.kicad_mod'),('U101','ADL5535_SOT89_PASTE_REVIEW.kicad_mod')]:
        mm=next(mm for mm in re.finditer(r'\(footprint\s+"',t) if f'(property "Reference" "{ref}"' in t[mm.start():m37.balanced_span(t,mm.start())[1]])
        a,b=m37.balanced_span(t,mm.start());p=t[a:b]
        # Library parser sees ref/value properties (KiCad supports properties in footprints).
        p=re.sub(r'\(footprint\s+"[^"]+"',f'(footprint "{outname[:-10]}"',p,count=1)
        p=re.sub(r'\(net \d+ "[^"]+"\)','',p)
        p=re.sub(r'\(at \d+(?:\.\d+)? \d+(?:\.\d+)?(?: 180)?\)','',p,count=1)
        p=p.replace('(tstamp ', '(tstamp ')
        (LIB/outname).write_text(p+'\n')

def make_preview(items):
    fig,axs=plt.subplots(2,1,figsize=(13.5,8.0),height_ratios=[2.2,1]);fig.patch.set_facecolor('#f7fafc')
    a=axs[0];a.add_patch(Rectangle((20,20),110,62,facecolor='#173349',edgecolor='#e5c576',lw=2))
    def draw(a,g,c,alpha=.9):
        if isinstance(g,MultiPolygon):
            for part in g.geoms:draw(a,part,c,alpha)
        else:
            xy=list(g.exterior.coords);a.add_patch(MPolygon(xy,closed=True,facecolor=c,edgecolor='none',alpha=alpha))
    for p in items:
        color= '#efc765' if p['net']==1 else '#ff8b7f' if p['net'] in (4,6) else '#44dfc8'
        draw(a,p['geom'],color,.9 if p['kind']=='pad' else .7)
        if p['kind']=='via':a.add_patch(Circle((p['x'],p['y']),radius=.15,color='#12334b'))
    a.text(21,25,'V3.8 • CUSTOM SMA GROUND LAND + ADL5535 THERMAL RETURN • NOT FOR FAB',color='white',weight='bold',fontsize=10)
    for x,y,ref,direction in [(28,36,'J101','left'),(122,36,'J102','right'),(28,65,'J103','left'),(122,65,'J104','right')]:
        xs=x-15.2 if direction=='left' else x+15.2
        a.plot([x,xs],[y,y],c='#fdf1ae',lw=1.5,ls='--');a.text(x,y+6.5,ref,color='white',ha='center',fontsize=9)
    a.set_xlim(11,140);a.set_ylim(85,17);a.set_aspect('equal');a.set_title('S3900E — PCB RF sperimentale, 110×62 mm',weight='bold')
    a.set_ylabel('Y [mm]');a.set_xlabel('X [mm]');a.grid(alpha=.1)
    b=axs[1];b.set_facecolor('#e7eef1')
    # left SMA local detail (J101)
    sma=[p for p in items if p['kind']=='pad' and p['ref']=='J101']
    for p in sma:draw(b,p['geom'],'#b5a46f' if p['net']==1 else '#16836f')
    b.text(27.5,29,'4 pads GND sagomati, geometria candidata (non approvata)',fontsize=9,ha='center')
    b.set_xlim(23,33);b.set_ylim(41,28);b.set_aspect('equal');b.grid(alpha=.2)
    fig.tight_layout();fig.savefig(MOD/'Anteprima_Footprint_Termico_V3.8.png',dpi=155);fig.savefig(MOD/'Anteprima_Footprint_Termico_V3.8.svg');plt.close(fig)


def main():
    MOD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True);LIB.mkdir(parents=True,exist_ok=True)
    assert PCB0.exists()
    refsummary=rewrite()
    d,items=manuf_review_and_tests()
    make_library();make_preview(items)
    (OUT/'Fonti_Primarie_V3.8.md').write_text('''# Fonti dimensionali e regole di progettazione — V3.8\n\n- TE Connectivity / Linx, CONSMA002-SMD-G Rev B, *recommended footprint*: https://www.mouser.com/datasheet/2/418/9/ENG_DS_CONSMA002_SMD_G_B-3238924.pdf\n- Analog Devices, ADL5535 Rev A, figure 16 e 17: https://www.analog.com/media/en/technical-documentation/data-sheets/adl5535.pdf\n- KiCad official footprint recommendations, pad paste coverage 50–80%: https://klc.kicad.org/footprint/f6/f6.3/\n- KiCad custom copper pads documentation: https://github.com/KiCad/kicad-doc/blob/master/src/pcbnew/pcbnew_creating_editing_footprints.adoc\n- PCBWay official 4-layer stackups: https://www.pcbway.com/multi-layer-laminated-structure.html\n\n## Limite importante\nLe piazzole SMA vengono *modellate come candidati sagomati*, non trascritte fedelmente dal disegno quotato. Controllo nativo DRC, CAD/3D, impedenza e processo di assemblaggio NON eseguiti.\n''')
    (OUT/'Registro_Problemi_Aperti_V3.8.csv').write_text('id;voce;esito;azione\nB01;SMA 4 GND pad geometry;CANDIDATA;Verificare original recommended footprint e CAD certificato\nB02;SMA x-axis projection;SOLO 2D;Controllo 3D, ingombro pannello e contatto RF\nB03;ADL5535 pad termico;COLLEGAMENTO F.Cu CANDIDATO;Confermare pasta e via tenting con assemblatore\nB04;Solder mask/paste;NON VALIDATI;Esaminare aperture e ponti di saldatura\nB05;KiCad ERC/DRC;NON ESEGUITI;Aprire progetto in ambiente KiCad e refill + DRC\nB06;Gerber e forature;NON PRODOTTI;Generare soltanto dopo approvazione\nB07;Misure RF;NON ESEGUITE;VNA S11/S21 e thermal powered test RX only\nB08;Stackup PCBWay;IPOTETICO;Confermare layer build e 50 ohm con produttore\nB09;SMA codice con suffisso -G;DA VERIFICARE;Confermare esatto part number acquisto\n',encoding='utf-8')
    print('PASS',sum(d['checks'].values()),'/',len(d['checks']),'MIN',d['audit']['min_2d_inter_net_copper_clearance_mm'],'SEGMENTS',d['audit']['segments'] if 'segments' in d['audit'] else '?')
if __name__=='__main__':main()
