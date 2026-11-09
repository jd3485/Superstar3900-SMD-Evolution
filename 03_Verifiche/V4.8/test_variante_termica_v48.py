#!/usr/bin/env python3
from pathlib import Path
import hashlib,re,json,sys
root=Path(__file__).resolve().parents[2]
a=json.loads((root/'03_Verifiche/V4.8/AUDIT_VARIANTE_TERMICA_V4.8.json').read_text())
src=(root/a['board_source']).read_bytes(); dst=(root/a['board_candidate']).read_bytes()
checks=[]
def ck(name,result):
    checks.append((name,bool(result)))
    print(('PASS' if result else 'FAIL')+' '+name)
ck('original SHA invariato',hashlib.sha256(src).hexdigest()==a['board_source_sha256'])
ck('candidato SHA invariato',hashlib.sha256(dst).hexdigest()==a['board_candidate_sha256'])
ck('sezioni via aggiunte esattamente sei',len(re.findall(rb'\(via \(at',dst))-len(re.findall(rb'\(via \(at',src))==6)
import uuid
lst=[]
for x,y in a['via_positions_mm']:
    tid=str(uuid.uuid5(uuid.NAMESPACE_DNS,f's3900e-v4.8-via-in-pad-GND-{x:.3f}-{y:.3f}'))
    lst.append(f'  (via (at {x:.3f} {y:.3f}) (size 0.55) (drill 0.25) (layers "F.Cu" "B.Cu") (net 1) (tstamp "{tid}"))')
block=('\n'.join(lst)+'\n').encode()
ck('differenza PCB limitata alle sei via GND',dst.count(block)==1 and dst.replace(block,b'',1)==src)
ck('numero via e rete',all(('(net 1) (tstamp ' in line) for line in lst))
xmin,ymin,xmax,ymax=a['U101_exposed_pad_bbox_mm']; r=a['via_copper_diameter_mm']/2
ck('centri e diametri dentro il pad',all(x-r>xmin and x+r<xmax and y-r>ymin and y+r<ymax for x,y in a['via_positions_mm']))
ck('passo tra vie maggiore del diametro',all(((x-u)**2+(y-v)**2)**.5>=2*r for i,(x,y) in enumerate(a['via_positions_mm']) for u,v in a['via_positions_mm'][i+1:]))
ck('studio non autorizzato alla fabbricazione',a['authorized_for_fab'] is False)
ck('nessun ERC/DRC nativo inventato',a['KiCad_ERC']=='NOT_RUN' and a['KiCad_DRC']=='NOT_RUN')
ck('nuova cartella schema presente',(root/'04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB.kicad_sch').exists())
print(f'RISULTATO: {sum(ok for _,ok in checks)}/{len(checks)}')
sys.exit(0 if all(ok for _,ok in checks) else 1)
