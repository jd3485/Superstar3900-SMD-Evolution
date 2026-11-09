#!/usr/bin/env python3
"""Run historical test scripts + V5.7; software-only, no native KiCad."""
from pathlib import Path
import json,os,subprocess,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[2]
tests={
'V4.0':'test_radio_supervisor_v40.py','V4.1':'test_audit_rf_v41.py','V4.2':'test_geometria_rf_v42.py',
'V4.3':'test_candidato_sma_v43.py','V4.4':'test_schema_pcb_v44.py','V4.5':'test_librerie_v45.py',
'V4.6':'test_rischi_v46.py','V4.7':'test_audit_te_v47.py','V4.8':'test_variante_termica_v48.py',
'V4.9':'test_v49.py','V5.0':'test_v50.py','V5.1':'test_v51.py','V5.2':'test_v52.py',
'V5.3':'test_v53.py','V5.4':'test_native_runner_v54.py','V5.5':'test_v55.py',
'V5.6':'test_continuita_v56.py','V5.7':'test_piani_gnd_v57.py'}
records=[]
def run_one(rev,fn):
    rel=Path('03_Verifiche')/rev/fn
    try:
        p=subprocess.run([sys.executable,'-B',str(ROOT/rel)],cwd=ROOT,text=True,capture_output=True,timeout=100,
                         env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        return {'revision':rev,'script':rel.as_posix(),'status':'PASS' if p.returncode==0 else 'FAIL',
                        'return_code':p.returncode,'tail':(p.stdout+'\n'+p.stderr)[-1500:]}
    except subprocess.TimeoutExpired:
        return {'revision':rev,'script':rel.as_posix(),'status':'TIMEOUT','return_code':None}
with ThreadPoolExecutor(max_workers=5) as pool:
    futures={pool.submit(run_one,rev,fn):rev for rev,fn in tests.items()}
    for future in as_completed(futures):
        item=future.result();records.append(item)
        print(item['revision'],item['status'],flush=True)
records.sort(key=lambda r:list(tests).index(r['revision']))
report={'revision':'V5.7','suite_count':len(tests),'passed':sum(r['status']=='PASS' for r in records),
        'native_erc':'NOT_RUN','native_drc':'NOT_RUN','fabrication_allowed':False,'results':records}
out=Path(__file__).with_name('REGRESSIONI_V5.7.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for r in records:print(r['revision'],r['status'])
print('TOTAL',report['passed'],'/',report['suite_count'])
raise SystemExit(0 if report['passed']==len(tests) else 1)
