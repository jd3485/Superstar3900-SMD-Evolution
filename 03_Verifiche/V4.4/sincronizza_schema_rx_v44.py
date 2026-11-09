#!/usr/bin/env python3
"""V4.4 - schematic candidate derived from PCB netnames, pin assignments and values.
Static model only. No KiCad tool is invoked; no ERC/DRC/production signoff.
"""
from __future__ import annotations
import csv, json, hashlib, re, uuid, importlib.util, sys
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'03_Verifiche/V4.4'
OLD_SCHEM=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.1/S3900E_RX_TEST_50R_V3_1_DRAFT.kicad_sch'
PCB=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V3.8/S3900E_RX_TEST_50R_V3_8_SHAPED_LAND_THERMAL_REVIEW_NOT_FOR_FAB.kicad_pcb'
PCB43=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.3_STUDIO_SMA/S3900E_RX_TEST_50R_V4_3_SMA_ENVELOPE_HYPOTHESIS_NOT_FOR_FAB.kicad_pcb'
NEW=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.4_SCHEMA_MATCH/S3900E_RX_TEST_50R_V4_4_MATCH_NETS_NOT_FOR_FAB.kicad_sch'
SRC_SHA='57dd24b13edb5dc987e3ad8cdae0d2d8cc7a1fa3aefb455a63ebc86559eec489'
module=ROOT/'03_Verifiche/V4.1/audit_rf_v41.py'
spec=importlib.util.spec_from_file_location('s3900_v44_legacy',module)
a=importlib.util.module_from_spec(spec)
sys.dont_write_bytecode=True
try:spec.loader.exec_module(a)
finally:sys.dont_write_bytecode=False


def balanced_segment(text,offset):
    assert text[offset]=='('
    lev=0; quoted=False; escaped=False
    for i in range(offset,len(text)):
        c=text[i]
        if quoted:
            if escaped:escaped=False
            elif c=='\\':escaped=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=='(':lev+=1
        elif c==')':
            lev-=1
            if lev==0:return text[offset:i+1]
    raise ValueError('Unclosed S-expression')


def parse_pcb(p=PCB):
    t=a.legacy.parse_sexpr(p.read_text(encoding='utf-8'))
    fps=a.footprint_map(t)
    rows=[];components={}
    for ref, fp in sorted(fps.items()):
        properties={q[1]:q[2] for q in a.subs(fp,'property')}
        components[ref]={'reference':ref,'value':properties['Value'],'footprint':fp[1]}
        pmap={}
        for p in a.subs(fp,'pad'):
            pin=p[1];net=a.val(p,'net');netname=net[1]
            if pin in pmap and pmap[pin]!=netname:
                raise AssertionError(f'Inconsistent repeated copper pads: {ref}.{pin}')
            pmap[pin]=netname
        for pin,net in sorted(pmap.items(),key=lambda q:int(q[0])):
            rows.append({'reference':ref,'value':properties['Value'],'footprint':fp[1],
                        'pin':pin,'net':net})
    return rows,components


