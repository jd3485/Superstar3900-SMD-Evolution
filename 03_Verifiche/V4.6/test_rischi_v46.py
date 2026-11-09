#!/usr/bin/env python3
"""Static and launcher tests; mocked KiCad is NOT a native ERC/DRC."""
from pathlib import Path
import json, tempfile, subprocess, hashlib, csv, os, importlib.util, re, shutil
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit',HERE/'audit_rischi_v46.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
checks=[]
def ck(label,cond):
    if not cond:raise AssertionError(label)
    checks.append(label)

def execute_fake(flag):
    with tempfile.TemporaryDirectory() as t:
        tmp=Path(t);bin_dir=tmp/'bin';bin_dir.mkdir()
        fak=(bin_dir/'kicad-cli')
        script='''#!/usr/bin/env python3
import sys,pathlib,json
args=sys.argv[1:]
if args==['version']: print('MOCK KiCad 10.0.0 - NOT REAL');sys.exit(0)
if args[-1]=='--help':
    print('--schematic-parity --severity-all --exit-code-violations --format' + (' --refill-zones' if %s else ''))
    sys.exit(0)
if '--output' in args:
    target=pathlib.Path(args[args.index('--output')+1]);target.write_text('{"mock_test_only": true}')
    sys.exit(0)
sys.exit(10)
''' % ('True' if flag else 'False')
        fak.write_text(script);fak.chmod(0o755)
        env=os.environ.copy();env['PATH']=str(bin_dir)+':'+env.get('PATH','')
        outdir=tmp/'results'
        proc=subprocess.run(['bash',str(HERE/'RUN_KICAD_RX_V46.sh'),str(outdir)],env=env,text=True,capture_output=True)
        return proc, (outdir/'STATUS.txt').read_text(), (outdir/'DRC_PARITY_REFILL_V4.6.json').exists()

def main():
    before=hashlib.sha256(a.BRD.read_bytes()).hexdigest()
    r=a.run()
    ck('Static audit tied to actual source SHA',r['pcb_sha256']==before)
    ck('Correct amplifier reference',r['ref']=='U101')
    ck('Paddle nominal width 1.80 mm',r['paddle_size_mm'][0]==1.8)
    ck('Paddle nominal height 3.48 mm',r['paddle_size_mm'][1]==3.48)
    ck('Paddle area 6.264 mm2',r['paddle_copper_area_mm2']==6.264)
    ck('Paddle GND net',r['paddle_net']=='GND_RF')
    ck('No via centers inside pad',r['vias_centered_inside_paddle']==0)
    ck('Nearest via net ground and 0.5 mm copper edge gap',r['closest_ground_via']['copper_edge_gap_mm']==.5)
    ck('Nearest via diameter 0.7 mm',r['closest_ground_via']['diameter_mm']==.7)
    ck('Nearest via drill 0.3 mm',r['closest_ground_via']['drill_mm']==.3)
    ck('Four zones enumerated',r['ground_zone_count']==4)
    ck('All four layer names enumerated',set(r['ground_zones_layers'])=={'F.Cu','In1.Cu','In2.Cu','B.Cu'})
    ck('Four relevant SMA connectors not supply header',sorted(x['ref'] for x in r['sma'])==['J101','J102','J103','J104'])
    ck('All SMA have four custom GND pads',all(x['custom_ground_pad_count']==4 for x in r['sma']))
    ck('No factory CAD validation claimed',r['manufacturer_cad_te'].endswith('NO_FULL_APPROVAL'))
    ck('No native KiCad run claimed',r['kicad_erc_drc']=='NOT_RUN')
    ck('No fabrication approval claimed',r['decision']=='NO_FAB_NO_PCBWAY_NO_TX')
    with (ROOT/'MANIFEST_SHA256_V4.5.csv').open(newline='') as f:
        manifest={row['path']:row['sha256'] for row in csv.DictReader(f)}
    ck('Candidate board identical to V4.5 archive',before==manifest[str(a.BRD.relative_to(ROOT))])
    proc,status,exists=execute_fake(False)
    ck('KiCad 9-like missing refill flag rejects closed',proc.returncode==4 and 'NOT_RUN:' in status and not exists)
    proc,status,exists=execute_fake(True)
    ck('Simulated KiCad10 command flags exercised (MOCK ONLY)',proc.returncode==0 and 'NOT_APPROVED' in status and exists)
    ck('Fake KiCad10 never changes historical PCB',hashlib.sha256(a.BRD.read_bytes()).hexdigest()==before)
    # Deliberate alteration: create a temp variant with a via centered in the pad, rejected.
    with tempfile.TemporaryDirectory() as t:
        copy=Path(t)/a.BRD.name; raw=a.BRD.read_text()
        orig='(via (at 68 31.05)'; repl='(via (at 68 33.00)'
        ck('Tampering target via exists in source',orig in raw)
        copy.write_text(raw.replace(orig,repl,1))
        original=a.BRD;a.BRD=copy
        try:
            try:a.run(); rejected=False
            except AssertionError:rejected=True
        finally:a.BRD=original
        ck('Mutation with via-in-pad is rejected',rejected)
    # restore audit report after mutation: run() checked before writing, but assure anyway
    a.run()
    ck('Source still unchanged after mutation test',hashlib.sha256(a.BRD.read_bytes()).hexdigest()==before)
    return checks
if __name__=='__main__':
    for entry in main():print('PASS',entry)
    print('SUCCESS',len(checks),'static/launcher tests, ZERO native KiCad runs')
