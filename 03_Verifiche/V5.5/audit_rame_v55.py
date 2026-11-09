#!/usr/bin/env python3
"""Independent static F.Cu copper check (Shapely), NOT native KiCad DRC.

No zones are filled, so this is a *partial* inter-net spacing screen only.
Never approves fabrication; never writes to the candidate KiCad source files.
"""
from pathlib import Path
import sys, math, json, hashlib, argparse, itertools, collections
from shapely.geometry import Point, LineString, Polygon, box
from shapely.affinity import translate, rotate, scale
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parents[2]
RX=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB'
PCB=RX/'S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB.kicad_pcb'
# Reuse the historical S-expression parser, not its geometry implementation.
sys.path.insert(0,str(ROOT/'03_Verifiche/V5.3'))
from audit_indipendente_v53 import parse, child, children, pval

EPS=1e-7

def numpair(tag): return float(tag[1]),float(tag[2])

def shape_pad(pad):
    """Pad copper in the pad's local frame; custom polygon coordinates are local."""
    sh=pad[3]
    sx,sy=numpair(child(pad,'size'))
    if sh=='circle': g=Point(0,0).buffer(sx/2,quad_segs=24)
    elif sh in ('rect','roundrect','custom'):
        base=box(-sx/2,-sy/2,sx/2,sy/2)
        if sh=='roundrect':
            ratio=child(pad,'roundrect_rratio')
            radius=min(sx,sy)*float(ratio[1]) if ratio else 0
            g=base.buffer(-radius,join_style=1).buffer(radius,join_style=1) if radius>EPS else base
        elif sh=='custom':
            shapes=[base]
            prim=child(pad,'primitives')
            for poly in children(prim,'gr_poly') if prim else []:
                pts=child(poly,'pts')
                coords=[numpair(xy) for xy in children(pts,'xy')]
                if len(coords)>=3:shapes.append(Polygon(coords))
            # Include the entire anchor: conservative for clearance.
            g=unary_union(shapes)
        else:g=base
    elif sh=='oval':
        radius=min(sx,sy)/2
        if sx>sy:
            g=LineString([(-(sx-sy)/2,0),((sx-sy)/2,0)]).buffer(radius,quad_segs=20)
        else:
            g=LineString([(0,-(sy-sx)/2),(0,(sy-sx)/2)]).buffer(radius,quad_segs=20)
    else:raise ValueError('Unsupported pad shape '+str(sh))
    at=child(pad,'at')
    x=float(at[1]);y=float(at[2]);angle=float(at[3]) if len(at)>3 else 0
    g=rotate(g,-angle,origin=(0,0),use_radians=False)
    return translate(g,xoff=x,yoff=y)

def actual_board_copper(text):
    board=parse(text)
    nets={int(n[1]):n[2] for n in children(board,'net')}
    items=[];pad_count=segment_count=via_count=0
    for fp in children(board,'footprint'):
        ref=pval(fp,'Reference')
        at=child(fp,'at');x,y=float(at[1]),float(at[2]);angle=float(at[3]) if len(at)>3 else 0
        for pad in children(fp,'pad'):
            layers=child(pad,'layers')
            if not layers or not any(l in ('F.Cu','*.Cu') for l in layers[1:]):continue
            padnet=child(pad,'net');net=int(padnet[1]) if padnet else 0
            geom=shape_pad(pad)
            geom=rotate(geom,-angle,origin=(0,0),use_radians=False)
            geom=translate(geom,xoff=x,yoff=y)
            items.append({'kind':'pad','id':f'{ref}:{pad[1]}:{pad_count}', 'net':net,'geometry':geom})
            pad_count+=1
    for seg in children(board,'segment'):
        if child(seg,'layer')[1]!='F.Cu':continue
        a=numpair(child(seg,'start'));b=numpair(child(seg,'end'))
        width=float(child(seg,'width')[1]);net=int(child(seg,'net')[1])
        geom=LineString([a,b]).buffer(width/2,cap_style=1,join_style=1,quad_segs=18)
        items.append({'kind':'segment','id':'track:'+str(segment_count),'net':net,'geometry':geom})
        segment_count+=1
    for via in children(board,'via'):
        layers=child(via,'layers')
        if 'F.Cu' not in layers[1:]:continue
        a=numpair(child(via,'at'));size=float(child(via,'size')[1]);net=int(child(via,'net')[1])
        geom=Point(*a).buffer(size/2,quad_segs=24)
        items.append({'kind':'via','id':'via:'+str(via_count),'net':net,'geometry':geom,
                      'drill_mm':float(child(via,'drill')[1]),'diameter_mm':size})
        via_count+=1
    zone_count=len(children(board,'zone'))
    filled_count=sum(bool(children(z,'filled_polygon')) for z in children(board,'zone'))
    return items,{'pads':pad_count,'segments':segment_count,'vias':via_count,'zones':zone_count,'filled_zone_polygons':filled_count},nets

def audit(text,threshold=0.30):
    items,counts,nets=actual_board_copper(text)
    comparisons=0;best=None;violations=[]; nearest=[]
    for a,b in itertools.combinations(items,2):
        if a['net']==b['net']:continue
        comparisons+=1
        distance=float(a['geometry'].distance(b['geometry']))
        v={'first':a['id'],'second':b['id'], 'net1':nets.get(a['net'],'?'),'net2':nets.get(b['net'],'?'),
           'clearance_mm':round(distance,5)}
        if best is None or distance<best['clearance_mm']:best=v
        nearest.append(v)
        if distance+EPS<threshold:violations.append(v)
    # Compute whether zone copper participates. None of these outcomes includes zone fills.
    return {'version':'V5.5','method':'independent Shapely top-copper shape-based distance screen',
            'board_sha256':hashlib.sha256(text.encode()).hexdigest(),
            'layer':'F.Cu','geometry_counts':counts, 'nets':len(nets)-1,
            'cross_net_pairs':comparisons,'screen_threshold_mm':threshold,
            'minimum_cross_net_clearance':best,
            'closest_12_cross_net_pairs':sorted(nearest,key=lambda x:x['clearance_mm'])[:12],
            'pairs_below_0_50mm':sum(v['clearance_mm']<0.50 for v in nearest),
            'clearance_screen_violations':sorted(violations,key=lambda x:x['clearance_mm']),
            'status':'STATIC_SCREEN_PASS' if not violations else 'STATIC_SCREEN_FAIL',
            'zone_refill':'NOT_RUN','native_erc':'NOT_RUN','native_drc':'NOT_RUN',
            'notes':['Covers F.Cu pads (including custom), tracks and through-via copper only.',
                    'Does not cover filled copper zones, exact KiCad polygon approximations, buried layers, masked solder, silk, drill/courtyard rules or full connectivity.',
                    'Screen threshold is an analytical parameter, NOT a verified KiCad design-rule setting.',
                    'Must not be treated as KiCad DRC or fabrication approval.'],
            'fabrication_allowed':False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pcb',type=Path,default=PCB)
    parser.add_argument('--threshold',type=float,default=0.30)
    parser.add_argument('--output',type=Path,default=None)
    args=parser.parse_args()
    result=audit(args.pcb.read_text(),args.threshold)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='notes' and k!='clearance_screen_violations'},indent=2,ensure_ascii=False))
    return 0 if result['status']=='STATIC_SCREEN_PASS' else 2

if __name__=='__main__':raise SystemExit(main())
