#!/usr/bin/env python3
"""ERC+DRC KiCad 10 su COPIA temporanea. Nessun file CAM.
Il successo dei comandi non conferisce MAI autorizzazione alla fabbricazione.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REL='04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB'
STEM='S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def call(args, cwd=None):
    try:
        p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,timeout=120)
        return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except (OSError,subprocess.TimeoutExpired) as e:
        return {'returncode':99,'stdout':'','stderr':str(e)}
def run(root:Path,out:Path,executable:str|None=None):
    out.mkdir(parents=True,exist_ok=True)
    source=root/REL
    board=source/(STEM+'.kicad_pcb'); sch=source/(STEM+'.kicad_sch')
    record={'revision':'V5.0','date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'source_board_sha256':sha(board),'source_schematic_sha256':sha(sch),
      'native_erc':'NOT_RUN','native_drc':'NOT_RUN','parity':'NOT_RUN','zones':'NOT_RUN',
      'fabrication_authorized':False,'release_gate':'BLOCKED','reason':''}
    exe=executable or shutil.which('kicad-cli')
    if not exe:
        record['reason']='kicad-cli assente: NON ESEGUITI ERC, DRC, riempimento zone e parita'
        (out/'STATUS_V5.0.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
        return record
    ver=call([exe,'version']);helpd=call([exe,'pcb','drc','--help']);helpe=call([exe,'sch','erc','--help'])
    record['kicad_version']=ver['stdout'].strip()+ver['stderr'].strip()
    required_d=['--refill-zones','--schematic-parity','--severity-all','--exit-code-violations','--format']
    required_e=['--severity-all','--exit-code-violations','--format']
    if (ver['returncode']!=0 or helpd['returncode']!=0 or helpe['returncode']!=0 or
        not re.search(r'\b10\.',record['kicad_version']) or
        any(x not in helpd['stdout']+helpd['stderr'] for x in required_d) or
        any(x not in helpe['stdout']+helpe['stderr'] for x in required_e)):
        record['reason']='CLI KiCad 10 o funzioni richieste non disponibili; nessun controllo nativo eseguito'
        (out/'STATUS_V5.0.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
        return record
    with tempfile.TemporaryDirectory(prefix='s3900v50_native_') as tmp:
        temp=Path(tmp)/'progetto'; shutil.copytree(source,temp)
        erc=call([exe,'sch','erc','--format','json','--severity-all','--exit-code-violations',
                  '--output',str(out/'ERC_V5.0.json'),str(temp/(STEM+'.kicad_sch'))],cwd=temp)
        drc=call([exe,'pcb','drc','--format','json','--severity-all','--exit-code-violations',
                  '--schematic-parity','--refill-zones','--output',str(out/'DRC_PARITY_REFILL_V5.0.json'),
                  str(temp/(STEM+'.kicad_pcb'))],cwd=temp)
        (out/'LOG_ERC_V5.0.txt').write_text(erc['stdout']+'\nSTDERR:\n'+erc['stderr'])
        (out/'LOG_DRC_V5.0.txt').write_text(drc['stdout']+'\nSTDERR:\n'+drc['stderr'])
        record['erc_exit_code']=erc['returncode'];record['drc_exit_code']=drc['returncode']
        eok=erc['returncode']==0 and (out/'ERC_V5.0.json').is_file() and (out/'ERC_V5.0.json').stat().st_size>0
        dok=drc['returncode']==0 and (out/'DRC_PARITY_REFILL_V5.0.json').is_file() and (out/'DRC_PARITY_REFILL_V5.0.json').stat().st_size>0
        record['native_erc']='COMMAND_COMPLETED_REVIEW_REQUIRED' if eok else 'FAILED_OR_INCOMPLETE'
        record['native_drc']='COMMAND_COMPLETED_REVIEW_REQUIRED' if dok else 'FAILED_OR_INCOMPLETE'
        record['parity']=record['zones']='INCLUDED_IN_DRC_REVIEW_REQUIRED' if dok else 'FAILED_OR_INCOMPLETE'
        record['reason']='Comandi eseguiti su copia: esaminare i report; restano bloccanti CAD TE, termica, DFM, stackup, RF e collaudi' if eok and dok else 'Controllo nativo fallito o incompleto; leggere i log'
    if sha(board)!=record['source_board_sha256'] or sha(sch)!=record['source_schematic_sha256']:
        raise RuntimeError('ALERT: gli originali sono stati modificati!')
    (out/'STATUS_V5.0.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
    return record

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--output-dir',type=Path,default=Path.cwd()/'KICAD_V50_REPORTS')
    a=p.parse_args()
    r=run(a.root.resolve(),a.output_dir.resolve())
    print(json.dumps(r,indent=2,ensure_ascii=False))
    if r['native_erc']=='NOT_RUN':raise SystemExit(3)
    if r['native_erc']=='FAILED_OR_INCOMPLETE' or r['native_drc']=='FAILED_OR_INCOMPLETE':raise SystemExit(5)
if __name__=='__main__':main()