def new_schematic_text():
    if hashlib.sha256(PCB.read_bytes()).hexdigest()!=SRC_SHA:
        raise AssertionError('V3.8 source PCB SHA changed')
    rows,parts=parse_pcb()
    rows43,parts43=parse_pcb(PCB43)
    if rows!=rows43 or parts!=parts43:
        raise AssertionError('V3.8 / V4.3 part-to-net mismatch: STOP')
    raw=OLD_SCHEM.read_text(encoding='utf-8')
    parsed=a.legacy.parse_sexpr(raw)
    # Validate original schematic carries one component for every PCB part.
    sch_parts={}
    for q in a.subs(parsed,'symbol'):
        props={k[1]:k[2] for k in a.subs(q,'property')}
        sch_parts[props['Reference']]={'value':props['Value'],'lib_id':a.val(q,'lib_id')[0]}
    if set(sch_parts)!=set(parts):raise AssertionError('V3.1 / PCB reference mismatch')
    # Embedded library symbols define pin locations in schematic local coordinate system.
    libs={s[1]:s for s in a.subs(a.one(parsed,'lib_symbols'),'symbol')}
    pins_by_type={}
    for k,s in libs.items():
        pinmap={}
        for unit in a.subs(s,'symbol'):
            for pin in a.subs(unit,'pin'):
                num=a.val(pin,'number')[0]
                pos=list(map(float,a.val(pin,'at')[:2]))
                if num in pinmap:raise AssertionError(f'Duplicate symbol pin: {k}.{num}')
                pinmap[num]=pos
        pins_by_type[k]=pinmap
    expected={ (x['reference'],x['pin']):x['net'] for x in rows}
    root_uuid=a.val(parsed,'uuid')[0]
    sch_title='S3900E_RX_TEST_50R_V4_4_MATCH_NETS_NOT_FOR_FAB'
    rawlibs=balanced_segment(raw,raw.index('(lib_symbols'))
    # New project basename and root UUID in copied instance records.
    placements=[]
    for m in re.finditer(r'\(symbol\s+\(lib_id\s+"',raw):
        item=balanced_segment(raw,m.start())
        node=a.legacy.parse_sexpr(item)
        props={x[1]:x[2] for x in a.subs(node,'property')}
        ref=props['Reference'];fp=parts[ref]['footprint'];value=parts[ref]['value']
        item=item.replace('S3900E_RX_TEST_50R_V3_1_DRAFT',sch_title)
        # Replace only exactly one Footprint property, originally blank or assigned.
        expr=r'(\(property "Footprint" )"[^"]*"'
        item,n=re.subn(expr,lambda m:m.group(1)+'"'+fp+'"',item,count=1)
        if n!=1:raise AssertionError('Footprint missing for '+ref)
        # Original J105 display value differs; align it with board.
        if value!=props['Value']:
            exprval=r'(\(property "Value" )"[^"]*"'
            item,n=re.subn(exprval,lambda m:m.group(1)+'"'+value+'"',item,count=1)
            if n!=1:raise AssertionError('Value property missing '+ref)
        placements.append(item)

    # Every electrical pin gets its own short wire + unique local label.
    # Equal labels join nets logically, not through long drawn wires. 5.08mm stubs.
    # All symbols here have orientation 0; fails closed otherwise.
    links=[];used=set()
    for q in a.subs(parsed,'symbol'):
        props={k[1]:k[2] for k in a.subs(q,'property')}
        ref=props['Reference'];typ=a.val(q,'lib_id')[0]
        px,py,*rest=list(map(float,a.val(q,'at')))
        if rest and abs(rest[0])>1e-9:raise AssertionError('Rotated placed symbol not supported '+ref)
        pins=pins_by_type[typ]
        have={x['pin'] for x in rows if x['reference']==ref}
        if set(pins)!=have:raise AssertionError(f'Unmatched physical pins {ref}: {set(pins)^have}')
        for pin,(lx,ly) in sorted(pins.items(),key=lambda pair:int(pair[0])):
            net=expected[ref,pin]
            x=round(px+lx,3);y=round(py-ly,3)
            if abs(lx)>1e-9: sx=round(x+5.08*(1 if lx>0 else -1),3); sy=y
            elif abs(ly)>1e-9: sx=x;sy=round(y-5.08*(1 if ly>0 else -1),3)
            else:raise AssertionError('Pin at origin '+ref+pin)
            def fmt(v):return f'{v:.3f}'
            # Distinct wire endpoints avoid accidental merges and short intersections.
            signature=(sx,sy)
            if signature in used:raise AssertionError('Overlapping label endpoint '+str(signature))
            used.add(signature)
            lid=str(uuid.uuid5(uuid.UUID(root_uuid),f'v44_wire_{ref}_{pin}'))
            labelid=str(uuid.uuid5(uuid.UUID(root_uuid),f'v44_netlabel_{ref}_{pin}'))
            links.append(f'(wire (pts (xy {fmt(x)} {fmt(y)}) (xy {fmt(sx)} {fmt(sy)})) '
                         f'(stroke (width 0) (type default)) (uuid "{lid}"))')
            links.append(f'(label "{net}" (at {fmt(sx)} {fmt(sy)} 0) '
                         f'(effects (font (size 1.0 1.0)) (justify left bottom)) (uuid "{labelid}"))')
    pre=f'''(kicad_sch (version 20231120) (generator "S3900E_V4_4_STATIC_SYNC_NOT_ERC")
(uuid "{root_uuid}") (paper "A3")
(title_block (title "Superstar 3900 - RF test board matching 15 references and 8 PCB nets")
 (date "2026-11-08") (rev "V4.4 NETLIST CANDIDATE - ERC NOT RUN"))
{rawlibs}
'''
    disclaimer='''(text "SCHEMATIC NET-MATCHED STATIC CANDIDATE V4.4 (PCB V3.8 / study V4.3).\nERC NOT RUN. NO FAB / NO PCBWAY / NO TX.\nSMA LAND PATTERN AND ADL5535 THERMALS UNAPPROVED.\nVERIFY FOOTPRINT LIBRARIES, PIN TYPES, BOM AND SCHEMATIC-PARITY IN NATIVE KICAD." (at 30 230 0) (effects (font (size 1.35 1.35))))'''
    text=pre+'\n'.join(placements)+'\n'+'\n'.join(links)+'\n'+disclaimer+'\n)\n'
    tree=a.legacy.parse_sexpr(text)
    if tree[0]!='kicad_sch' or len(a.subs(tree,'symbol'))!=15 or len(a.subs(tree,'wire'))!=len(rows):
        raise AssertionError('New schematic parse or count invalid')
    return text,rows,parts


