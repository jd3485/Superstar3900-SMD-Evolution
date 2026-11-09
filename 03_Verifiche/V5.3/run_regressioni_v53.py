#!/usr/bin/env python3
"""Reproduce V4.0–V5.3 software regressions; no native KiCad checks."""
from pathlib import Path
import json,sys,subprocess,os,datetime
ROOT=Path(__file__).resolve().parents[2]
SUITES=[
 'V4.0/test_radio_supervisor_v40.py',
 'V4.1/test_audit_rf_v41.py',
 'V4.2/test_geometria_rf_v42.py',
 'V4.3/test_candidato_sma_v43.py',
 'V4.4/test_schema_pcb_v44.py',
 'V4.5/test_librerie_v45.py',
 'V4.6/test_rischi_v46.py',
 'V4.7/test_audit_te_v47.py',
 'V4.8/test_variante_termica_v48.py',
 'V4.9/test_v49.py',
 'V5.0/test_v50.py',
 'V5.1/test_v51.py',
 'V5.2/test_v52.py',
 'V5.3/test_v53.py',
]
def main():
 results=[];env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
 for suite in SUITES:
  command=[sys.executable,'-B',str(ROOT/'03_Verifiche'/suite)]
  try:
   run=subprocess.run(command,cwd=ROOT,env=env,text=True,capture_output=True,timeout=45)
   res={'suite':suite,'exit_code':run.returncode,'passed':run.returncode==0,'stdout_tail':run.stdout[-1200:],'stderr_tail':run.stderr[-1200:]}
  except subprocess.TimeoutExpired:
   res={'suite':suite,'exit_code':None,'passed':False,'error':'Timeout 45 s'}
  results.append(res)
 output={'version':'V5.3','suite_count':len(results),'successful_suites':sum(x['passed'] for x in results),'results':results,'limitation':'Static/software checks only; native KiCad NOT_RUN'}
 path=ROOT/'03_Verifiche/V5.3/REGRESSIONI_V5.3.json'
 path.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
 print(f"Suites passed: {output['successful_suites']}/{output['suite_count']}")
 for r in results:print('OK' if r['passed'] else 'FAIL',r['suite'])
 return 0 if all(x['passed'] for x in results) else 1
if __name__=='__main__':sys.exit(main())
