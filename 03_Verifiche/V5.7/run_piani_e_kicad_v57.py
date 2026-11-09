#!/usr/bin/env python3
"""V5.7 fail-closed: static zone envelope + topology, then KiCad 10 on a copy if available.
No step authorizes fabrication, even if native reports appear successful.
"""
from pathlib import Path
import argparse, json, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
THIS=Path(__file__).resolve().parent
AUDIT=THIS/'audit_piani_gnd_v57.py'
TOPO=ROOT/'03_Verifiche/V5.6/audit_continuita_fcu_v56.py'
NATIVE=ROOT/'03_Verifiche/V5.5/run_native_v55.py'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    stages=[]
    for label,script,output in [('zone_envelope',AUDIT,'AUDIT_PIANI_GND_V5.7.json'),
                                ('topology_fcu',TOPO,'AUDIT_TOPOLOGIA_V5.7.json')]:
        p=subprocess.run([sys.executable,'-B',str(script),'--output',str(out/output)],
                          capture_output=True,text=True,cwd=ROOT)
        (out/f'LOG_{label.upper()}_V5.7.txt').write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
        stages.append({'step':label,'exit_code':p.returncode,'status':'STATIC_PASS' if p.returncode==0 else 'STATIC_FAIL'})
    available=bool(shutil.which('kicad-cli'))
    status={'revision':'V5.7','static_results':stages,'native_kicad_found':available,
            'native_status':'NOT_RUN','native_code':None,'release':'BLOCKED_NOT_FOR_FAB',
            'fabrication_allowed':False,'tx_allowed':False}
    if any(s['exit_code']!=0 for s in stages):
        status['native_status']='NOT_RUN_STATIC_FAILED';exit_code=3
    elif not available:
        status['native_status']='NOT_RUN_KICAD_MISSING';exit_code=5
    else:
        p=subprocess.run([sys.executable,'-B',str(NATIVE),'--output',str(out/'NATIVE_REPORTS_V5.7')],
                         capture_output=True,text=True,cwd=ROOT)
        (out/'LOG_NATIVE_V5.7.txt').write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
        status['native_code']=p.returncode
        status['native_status']='REPORTS_AWAIT_ENGINEER_REVIEW' if p.returncode==0 else 'NATIVE_FAILED_REVIEW_REQUIRED'
        exit_code=0 if p.returncode==0 else 5
    (out/'STATUS_V5.7.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(status,indent=2,ensure_ascii=False))
    return exit_code
if __name__=='__main__':raise SystemExit(main())