def validate_schematic(text,rows,parts):
    tree=a.legacy.parse_sexpr(text)
    place={}
    for sym in a.subs(tree,'symbol'):
        props={k[1]:k[2] for k in a.subs(sym,'property')}
        if props['Reference'] in place:raise AssertionError('Duplicate reference')
        place[props['Reference']]=props
    assert len(place)==len(parts)==15
    for ref,props in place.items():
        if props['Value']!=parts[ref]['value'] or props['Footprint']!=parts[ref]['footprint']:
            raise AssertionError(f'BOM / footprint mismatch at {ref}')
    labels=a.subs(tree,'label'); wires=a.subs(tree,'wire')
    if len(wires)!=len(rows) or len(labels)!=len(rows):raise AssertionError('Wire/pin count mismatch')
    label_pos=defaultdict(list)
    for label in labels:
        point=tuple(round(float(z),3) for z in a.val(label,'at')[:2]); label_pos[point].append(label[1])
    # Reconstruct pin endpoint from OLD lib symbols + V4.4 placed symbols,
    # check that a single wire originates at pin and ends in its expected label.
    libs={s[1]:s for s in a.subs(a.one(tree,'lib_symbols'),'symbol')}
    pindef={}
    for typ,s in libs.items():
        pd={}
        for unit in a.subs(s,'symbol'):
            for pin in a.subs(unit,'pin'):
                pd[a.val(pin,'number')[0]]=[float(z) for z in a.val(pin,'at')[:2]]
        pindef[typ]=pd
    graph=defaultdict(list)
    for wire in wires:
        q=a.subs(a.one(wire,'pts'),'xy')
        p1=tuple(round(float(x),3) for x in q[0][1:3]);p2=tuple(round(float(x),3) for x in q[1][1:3])
        graph[p1].append(p2);graph[p2].append(p1)
    for item in rows:
        ref,pin,net=item['reference'],item['pin'],item['net']
        sym=next(s for s in a.subs(tree,'symbol') if {q[1]:q[2] for q in a.subs(s,'property')}['Reference']==ref)
        xy=[float(z) for z in a.val(sym,'at')[:2]]
        local=pindef[a.val(sym,'lib_id')[0]][pin]
        anchor=(round(xy[0]+local[0],3),round(xy[1]-local[1],3))
        ends=graph[anchor]
        if len(ends)!=1:raise AssertionError(f'{ref}.{pin}: wires at anchor {len(ends)}')
        wire_end=ends[0]
        if label_pos[wire_end]!=[net]:raise AssertionError(f'{ref}.{pin}: expected {net}, actual {label_pos[wire_end]}')
    return {'schematic_part_count':len(parts),'mapped_pins':len(rows),
            'unique_nets':len(set(r['net'] for r in rows)), 'all_pin_nets_match':True,
            'footprint_ids_match':True,'passive_symbol_types_not_qualified':True,
            'source_original_sha256':hashlib.sha256(PCB.read_bytes()).hexdigest(),
            'native_erc_executed':False,'native_drc_executed':False,
            'schematic_pcb_uuid_links_verified':False,'cad_te_approved':False,'thermal_approved':False}


def main():
    OUT.mkdir(parents=True,exist_ok=True);NEW.parent.mkdir(parents=True,exist_ok=True)
    text,rows,parts=new_schematic_text()
    report=validate_schematic(text,rows,parts)
    if NEW.exists() and NEW.read_text(encoding='utf-8')!=text:
        raise AssertionError('Existing V4.4 schematic differs; STOP without overwrite')
    NEW.write_text(text,encoding='utf-8')
    # CSV manifest of pin-to-net mapping
    with (OUT/'NETMAP_RX_PCB_V4.4.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,['reference','value','footprint','pin','net']);w.writeheader();w.writerows(rows)
    (OUT/'VERIFICA_SCHEMA_PCB_V4.4.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
