#!/usr/bin/env python3
"""Independent, conservative 2D F.Cu & pin/net audit; NOT KiCad ERC/DRC or zone fill.
Requires shapely, matplotlib for preview. Generated geometry approximates SMD roundrect
as axis-aligned rectangles, ignores mask/courtyard/copper-zone. Never FAB release.
"""
import csv, json, re
from collections import defaultdict
from pathlib import Path
from shapely.geometry import Point,LineString,box,MultiPolygon
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[2]
PCB=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.6/S3900E_RX_TEST_50R_V3_6_GND_RETURN_STUDY_NOT_FOR_FAB.kicad_pcb'
SCH_CSV=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.1/Elenco_Reti_RX_Test_V3.1.csv'
OUT=Path(__file__).parent

def parse_sexpr(t):
    tok=re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',t)
    def read(i):
        if tok[i]!='(':
            q=tok[i]
            return (q[1:-1] if q.startswith('"') else q),i+1
        node=[];i+=1
        while i<len(tok) and tok[i]!=')':
            child,i=read(i);node.append(child)
        if i>=len(tok):raise ValueError('Unbalanced S expression')
        return node,i+1
    out,j=read(0)
    if j!=len(tok): raise ValueError('Trailing tokens')
    return out

def subs(node,name):return [x for x in node if isinstance(x,list) and x and x[0]==name]
def one(node,name):
    q=subs(node,name)
    if not q:raise ValueError('missing '+name)
    return q[0]
def num(a):return float(a)

def inspect(pcb):
    node=parse_sexpr(pcb.read_text())
    assert node[0]=='kicad_pcb'
    nets={int(x[1]):x[2] for x in subs(node,'net')}
    items=[];pads=defaultdict(list);padmap={}
    for fp in subs(node,'footprint'):
        prop={q[1]:q[2] for q in subs(fp,'property')}
        ref=prop.get('Reference','?')
        loc=one(fp,'at'); x0,y0=num(loc[1]),num(loc[2]); rot=num(loc[3]) if len(loc)>3 else 0
        if abs(rot)>0.0001:raise ValueError('pad footprint rotations unsupported in review '+ref)
        for p in subs(fp,'pad'):
            loc=one(p,'at');size=one(p,'size');net=one(p,'net')
            x=x0+num(loc[1]);y=y0+num(loc[2]);w,h=num(size[1]),num(size[2]);nn=int(net[1]);pin=p[1]
            if p[3]=='circle':geom=Point(x,y).buffer(w/2,resolution=32)
            else: geom=box(x-w/2,y-h/2,x+w/2,y+h/2)
            ent={'kind':'pad','ref':ref,'pin':pin,'net':nn,'x':x,'y':y,'width':w,'height':h,'geom':geom}
            items.append(ent);pads[nn].append(ent);padmap.setdefault(f'{ref}.{pin}',set()).add(nn)
    for seg in subs(node,'segment'):
        a=one(seg,'start'); b=one(seg,'end');width=num(one(seg,'width')[1]);nn=int(one(seg,'net')[1]);
        x,y,x2,y2=num(a[1]),num(a[2]),num(b[1]),num(b[2]);geom=LineString([(x,y),(x2,y2)]).buffer(width/2,cap_style=1,resolution=12)
        items.append({'kind':'segment','net':nn,'start':(x,y),'end':(x2,y2),'width':width,'geom':geom})
    for v in subs(node,'via'):
        pt=one(v,'at'); size=num(one(v,'size')[1]);nn=int(one(v,'net')[1]);x,y=num(pt[1]),num(pt[2]);
        items.append({'kind':'via','net':nn,'x':x,'y':y,'diameter':size,'geom':Point(x,y).buffer(size/2,resolution=24)})
    return node,nets,items,pads,padmap

def schematic_diff(padmap,nets):
    xwalk={'RF_LNA_IN':'RF_LNA_INPUT','RFOUT_BIAS':'RF_BIAS_OUT','RF_PAD_IN':'RF_ATTEN_IN','RF_PAD_OUT':'RF_ATTEN_OUT'}
    bad=[];ok=0
    with SCH_CSV.open() as f:
        for r in csv.DictReader(f):
            expected=xwalk.get(r['Net'],r['Net'])
            for entry in r['Connected pins'].split(';'):
                pin=entry.strip();actual=[nets[k] for k in padmap.get(pin,[])]
                if expected not in actual:bad.append({'pin':pin,'expected':expected,'actual':actual})
                else:ok+=1
    return ok,bad

