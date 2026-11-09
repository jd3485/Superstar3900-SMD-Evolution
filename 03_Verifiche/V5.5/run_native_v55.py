#!/usr/bin/env python3
"""Run V5.4 native process, then V5.5 semantic JSON validation. Never approves FAB."""
from pathlib import Path
import argparse, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
PREV=ROOT/'03_Verifiche/V5.4/run_native_v54.py'
VALID=Path(__file__).with_name('validate_native_reports_v55.py')
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    before=subprocess.run([sys.executable,'-B',str(PREV),'--output',str(out)],capture_output=True,text=True)
    (out/'LOG_RUNNER_V5.4.txt').write_text(before.stdout+'\n'+before.stderr,encoding='utf-8')
    after=subprocess.run([sys.executable,'-B',str(VALID),str(out),'--output',str(out/'SUMMARY_V5.5.json')],capture_output=True,text=True)
    (out/'LOG_VALIDATOR_V5.5.txt').write_text(after.stdout+'\n'+after.stderr,encoding='utf-8')
    s=json.loads((out/'SUMMARY_V5.5.json').read_text())
    print(json.dumps({'runner_exit':before.returncode,'validator_exit':after.returncode,
                      'validation_status':s['status'],'fabrication_allowed':False},indent=2))
    return 0 if before.returncode==0 and after.returncode==0 else 5
if __name__=='__main__':sys.exit(main())
