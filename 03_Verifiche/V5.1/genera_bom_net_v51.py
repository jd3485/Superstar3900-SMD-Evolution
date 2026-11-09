#!/usr/bin/env python3
"""Audit NON NATIVO dello schema elettrico per un candidato RX KiCad.
Legge il PCB, esporta BOM/netlist fisica e verifica alcune invarianti.
NON esegue KiCad ERC/DRC, non produce output CAM e NON approva la fabbricazione.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import csv, hashlib, io, json, math, re

ROOT = Path(__file__).resolve().parents[2]
BOARD_REL = Path('04_KiCad/Modulo_RX_Test_50ohm_V4.8_TERMICA_6VIE_STUDIO_NON_FAB/S3900E_RX_TEST_50R_V4_8_6VIE_STUDIO_NOT_FOR_FAB.kicad_pcb')
SCHEM_REL = BOARD_REL.with_suffix('.kicad_sch')


def block(s: str, index: int) -> str:
    if s[index] != '(': raise ValueError('expression does not start with (')
    level=0; quoted=False; escaped=False
    for j in range(index,len(s)):
        c=s[j]
        if quoted:
            if escaped: escaped=False
            elif c=='\\': escaped=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c=='(': level+=1
        elif c==')':
            level-=1
            if level==0: return s[index:j+1]
    raise ValueError('Unbalanced PCB S-expression')


def extract(text: str, prefix: str) -> list[str]:
    return [block(text,m.start()) for m in re.finditer(re.escape(prefix),text)]


def property_(body:str, key:str) -> str:
    m=re.search(r'\(property "'+re.escape(key)+r'" "([^\"]*)"',body)
    if not m: raise ValueError('Missing '+key)
    return m.group(1)


def audit(root:Path=ROOT) -> dict:
    bp=root/BOARD_REL;sp=root/SCHEM_REL
    b=bp.read_bytes();sch=sp.read_bytes();s=b.decode('utf-8')
    netmap={int(k):v for k,v in re.findall(r'\(net (\d+) "([^"]*)"\)',s.split('(footprint ')[0])}
    if not netmap or netmap.get(1)!='GND_RF': raise ValueError('Missing RF ground net')
    records=[];pins=[];refs=set()
    for fp in extract(s,'(footprint "'):
        reference=property_(fp,'Reference');value=property_(fp,'Value')
        name=re.match(r'\(footprint "([^\"]+)"',fp)
        if not name: raise ValueError('Missing footprint name')
        if reference in refs: raise ValueError('Duplicate reference '+reference)
        refs.add(reference)
        actual_pins=set()
        for pad in extract(fp,'(pad "'):
            number=re.match(r'\(pad "([^\"]+)"',pad).group(1)
            net=re.search(r'\(net (\d+) "([^"]+)"\)',pad)
            if not net:raise ValueError('Unconnected copper pad '+reference+'/'+number)
            k=int(net.group(1)); label=net.group(2)
            if netmap.get(k)!=label: raise ValueError('Net id/name mismatch '+reference+'/'+number)
            actual_pins.add((number,label))
        if not actual_pins:raise ValueError('No pads '+reference)
        for num, label in sorted(actual_pins):pins.append({'reference':reference,'pin':num,'net':label})
        if reference.startswith('J') and reference in ('J101','J102','J103','J104'):
            cls='RF connector';mpn='CONSMA002-SMD-G — da confermare TE';status='FOOTPRINT_NON_APPROVATO'
        elif reference=='U101':
            cls='RF amplifier';mpn='ADL5535 — verifica disponibilita e package';status='TERMICA_NON_APPROVATA'
        elif reference=='J105':
            cls='bench power input';mpn='Da definire (pads saldatura)';status='ASSEMBLAGGIO_DA_DEFINIRE'
        elif reference.startswith('R'):
            cls='resistor';mpn='Non assegnato';status='BOM_PRELIMINARE'
        elif reference.startswith('C'):
            cls='capacitor';mpn='Non assegnato';status='BOM_PRELIMINARE'
        elif reference.startswith('L'):
            cls='inductor';mpn='Non assegnato';status='BOM_PRELIMINARE'
        else:raise ValueError('Unexpected designator '+reference)
        records.append({'reference':reference,'value':value,'footprint':name.group(1),'type':cls,
                        'manufacturer_part_number':mpn,'approval_status':status,
                        'electrical_pins':len(actual_pins)})
    records.sort(key=lambda x:(x['reference'][0],int(re.search(r'\d+',x['reference']).group())))
    pins.sort(key=lambda x:(x['reference'],x['pin'],x['net']))
    if len(records)!=15:raise ValueError(f'Unexpected component count {len(records)}')
    if set(netmap.values())-set([''])!=set(p['net'] for p in pins):raise ValueError('Missing PCB nets')
    if len(netmap)!=9 or len([x for x in netmap.values() if x])!=8: raise ValueError('Unexpected number of nets')
    if len(pins)!=31:raise ValueError(f'Unexpected distinct electrical pins {len(pins)}')
    if sum(r['type']=='RF connector' for r in records)!=4:raise ValueError('SMA quantity changed')
    # A passive-only attenuation model; RF parasitics deliberately excluded.
    rv={r['reference']:r['value'] for r in records}
    if any(rv[k]!='150R' for k in ('R201','R202')) or rv['R203']!='37.4R':
        raise ValueError('Attenuator values have changed: review nominal model')
    rs=150.; rseries=37.4; z0=50.
    A=D=1+rseries/rs;B=rseries;C=2/rs+rseries/(rs*rs)
    den=A+B/z0+C*z0+D
    s21=2/den; s11=(A+B/z0-C*z0-D)/den
    pad_ideal_db=-20*math.log10(abs(s21))
    pinbyref={r['reference']:{p['pin']:p['net'] for p in pins if p['reference']==r['reference']} for r in records}
    expected={'J101':{'1':'RF_LNA_INPUT','2':'GND_RF'},
              'J102':{'1':'RF_LNA_OUT','2':'GND_RF'},
              'J103':{'1':'RF_ATTEN_IN','2':'GND_RF'},
              'J104':{'1':'RF_ATTEN_OUT','2':'GND_RF'},
              'J105':{'1':'+5V_BENCH','2':'GND_RF'},
              'U101':{'1':'RF_LNA_IC_IN','2':'GND_RF','3':'RF_BIAS_OUT'},
              'L101':{'1':'+5V_BENCH','2':'RF_BIAS_OUT'},
              'R201':{'1':'RF_ATTEN_IN','2':'GND_RF'},
              'R202':{'1':'RF_ATTEN_OUT','2':'GND_RF'},
              'R203':{'1':'RF_ATTEN_IN','2':'RF_ATTEN_OUT'}}
    for ref,mp in expected.items():
        if pinbyref.get(ref)!=mp:raise ValueError('Critical pin-net mismatch '+ref)
    # Only check actual local lib availability; does not prove KiCad parse/import.
    dir_=bp.parent
    missing=[]
    for rec in records:
        lib,short=rec['footprint'].split(':',1)
        p=dir_/(lib+'.pretty')/(short+'.kicad_mod')
        if not p.is_file():missing.append(str(p.relative_to(root)))
    if missing:raise ValueError('Missing local footprints: '+', '.join(missing))
    return {'revision':'V5.1','scope':'STATIC_BOM_NETLIST_FROM_UNAPPROVED_CANDIDATE',
      'source_board':str(BOARD_REL),'source_schematic':str(SCHEM_REL),
      'source_board_sha256':hashlib.sha256(b).hexdigest(),
      'source_schematic_sha256':hashlib.sha256(sch).hexdigest(),
      'total_components':len(records),'distinct_electrical_pins':len(pins),'non_empty_nets':len(netmap)-1,
      'footprint_local_files_present':True,
      'attenuator_ideal_50ohm_db':round(pad_ideal_db,6),
      'attenuator_s11_ideal_db':round(20*math.log10(abs(s11)),5),
      'components':records,'pins':pins,
      'limitations':['Non e un BOM approvato: MPN, potenza, tolleranze, derating e fornitura mancanti',
      'Il valore RF e solo modello resistivo ideale; nessuna misura o simulazione EM',
      'Le reti sono lette dal PCB; la parita con lo schema richiede KiCad nativo',
      'Nessun ERC, DRC, controllo impedenza, approvazione produttore o montaggio'],
      'native_erc':'NOT_RUN','native_drc':'NOT_RUN','fabrication_allowed':False,'tx_allowed':False}


def csv_bytes(rows:list[dict],columns:list[str]) -> bytes:
    buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=columns,lineterminator='\n');w.writeheader();w.writerows(rows)
    return buf.getvalue().encode('utf-8')


def save(root:Path=ROOT,out:Path|None=None) -> dict:
    result=audit(root)
    out=out or (root/'03_Verifiche/V5.1')
    out.mkdir(parents=True,exist_ok=True)
    (out/'BOM_RX_CANDIDATA_V5.1.csv').write_bytes(csv_bytes(result['components'],
        ['reference','value','footprint','type','manufacturer_part_number','approval_status','electrical_pins']))
    (out/'PIN_NET_RX_CANDIDATA_V5.1.csv').write_bytes(csv_bytes(result['pins'],['reference','pin','net']))
    (out/'AUDIT_BOM_NET_V5.1.json').write_text(json.dumps({k:v for k,v in result.items() if k not in ('components','pins')},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':
    d=save();print(f"V5.1 static inventory: {d['total_components']} components, {d['distinct_electrical_pins']} distinct pins, {d['non_empty_nets']} nets. NO FAB.")