def audit(pcb,record=True):
    tree,nets,items,pads,padmap=inspect(pcb)
    comps=defaultdict(list)
    for ent in items:comps[ent['net']].append(ent)
    copper=[e for e in items if e['net']>0]
    clearance_mm=0.20
    faults=[];minclear=(1e5,None)
    for i,a in enumerate(copper):
        for b in copper[i+1:]:
            if a['net']==b['net']:continue
            d=a['geom'].distance(b['geom'])
            if d<minclear[0]:minclear=(d,(a['kind'],a.get('ref',''),a['net'],b['kind'],b.get('ref',''),b['net']))
            if d+1e-6<clearance_mm:
                faults.append({'distance_mm':round(d,4),'a':f"{a['kind']} {a.get('ref','')}/{nets[a['net']]}",'b':f"{b['kind']} {b.get('ref','')}/{nets[b['net']]}"})
    # Non-GND components must be connected via top-layer (without assuming filled zones).
    disconnected={}
    for netid in range(2,9):
        shapes=[e['geom'] for e in comps[netid]]
        geom=unary_union(shapes)
        ncomp= len(geom.geoms) if isinstance(geom,MultiPolygon) else 1
        if ncomp!=1:disconnected[nets[netid]]=ncomp
    # Each ground pad should reach at least one via through top Cu, but each separate via
    # waits for native plane refill to connect the global GND return.
    ground_items=comps[1]
    ground_pads=[e for e in ground_items if e['kind']=='pad']
    ground_vias=[e for e in ground_items if e['kind']=='via']
    ground_segs=[e for e in ground_items if e['kind']=='segment']
    isolated=[]
    for p in ground_pads:
        if any(p['geom'].intersects(v['geom']) for v in ground_vias):continue
        hits=[seg for seg in ground_segs if seg['geom'].intersects(p['geom'])]
        if not hits:
            isolated.append(f"{p['ref']}.{p['pin']}");continue
        visited={id(p)};todo=[p['geom']];via_ok=False
        while todo:
            cur=todo.pop()
            for e in ground_segs+ground_vias:
                if id(e) in visited:continue
                if cur.intersects(e['geom']):
                    visited.add(id(e));todo.append(e['geom'])
                    if e['kind']=='via':via_ok=True
            if via_ok:break
        if not via_ok:isolated.append(f"{p['ref']}.{p['pin']}")
    ok,scherr=schematic_diff(padmap,nets)
    zone_layer=[one(z,'layer')[1] for z in subs(tree,'zone')]
    summary={
        'revision':'V3.6', 'project':'S3900E module RX 50ohm',
        'manufacturing_release':'BLOCKED - NO GERBERS',
        'checks_performed':['balanced sexpr parse','pad-net comparison with schematic pin table','conservative 2D F.Cu inter-net clearance','trace topology for seven signal/power nets','ground pad to local via reachability','ground region layer declarations'],
        'native_kicad_erc_drc':'NOT RUN - kicad-cli absent',
        'footprints':len(subs(tree,'footprint')),'nets':len(nets)-1,
        'segments':len(subs(tree,'segment')),'vias':len(subs(tree,'via')),
        'zones_declared_unfilled':zone_layer,
        'min_2d_inter_net_copper_clearance_mm':round(minclear[0],4),'closest_copper_pair':minclear[1],
        'minimum_review_clearance_mm':clearance_mm,'2d_clash_count':len(faults),'2d_clashes':faults[:50],
        'unconnected_nonground_nets':disconnected,
        'ground_pad_count':len(ground_pads),'ground_via_count':len(ground_vias),
        'ground_pads_without_explicit_local_via':isolated,
        'schematic_pin_assignments_ok':ok,'schematic_pin_mismatches':scherr,
        'sma_center_2_05mm':'manufacturer drawing shows diameter 2.05 feature; in-board circle is a copper PLACEHOLDER and mechanical function unresolved',
        'copper_zones_filled':'NO',
        'model_limitations':['not a KiCad ERC/DRC','no soldermask/solderpaste/silkscreen conflicts','no 3D mechanical fit / exact SMA launch','no thermal simulation','no RF EM/impedance simulation','L1-L2 stack-up NOT confirmed by PCBWay','cannot prove GND plane connectivity without zone refill','pad shape roundrect treated as rect (conservative)','does not verify formal KiCad file load'],
        'release_blockers':['exact TE SMA footprint, center feature and edge-overhang','confirm ADL5535 Fig17 paste/thermals','native KiCad DRC and zone refill','controlled impedance manufacturing stackup','VNA/S11/S21 and powered tests','TX disconnected: dedicated RX-only bench circuit']
    }
    if record:(OUT/'Rapporto_Audit_Indipendente_V3.6.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    return summary,items

def plot(items):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle,Circle
    fig,ax=plt.subplots(figsize=(14,7.6))
    ax.add_patch(Rectangle((20,20),110,62,facecolor='#071626',edgecolor='#e9dfb0',lw=2))
    # Dark theme only in saved plot; no user chart tool restrictions here (internal file PNG engineering drawing).
    colors={1:'#2db79c',2:'#e7bd67',3:'#e7bd67',4:'#e7bd67',5:'#e7bd67',6:'#f39c6b',7:'#adcbe8',8:'#adcbe8'}
    for e in items:
        c=colors.get(e['net'],'#cccccc')
        if e['kind']=='segment':
            a,b=e['start'],e['end'];ax.plot([a[0],b[0]],[a[1],b[1]],color=c,lw= max(1.5,e['width']*4),zorder=2)
        elif e['kind']=='via':
            ax.add_patch(Circle((e['x'],e['y']), e['diameter']*.60, facecolor='#0d3944', edgecolor=c,lw=1.1,zorder=5))
        elif e['kind']=='pad':
            if e['ref'].startswith('J10') and e['pin']=='1':
                ax.add_patch(Circle((e['x'],e['y']),e['width']/2,facecolor=c,edgecolor='white',lw=.3,zorder=4))
            else:
                ax.add_patch(Rectangle((e['x']-e['width']/2,e['y']-e['height']/2),e['width'],e['height'],facecolor=c,edgecolor='white',lw=.2,zorder=4))
    labels=[('J101',28,29.5),('C101',52,32),('U101',68,27.5),('C102',92,32),('J102',122,29.5),('J103',28,57.5),('R201',54,62),('R203',74,61),('R202',92,62),('J104',122,57.5),('J105',108,52.5)]
    for label,x,y in labels: ax.text(x,y,label,color='#e8f4ff',ha='center',va='center',fontsize=8)
    ax.set_xlim(18,132);ax.set_ylim(84,18);ax.set_aspect('equal');ax.set_facecolor('#0b1d30');
    ax.set_title('S3900E V3.6  |  RF test PCB - Ground return / via stitching STUDY',fontsize=14)
    ax.set_xlabel('X [mm]');ax.set_ylabel('Y [mm]');ax.grid(alpha=.08,color='white')
    fig.text(.5,.015,'NOT FOR FABRICATION  |  footprint SMA unresolved  |  zones declared but UNFILLED  |  no KiCad DRC',ha='center',fontsize=9,color='#d65742')
    fig.tight_layout(rect=(0,.03,1,.97));p=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.6/Anteprima_Ritorni_Massa_V3.6.png'
    fig.savefig(p,dpi=165);plt.close(fig)
    return p

if __name__=='__main__':
    import sys
    report,items=audit(PCB)
    print(json.dumps({k:v for k,v in report.items() if k in ('footprints','nets','segments','vias','zones_declared_unfilled','min_2d_inter_net_copper_clearance_mm','2d_clash_count','unconnected_nonground_nets','ground_pad_count','ground_pads_without_explicit_local_via','schematic_pin_assignments_ok','schematic_pin_mismatches')},indent=2))
    print('PREVIEW',plot(items))
    if report['2d_clash_count'] or report['unconnected_nonground_nets'] or report['schematic_pin_mismatches'] or report['ground_pads_without_explicit_local_via']:
        sys.exit('AUDIT FAIL / review above')
    print('INDEPENDENT 2D/PIN STATIC REVIEW OK - NOT KICAD DRC')
