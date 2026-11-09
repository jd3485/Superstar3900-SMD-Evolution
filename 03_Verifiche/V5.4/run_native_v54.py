#!/usr/bin/env python3
"""KiCad 10 ERC and DRC/parity on a temporary copy. Never releases fabrication.
Exit 0 = reports generated with zero CLI violations, but REVIEW REQUIRED;
exit 3 = unavailable or incompatible; exit 5 = violations/error/incomplete.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile
ROOT = Path(__file__).resolve().parents[2]
REL = Path('04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB')
STEM = 'S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB'
MAX_SECONDS = 240

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*')) if p.is_file()}

def launch(args, cwd=None):
    try:
        proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=MAX_SECONDS,
                              env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        return {'exit_code': proc.returncode, 'stdout': proc.stdout[-50000:], 'stderr': proc.stderr[-50000:]}
    except Exception as exc:
        return {'exit_code': 99, 'stdout':'', 'stderr': repr(exc)}

def json_valid(path):
    try:
        obj = json.loads(path.read_text(encoding='utf-8'))
        return isinstance(obj, dict) and bool(obj)
    except (OSError, ValueError, UnicodeError):
        return False

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True, type=Path)
    opts = p.parse_args(argv)
    out = opts.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    source = ROOT / REL
    baseline = inventory(source)
    status = {
        'revision': 'V5.4',
        'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'candidate': str(REL),
        'kicad_version': None,
        'source_sha256': baseline,
        'native_erc': 'NOT_RUN', 'native_drc': 'NOT_RUN',
        'zone_refill': 'NOT_RUN', 'schematic_parity': 'NOT_RUN',
        'fab_authorized': False, 'tx_enabled': False,
        'release': 'BLOCKED_NOT_FOR_FAB',
        'notes': [],
    }
    code = 3
    try:
        if not baseline or not (source / (STEM + '.kicad_sch')).is_file() or not (source / (STEM+'.kicad_pcb')).is_file():
            status['notes'].append('Candidate files missing: native check not performed')
        else:
            exe = shutil.which('kicad-cli')
            if not exe:
                status['notes'].append('kicad-cli absent; ERC/DRC/parity NOT_RUN')
            else:
                version = launch([exe, 'version'])
                status['kicad_version'] = (version['stdout'] + version['stderr']).strip()
                eh = launch([exe, 'sch', 'erc', '--help'])
                dh = launch([exe, 'pcb', 'drc', '--help'])
                eopt = eh['stdout'] + eh['stderr']
                dopt = dh['stdout'] + dh['stderr']
                ereq = ('--format', '--severity-all', '--exit-code-violations')
                dreq = ('--format', '--severity-all', '--exit-code-violations', '--refill-zones', '--schematic-parity')
                if (version['exit_code'] != 0 or eh['exit_code'] != 0 or dh['exit_code'] != 0
                    or not re.search(r'(?<!\d)10\.\d+', status['kicad_version'])
                    or any(s not in eopt for s in ereq) or any(s not in dopt for s in dreq)):
                    status['notes'].append('KiCad 10 or essential CLI flags not confirmed; NOT_RUN')
                else:
                    with tempfile.TemporaryDirectory(prefix='s3900_native_v54_') as temp:
                        target = Path(temp) / 'candidate'
                        shutil.copytree(source, target)
                        sch = target / (STEM+'.kicad_sch')
                        pcb = target / (STEM+'.kicad_pcb')
                        commands = [
                            ('erc', [exe, 'sch', 'erc', '--format', 'json', '--severity-all',
                                     '--exit-code-violations', '--output', str(out/'ERC_V5.4.json'), str(sch)]),
                            ('drc', [exe, 'pcb', 'drc', '--format', 'json', '--severity-all',
                                     '--exit-code-violations', '--schematic-parity', '--refill-zones',
                                     '--output', str(out/'DRC_PARITY_V5.4.json'), str(pcb)])
                        ]
                        code = 0
                        for which, command in commands:
                            r = launch(command, cwd=target)
                            (out / ('LOG_'+which.upper()+'_V5.4.txt')).write_text(
                                'EXIT_CODE='+str(r['exit_code'])+'\n'+r['stdout']+'\n'+r['stderr'], encoding='utf-8')
                            report = out / ('ERC_V5.4.json' if which=='erc' else 'DRC_PARITY_V5.4.json')
                            status['native_'+which+'_exit_code'] = r['exit_code']
                            status['native_'+which] = ('EXECUTED_REVIEW_REQUIRED' if r['exit_code']==0 and json_valid(report)
                                                        else 'VIOLATIONS_OR_INCOMPLETE')
                            if which=='drc':
                                status['zone_refill'] = status['schematic_parity'] = ('INCLUDED_IN_DRC_REVIEW_REQUIRED'
                                  if json_valid(report) else 'INCOMPLETE')
                            if status['native_'+which] != 'EXECUTED_REVIEW_REQUIRED':
                                code = 5
                        status['notes'].append('Native reports must be reviewed; never automatic fabrication approval')
    finally:
        status['source_unchanged'] = inventory(source) == baseline
        if not status['source_unchanged']:
            code = 5
            status['notes'].append('SOURCE FILE MODIFIED: BLOCKED')
        (out / 'STATUS_V5.4.json').write_text(json.dumps(status, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        print(json.dumps({k:v for k,v in status.items() if k!='source_sha256'}, indent=2, ensure_ascii=False))
    return code

if __name__=='__main__':
    sys.exit(main())
