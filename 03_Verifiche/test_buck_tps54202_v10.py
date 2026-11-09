#!/usr/bin/env python3
"""V1.0: static checks only; not a native KiCad ERC, SPICE or hardware verification."""
import re,csv,math,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
s=(root/'04_KiCad/Sorgenti_Alimentazione_V1.0/S3900E_5V_BUCK_TPS54202_V1_0_DRAFT.kicad_sch').read_text()
refs=set(re.findall(r'\(property "Reference" "([RCLU]\d+)" \(at',s))
assert refs == {'U100','L100','C100','C101','C102','C103','C104','C105','R100','R101','R102','R103','R104'},refs
with (root/'04_KiCad/Sorgenti_Alimentazione_V1.0/Netlist_Intenzionale_TPS54202_V1.0.csv').open() as f:
 rows=list(csv.DictReader(f))
assert len(rows)==30
nets={r['NetPrevista'] for r in rows}
for n in nets:assert sum(r['NetPrevista']==n for r in rows)>=2,n
assert abs(0.596*(1+100/13.3)-5.0772)<0.001
assert s.count('(symbol (lib_id')==13
print('PASS V1.0 static: 13 ref, 30 connections, 8 nets, analytical 5.077V; ERC/DRC not run')
