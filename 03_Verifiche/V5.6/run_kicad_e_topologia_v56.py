#!/usr/bin/env python3
"""Local/CI gate: static topology FIRST, native KiCad second. NO FAB.
Writes review evidence into output directory; never edits original board.
"""
from pathlib import Path
import argparse, json, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
STATIC=Path(__file__).with_name('audit_continuita_fcu_v56.py')
NATIVE=ROOT/'03_Verifiche/V5.5/run_native_v55.py'
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    s=subprocess.run([sys.executable,'-B',str(STATIC),'--output',str(out/'AUDIT_CONTINUITA_V5.6.json')],capture_output=True,text=True)
    (out/'LOG_STATIC_V5.6.txt').write_text(s.stdout+'\n'+s.stderr,encoding='utf-8')
    result={'revision':'V5.6','static_return_code':s.returncode,'kicad_cli_available':bool(shutil.which('kicad-cli')),
            'native_status':'NOT_RUN','native_return_code':None,'release':'BLOCKED_NOT_FOR_FAB',
            'fabrication_allowed':False}
    if s.returncode!=0:
        result['native_status']='NOT_RUN_STATIC_FAILED'
        code=3
    elif not shutil.which('kicad-cli'):
        result['native_status']='NOT_RUN_KICAD_MISSING'
        code=5
    else:
        r=subprocess.run([sys.executable,'-B',str(NATIVE),'--output',str(out/'NATIVE_V5.6')],
                         capture_output=True,text=True)
        (out/'LOG_NATIVE_V5.6.txt').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
        result['native_return_code']=r.returncode
        result['native_status']='REVIEW_REPORTS_REQUIRED' if r.returncode==0 else 'FAILED_REVIEW_REPORTS'
        code=0 if r.returncode==0 else 5
    (out/'STATUS_V5.6.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return code
if __name__=='__main__':raise SystemExit(main())
