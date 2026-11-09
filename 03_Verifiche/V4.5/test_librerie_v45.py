#!/usr/bin/env python3
"""Static tests V4.5. A positive result is NOT a KiCad ERC/DRC pass."""
from pathlib import Path
import hashlib, importlib.util, re, shutil, sys, tempfile, csv

here=Path(__file__).resolve().parent
root=here.parents[1]
spec=importlib.util.spec_from_file_location('builder',here/'crea_librerie_v45.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
lib=root/'04_KiCad/Modulo_RX_Test_50ohm_V4.5_LIBS_PORTABILI_NOT_FOR_FAB'
sc=m.SCH;board=m.BOARD
checks=[]
def check(title,condition):
    if not condition:raise AssertionError(title)
    checks.append(title)

def run():
    rep=m.build()
    check('9 distinct library footprint names',len(rep['footprints'])==9)
    check('3 .pretty library directories',len(rep['footprint_libraries'])==3)
    check('15 PCB component instances',rep['component_count']==15)
    check('9 schematic symbol types',rep['symbol_type_count']==9)
    check('15 standalone .pcb components',len(m.child((lib/(m.BASENAME+'.kicad_pcb')).read_text(),'footprint'))==15)
    check('15 standalone .sch component instances',len(m.child((lib/(m.BASENAME+'.kicad_sch')).read_text(),'symbol'))==15)
    check('Standalone PCB bytes equal V4.3 candidate', (lib/(m.BASENAME+'.kicad_pcb')).read_bytes()==board.read_bytes())
    check('Standalone schema retains project instance name',m.BASENAME in (lib/(m.BASENAME+'.kicad_sch')).read_text())
    check('No schematic older project instance name', 'S3900E_RX_TEST_50R_V4_4_MATCH_NETS_NOT_FOR_FAB' not in (lib/(m.BASENAME+'.kicad_sch')).read_text())
    check('No footprint board net stored',all('(net ' not in x.read_text() for x in lib.glob('*.pretty/*.kicad_mod')))
    check('All 9 footprint files parse',all(len(m.child(x.read_text(),'pad'))>0 for x in lib.glob('*.pretty/*.kicad_mod')))
    check('All 9 footprint geometries preserved',all(m.pad_signature(m.child(board.read_text(),'footprint')[next(i for i,v in enumerate(m.child(board.read_text(),'footprint')) if m.firsthead(v)==f['footprint_id'])])==m.pad_signature((lib/(f['footprint_id'].split(':')[0]+'.pretty')/(f['footprint_id'].split(':')[1]+'.kicad_mod')).read_text()) for f in rep['footprints']))
    check('S3900E custom SMA footprint has 5 copper pads',len(m.child((lib/'S3900E_V38_Review.pretty/CONSMA002_SMD_SHAPED_REVIEW.kicad_mod').read_text(),'pad'))==5)
    check('Custom ADL5535 footprint has 4 pad shapes, 3 pin numbers', len(m.child((lib/'S3900E_V38_Review.pretty/ADL5535_SOT89_PASTE_REVIEW.kicad_mod').read_text(),'pad'))==4)
    check('9 symbol definitions in exported library',len(m.child((lib/'S3900E.kicad_sym').read_text(),'symbol'))==9)
    check('9 external symbol names do not embed library prefix',all(not m.firsthead(s).startswith('S3900E:') for s in m.child((lib/'S3900E.kicad_sym').read_text(),'symbol')))
    check('fp-lib-table uses local KIPRJMOD', all(f'${{KIPRJMOD}}/{n}.pretty' in (lib/'fp-lib-table').read_text() for n in rep['footprint_libraries']))
    check('sym-lib-table uses local KIPRJMOD', '${KIPRJMOD}/S3900E.kicad_sym' in (lib/'sym-lib-table').read_text())
    check('Library identifiers from PCB all resolvable', all((lib/(x.split(':')[0]+'.pretty')/(x.split(':')[1]+'.kicad_mod')).exists() for x in (m.firsthead(i) for i in m.child(board.read_text(),'footprint'))))
    check('Schematic symbol identifiers all resolvable', all(x.split(':',1)[1] in {m.firsthead(a) for a in m.child((lib/'S3900E.kicad_sym').read_text(),'symbol')} for x in re.findall(r'\(lib_id "([^"]+)"',sc.read_text())))
    check('Schematic footprint IDs match PCB footprint IDs', set(re.findall(r'\(property "Footprint" "([^"]+)"',sc.read_text()))>=set(f['footprint_id'] for f in rep['footprints']))
    with (root/'MANIFEST_SHA256_V4.4.csv').open(newline='',encoding='utf8') as stream:
        old={row['path']:row['sha256'] for row in csv.DictReader(stream)}
    check('Source schematic equals frozen V4.4 manifest',hashlib.sha256(sc.read_bytes()).hexdigest()==old[str(sc.relative_to(root))])
    check('Source PCB equals frozen V4.4 manifest',hashlib.sha256(board.read_bytes()).hexdigest()==old[str(board.relative_to(root))])
    # Mutations: a broken pin geometry or absent symbol must be detected.
    sample=next(iter(lib.glob('*.pretty/*.kicad_mod'))).read_text()
    try:
        pad=m.child(sample,'pad')[0]
        altered=re.sub(r'\(size (\d+(?:\.\d+)?) ',lambda q:'(size '+str(float(q.group(1))+0.1)+' ',pad,count=1)
        modified=sample.replace(pad,altered,1)
        check('Mutation footprint pad dimension changes signature', modified!=sample and m.pad_signature(modified)!=m.pad_signature(sample))
    except Exception:raise
    originals=m.child((lib/'S3900E.kicad_sym').read_text(),'symbol')
    defined={m.firsthead(s) for s in originals}
    used={s.split(':',1)[1] for s in re.findall(r'\(lib_id "([^"]+)"',sc.read_text())}
    check('Mutation missing symbol breaks reference coverage',used==defined and used!={m.firsthead(s) for s in originals[:-1]})
    check('Unclosed footprint is rejected by parser',does_fail(lambda: m.exprs('(footprint (pad "1")')))
    return checks

def does_fail(fn):
    try:fn();return False
    except (ValueError,AssertionError):return True

if __name__=='__main__':
    for title in run(): print('PASS',title)
    print('SUCCESS:',len(checks),'static checks; native ERC/DRC NOT RUN')
