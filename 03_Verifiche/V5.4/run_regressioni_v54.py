#!/usr/bin/env python3
"""Non-native software regressions. Never modifies historical result files."""
from pathlib import Path
import datetime, json, os, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS = [
'V4.0/test_radio_supervisor_v40.py','V4.1/test_audit_rf_v41.py',
'V4.2/test_geometria_rf_v42.py','V4.3/test_candidato_sma_v43.py',
'V4.4/test_schema_pcb_v44.py','V4.5/test_librerie_v45.py',
'V4.6/test_rischi_v46.py','V4.7/test_audit_te_v47.py',
'V4.8/test_variante_termica_v48.py','V4.9/test_v49.py',
'V5.0/test_v50.py','V5.1/test_v51.py','V5.2/test_v52.py',
'V5.3/test_v53.py', 'V5.4/test_native_runner_v54.py']

def main():
  results=[]
  env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
  for p in PREVIOUS:
    cmd=[sys.executable,'-B',str(ROOT/'03_Verifiche'/p)]
    try:
      r=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,timeout=90)
      results.append({'script':p,'exit_code':r.returncode,'passed':r.returncode==0,'output_tail':(r.stdout+'\n'+r.stderr)[-2000:]})
    except subprocess.TimeoutExpired:
      results.append({'script':p,'exit_code':124,'passed':False,'output_tail':'TIMEOUT'})
  obj={'revision':'V5.4','date':'2026-11-08','native_kicad':'NOT_RUN',
       'software_suites':len(results),'passed':sum(r['passed'] for r in results),
       'description':'Static/software checks and MOCK CLI scenarios; not KiCad native DRC/ERC',
       'results':results}
  out=Path(__file__).with_name('REGRESSIONI_V5.4.json')
  out.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
  print(obj['passed'],'/',obj['software_suites'])
  for r in results: print('PASS' if r['passed'] else 'FAIL',r['script'])
  return 0 if obj['passed']==obj['software_suites'] else 1
if __name__=='__main__':sys.exit(main())
