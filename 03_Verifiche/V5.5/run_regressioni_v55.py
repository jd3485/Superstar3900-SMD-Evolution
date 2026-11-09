#!/usr/bin/env python3
"""Run all software test suites V4.0-V5.5, no KiCad native assertion."""
from pathlib import Path
import os,sys,subprocess,json,datetime
R=Path(__file__).resolve().parents[2]
paths=[
 'V4.0/test_radio_supervisor_v40.py','V4.1/test_audit_rf_v41.py',
 'V4.2/test_geometria_rf_v42.py','V4.3/test_candidato_sma_v43.py',
 'V4.4/test_schema_pcb_v44.py','V4.5/test_librerie_v45.py',
 'V4.6/test_rischi_v46.py','V4.7/test_audit_te_v47.py',
 'V4.8/test_variante_termica_v48.py','V4.9/test_v49.py',
 'V5.0/test_v50.py','V5.1/test_v51.py','V5.2/test_v52.py',
 'V5.3/test_v53.py','V5.4/test_native_runner_v54.py','V5.5/test_v55.py']
results=[]
for item in paths:
 p=R/'03_Verifiche'/item
 r=subprocess.run([sys.executable,'-B',str(p)],cwd=R,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},
                  text=True,capture_output=True,timeout=90)
 results.append({'script':item,'exit_code':r.returncode,'passed':r.returncode==0,
                 'tail':(r.stdout+'\n'+r.stderr)[-400:]})
report={'revision':'V5.5','date':'2026-11-08','software_suites':len(results),
        'passed':sum(x['passed'] for x in results),'native_kicad':'NOT_RUN',
        'fabrication_allowed':False,'results':results}
(R/'03_Verifiche/V5.5/REGRESSIONI_V5.5.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(report['passed'],'/',len(results))
for r in results: print('PASS' if r['passed'] else 'FAIL',r['script'])
raise SystemExit(0 if report['passed']==len(results) else 1)
