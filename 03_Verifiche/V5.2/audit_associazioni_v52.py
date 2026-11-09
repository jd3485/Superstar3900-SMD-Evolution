#!/usr/bin/env python3
"""V5.2: static identity checks, NOT KiCad ERC/DRC."""
from pathlib import Path
import re,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB'
NEW=ROOT/'04_KiCad/Modulo_RX_Test_50ohm_V5.2_PARITY_LINK_STUDY_NOT_FOR_FAB'
OLDSTEM='S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB'
NEWSTEM='S3900E_RX_TEST_50R_V5_2_LINKED_STUDY_NOT_FOR_FAB'
OLDPROJECT='S3900E_RX_TEST_50R_V4_5_LIBS_CANDIDATE_NOT_FOR_FAB'
def forms(text,head):
 result=[];pos=0
 while True:
  p=text.find(head,pos)
  if p<0:return result
  depth=0;inside=False;esc=False
  for i in range(p,len(text)):
   c=text[i]
   if inside:
    if esc:esc=False
    elif c=='\\':esc=True
    elif c=='"':inside=False
   elif c=='"':inside=True
   elif c=='(':depth+=1
   elif c==')':
    depth-=1
    if depth==0:
     result.append(text[p:i+1]);pos=i+1;break
  else:raise ValueError('Invalid S-expression')
def components(text,kind):
 blocks=forms(text,'(symbol (lib_id ' if kind=='sch' else '(footprint ')
 result={}
 for block in blocks:
  ref=re.search(r'\(property "Reference" "([A-Za-z]+\d+)"',block)
  if ref:
   assert ref.group(1) not in result
   result[ref.group(1)]=block
 return result
def check(olds,oldb,news,newb):
 failures=[]
 def assertit(test,msg):
  if not test:failures.append(msg)
 try:
  o=components(olds,'sch'); n=components(news,'sch'); p=components(newb,'pcb')
  root=re.search(r'\(uuid "([a-f0-9-]{36})"\)',olds)
  assertit(root is not None,'Root UUID missing')
  assertit(len(o)==len(n)==len(p)==15,'Reference list mismatch')
  assertit(set(o)==set(n)==set(p),'Different component references')
  assertit(olds.count('(project "'+OLDPROJECT+'"')==15,'Baseline V4.8 project mismatch not detected')
  assertit(news.count('(project "'+NEWSTEM+'"')==15,'New project instances not all renamed')
  assertit(news.replace('(project "'+NEWSTEM+'"','(project "'+OLDPROJECT+'"')==olds,'Unexpected schematic changes')
  assertit(re.sub(r' \(path "/[a-f0-9-]+/[a-f0-9-]+"\)','',newb)==oldb,'Copper or other PCB content changed')
  for ref,oldblock in o.items():
   uid=re.search(r'\(uuid "([a-f0-9-]{36})"\)',oldblock)
   assertit(uid is not None,'Missing UUID '+ref)
   if uid and root and ref in p:
    expected='(path "/'+root.group(1)+'/'+uid.group(1)+'")'
    assertit(p[ref].count(expected)==1,'Incorrect PCB path '+ref)
   assertit(ref in n and n[ref].replace('(project "'+NEWSTEM+'"','(project "'+OLDPROJECT+'"')==oldblock,'Symbol changed '+ref)
 except Exception as exc:failures.append(str(exc))
 return failures

def main():
 olds=(OLD/(OLDSTEM+'.kicad_sch')).read_text()
 oldb=(OLD/(OLDSTEM+'.kicad_pcb')).read_text()
 news=(NEW/(NEWSTEM+'.kicad_sch')).read_text()
 newb=(NEW/(NEWSTEM+'.kicad_pcb')).read_text()
 f=check(olds,oldb,news,newb)
 print(json.dumps({'revision':'V5.2','static_identity_checks':'PASS' if not f else 'FAIL', 'failures':f,'components':15,'link_paths':15,'native_erc':'NOT_RUN','native_drc':'NOT_RUN','fabrication_allowed':False},ensure_ascii=False,indent=2))
 return 1 if f else 0
if __name__=='__main__':sys.exit(main())
