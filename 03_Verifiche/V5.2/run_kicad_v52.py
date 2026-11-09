#!/usr/bin/env python3
"""KiCad 10 native ERC/DRC on a disposable copy; no production files."""
from pathlib import Path
import argparse,subprocess,shutil,tempfile,json,hashlib,re,datetime,sys
ROOT=Path(__file__).resolve().parents[2]
FOLDER='04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB'
STEM='S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(args,cwd=None):
 try:
  p=subprocess.run(args,cwd=cwd,timeout=180,text=True,capture_output=True)
  return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 except Exception as ex:return {'returncode':99,'stdout':'','stderr':str(ex)}
def main():
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);args=a.parse_args()
 out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 src=ROOT/FOLDER;pcb=src/(STEM+'.kicad_pcb');sch=src/(STEM+'.kicad_sch')
 initial={'board':sha(pcb),'schematic':sha(sch)}
 status={'revision':'V5.2','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'source_sha256':initial,'erc':'NOT_RUN','drc':'NOT_RUN','refill':'NOT_RUN','parity':'NOT_RUN',
  'release':'BLOCKED','fabrication_authorized':False,'TX_allowed':False,'reason':''}
 exe=shutil.which('kicad-cli')
 if not exe:status['reason']='kicad-cli non disponibile in questo ambiente'
 else:
  ver=cmd([exe,'version']);eh=cmd([exe,'sch','erc','--help']);dh=cmd([exe,'pcb','drc','--help'])
  h=dh['stdout']+dh['stderr'];he=eh['stdout']+eh['stderr']
  if ver['returncode'] or eh['returncode'] or dh['returncode'] or not re.search(r'\b10\.',ver['stdout']+ver['stderr']) or any(x not in h for x in ('--refill-zones','--schematic-parity','--severity-all','--format','--exit-code-violations')) or any(x not in he for x in ('--severity-all','--format','--exit-code-violations')):
   status['reason']='KiCad 10 compatibile o opzioni necessarie non confermati'
  else:
   with tempfile.TemporaryDirectory(prefix='s3900_v52_') as tmp:
    work=Path(tmp)/'board';shutil.copytree(src,work)
    erc=cmd([exe,'sch','erc','--format','json','--severity-all','--exit-code-violations','--output',str(out/'ERC_V5.2.json'),str(work/(STEM+'.kicad_sch'))],cwd=work)
    drc=cmd([exe,'pcb','drc','--format','json','--severity-all','--exit-code-violations','--schematic-parity','--refill-zones','--output',str(out/'DRC_V5.2.json'),str(work/(STEM+'.kicad_pcb'))],cwd=work)
    (out/'LOG_ERC.txt').write_text(erc['stdout']+'\n'+erc['stderr']);(out/'LOG_DRC.txt').write_text(drc['stdout']+'\n'+drc['stderr'])
    for key,result,report in [('erc',erc,'ERC_V5.2.json'),('drc',drc,'DRC_V5.2.json')]:
     status[key+'_exit_code']=result['returncode'];status[key]='COMPLETED_REVIEW_REQUIRED' if result['returncode']==0 and (out/report).is_file() and (out/report).stat().st_size>0 else 'FAILED_OR_INCOMPLETE'
    if status['drc']=='COMPLETED_REVIEW_REQUIRED':status['refill']=status['parity']='IN_DRC_REVIEW_REQUIRED'
    status['reason']='Rapporti prodotti: richiedono revisione umana. Tutti gli altri gate di fabbricazione restano OPEN.'
 assert initial=={'board':sha(pcb),'schematic':sha(sch)},'SOURCE ALTERED'
 (out/'STATUS_V5.2.json').write_text(json.dumps(status,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(status,indent=2,ensure_ascii=False))
 return 3 if status['erc']=='NOT_RUN' else 5 if status['erc']=='FAILED_OR_INCOMPLETE' or status['drc']=='FAILED_OR_INCOMPLETE' else 0
if __name__=='__main__':sys.exit(main())
