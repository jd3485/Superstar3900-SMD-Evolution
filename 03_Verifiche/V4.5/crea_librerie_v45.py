#!/usr/bin/env python3
"""V4.5: portable *study* footprint/symbol libraries from embedded PCB and schematic.
No native KiCad run, no verification against manufacturer CAD and no fabrication approval.
Does not modify any historical file. Run from anywhere with stdlib Python 3.
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
import hashlib, json, re, shutil

ROOT=Path(__file__).resolve().parents[2]
BOARD=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.3_STUDIO_SMA/S3900E_RX_TEST_50R_V4_3_SMA_ENVELOPE_HYPOTHESIS_NOT_FOR_FAB.kicad_pcb'
SCH=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.4_SCHEMA_MATCH/S3900E_RX_TEST_50R_V4_4_MATCH_NETS_NOT_FOR_FAB.kicad_sch'
DST=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB'
BASENAME='S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB'
REPORT=ROOT/'03_Verifiche/V4.5/INVENTARIO_LIBRERIE_V4.5.json'

# A lexical scanner that respects parentheses inside string literals.
def exprs(text):
    """Return (head, full_expression) for all *immediate* children of a root expression."""
    if not text.lstrip().startswith('('):raise ValueError('Not an S-expression')
    pos=text.index('('); level=0; in_str=False; escape=False; start=None; found=[]
    for i in range(pos,len(text)):
        c=text[i]
        if in_str:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':in_str=False
            continue
        if c=='"':in_str=True;continue
        if c=='(':
            if level==1:start=i
            level+=1
        elif c==')':
            level-=1
            if level<0: raise ValueError('Unbalanced bracket')
            if level==1 and start is not None:
                s=text[start:i+1]
                match=re.match(r'\(\s*([^\s()]+)',s)
                if match:found.append((match.group(1),s))
                start=None
            if level==0:
                if text[i+1:].strip():raise ValueError('Trailing tokens')
                return found
    raise ValueError('Unclosed expression')

def firsthead(segment):
    match=re.match(r'\(\s*[^\s()]+\s+"((?:\\.|[^"])*)"',segment)
    if not match:raise ValueError('Missing quoted name')
    return match.group(1)

def child(segment, name):
    return [x for h,x in exprs(segment) if h==name]

def pad_signature(fp):
    """Geometry/pin identity only, independent of reference, net and timestamp."""
    pads=[]
    for p in child(fp,'pad'):
        clean=re.sub(r'\(net\s+\d+\s+"[^"]*"\)','',p)
        clean=re.sub(r'\(tstamp\s+"[^"]*"\)','',clean)
        clean=re.sub(r'\s+',' ',clean).strip()
        pads.append(clean)
    return tuple(sorted(pads))

def library_footprint(board_fp, name):
    node=exprs(board_fp)
    keep=[]
    for head,chunk in node:
        if head in ('at','tstamp','path','sheetname','sheetfile','locked'):
            continue
        if head=='property':
            if chunk.startswith('(property "Reference" '):
                chunk=re.sub(r'^(\(property "Reference" )"[^"]+"',r'\1"REF**"',chunk,count=1)
            if chunk.startswith('(property "Value" '):
                chunk=re.sub(r'^(\(property "Value" )"[^"]*"',lambda m:m.group(1)+'"'+name+'"',chunk,count=1)
        if head=='pad':
            chunk=re.sub(r'\s*\(net\s+\d+\s+"[^"]*"\)','',chunk)
        keep.append(chunk)
    # Root layer and pad coordinates remain in footprint-local coordinates.
    return '(footprint "'+name+'"\n  '+'\n  '.join(keep)+'\n)\n'

def build():
    raw_b=BOARD.read_text('utf-8');raw_s=SCH.read_text('utf-8')
    bnodes=child(raw_b,'footprint')
    if len(bnodes)!=15: raise AssertionError('Unexpected number of PCB components')
    groups=defaultdict(list)
    for f in bnodes:groups[firsthead(f)].append(f)
    assert len(groups)==9, sorted(groups)
    for fid,instances in groups.items():
        signatures={pad_signature(x) for x in instances}
        if len(signatures)!=1:raise AssertionError('Different pad geometries share library ID '+fid)
        if not signatures.pop():raise AssertionError('Footprint without pads '+fid)
    lib_s_exps=child(raw_s,'lib_symbols')
    if len(lib_s_exps)!=1:raise AssertionError('Missing lib_symbols')
    embedded=child(lib_s_exps[0],'symbol')
    sym_names={firsthead(sym) for sym in embedded}
    if len(sym_names)!=9 or not all(s.startswith('S3900E:') for s in sym_names):raise AssertionError('Symbol library unexpected')
    used={re.search(r'\(lib_id "([^"]+)"',sym).group(1) for sym in child(raw_s,'symbol')}
    if used!=sym_names:raise AssertionError('Embedded symbols do not match instantiated ones')

    DST.mkdir(parents=True,exist_ok=True)
    names=sorted(set(x.split(':')[0] for x in groups))
    for name in names:(DST/(name+'.pretty')).mkdir(exist_ok=True)
    for fid,instances in sorted(groups.items()):
        nick,name=fid.split(':',1)
        target=DST/(nick+'.pretty')/(name+'.kicad_mod')
        target.write_text(library_footprint(instances[0],name),encoding='utf8')
    fp_table='(fp_lib_table\n'+''.join(f'  (lib (name "{n}")(type "KiCad")(uri "${{KIPRJMOD}}/{n}.pretty")(options "")(descr "S3900E V4.5 experimental footprint, NOT approved for fabrication"))\n' for n in names)+')\n'
    (DST/'fp-lib-table').write_text(fp_table,'utf8')

    sanitized=[]
    for sym in sorted(embedded,key=firsthead):
        # In a standalone symbol library the root symbol has an unqualified name.
        fullname=firsthead(sym);short=fullname.split(':',1)[1]
        sanitized.append(sym.replace('"'+fullname+'"','"'+short+'"',1))
    sym_lib='(kicad_symbol_lib (version 20231120) (generator "s3900e_v45")\n'+'\n'.join(sanitized)+'\n)\n'
    (DST/'S3900E.kicad_sym').write_text(sym_lib,'utf8')
    (DST/'sym-lib-table').write_text('(sym_lib_table\n  (lib (name "S3900E")(type "KiCad")(uri "${KIPRJMOD}/S3900E.kicad_sym")(options "")(descr "S3900E V4.5 experimental RX symbols"))\n)\n','utf8')
    schem_out=raw_s.replace('S3900E_RX_TEST_50R_V4_4_MATCH_NETS_NOT_FOR_FAB',BASENAME)
    assert schem_out!=raw_s
    schem_out=schem_out.replace('V4.4 NETLIST CANDIDATE - ERC NOT RUN','V4.5 LIB PORTABLE STUDY - ERC NOT RUN')
    (DST/(BASENAME+'.kicad_sch')).write_text(schem_out,'utf8')
    shutil.copyfile(BOARD,DST/(BASENAME+'.kicad_pcb'))

    # Confirm exported shapes match parent PCB and scan for unresolved library names.
    geo=[]
    for fid,instances in sorted(groups.items()):
        nick,name=fid.split(':',1)
        path=DST/(nick+'.pretty')/(name+'.kicad_mod')
        created=path.read_text('utf8')
        if pad_signature(instances[0])!=pad_signature(created):raise AssertionError('Extracted pad geometry changed '+fid)
        if re.search(r'\(net\s+\d+\s+"',created):raise AssertionError('Board net leaked into footprint '+fid)
        geo.append({'footprint_id':fid,'instances':len(instances),'pad_primitives':len(child(created,'pad')),
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    exported_board=(DST/(BASENAME+'.kicad_pcb')).read_bytes()
    if exported_board!=BOARD.read_bytes():raise AssertionError('PCB changed during copy')
    if len(child((DST/(BASENAME+'.kicad_sch')).read_text('utf8'),'symbol'))!=15:raise AssertionError('Symbols missing')
    out={'version':'4.5','status':'STATIC_LIBRARY_RECONSTRUCTION_ONLY_NOT_FOR_FAB',
         'source_board_sha256':hashlib.sha256(BOARD.read_bytes()).hexdigest(),
         'source_schematic_sha256':hashlib.sha256(SCH.read_bytes()).hexdigest(),
         'footprint_libraries':names,'footprints':geo,'symbol_library':'S3900E.kicad_sym',
         'symbols':sorted(sym_names),'component_count':len(bnodes),'symbol_type_count':len(embedded),
         'native_erc_drc':'NOT_RUN','manufacturer_cad_check':'NOT_APPROVED'}
    REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8')
    return out

if __name__=='__main__':
    report=build()
    print('OK: components',report['component_count'],'footprints',len(report['footprints']),
          'symbol types',report['symbol_type_count'],'(static checks only)')
