#!/usr/bin/env python3
"""V4.0–V5.6 software-only regressions. Native KiCad never represented as run."""
from pathlib import Path
import subprocess, json, os, sys
ROOT=Path(__file__).resolve().parents[2]
tests={
 'V4.0':'test_radio_supervisor_v40.py','V4.1':'test_audit_rf_v41.py',
 'V4.2':'test_geometria_rf_v42.py','V4.3':'test_candidato_sma_v43.py',
 'V4.4':'test_schema_pcb_v44.py','V4.5':'test_librerie_v45.py',
 'V4.6':'test_rischi_v46.py','V4.7':'test_audit_te_v47.py',
 'V4.8':'test_variante_termica_v48.py','V4.9':'test_v49.py',
 'V5.0':'test_v50.py','V5.1':'test_v51.py','V5.2':'test_v52.py',
 'V5.3':'test_v53.py','V5.4':'test_native_runner_v54.py',
 'V5.5':'test_v55.py','V5.6':'test_continuita_v56.py'}
records=[]
for revision,filename in tests.items():
    rel=Path('03_Verifiche')/revision/filename
    proc=subprocess.run([sys.executable,'-B',str(ROOT/rel)],cwd=ROOT,capture_output=True,
            text=True,timeout=120,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    records.append({'revision':revision,'script':str(rel),'status':'PASS' if proc.returncode==0 else 'FAIL',
                    'return_code':proc.returncode,'last_output':(proc.stdout+'\n'+proc.stderr)[-2000:]})
report={'revision':'V5.6','total_suites':len(records),'passed':sum(x['status']=='PASS' for x in records),
        'native_erc':'NOT_RUN','native_drc':'NOT_RUN','fabrication_allowed':False,'results':records}
out=Path(__file__).with_name('REGRESSIONI_V5.6.json')
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"Suites software {report['passed']}/{report['total_suites']}")
for r in records:print(r['revision'],r['status'],r['return_code'])
raise SystemExit(0 if report['passed']==len(records) else 1)
