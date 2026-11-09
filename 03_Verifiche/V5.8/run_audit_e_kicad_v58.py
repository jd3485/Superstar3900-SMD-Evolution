#!/usr/bin/env python3
"""Fail-closed V5.8 runner. Native KiCad is attempted only after RF screen passes."""
from pathlib import Path
import argparse,json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,'-B',str(HERE/'audit_ritorno_rf_v58.py'),'--output',str(out/'AUDIT_RF.json')]
    s=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    (out/'LOG_AUDIT_RF.txt').write_text(s.stdout+'\n'+s.stderr,encoding='utf-8')
    report={'revision':'V5.8','static_rf_audit':'PASS' if s.returncode==0 else 'FAIL',
            'kicad_cli_present':bool(shutil.which('kicad-cli')),
            'native_status':'NOT_RUN','release':'BLOCKED_NO_FAB',
            'fabrication_allowed':False,'tx_allowed':False}
    if s.returncode:
        report['native_status']='NOT_RUN_STATIC_AUDIT_FAILED';code=3
    elif not report['kicad_cli_present']:
        report['native_status']='NOT_RUN_KICAD_MISSING';code=5
    else:
        native=subprocess.run([sys.executable,'-B',str(ROOT/'03_Verifiche/V5.7/run_piani_e_kicad_v57.py'),
          '--output',str(out/'NATIVE_AND_GND')],cwd=ROOT,capture_output=True,text=True)
        (out/'LOG_NATIVE.txt').write_text(native.stdout+'\n'+native.stderr,encoding='utf-8')
        report['native_exit_code']=native.returncode
        report['native_status']='REPORTS_TO_REVIEW' if native.returncode==0 else 'NATIVE_FAILED_REVIEW_REQUIRED'
        code=0 if native.returncode==0 else 5
    (out/'STATUS_V5.8.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return code
if __name__=='__main__':raise SystemExit(main())
